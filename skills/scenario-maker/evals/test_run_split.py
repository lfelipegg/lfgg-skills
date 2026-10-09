"""Offline regressions for rejecting invalid split inputs before paid capture."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

import run_split

EVALS = Path(__file__).resolve().parent


class SplitPreflightTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="scenario-split-preflight-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.evals = self.root / "evals"
        self.evals.mkdir()
        for filename in run_split.EVALUATION_FILES:
            target = self.evals / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(EVALS / filename, target)

        fixture_names = set()
        for filename in (*run_split.CASE_FILES, "split-boundaries.jsonl"):
            for row in self.rows(filename):
                fixture_names.update(row["fixtures"])
        for name in sorted(fixture_names):
            target = self.evals / "fixtures" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(EVALS / "fixtures" / name, target)

        self.baseline = self.root / "before"
        self.candidate_root = self.root / "skills"
        self.make_package(self.baseline, "scenario-maker", baseline=True)
        for skill in run_split.SKILLS:
            self.make_package(self.candidate_root / skill, skill)
        self.output = self.root / "captures"

    def make_package(self, root, skill, baseline=False):
        """Create complete, tiny package inputs without copying runtime CSVs."""
        files = set(run_split.COMMON_RUNTIME_FILES)
        files.update(run_split.MODEL_FILES[skill])
        if baseline:
            files.discard("references/models/wan.md")
        else:
            files.update(run_split.PACKAGE_FILES)
        for filename in sorted(files):
            target = root / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"Temporary preflight input: {filename}\n", encoding="utf-8")
        (root / "SKILL.md").write_text(
            f"---\nname: {skill}\ndescription: Disposable preflight fixture.\n---\n"
            f"# {skill}\n",
            encoding="utf-8",
        )

    def rows(self, filename):
        return [
            json.loads(line)
            for line in (self.evals / filename).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def write_rows(self, filename, rows):
        (self.evals / filename).write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )

    def assert_rejected_before_capture(self, message):
        # Popen is the external runtime boundary, independent of whether the
        # runner imports capture directly or calls it through run_baseline.
        with mock.patch(
            "subprocess.Popen",
            side_effect=AssertionError("Invalid inputs must not launch paid capture"),
        ) as launch:
            with self.assertRaisesRegex(run_split.InputError, message):
                run_split.preflight(
                    self.baseline, self.candidate_root, "corpus", evals=self.evals
                )
            with mock.patch.object(run_split, "EVALS", self.evals):
                with contextlib.redirect_stderr(io.StringIO()) as errors:
                    with self.assertRaises(SystemExit) as stopped:
                        run_split.main([
                            "--baseline", str(self.baseline),
                            "--candidate-root", str(self.candidate_root),
                            "--out", str(self.output),
                            "--suite", "corpus",
                            "--timeout", "1",
                            "--jobs", "1",
                        ])
            self.assertEqual(stopped.exception.code, 2)
            self.assertRegex(errors.getvalue(), message)
            launch.assert_not_called()
        self.assertFalse(self.output.exists(), "Rejected input must not create evidence")

    def test_complete_inputs_resolve_explicit_case_ownership_without_capture(self):
        with mock.patch(
            "subprocess.Popen",
            side_effect=AssertionError("Preflight must not launch paid capture"),
        ) as launch:
            validated = run_split.preflight(
                self.baseline, self.candidate_root, "corpus", evals=self.evals
            )
            cases = {row["id"]: row for row in validated["cases"]}
            self.assertEqual(cases["case-01"]["selected_skill"], "scenario-maker-sdxl")
            self.assertEqual(
                cases["h3-dev-21h"]["selected_skill"], "scenario-maker-minimax-h3"
            )
            self.assertEqual(cases["p4-dev-10"]["selected_skill"], "scenario-maker")
            launch.assert_not_called()

    def test_missing_ownership_is_rejected_before_capture(self):
        path = self.evals / "split-routes.json"
        routes = json.loads(path.read_text(encoding="utf-8"))
        del routes["case-02"]
        path.write_text(json.dumps(routes) + "\n", encoding="utf-8")
        self.assert_rejected_before_capture("case-02")

    def test_duplicate_json_ownership_key_is_rejected_before_capture(self):
        path = self.evals / "split-routes.json"
        source = path.read_text(encoding="utf-8").rstrip()
        path.write_text(
            source[:-1] + ',\n  "case-01": "scenario-maker-pony"\n}\n',
            encoding="utf-8",
        )
        self.assert_rejected_before_capture("(?i)duplicate.*case-01|case-01.*duplicate")

    def test_duplicate_source_ids_are_rejected_within_and_across_files(self):
        filename = "phase-three-probes.jsonl"
        original = self.rows(filename)
        for duplicate in (original[0], self.rows("h3-probes.jsonl")[0]):
            with self.subTest(duplicate_id=duplicate["id"]):
                self.write_rows(filename, [*original, duplicate])
                self.assert_rejected_before_capture(
                    rf"(?i)duplicate.*{duplicate['id']}|{duplicate['id']}.*duplicate"
                )

    def test_unsafe_existing_fixture_paths_are_rejected_before_capture(self):
        outside = self.evals / "outside.png"
        outside.write_bytes(b"fixture must not escape its declared directory")
        (self.evals / "fixtures" / "nested").mkdir()
        filename = "phase-three-probes.jsonl"
        for fixture in ("../outside.png", "nested/../../outside.png", str(outside)):
            with self.subTest(fixture=fixture):
                rows = self.rows(filename)
                rows[0]["fixtures"] = [fixture]
                self.write_rows(filename, rows)
                self.assert_rejected_before_capture("(?i)fixture")

    def test_missing_selected_package_is_rejected_before_capture(self):
        shutil.rmtree(self.candidate_root / "scenario-maker-sdxl")
        self.assert_rejected_before_capture("scenario-maker-sdxl")


if __name__ == "__main__":
    unittest.main()
