import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DanbooruLookupTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        self.tags_csv = self.root / "danbooru_tags.csv"
        self.cooccurrence_csv = self.root / "danbooru_tags_cooccurrence.csv"
        self.db_path = self.root / "danbooru_tags.sqlite"
        self.write_csvs()

    def tearDown(self):
        self.tmpdir.cleanup()

    def write_csvs(self):
        with self.tags_csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["tag", "category", "count", "alias"])
            writer.writeheader()
            writer.writerows(
                [
                    {"tag": "1girl", "category": "0", "count": "1000", "alias": "girl,solo female"},
                    {"tag": "solo", "category": "0", "count": "900", "alias": "alone"},
                    {"tag": "black_hair", "category": "0", "count": "800", "alias": "raven hair,dark hair"},
                    {"tag": "long_hair", "category": "0", "count": "700", "alias": "long hair"},
                    {"tag": "hair_ornament", "category": "0", "count": "2000000", "alias": "hair accessory"},
                    {"tag": "rain", "category": "0", "count": "400", "alias": "rainy"},
                    {"tag": "artist_name", "category": "1", "count": "50", "alias": "sample artist"},
                ]
            )
        with self.cooccurrence_csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["tag_a", "tag_b", "count"])
            writer.writeheader()
            writer.writerows(
                [
                    {"tag_a": "1girl", "tag_b": "solo", "count": "650.0"},
                    {"tag_a": "black_hair", "tag_b": "long_hair", "count": "550.0"},
                    {"tag_a": "rain", "tag_b": "1girl", "count": "300.0"},
                    {"tag_a": "hair_ornament", "tag_b": "1girl", "count": "100.0"},
                ]
            )

    def build_index(self):
        builder = load_script("build_danbooru_index")
        builder.build_index(self.tags_csv, self.cooccurrence_csv, self.db_path, force=True)

    def test_builder_creates_tables_and_indexes(self):
        self.build_index()
        sqlite3 = __import__("sqlite3")
        with sqlite3.connect(self.db_path) as conn:
            tables = {
                row[0]
                for row in conn.execute(
                    "select name from sqlite_master where type = 'table' order by name"
                )
            }
            indexes = {
                row[0]
                for row in conn.execute(
                    "select name from sqlite_master where type = 'index' order by name"
                )
            }
        self.assertGreaterEqual({"tags", "aliases", "cooccurrence", "metadata"}, tables)
        self.assertIn("idx_aliases_normalized_alias", indexes)
        self.assertIn("idx_tags_count", indexes)
        self.assertIn("idx_cooccurrence_tag_a_count", indexes)
        self.assertIn("idx_cooccurrence_tag_b_count", indexes)

    def test_alias_splitting_maps_aliases_to_canonical_tags(self):
        self.build_index()
        lookup = load_script("danbooru_lookup")
        results = lookup.aliases(self.db_path, "raven hair", limit=5)
        self.assertEqual(results[0]["tag"], "black_hair")
        self.assertEqual(results[0]["alias"], "raven hair")

    def test_alias_chunk_flush_waits_for_tag_rows(self):
        builder = load_script("build_danbooru_index")
        original_chunk_size = builder.CHUNK_SIZE
        builder.CHUNK_SIZE = 2
        try:
            builder.build_index(self.tags_csv, self.cooccurrence_csv, self.db_path, force=True)
        finally:
            builder.CHUNK_SIZE = original_chunk_size

        lookup = load_script("danbooru_lookup")
        results = lookup.aliases(self.db_path, "solo female", limit=5)
        self.assertEqual(results[0]["tag"], "1girl")

    def test_search_ranks_exact_and_alias_hits_above_loose_matches(self):
        self.build_index()
        lookup = load_script("danbooru_lookup")

        exact_results = lookup.search(self.db_path, "black hair", limit=5)
        self.assertEqual(exact_results[0]["tag"], "black_hair")
        self.assertEqual(exact_results[0]["match"], "exact_tag")

        alias_results = lookup.search(self.db_path, "raven hair", limit=5)
        self.assertEqual(alias_results[0]["tag"], "black_hair")
        self.assertEqual(alias_results[0]["match"], "exact_alias")
        self.assertNotEqual(alias_results[0]["tag"], "hair_ornament")

    def test_related_works_from_either_cooccurrence_direction(self):
        self.build_index()
        lookup = load_script("danbooru_lookup")

        from_left = lookup.related(self.db_path, "black_hair", limit=5)
        self.assertEqual(from_left[0]["tag"], "long_hair")

        from_right = lookup.related(self.db_path, "long_hair", limit=5)
        self.assertEqual(from_right[0]["tag"], "black_hair")

    def test_suggest_returns_seed_matches_and_related_candidates(self):
        self.build_index()
        lookup = load_script("danbooru_lookup")
        results = lookup.suggest(self.db_path, "solo girl with long black hair in rain", limit=5)
        tags = [result["tag"] for result in results]
        sources = {result["tag"]: result["source"] for result in results}

        self.assertEqual({"solo", "1girl", "black_hair", "long_hair", "rain"}, set(tags))
        self.assertNotIn("hair_ornament", tags)
        self.assertEqual(sources["1girl"], "seed")
        self.assertEqual(sources["long_hair"], "seed")

    def test_cli_json_output_is_stable(self):
        self.build_index()
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "danbooru_lookup.py"),
                "--db",
                str(self.db_path),
                "--json",
                "search",
                "black hair",
                "--limit",
                "1",
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["command"], "search")
        self.assertEqual(payload["results"][0]["tag"], "black_hair")


if __name__ == "__main__":
    unittest.main()
