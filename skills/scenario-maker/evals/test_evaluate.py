"""Regression for real OMP lookup calls using an explicit workspace cwd."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

EVALS = Path(__file__).resolve().parent


class LookupTraceEvidenceTest(unittest.TestCase):
    def test_captured_lookup_is_scored_and_available_to_human_review(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "scores"
            subprocess.run([
                "python3", str(EVALS / "evaluate.py"),
                "--cases", str(EVALS / "cases.jsonl"),
                "--results", str(EVALS / "fixtures/lookup-trace"),
                "--out", str(output),
            ], check=True, capture_output=True, text=True)
            scores = [json.loads(line) for line in (output / "scores.jsonl").read_text().splitlines()]
            lookup_scores = [row for row in scores if row["case_id"] == "case-11"]
            self.assertEqual({row["attempt"] for row in lookup_scores}, {1, 2, 3})
            for row in lookup_scores:
                criteria = {item["criterion_id"]: item for item in row["criteria"]}
                self.assertEqual(criteria["C11-TRACE"]["state"], "passed")
                self.assertEqual(criteria["C11-LOOKUP-EVIDENCE"]["state"], "not-run")
            cards = [json.loads(line) for line in (output / "review-packet.jsonl").read_text().splitlines()]
            for card in cards:
                if "observable_lookup_trace" not in card:
                    continue
                trace = card["observable_lookup_trace"]
                self.assertEqual(trace["availability"], "available")
                self.assertNotIn("/tmp/scenario-maker-eval-", json.dumps(card))


if __name__ == "__main__":
    unittest.main()
