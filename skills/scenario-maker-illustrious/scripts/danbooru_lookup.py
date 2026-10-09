#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_danbooru_index import CATEGORY_NAMES, DEFAULT_COOCCURRENCE_CSV, DEFAULT_DB, DEFAULT_TAGS_CSV, build_index


STOPWORDS = {
    "a",
    "an",
    "and",
    "at",
    "by",
    "for",
    "from",
    "in",
    "into",
    "of",
    "on",
    "the",
    "to",
    "under",
    "with",
}


def category_name(category):
    return CATEGORY_NAMES.get(category, "unknown")


def normalize_lookup_text(value):
    return "_".join((value or "").strip().casefold().split())


def escape_like(value):
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def ensure_index(db_path=DEFAULT_DB):
    db_path = Path(db_path)
    if not db_path.exists():
        build_index(DEFAULT_TAGS_CSV, DEFAULT_COOCCURRENCE_CSV, db_path, force=False)
    return db_path


def connect(db_path):
    db_path = ensure_index(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def result_from_row(row, match=None, alias=None, score=0):
    category = row["category"]
    return {
        "tag": row["tag"],
        "category": category,
        "category_name": category_name(category),
        "count": row["count"],
        "match": match,
        "alias": alias,
        "score": score,
    }


def add_candidate(candidates, row, match, alias=None, score=0):
    tag = row["tag"]
    result = result_from_row(row, match=match, alias=alias, score=score)
    current = candidates.get(tag)
    if current is None or (result["score"], result["count"]) > (current["score"], current["count"]):
        candidates[tag] = result


def search(db_path, query, limit=20):
    normalized = normalize_lookup_text(query)
    if not normalized:
        return []

    like_value = escape_like(normalized)
    prefix = f"{like_value}%"
    contains = f"%{like_value}%"
    candidates = {}

    with connect(db_path) as conn:
        for row in conn.execute(
            "select tag, category, count from tags where tag = ?",
            (normalized,),
        ):
            add_candidate(candidates, row, "exact_tag", score=600000)

        for row in conn.execute(
            """
            select t.tag, t.category, t.count, a.alias
            from aliases a
            join tags t on t.tag = a.tag
            where a.normalized_alias = ?
            order by t.count desc, t.tag asc
            limit ?
            """,
            (normalized, limit),
        ):
            add_candidate(candidates, row, "exact_alias", alias=row["alias"], score=500000)

        for row in conn.execute(
            """
            select tag, category, count
            from tags
            where tag like ? escape '\\'
            order by count desc, tag asc
            limit ?
            """,
            (prefix, limit),
        ):
            add_candidate(candidates, row, "prefix_tag", score=400000)

        for row in conn.execute(
            """
            select t.tag, t.category, t.count, a.alias
            from aliases a
            join tags t on t.tag = a.tag
            where a.normalized_alias like ? escape '\\'
            order by t.count desc, t.tag asc
            limit ?
            """,
            (prefix, limit),
        ):
            add_candidate(candidates, row, "prefix_alias", alias=row["alias"], score=350000)

        for row in conn.execute(
            """
            select tag, category, count
            from tags
            where tag like ? escape '\\'
            order by count desc, tag asc
            limit ?
            """,
            (contains, limit),
        ):
            add_candidate(candidates, row, "contains_tag", score=200000)

        for row in conn.execute(
            """
            select t.tag, t.category, t.count, a.alias
            from aliases a
            join tags t on t.tag = a.tag
            where a.normalized_alias like ? escape '\\'
            order by t.count desc, t.tag asc
            limit ?
            """,
            (contains, limit),
        ):
            add_candidate(candidates, row, "contains_alias", alias=row["alias"], score=150000)

    return sorted(candidates.values(), key=lambda item: (-item["score"], -item["count"], item["tag"]))[:limit]


def tag_info(db_path, tag, alias_limit=20):
    normalized = normalize_lookup_text(tag)
    with connect(db_path) as conn:
        row = conn.execute(
            "select tag, category, count, alias from tags where tag = ?",
            (normalized,),
        ).fetchone()
        if row is None:
            return None
        alias_rows = conn.execute(
            """
            select alias
            from aliases
            where tag = ?
            order by normalized_alias asc
            limit ?
            """,
            (normalized, alias_limit),
        ).fetchall()
    return {
        "tag": row["tag"],
        "category": row["category"],
        "category_name": category_name(row["category"]),
        "count": row["count"],
        "aliases": [alias_row["alias"] for alias_row in alias_rows],
    }


def aliases(db_path, query, limit=20):
    normalized = normalize_lookup_text(query)
    if not normalized:
        return []

    like_value = escape_like(normalized)
    prefix = f"{like_value}%"
    contains = f"%{like_value}%"

    with connect(db_path) as conn:
        rows = conn.execute(
            """
            select a.alias, a.normalized_alias, t.tag, t.category, t.count,
                case
                    when a.normalized_alias = ? then 0
                    when a.normalized_alias like ? escape '\\' then 1
                    else 2
                end as rank
            from aliases a
            join tags t on t.tag = a.tag
            where a.normalized_alias = ?
                or a.normalized_alias like ? escape '\\'
                or a.normalized_alias like ? escape '\\'
            order by rank asc, t.count desc, a.normalized_alias asc, t.tag asc
            limit ?
            """,
            (normalized, prefix, normalized, prefix, contains, limit),
        ).fetchall()

    return [
        {
            "alias": row["alias"],
            "normalized_alias": row["normalized_alias"],
            "tag": row["tag"],
            "category": row["category"],
            "category_name": category_name(row["category"]),
            "count": row["count"],
        }
        for row in rows
    ]


def related(db_path, tag, limit=30):
    normalized = normalize_lookup_text(tag)
    if not normalized:
        return []

    with connect(db_path) as conn:
        rows = conn.execute(
            """
            with related_tags as (
                select tag_b as tag, count from cooccurrence where tag_a = ?
                union all
                select tag_a as tag, count from cooccurrence where tag_b = ?
            ),
            ranked as (
                select tag, max(count) as cooccurrence_count
                from related_tags
                group by tag
            )
            select r.tag, r.cooccurrence_count, t.category, t.count
            from ranked r
            left join tags t on t.tag = r.tag
            order by r.cooccurrence_count desc, coalesce(t.count, 0) desc, r.tag asc
            limit ?
            """,
            (normalized, normalized, limit),
        ).fetchall()

    return [
        {
            "tag": row["tag"],
            "category": row["category"],
            "category_name": category_name(row["category"]) if row["category"] is not None else "unknown",
            "count": row["count"] or 0,
            "cooccurrence_count": row["cooccurrence_count"],
        }
        for row in rows
    ]


def phrase_candidates(text, max_words=3):
    words = [word for word in re.findall(r"[\w]+", text.casefold()) if word not in STOPWORDS]
    phrases = []
    seen = set()

    def add_phrase(phrase):
        normalized = normalize_lookup_text(phrase)
        if normalized and normalized not in seen:
            seen.add(normalized)
            phrases.append(phrase)

    for width in range(max_words, 0, -1):
        for start in range(0, max(len(words) - width + 1, 0)):
            add_phrase(" ".join(words[start : start + width]))
            if width == 3:
                add_phrase(f"{words[start]} {words[start + 2]}")
    return phrases


def suggest(db_path, text, limit=40):
    seeds = {}
    for phrase in phrase_candidates(text):
        for hit in search(db_path, phrase, limit=5):
            if hit["match"] not in {"exact_tag", "exact_alias"}:
                continue
            seed_score = hit["score"] + hit["count"]
            current = seeds.get(hit["tag"])
            if current is None or seed_score > current["score"]:
                seeds[hit["tag"]] = {
                    "tag": hit["tag"],
                    "category": hit["category"],
                    "category_name": hit["category_name"],
                    "count": hit["count"],
                    "source": "seed",
                    "matched": phrase,
                    "match": hit["match"],
                    "score": seed_score,
                }

    candidates = dict(seeds)
    for seed in list(seeds.values()):
        for related_hit in related(db_path, seed["tag"], limit=10):
            if related_hit["tag"] in candidates:
                continue
            candidates[related_hit["tag"]] = {
                "tag": related_hit["tag"],
                "category": related_hit["category"],
                "category_name": related_hit["category_name"],
                "count": related_hit["count"],
                "source": f"related:{seed['tag']}",
                "matched": seed["tag"],
                "match": "cooccurrence",
                "score": related_hit["cooccurrence_count"],
                "cooccurrence_count": related_hit["cooccurrence_count"],
            }

    return sorted(
        candidates.values(),
        key=lambda item: (item["source"] != "seed", -item["score"], -item["count"], item["tag"]),
    )[:limit]


def format_tag_line(result):
    pieces = [
        result["tag"],
        f"[{result['category_name']}]",
        f"count={result['count']}",
    ]
    if result.get("match"):
        pieces.append(f"match={result['match']}")
    if result.get("alias"):
        pieces.append(f"alias={result['alias']}")
    if result.get("source"):
        pieces.append(f"source={result['source']}")
    if result.get("cooccurrence_count") is not None:
        pieces.append(f"cooccurrence={result['cooccurrence_count']:g}")
    return " ".join(pieces)


def print_plain(command, payload):
    if command == "tag":
        if payload is None:
            print("No tag found.")
            return
        print(f"{payload['tag']} [{payload['category_name']}] count={payload['count']}")
        if payload["aliases"]:
            print("aliases: " + ", ".join(payload["aliases"]))
        return

    if not payload:
        print("No results.")
        return

    for result in payload:
        if command == "aliases":
            print(
                "{alias} -> {tag} [{category_name}] count={count}".format(
                    **result
                )
            )
        else:
            print(format_tag_line(result))


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Query the bundled Danbooru SQLite tag index.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Search canonical tags and aliases.")
    search_parser.add_argument("query", nargs="+")
    search_parser.add_argument("--limit", type=int, default=20)

    tag_parser = subparsers.add_parser("tag", help="Show details for a canonical tag.")
    tag_parser.add_argument("tag")
    tag_parser.add_argument("--alias-limit", type=int, default=20)

    aliases_parser = subparsers.add_parser("aliases", help="Search aliases and their canonical tags.")
    aliases_parser.add_argument("query", nargs="+")
    aliases_parser.add_argument("--limit", type=int, default=20)

    related_parser = subparsers.add_parser("related", help="Show co-occurring tags.")
    related_parser.add_argument("tag")
    related_parser.add_argument("--limit", type=int, default=30)

    suggest_parser = subparsers.add_parser("suggest", help="Suggest tags from natural-language text.")
    suggest_parser.add_argument("text", nargs="+")
    suggest_parser.add_argument("--limit", type=int, default=40)

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if args.command == "search":
        query = " ".join(args.query)
        result = search(args.db, query, limit=args.limit)
        payload = {"command": args.command, "query": query, "results": result}
    elif args.command == "tag":
        result = tag_info(args.db, args.tag, alias_limit=args.alias_limit)
        payload = {"command": args.command, "query": args.tag, "result": result}
    elif args.command == "aliases":
        query = " ".join(args.query)
        result = aliases(args.db, query, limit=args.limit)
        payload = {"command": args.command, "query": query, "results": result}
    elif args.command == "related":
        result = related(args.db, args.tag, limit=args.limit)
        payload = {"command": args.command, "query": args.tag, "results": result}
    elif args.command == "suggest":
        query = " ".join(args.text)
        result = suggest(args.db, query, limit=args.limit)
        payload = {"command": args.command, "query": query, "results": result}
    else:
        raise ValueError(f"Unsupported command: {args.command}")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    if "results" in payload:
        print_plain(args.command, payload["results"])
    else:
        print_plain(args.command, payload["result"])


if __name__ == "__main__":
    main()
