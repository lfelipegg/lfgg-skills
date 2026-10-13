"""Deterministic historical acceptance bindings and independent adjudication tests."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import review_acceptance_history as history
import review_split as review
import run_baseline as rb


def _events(text):
    return [{"type": "message_end", "message": {"role": "assistant", "stopReason": "stop",
              "content": [{"type": "text", "text": text}]}}, {"type": "agent_end", "isTerminal": True}]


def _save_trace(path, events):
    path.write_text("".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events), encoding="utf-8")


def _judgment(packet, a="failed", b="passed", independent=False):
    def evidence(label):
        return {"reason": "The required binding is assessed against the complete response.",
                "observations": [{"path": f"/outputs/{label}/final_output", "quote": packet["outputs"][label]["final_output"]}],
                "rules": [{"path": "/criteria/0/description", "quote": packet["criteria"][0]["description"]}]}
    return {"case_id": packet["case_id"], "attempt": packet["attempt"], "reviewer_kind": "ai",
            "criteria": [{"id": history.CRITERION_ID, "a": a, "b": b, "evidence": {"a": evidence("a"), "b": evidence("b")}}],
            "regression": a != b,
            "rationale": {"explanation": "Independently inspected all repetitions.", "novel_contract_failures": []}
                         if independent else "Original baseline-only binding allegation."}


class HistoricalFixture:
    """Use real packet/capture/envelope validation, not mocked success predicates."""
    def __init__(self, root):
        self.root = root
        self.source = root / "ai-review"
        self.source.mkdir()
        self.inputs = root / "inputs"
        self.inputs.mkdir()
        (self.inputs / "omp-config.json").write_text("{}\n", encoding="utf-8")
        (self.source / "provenance").mkdir()
        for name, content in (("review_split.py", "# historical implementation\n"),
                              ("reviewer-system.txt", "Review the complete evidence.\n"), ("omp-config.json", "{}\n")):
            (self.source / "provenance" / name).write_text(content, encoding="utf-8")
        self.case = {"id": history.CASE_ID, "case_source": "h3-guide-probes.jsonl", "selected_skill": "scenario-maker-minimax-h3",
                     "request": "Bind all references in their supplied order.", "fixtures": []}
        baseline_files = {"SKILL.md": "b" * 64}
        candidate_files = {"scenario-maker-minimax-h3": {"SKILL.md": "c" * 64}}
        self.corpus = {"root": root / "corpus", "inputs": self.inputs, "baseline": root / "baseline",
                       "cases": {history.CASE_ID: self.case}, "captures": {},
                       "manifest": {"suite": "corpus", "baseline_revision": history.BASELINE_REVISION,
                                    "candidate_revision": history.CANDIDATE_REVISION, "candidate_snapshots": {},
                                    "source_manifests": {"baseline": baseline_files, "candidate": candidate_files},
                                    "fixtures": {}, "schedule": [], "attempts": []}}
        self.corpus["root"].mkdir()
        self.boundary = {"root": root / "boundary", "manifest": {"suite": "boundary", "baseline_revision": history.BASELINE_REVISION,
                         "candidate_revision": history.CANDIDATE_REVISION}}
        self.boundary["root"].mkdir()
        for attempt in (1, 2, 3):
            for side in ("baseline", "candidate"):
                directory = self.corpus["root"] / "probes" / side / history.CASE_ID / f"attempt-{attempt}"
                directory.mkdir(parents=True)
                text = f"{side.title()} reference response, repetition {attempt}."
                events = _events(text)
                _save_trace(directory / "trace.jsonl", events)
                (directory / "output.txt").write_text(text, encoding="utf-8")
                (directory / "stderr.txt").write_text("", encoding="utf-8")
                (directory / "request.txt").write_text("Use the explicitly selected Scenario Maker skill in ./selected-skill/SKILL.md.\n\n" + self.case["request"], encoding="utf-8")
                selected = "scenario-maker" if side == "baseline" else self.case["selected_skill"]
                files = baseline_files if side == "baseline" else candidate_files[selected]
                record = {"case_id": history.CASE_ID, "attempt": attempt, "comparison_side": side,
                          "selected_skill": selected, "selected_skill_sha256": rb.manifest_identity(files),
                          "case_source": self.case["case_source"], "revision": self.corpus["manifest"][side + "_revision"],
                          "model_requested": rb.MODEL, "reasoning_requested": "high",
                          "attempt_manifest": (directory / "attempt.json").relative_to(self.corpus["root"]).as_posix(),
                          "raw": {"trace": "trace.jsonl", "output": "output.txt", "partial_output": None},
                          "raw_checksums": {name: rb.digest(directory / name) for name in ("trace.jsonl", "output.txt", "stderr.txt", "request.txt")},
                          "artifacts": [], "execution": {"status": "completed", "exit_code": 0},
                          "trace_complete": True, "evidence_errors": [], "cwd": f"/tmp/generator/{side}/{history.CASE_ID}/attempt-{attempt}"}
                rb.save_json(directory / "attempt.json", record)
                record["attempt_manifest_sha256"] = rb.digest(directory / "attempt.json")
                slot = {"case_id": history.CASE_ID, "attempt": attempt, "side": side}
                self.corpus["manifest"]["schedule"].append(slot)
                self.corpus["manifest"]["attempts"].append(record)
                capture = review.validate_attempt(self.corpus["root"], self.case, slot, record, self.corpus["manifest"])
                self.corpus["captures"][(history.CASE_ID, attempt, side)] = capture
        self.packets, self.mappings = [], []
        for attempt in (1, 2, 3):
            sides = ("baseline", "candidate") if attempt == 2 else ("candidate", "baseline")
            captures = [self.corpus["captures"][(history.CASE_ID, attempt, side)] for side in sides]
            clean = review.normalizer(self.corpus, captures)
            packet = {"case_id": history.CASE_ID, "attempt": attempt, "paired": True, "request": self.case["request"], "fixtures": [],
                      "criteria": [{"id": history.CRITERION_ID, "description": "Bind the supplied visual references.", "severity": "hard"}],
                      "rubric": {"references": [], "invocation_contract": None},
                      "outputs": {"a": review.output_for(captures[0], clean), "b": review.output_for(captures[1], clean)}}
            self.packets.append({"packet": packet, "suite": "corpus", "run": self.corpus})
            self.mappings.append({"case_id": history.CASE_ID, "attempt": attempt, "suite": "corpus", "a": sides[0], "b": sides[1],
                                  "raw_attempts": {side: str(capture["directory"]) for side, capture in zip(sides, captures)}})
            directory = self.source / "packets" / history.CASE_ID / f"attempt-{attempt}"
            directory.mkdir(parents=True)
            rb.save_json(directory / "packet.json", packet)
        # The complete input interfaces have 411 slots. Only the three historical
        # packets and six captures are physically needed by this module.
        for index in range(408):
            packet = copy.deepcopy(self.packets[0]["packet"])
            packet["case_id"] = f"unrelated-{index:03}"
            self.packets.append({"packet": packet, "suite": "corpus", "run": self.corpus})
            self.mappings.append({"case_id": packet["case_id"], "attempt": 1, "suite": "corpus", "a": "baseline", "b": "candidate",
                                  "raw_attempts": {"baseline": f"/unrelated/{index}/baseline", "candidate": f"/unrelated/{index}/candidate"}})
        self.manifest = {"kind": "independent-blinded-ai-split-review", "reviewer_kind": "ai", "model_requested": rb.MODEL,
                         "reasoning_requested": "high", "expected_packets": 411, "expected_capture_slots": 798,
                         "timeout_seconds": 900, "jobs": 3, "tools_requested": history.TOOLS, "blinding_limits": review.BLINDING_LIMITS,
                         "omp_version": "retained offline fixture", "omp_version_error": None,
                         "results": str(self.corpus["root"]), "boundary_results": str(self.boundary["root"]),
                         "baseline_revision": history.BASELINE_REVISION, "candidate_revision": history.CANDIDATE_REVISION,
                         "provenance_files": {name: rb.digest(self.source / "provenance" / name) for name in history.PROVENANCE_FILES},
                         "packets": [{"case_id": item["packet"]["case_id"], "attempt": item["packet"]["attempt"], "suite": item["suite"],
                                      "path": f"packets/{item['packet']['case_id']}/attempt-{item['packet']['attempt']}/packet.json",
                                      "sha256": history._json_hash(item["packet"])} for item in self.packets]}
        self.save_manifests()
        rb.save_json(self.source / "label-map.json", self.mappings)
        self.review_directory = self.source / "reviews" / history.CASE_ID / "attempt-2"
        self.review_directory.mkdir(parents=True)
        packet = self.packets[1]["packet"]
        self.original = _judgment(packet)
        self.workspace = root / "former-workspace" / history.CASE_ID / "attempt-2"
        request = history._request(packet)
        self.command = ["omp", "--cwd", str(self.workspace), "--print", "--mode", "json", "--model", rb.MODEL,
                        "--thinking", "high", "--no-session", "--no-title", "--no-prewalk", "--no-skills", "--no-rules",
                        "--no-extensions", "--no-lsp", "--no-pty", "--tools", "read,grep,glob", "--approval-mode", "yolo",
                        "--config", str(self.source / "provenance/omp-config.json"),
                        "--system-prompt", str(self.source / "provenance/reviewer-system.txt"), "--max-time", "900s", request]
        rb.save_json(self.review_directory / "command.json", self.command)
        (self.review_directory / "request.txt").write_text(request, encoding="utf-8")
        (self.review_directory / "stderr.txt").write_text("", encoding="utf-8")
        self.record = {"case_id": history.CASE_ID, "attempt": 2, "reviewer_kind": "ai", "mode": "review", "valid": True,
                       "validation_errors": [], "execution": {"status": "completed", "exit_code": 0, "error": None},
                       "packet_sha256": self.manifest["packets"][1]["sha256"], "command": self.command, "cwd": str(self.workspace),
                       "trace_complete": True}
        self.replace_original_judgment(self.original)

    def save_manifests(self):
        for run in (self.corpus, self.boundary):
            rb.save_json(run["root"] / "manifest.json", run["manifest"])
        self.manifest["capture_manifest_hashes"] = {"corpus": rb.digest(self.corpus["root"] / "manifest.json"),
                                                     "boundary": rb.digest(self.boundary["root"] / "manifest.json")}
        rb.save_json(self.source / "manifest.json", self.manifest)

    def replace_original_judgment(self, value):
        final = json.dumps(value, ensure_ascii=False)
        events = _events(final)
        _save_trace(self.review_directory / "trace.jsonl", events)
        (self.review_directory / "output.txt").write_text(final, encoding="utf-8")
        metadata = review.review_metadata(events)
        rb.save_json(self.review_directory / "context.json", {"system_prompt": (self.source / "provenance/reviewer-system.txt").read_text(),
                    "system_sha256": rb.digest(self.source / "provenance/reviewer-system.txt"),
                    "config_sha256": rb.digest(self.source / "provenance/omp-config.json"), "tools_requested": history.TOOLS, **metadata})
        self.record.update(judgment=copy.deepcopy(value), parsed_output=copy.deepcopy(value), model_metadata=metadata)
        self.reseal_original_raw()

    def reseal_original_raw(self):
        self.record["raw_checksums"] = {path.name: rb.digest(path) for path in self.review_directory.iterdir() if path.name != "review.json"}
        rb.save_json(self.review_directory / "review.json", self.record)

    def prepare(self):
        return history.prepare_history(self.source, self.packets, self.mappings, self.corpus, self.boundary)

    def prepare_source(self, other_sources=(), during_build=None):
        # These compact fixtures omit unrelated capture/preflight material.
        # Only assembly is supplied here; historical packets, labels, raw
        # captures, reviewer envelopes and their bindings use real validation.
        fixtures = (self, *other_sources)
        def preflight(results, boundary_results):
            for fixture in fixtures:
                if (results, boundary_results) == (fixture.corpus["root"], fixture.boundary["root"]):
                    return fixture.corpus, fixture.boundary
            raise review.ReviewError("unknown fixture capture roots")
        def build(corpus, boundary):
            for fixture in fixtures:
                if corpus is fixture.corpus and boundary is fixture.boundary:
                    if during_build is not None:
                        during_build()
                    return fixture.packets, fixture.mappings
            raise review.ReviewError("unknown fixture captures")
        with mock.patch.object(review, "preflight", side_effect=preflight), mock.patch.object(review, "build_packets", side_effect=build):
            return history.prepare_source_history(self.source)


class HistoricalPreparationTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.fixture = HistoricalFixture(Path(self.temporary.name))

    def test_swapped_repetitions_are_aligned_to_original_allegation_labels(self):
        result = self.fixture.prepare()
        packet = result["packet"]
        self.assertEqual(packet["alleged_review"]["criteria"][0]["a"], "failed")
        self.assertEqual(packet["alleged_review"]["criteria"][0]["b"], "passed")
        for label, side in (("a", "Baseline"), ("b", "Candidate")):
            self.assertEqual([row["attempt"] for row in packet["repetition_evidence"][label]], [1, 2, 3])
            self.assertEqual([row["output"]["final_output"] for row in packet["repetition_evidence"][label]],
                             [f"{side} reference response, repetition {attempt}." for attempt in (1, 2, 3)])
        self.assertEqual(result["label_alignment"]["repetitions"][0]["history_labels"], {"a": "b", "b": "a"})
        self.assertFalse(result["label_alignment"]["allegation"]["candidate_regression"])
        self.assertNotIn("label_alignment", packet)
        self.assertNotIn("raw_attempts", packet)
        self.assertNotIn("source_review", packet)
        required = [self.fixture.source / "manifest.json", self.fixture.source / "label-map.json",
                    self.fixture.review_directory / "review.json", self.fixture.review_directory / "trace.jsonl"]
        required.extend(self.fixture.corpus["captures"][(history.CASE_ID, attempt, side)]["directory"] / "attempt.json"
                        for attempt in (1, 2, 3) for side in ("baseline", "candidate"))
        for path in required:
            self.assertEqual(result["bindings"][str(path)], rb.digest(path))
        self.assertTrue(all(Path(path).is_absolute() for path in result["bindings"]))

    def test_source_preparation_ignores_repaired_packet_identity_and_ordering(self):
        fresh_root = self.fixture.root / "repaired"
        fresh_root.mkdir()
        fresh = HistoricalFixture(fresh_root)
        fresh.corpus["manifest"]["candidate_revision"] = "new-repaired-source"
        fresh.packets.reverse()
        for row in fresh.mappings:
            row["a"], row["b"] = row["b"], row["a"]
        for item in fresh.packets:
            item["packet"]["outputs"]["a"]["final_output"] = "New repaired response."
        result = self.fixture.prepare_source(other_sources=(fresh,))
        self.assertEqual(result["packet"], self.fixture.prepare()["packet"])
        self.assertEqual(result["first"], self.fixture.record)
        self.assertEqual(result["label_alignment"]["original_labels"], {"a": "baseline", "b": "candidate"})
        self.assertEqual(result["label_alignment"]["repetitions"][0]["history_labels"], {"a": "b", "b": "a"})
        for label, side in (("a", "Baseline"), ("b", "Candidate")):
            self.assertEqual([row["output"]["final_output"] for row in result["packet"]["repetition_evidence"][label]],
                             [f"{side} reference response, repetition {attempt}." for attempt in (1, 2, 3)])
        required = [self.fixture.source / "manifest.json", self.fixture.source / "label-map.json",
                    self.fixture.corpus["root"] / "manifest.json", self.fixture.boundary["root"] / "manifest.json"]
        required.extend(self.fixture.source / "provenance" / name for name in history.PROVENANCE_FILES)
        required.extend(self.fixture.review_directory / name for name in history.RAW_FILES | {"review.json"})
        for attempt in (1, 2, 3):
            required.append(self.fixture.source / "packets" / history.CASE_ID / f"attempt-{attempt}" / "packet.json")
            for side in ("baseline", "candidate"):
                directory = self.fixture.corpus["captures"][(history.CASE_ID, attempt, side)]["directory"]
                required.extend(directory / name for name in ("attempt.json", "trace.jsonl", "output.txt"))
        for path in required:
            self.assertEqual(result["bindings"][str(path)], rb.digest(path))
        self.assertFalse(any(fresh_root in Path(path).parents for path in result["bindings"]))

    def test_source_preparation_rejects_original_capture_tampering(self):
        directory = self.fixture.corpus["captures"][(history.CASE_ID, 3, "baseline")]["directory"]
        (directory / "output.txt").write_text("Changed retained response.", encoding="utf-8")
        with self.assertRaises(review.ReviewError):
            self.fixture.prepare_source()

    def test_source_preparation_keeps_original_revision_guard(self):
        self.fixture.corpus["manifest"]["candidate_revision"] = "new-repaired-source"
        self.fixture.manifest["candidate_revision"] = "new-repaired-source"
        self.fixture.save_manifests()
        with self.assertRaisesRegex(review.ReviewError, "capture identity mismatch"):
            self.fixture.prepare_source()

    def test_source_preparation_keeps_original_label_direction_guard(self):
        self.fixture.mappings[1]["a"], self.fixture.mappings[1]["b"] = "candidate", "baseline"
        rb.save_json(self.fixture.source / "label-map.json", self.fixture.mappings)
        with self.assertRaisesRegex(review.ReviewError, "original historical labels"):
            self.fixture.prepare_source()

    def test_source_preparation_rejects_manifest_change_after_root_selection(self):
        def change_manifest():
            self.fixture.manifest["omp_version"] = "Changed retained provenance"
            rb.save_json(self.fixture.source / "manifest.json", self.fixture.manifest)
        with self.assertRaisesRegex(review.ReviewError, "hash mismatch"):
            self.fixture.prepare_source(during_build=change_manifest)

    def test_source_preparation_rejects_rebound_original_capture_hash(self):
        self.fixture.manifest["capture_manifest_hashes"]["corpus"] = "0" * 64
        rb.save_json(self.fixture.source / "manifest.json", self.fixture.manifest)
        with self.assertRaisesRegex(review.ReviewError, "capture manifest hash mismatch"):
            self.fixture.prepare_source()

    def test_historical_disposition_is_required_even_when_new_initial_passes(self):
        result = self.fixture.prepare()
        fresh = _judgment(self.fixture.packets[1]["packet"], a="passed", b="passed")
        self.assertFalse(review.needs_adjudication(fresh, self.fixture.packets[1]["packet"]))
        unresolved = review.disposition(result["first"], None, result["packet"])
        self.assertTrue(unresolved["unresolved"])
        self.assertEqual(unresolved["allegations"], [{"criterion_id": history.CRITERION_ID, "label": "a", "state": "unresolved"}])
        independent = _judgment(result["packet"], a="passed", b="passed", independent=True)
        review.validate_judgment(independent, result["packet"])
        resolved = review.disposition(result["first"], {"valid": True, "judgment": independent}, result["packet"])
        self.assertFalse(resolved["unresolved"])
        self.assertEqual(resolved["allegations"][0]["state"], "rejected-on-evidence")

    def test_prepared_packet_runs_existing_reviewer_with_no_provider(self):
        result = self.fixture.prepare()
        packet = result["packet"]
        value = _judgment(packet, independent=True)
        destination = self.fixture.root / "future" / "ai-review" / "historical-adjudications" / history.CASE_ID / "attempt-2"
        def launch(command, **kwargs):
            self.assertEqual(kwargs["stdin"], subprocess.DEVNULL)
            self.assertIn("Perform independent adjudication", command[-1])
            kwargs["stdout"].write("".join(json.dumps(event) + "\n" for event in _events(json.dumps(value))).encode())
            return mock.Mock(wait=mock.Mock(return_value=0))
        with mock.patch.object(review.subprocess, "Popen", side_effect=launch) as process:
            independent = review.run_reviewer(packet, destination, self.fixture.root / "new-workspace",
                                              self.fixture.source / "provenance/reviewer-system.txt",
                                              self.fixture.source / "provenance/omp-config.json", 900)
        self.assertEqual(process.call_count, 1)
        self.assertTrue(independent["valid"])
        resolved = review.disposition(result["first"], independent, packet)
        self.assertEqual(resolved["state"], "confirmed")
        self.assertEqual(resolved["allegations"][0]["label"], "a")
        self.assertEqual(independent["judgment"]["criteria"][0]["b"], "passed")

    def test_changed_cached_judgment_cannot_replace_original_raw_final(self):
        self.fixture.record["judgment"]["criteria"][0]["a"] = "passed"
        rb.save_json(self.fixture.review_directory / "review.json", self.fixture.record)
        with self.assertRaisesRegex(review.ReviewError, "judgment/parsed/final"):
            self.fixture.prepare()

    def test_changed_original_raw_fails_its_retained_checksum(self):
        (self.fixture.review_directory / "output.txt").write_text("tampered", encoding="utf-8")
        with self.assertRaisesRegex(review.ReviewError, "hash mismatch"):
            self.fixture.prepare()

    def test_resealed_changed_output_still_must_match_terminal_trace(self):
        (self.fixture.review_directory / "output.txt").write_text("tampered", encoding="utf-8")
        self.fixture.reseal_original_raw()
        with self.assertRaisesRegex(review.ReviewError, "final output differs"):
            self.fixture.prepare()

    def test_resealed_fabricated_citation_still_fails_judgment_validation(self):
        value = copy.deepcopy(self.fixture.original)
        value["criteria"][0]["evidence"]["a"]["observations"][0]["quote"] = "invented evidence"
        self.fixture.replace_original_judgment(value)
        with self.assertRaisesRegex(review.ReviewError, "literal evidence quote"):
            self.fixture.prepare()

    def test_terminal_trace_required_even_with_resealed_hashes(self):
        path = self.fixture.review_directory / "trace.jsonl"
        _save_trace(path, _events(json.dumps(self.fixture.original))[:-1])
        self.fixture.reseal_original_raw()
        with self.assertRaisesRegex(review.ReviewError, "terminal trace"):
            self.fixture.prepare()

    def test_original_packet_hash_cannot_be_rebound_to_new_packet(self):
        self.fixture.record["packet_sha256"] = "0" * 64
        rb.save_json(self.fixture.review_directory / "review.json", self.fixture.record)
        with self.assertRaisesRegex(review.ReviewError, "packet hash mismatch"):
            self.fixture.prepare()

    def test_null_raw_checksum_cannot_disable_original_binding(self):
        self.fixture.record["raw_checksums"]["trace.jsonl"] = None
        rb.save_json(self.fixture.review_directory / "review.json", self.fixture.record)
        with self.assertRaisesRegex(review.ReviewError, "checksum is invalid"):
            self.fixture.prepare()

    def test_cached_valid_flag_cannot_override_failed_execution(self):
        self.fixture.record["execution"]["status"] = "timeout"
        rb.save_json(self.fixture.review_directory / "review.json", self.fixture.record)
        with self.assertRaisesRegex(review.ReviewError, "execution is not complete"):
            self.fixture.prepare()

    def test_missing_raw_repetition_blocks_supplemental_preparation(self):
        directory = self.fixture.corpus["captures"][(history.CASE_ID, 3, "candidate")]["directory"]
        (directory / "trace.jsonl").unlink()
        with self.assertRaisesRegex(review.ReviewError, "raw repetition unavailable"):
            self.fixture.prepare()

    def test_missing_packet_repetition_is_not_substituted(self):
        self.fixture.packets.pop(0)
        with self.assertRaisesRegex(review.ReviewError, "coverage"):
            self.fixture.prepare()

    def test_fresh_packet_drift_blocks_old_judgment_reuse(self):
        self.fixture.packets[0]["packet"]["request"] = "Changed request"
        with self.assertRaisesRegex(review.ReviewError, "differs from current complete rebuild"):
            self.fixture.prepare()

    def test_old_side_map_must_agree_with_fresh_deterministic_mapping(self):
        old = copy.deepcopy(self.fixture.mappings)
        old[0]["a"], old[0]["b"] = old[0]["b"], old[0]["a"]
        rb.save_json(self.fixture.source / "label-map.json", old)
        with self.assertRaisesRegex(review.ReviewError, "label map differs"):
            self.fixture.prepare()

    def test_even_consistently_relabelled_target_cannot_reverse_original_allegation(self):
        self.fixture.mappings[1]["a"], self.fixture.mappings[1]["b"] = "candidate", "baseline"
        rb.save_json(self.fixture.source / "label-map.json", self.fixture.mappings)
        with self.assertRaisesRegex(review.ReviewError, "original historical labels"):
            self.fixture.prepare()

    def test_raw_history_paths_cannot_be_reassigned_across_repetitions(self):
        labels = self.fixture.mappings[0]
        labels["raw_attempts"]["baseline"] = self.fixture.mappings[1]["raw_attempts"]["baseline"]
        rb.save_json(self.fixture.source / "label-map.json", self.fixture.mappings)
        with self.assertRaisesRegex(review.ReviewError, "capture path mismatch"):
            self.fixture.prepare()

    def test_capture_manifest_drift_is_detected_without_silent_refresh(self):
        manifest = copy.deepcopy(self.fixture.corpus["manifest"])
        manifest["candidate_revision"] = "different-source"
        rb.save_json(self.fixture.corpus["root"] / "manifest.json", manifest)
        with self.assertRaisesRegex(review.ReviewError, "manifest differs from preflight"):
            self.fixture.prepare()

    def test_recovery_manifest_is_not_a_historical_source(self):
        self.fixture.manifest["kind"] = "review-only-split-recovery"
        self.fixture.save_manifests()
        with self.assertRaisesRegex(review.ReviewError, "control mismatch: kind"):
            self.fixture.prepare()


if __name__ == "__main__":
    unittest.main()
