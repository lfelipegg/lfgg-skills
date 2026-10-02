import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "character_generator.py"


def run_cli(*args, check=True):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=check,
        text=True,
        capture_output=True,
    )


class CharacterGeneratorTest(unittest.TestCase):
    def test_seeded_random_generation_is_deterministic(self):
        first = run_cli("--seed", "7", "--count", "2").stdout
        second = run_cli("--seed", "7", "--count", "2").stdout

        self.assertEqual(first, second)
        self.assertIn("Character 1", first)
        self.assertIn("Character 2", first)

    def test_default_output_includes_danbooru_and_prose(self):
        output = run_cli("--seed", "1").stdout

        self.assertIn("Danbooru:", output)
        self.assertIn("Prose:", output)
        self.assertRegex(output, r"1(girl|boy|other)")
        self.assertIn("adult", output.casefold())

    def test_json_output_contains_required_groups_and_rendered_prompts(self):
        output = run_cli("--seed", "3", "--format", "json").stdout
        payload = json.loads(output)

        self.assertEqual(1, len(payload["characters"]))
        character = payload["characters"][0]
        for field in [
            "gender",
            "hair_color",
            "bangs",
            "hair_style",
            "hair_length",
            "skin_color",
            "body_type",
            "clothes",
            "breast_size",
            "tanline",
            "danbooru",
            "prose",
        ]:
            self.assertIn(field, character)

    def test_female_generation_includes_breast_size(self):
        output = run_cli("--gender", "female", "--seed", "10", "--format", "json").stdout
        character = json.loads(output)["characters"][0]

        self.assertIsNotNone(character["breast_size"])
        self.assertIn(character["breast_size"]["tag"], character["danbooru"])

    def test_male_and_nonbinary_generation_omit_breast_size(self):
        for gender in ["male", "nonbinary"]:
            output = run_cli("--gender", gender, "--seed", "10", "--format", "json").stdout
            character = json.loads(output)["characters"][0]

            self.assertIsNone(character["breast_size"])
            self.assertNotIn("breasts", character["danbooru"])

    def test_breast_size_rejected_for_non_female_gender(self):
        result = run_cli("--gender", "male", "--breast-size", "large", check=False)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("--breast-size can only be used with --gender female", result.stderr)

    def test_friendly_overrides_are_normalized(self):
        output = run_cli(
            "--gender",
            "female",
            "--hair-color",
            "black",
            "--bangs",
            "parted",
            "--hair-style",
            "high ponytail",
            "--hair-length",
            "long",
            "--skin-color",
            "dark",
            "--body-type",
            "athletic",
            "--clothes",
            "hoodie",
            "--breast-size",
            "medium",
            "--format",
            "json",
        ).stdout
        character = json.loads(output)["characters"][0]

        self.assertIn("black_hair", character["danbooru"])
        self.assertIn("parted_bangs", character["danbooru"])
        self.assertIn("high_ponytail", character["danbooru"])
        self.assertIn("long_hair", character["danbooru"])
        self.assertIn("dark_skin", character["danbooru"])
        self.assertIn("toned", character["danbooru"])
        self.assertIn("abs", character["danbooru"])
        self.assertIn("hoodie", character["danbooru"])
        self.assertIn("medium_breasts", character["danbooru"])

    def test_revealing_tanline_requires_opt_in(self):
        rejected = run_cli("--tanline", "pasties tan", check=False)

        self.assertNotEqual(0, rejected.returncode)
        self.assertIn("requires --allow-revealing", rejected.stderr)

        accepted = run_cli("--tanline", "pasties tan", "--allow-revealing").stdout
        self.assertIn("pasties_tan", accepted)

    def test_format_danbooru_prints_only_tags(self):
        output = run_cli("--seed", "2", "--format", "danbooru").stdout.strip()

        self.assertNotIn("Prose:", output)
        self.assertNotIn("Danbooru:", output)
        self.assertIn(",", output)

    def test_list_options_prints_group_names_and_aliases(self):
        output = run_cli("--list-options").stdout

        self.assertIn("gender", output)
        self.assertIn("hair_color", output)
        self.assertIn("body_type", output)
        self.assertIn("athletic", output)

    def test_minor_coded_terms_are_rejected(self):
        result = run_cli("--clothes", "schoolgirl", check=False)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("minor-coded", result.stderr)


if __name__ == "__main__":
    unittest.main()
