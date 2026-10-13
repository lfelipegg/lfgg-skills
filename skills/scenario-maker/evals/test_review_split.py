"""Offline semantic-review uncertainty, grounding, and three-repetition gates."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import review_split as review


def packet(attempt=1, paired=True, advisory=False):
    output = {"available": True, "capture_issues": [], "final_output": "A blue mug remains on a white shelf.",
              "partial_output": None, "artifacts": [], "tool_evidence": []}
    return {"case_id": "test-case", "attempt": attempt, "paired": paired, "request": "Preserve the blue mug on the white shelf.",
            "criteria": [{"id": "ORIGINAL-PRESERVE", "description": "Preserve all supplied facts.", "severity": "hard"},
                         {"id": "ORIGINAL-STYLE", "description": "Use concise natural language.", "severity": "advisory" if advisory else "hard"}],
            "rubric": {"references": [{"path": "references/constraints-and-revisions.md", "text": "Preserve all supplied facts."}], "invocation_contract": None},
            "fixtures": [], "outputs": {"a": copy.deepcopy(output), "b": copy.deepcopy(output) if paired else None}}


def judgment(source, a="passed", b="passed", style_a="passed", style_b="passed", adjudication=False):
    def proof(label, state, index):
        return {"reason": "Observed output evaluated against supplied contract.",
                "observations": [] if state == "not-run" else [{"path": f"/outputs/{label}/final_output", "quote": "blue mug"}],
                "rules": [] if state == "not-run" else [{"path": f"/criteria/{index}/description", "quote": source["criteria"][index]["description"]}]}
    criteria = []
    for index, (left, right) in enumerate(((a, b), (style_a, style_b))):
        criteria.append({"id": source["criteria"][index]["id"], "a": left, "b": right if source["paired"] else None,
                         "evidence": {"a": proof("a", left, index), "b": proof("b", right, index) if source["paired"] else None}})
    hard = [item for index, item in enumerate(criteria) if source["criteria"][index]["severity"] == "hard"]
    changed = source["paired"] and any({item["a"], item["b"]} == {"passed", "failed"} for item in hard)
    missing = any(item[label] == "not-run" for item in hard for label in (("a", "b") if source["paired"] else ("a",)))
    regression = None if not source["paired"] else True if changed else None if missing else False
    return {"case_id": source["case_id"], "attempt": source["attempt"], "reviewer_kind": "ai", "criteria": criteria,
            "regression": regression, "rationale": {"explanation": "Independent reassessment.", "novel_contract_failures": []} if adjudication else "Contract-based comparison."}


def envelope(value, valid=True):
    return {"valid": valid, "judgment": value}


class JudgmentValidationTest(unittest.TestCase):
    def test_original_ids_and_complete_grounded_review_are_accepted(self):
        source = packet()
        value = judgment(source)
        self.assertIs(review.validate_judgment(value, source), value)
        self.assertEqual(review.criteria_for({"id": "probe", "expected_behavior": ["First", "Second"]}), [
            {"id": "probe-E1", "description": "First", "severity": "hard", "method": "ai-supplemental"},
            {"id": "probe-E2", "description": "Second", "severity": "hard", "method": "ai-supplemental"}])

    def test_review_identity_is_bound_to_its_noninitial_repetition(self):
        source = packet(attempt=2)
        value = judgment(source)
        self.assertIs(review.validate_judgment(value, source), value)
        for field, wrong in (("case_id", "another-case"), ("attempt", 1), ("attempt", 2.0), ("attempt", True)):
            with self.subTest(field=field, wrong=wrong):
                invalid = copy.deepcopy(value)
                invalid[field] = wrong
                with self.assertRaisesRegex(review.ReviewError, "case ID/attempt mismatch"):
                    review.validate_judgment(invalid, source)

    def test_missing_duplicate_and_unknown_criteria_are_rejected(self):
        source = packet()
        for mutation in ("missing", "duplicate", "unknown"):
            with self.subTest(mutation=mutation):
                value = judgment(source)
                if mutation == "missing":
                    value["criteria"].pop()
                elif mutation == "duplicate":
                    value["criteria"].append(copy.deepcopy(value["criteria"][0]))
                else:
                    value["criteria"][0]["id"] = "replacement-ID"
                with self.assertRaisesRegex(review.ReviewError, "coverage"):
                    review.validate_judgment(value, source)

    def test_human_identity_and_invalid_states_are_rejected(self):
        source = packet()
        value = judgment(source)
        value["reviewer_kind"] = "human:AI"
        with self.assertRaisesRegex(review.ReviewError, "must be ai"):
            review.validate_judgment(value, source)
        value = judgment(source)
        value["criteria"][0]["a"] = "probably-passed"
        with self.assertRaisesRegex(review.ReviewError, "state"):
            review.validate_judgment(value, source)

    def test_missing_capture_cannot_be_promoted_by_partial_output(self):
        source = packet()
        source["outputs"]["a"].update(available=False, final_output=None, partial_output="blue mug")
        with self.assertRaisesRegex(review.ReviewError, "missing/failed capture"):
            review.validate_judgment(judgment(source), source)
        uncertain = judgment(source, a="not-run", style_a="not-run")
        self.assertIs(review.validate_judgment(uncertain, source), uncertain)
        self.assertIsNone(uncertain["regression"])

    def test_single_output_requires_b_and_b_evidence_null(self):
        source = packet(paired=False)
        value = judgment(source)
        review.validate_judgment(value, source)
        for field in ("b", "evidence"):
            invalid = copy.deepcopy(value)
            if field == "b":
                invalid["criteria"][0]["b"] = "passed"
            else:
                invalid["criteria"][0]["evidence"]["b"] = {"reason": "Invented baseline"}
            with self.assertRaisesRegex(review.ReviewError, "must be null"):
                review.validate_judgment(invalid, source)

    def test_missing_fabricated_and_wrong_side_evidence_are_rejected(self):
        source = packet()
        for mutation in ("missing", "fabricated", "wrong-side", "rubric-header"):
            with self.subTest(mutation=mutation):
                value = judgment(source)
                proof = value["criteria"][0]["evidence"]["a"]
                if mutation == "missing":
                    proof["observations"] = []
                elif mutation == "fabricated":
                    proof["observations"][0]["quote"] = "a scene fact that does not exist"
                elif mutation == "wrong-side":
                    proof["observations"][0]["path"] = "/outputs/b/final_output"
                else:
                    proof["rules"][0] = {"path": "/rubric/references/0/path", "quote": "constraints"}
                with self.assertRaises(review.ReviewError):
                    review.validate_judgment(value, source)

    def test_regression_is_direction_neutral_but_not_a_style_preference(self):
        source = packet(advisory=True)
        for left, right in (("passed", "failed"), ("failed", "passed")):
            value = judgment(source, a=left, b=right)
            self.assertTrue(review.validate_judgment(value, source)["regression"])
            value["regression"] = False
            with self.assertRaisesRegex(review.ReviewError, "regression inconsistent"):
                review.validate_judgment(value, source)
        advisory = judgment(source, style_b="failed")
        self.assertFalse(review.validate_judgment(advisory, source)["regression"])
        self.assertFalse(review.needs_adjudication(advisory, source))

    def test_adjudication_schema_and_novelty_are_grounded_and_hard_only(self):
        source = packet(advisory=True)
        source["review_mode"] = "independent-adjudication"
        source["repetition_evidence"] = {label: [{"attempt": attempt, "output": copy.deepcopy(source["outputs"][label])} for attempt in (1, 2, 3)] for label in ("a", "b")}
        value = judgment(source, b="failed", adjudication=True)
        claim = {"criterion_id": "ORIGINAL-PRESERVE", "label": "b", "category": "preservation", "reason": "Specific condition absent from all opposite-side attempts.",
                 "observations": [{"path": "/outputs/b/final_output", "quote": "blue mug"}],
                 "rules": [{"path": "/criteria/0/description", "quote": "Preserve all supplied facts."}],
                 "comparisons": [{"path": "/repetition_evidence/a/0/output/final_output", "quote": "blue mug"}]}
        value["rationale"]["novel_contract_failures"] = [claim]
        review.validate_judgment(value, source)
        for mutation in ("string-rationale", "advisory", "passed-side", "no-comparison", "fake-quote"):
            with self.subTest(mutation=mutation):
                invalid = copy.deepcopy(value)
                if mutation == "string-rationale":
                    invalid["rationale"] = "Unstructured assertion"
                elif mutation == "advisory":
                    invalid["rationale"]["novel_contract_failures"][0]["criterion_id"] = "ORIGINAL-STYLE"
                elif mutation == "passed-side":
                    invalid["rationale"]["novel_contract_failures"][0]["label"] = "a"
                elif mutation == "no-comparison":
                    invalid["rationale"]["novel_contract_failures"][0]["comparisons"] = []
                else:
                    invalid["rationale"]["novel_contract_failures"][0]["rules"][0]["quote"] = "made up source rule"
                with self.assertRaises(review.ReviewError):
                    review.validate_judgment(invalid, source)

    def test_missing_adjudication_stays_unresolved_and_reversal_rejects_allegation(self):
        source = packet()
        first = envelope(judgment(source, b="failed"))
        unresolved = review.disposition(first, None, source)
        self.assertTrue(unresolved["unresolved"])
        self.assertEqual(unresolved["judgment"]["criteria"][0]["b"], "failed")
        reversal = envelope(judgment(source, a="failed", b="passed", adjudication=True))
        final = review.disposition(first, reversal, source)
        self.assertEqual(final["state"], "rejected-on-evidence")
        self.assertEqual(final["allegations"][0]["state"], "rejected-on-evidence")


class AggregationTest(unittest.TestCase):
    def cohort(self, states, advisory=False, paired=True, boundary=False):
        packets, mappings, reviews, adjudications = [], [], {}, {}
        for attempt, (baseline, candidate) in enumerate(states, 1):
            source = packet(attempt=attempt, paired=paired, advisory=advisory)
            key = source["case_id"], attempt
            packets.append({"packet": source, "suite": "boundary" if boundary else "corpus"})
            # Exercise both orientations, rather than assume A is baseline.
            flipped = paired and attempt == 2
            mappings.append({"case_id": source["case_id"], "attempt": attempt,
                             "a": "candidate" if flipped or not paired else "baseline", "b": "baseline" if flipped else "candidate" if paired else None})
            left, right = (candidate, baseline) if flipped or not paired else (baseline, candidate)
            value = judgment(source, a=left, b=right)
            reviews[key] = envelope(value)
            if review.needs_adjudication(value, source):
                adjudications[key] = envelope(judgment(source, a=left, b=right, adjudication=True))
        return packets, mappings, reviews, adjudications

    def test_equal_counts_do_not_create_stricter_per_slot_gate(self):
        data = self.cohort([("failed", "passed"), ("passed", "failed"), ("passed", "passed")])
        summary = review.aggregate(*data)
        self.assertTrue(summary["gates"]["candidate_per_criterion_failures_not_above_baseline"])
        self.assertTrue(summary["gates"]["no_new_candidate_contract_failures"])
        self.assertEqual(len(summary["preexisting_baseline_failures"]), 1)
        self.assertEqual(summary["raw_counts"]["alleged_regressions"], 2)

    def test_excess_failures_and_always_passing_protection_block(self):
        data = self.cohort([("passed", "passed"), ("passed", "failed"), ("passed", "passed")])
        summary = review.aggregate(*data)
        self.assertFalse(summary["gates"]["candidate_per_criterion_failures_not_above_baseline"])
        self.assertFalse(summary["gates"]["baseline_always_pass_protected"])
        self.assertEqual(summary["baseline_always_pass_violations"][0]["candidate"]["failed"], 1)

    def test_single_boundary_failure_and_missing_review_never_pass(self):
        data = self.cohort([("passed", "failed"), ("passed", "passed"), ("passed", "passed")], paired=False, boundary=True)
        summary = review.aggregate(*data)
        self.assertFalse(summary["gates"]["all_boundary_checks_pass"])
        data[2].pop(("test-case", 3))
        incomplete = review.aggregate(*data)
        self.assertFalse(incomplete["gates"]["reviews_complete"])
        self.assertTrue(incomplete["not_run"])

    def test_adjudication_history_keeps_same_anonymous_side_across_all_reps(self):
        data = self.cohort([("failed", "passed"), ("passed", "failed"), ("passed", "passed")])
        packets, mappings, reviews, _ = data
        for item in packets:
            source = item["packet"]
            labels = mappings[source["attempt"] - 1]
            for label in ("a", "b"):
                source["outputs"][label]["final_output"] = f"{labels[label]} observation {source['attempt']}"
        current = packets[1]
        independent = review.adjudication_packet(current, packets, mappings, reviews[("test-case", 2)])
        self.assertEqual([row["attempt"] for row in independent["repetition_evidence"]["a"]], [1, 2, 3])
        self.assertEqual([row["output"]["final_output"] for row in independent["repetition_evidence"]["a"]],
                         [f"candidate observation {attempt}" for attempt in (1, 2, 3)])
        self.assertNotIn("label-map", independent)

    def test_explicit_independent_novelty_blocks_even_when_counts_equal(self):
        data = self.cohort([("failed", "passed"), ("passed", "failed"), ("passed", "passed")])
        candidate_failure = data[3][("test-case", 2)]["judgment"]
        candidate_failure["rationale"]["novel_contract_failures"] = [{"criterion_id": "ORIGINAL-PRESERVE", "label": "a", "category": "preservation", "reason": "Different, evidence-backed contract failure.", "observations": [], "rules": [], "comparisons": []}]
        # Aggregate consumes strictly validated envelopes; citation validation
        # itself is covered above. This unit isolates the novelty gate.
        summary = review.aggregate(*data)
        self.assertTrue(summary["gates"]["candidate_per_criterion_failures_not_above_baseline"])
        self.assertFalse(summary["gates"]["no_new_candidate_contract_failures"])


@unittest.skipUnless(os.name == "posix", "POSIX pipe and executable semantics")
class ReviewerProcessTest(unittest.TestCase):
    def test_reviewer_receives_eof_while_parent_stdin_pipe_stays_open(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executable = root / "bin" / "omp"
            executable.parent.mkdir()
            executable.write_text(
                f"#!{sys.executable}\n"
                "import os, select, sys\n"
                "ready, _, _ = select.select([0], [], [], 2)\n"
                "if not ready or os.read(0, 1) != b'':\n"
                "    sys.stderr.write('stdin did not receive EOF\\n')\n"
                "    sys.exit(23)\n"
                "sys.stderr.write('stdin EOF\\n')\n",
                encoding="utf-8",
            )
            executable.chmod(0o755)
            (root / "input.json").write_text(json.dumps(packet()), encoding="utf-8")
            (root / "system.txt").write_text("Offline stdin diagnostic.", encoding="utf-8")
            (root / "config.json").write_text("{}", encoding="utf-8")
            runner = (
                "import json, sys; from pathlib import Path; "
                "sys.path.insert(0, sys.argv[1]); import review_split as review; "
                "root = Path(sys.argv[2]); "
                "result = review.run_reviewer(json.loads((root / 'input.json').read_text()), "
                "root / 'reviews/test-case/attempt-1', root / 'scratch', "
                "root / 'system.txt', root / 'config.json', 900); "
                "print(json.dumps(result['execution']))"
            )
            environment = {**os.environ, "PATH": str(executable.parent), "PYTHONDONTWRITEBYTECODE": "1"}
            # This pipe's writer stays open through both reviewer and runner exit.
            with subprocess.Popen(
                [sys.executable, "-c", runner, str(review.EVALS), str(root)],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=environment,
            ) as process:
                try:
                    process.wait(timeout=10)
                    output, error = process.stdout.read(), process.stderr.read()
                finally:
                    if process.poll() is None:
                        process.kill()
                    process.wait()
                self.assertFalse(process.stdin.closed)
                self.assertEqual(process.returncode, 0, error.decode())
                self.assertEqual(json.loads(output), {"status": "completed", "exit_code": 0, "error": None})
            self.assertEqual((root / "reviews/test-case/attempt-1/stderr.txt").read_text(), "stdin EOF\n")


class CaptureEvidenceTest(unittest.TestCase):
    def test_reviewer_queries_are_local_and_escape_or_write_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source = packet()
            events = [{"type": "tool_execution_start", "toolName": "read", "args": {"path": "packet.json?q=.outputs.a.final_output&raw=true"}},
                      {"type": "tool_execution_start", "toolName": "glob", "args": {"path": "**/*.json"}}]
            self.assertEqual(review.reviewer_tool_violations(events, workspace, source), [])
            for name, path in (("read", "../label-map.json"), ("read", "https://example.test/"), ("write", "packet.json")):
                with self.subTest(name=name, path=path):
                    forbidden = [{"type": "tool_execution_start", "toolName": name, "args": {"path": path}}]
                    self.assertTrue(review.reviewer_tool_violations(forbidden, workspace, source))

    def test_missing_slot_is_retained_and_integrity_mismatch_rejects_before_launch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            case = {"id": "test-case", "request": "Preserve the blue mug.", "fixtures": [], "selected_skill": "scenario-maker", "case_source": "cases.jsonl"}
            slot = {"case_id": "test-case", "attempt": 1, "side": "baseline"}
            files = {"SKILL.md": "0" * 64}
            manifest = {"suite": "corpus", "source_manifests": {"baseline": files}, "baseline_revision": review.rb.manifest_identity(files)}
            with mock.patch("subprocess.Popen", side_effect=AssertionError("No paid model in validation")) as launch:
                missing = review.validate_attempt(root, case, slot, None, manifest)
                self.assertFalse(missing["available"])
                directory = review.attempt_directory(root, case, 1, "baseline", "corpus")
                directory.mkdir(parents=True)
                (directory / "output.txt").write_text("retained output", encoding="utf-8")
                record = {"case_id": "test-case", "attempt": 1, "comparison_side": "baseline", "selected_skill": "scenario-maker",
                          "selected_skill_sha256": review.rb.manifest_identity(files), "case_source": "cases.jsonl", "revision": manifest["baseline_revision"],
                          "model_requested": review.rb.MODEL, "reasoning_requested": "high", "attempt_manifest": (directory / "attempt.json").relative_to(root).as_posix(),
                          "raw": {"output": "output.txt"}, "raw_checksums": {"output.txt": "f" * 64}, "artifacts": []}
                review.rb.save_json(directory / "attempt.json", record)
                record["attempt_manifest_sha256"] = review.rb.digest(directory / "attempt.json")
                with self.assertRaisesRegex(review.ReviewError, "hash mismatch"):
                    review.validate_attempt(root, case, slot, record, manifest)
                launch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
