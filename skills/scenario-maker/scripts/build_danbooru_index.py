#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import os
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "docs" / "danbooru_tags"
DEFAULT_TAGS_CSV = DATA_DIR / "danbooru_tags.csv"
DEFAULT_COOCCURRENCE_CSV = DATA_DIR / "danbooru_tags_cooccurrence.csv"
DEFAULT_DB = DATA_DIR / "danbooru_tags.sqlite"
CHUNK_SIZE = 10000


CATEGORY_NAMES = {
    0: "general",
    1: "artist",
    3: "copyright",
    4: "character",
    5: "meta",
}


def split_aliases(raw_aliases):
    return [alias.strip() for alias in (raw_aliases or "").split(",") if alias.strip()]


def normalize_lookup_text(value):
    return "_".join((value or "").strip().casefold().split())


def create_schema(conn):
    conn.executescript(
        """
        create table tags (
            tag text primary key,
            category integer not null,
            count integer not null,
            alias text not null default ''
        );

        create table aliases (
            alias text not null,
            normalized_alias text not null,
            tag text not null,
            primary key (alias, tag),
            foreign key (tag) references tags(tag)
        );

        create table cooccurrence (
            tag_a text not null,
            tag_b text not null,
            count real not null
        );

        create table metadata (
            key text primary key,
            value text not null
        );

        create index idx_tags_count on tags(count desc);
        create index idx_aliases_normalized_alias on aliases(normalized_alias);
        create index idx_aliases_tag on aliases(tag);
        create index idx_cooccurrence_tag_a_count on cooccurrence(tag_a, count desc);
        create index idx_cooccurrence_tag_b_count on cooccurrence(tag_b, count desc);
        """
    )


def require_columns(reader, required, path):
    missing = [column for column in required if column not in (reader.fieldnames or [])]
    if missing:
        raise ValueError(f"{path} is missing required columns: {', '.join(missing)}")


def load_tags(conn, tags_csv):
    tag_rows = 0
    alias_rows = 0

    def flush_tags(tag_chunk):
        if tag_chunk:
            conn.executemany(
                "insert or replace into tags(tag, category, count, alias) values (?, ?, ?, ?)",
                tag_chunk,
            )
            tag_chunk.clear()

    def flush_aliases(alias_chunk):
        if alias_chunk:
            conn.executemany(
                "insert or ignore into aliases(alias, normalized_alias, tag) values (?, ?, ?)",
                alias_chunk,
            )
            alias_chunk.clear()

    with Path(tags_csv).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        require_columns(reader, ["tag", "category", "count", "alias"], tags_csv)
        tag_chunk = []
        alias_chunk = []

        for row in reader:
            tag = row["tag"].strip()
            if not tag:
                continue

            tag_chunk.append(
                (
                    tag,
                    int(row["category"] or 0),
                    int(float(row["count"] or 0)),
                    row.get("alias") or "",
                )
            )
            tag_rows += 1

            for alias in split_aliases(row.get("alias")):
                alias_chunk.append((alias, normalize_lookup_text(alias), tag))
                alias_rows += 1

            if len(tag_chunk) >= CHUNK_SIZE:
                flush_tags(tag_chunk)

            if len(alias_chunk) >= CHUNK_SIZE:
                flush_tags(tag_chunk)
                flush_aliases(alias_chunk)

        flush_tags(tag_chunk)
        flush_aliases(alias_chunk)

    return tag_rows, alias_rows


def load_cooccurrence(conn, cooccurrence_csv):
    cooccurrence_rows = 0
    with Path(cooccurrence_csv).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        require_columns(reader, ["tag_a", "tag_b", "count"], cooccurrence_csv)
        chunk = []

        for row in reader:
            tag_a = row["tag_a"].strip()
            tag_b = row["tag_b"].strip()
            if not tag_a or not tag_b:
                continue

            chunk.append((tag_a, tag_b, float(row["count"] or 0)))
            cooccurrence_rows += 1

            if len(chunk) >= CHUNK_SIZE:
                conn.executemany(
                    "insert into cooccurrence(tag_a, tag_b, count) values (?, ?, ?)",
                    chunk,
                )
                chunk.clear()

        if chunk:
            conn.executemany(
                "insert into cooccurrence(tag_a, tag_b, count) values (?, ?, ?)",
                chunk,
            )

    return cooccurrence_rows


def write_metadata(conn, tags_csv, cooccurrence_csv, tag_rows, alias_rows, cooccurrence_rows):
    values = {
        "schema_version": "1",
        "tags_csv": str(Path(tags_csv)),
        "cooccurrence_csv": str(Path(cooccurrence_csv)),
        "tag_rows": str(tag_rows),
        "alias_rows": str(alias_rows),
        "cooccurrence_rows": str(cooccurrence_rows),
    }
    conn.executemany(
        "insert into metadata(key, value) values (?, ?)",
        sorted(values.items()),
    )


def build_index(tags_csv=DEFAULT_TAGS_CSV, cooccurrence_csv=DEFAULT_COOCCURRENCE_CSV, db_path=DEFAULT_DB, force=False):
    tags_csv = Path(tags_csv)
    cooccurrence_csv = Path(cooccurrence_csv)
    db_path = Path(db_path)
    temp_path = db_path.with_name(f"{db_path.name}.tmp")

    if db_path.exists() and not force:
        raise FileExistsError(f"{db_path} already exists; pass force=True or --force to rebuild")
    if not tags_csv.exists():
        raise FileNotFoundError(f"Missing tag CSV: {tags_csv}")
    if not cooccurrence_csv.exists():
        raise FileNotFoundError(f"Missing co-occurrence CSV: {cooccurrence_csv}")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    if temp_path.exists():
        temp_path.unlink()

    conn = sqlite3.connect(temp_path)
    try:
        conn.execute("pragma journal_mode = off")
        conn.execute("pragma synchronous = off")
        conn.execute("pragma temp_store = memory")
        conn.execute("pragma foreign_keys = on")
        create_schema(conn)
        tag_rows, alias_rows = load_tags(conn, tags_csv)
        cooccurrence_rows = load_cooccurrence(conn, cooccurrence_csv)
        write_metadata(conn, tags_csv, cooccurrence_csv, tag_rows, alias_rows, cooccurrence_rows)
        conn.commit()
    except Exception:
        conn.close()
        if temp_path.exists():
            temp_path.unlink()
        raise
    else:
        conn.close()
        os.replace(temp_path, db_path)

    return {
        "db_path": db_path,
        "tag_rows": tag_rows,
        "alias_rows": alias_rows,
        "cooccurrence_rows": cooccurrence_rows,
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Build a SQLite index for bundled Danbooru tag CSVs.")
    parser.add_argument("--tags-csv", type=Path, default=DEFAULT_TAGS_CSV)
    parser.add_argument("--cooccurrence-csv", type=Path, default=DEFAULT_COOCCURRENCE_CSV)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--force", action="store_true", help="Replace an existing SQLite index.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    result = build_index(args.tags_csv, args.cooccurrence_csv, args.db, force=args.force)
    print(
        "Built {db_path} ({tag_rows} tags, {alias_rows} aliases, {cooccurrence_rows} co-occurrences)".format(
            **result
        )
    )


if __name__ == "__main__":
    main()
