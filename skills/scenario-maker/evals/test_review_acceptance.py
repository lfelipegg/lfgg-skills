"""No-provider acceptance gates, permanent claims and synthetic subprocess evidence."""
import copy
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import review_acceptance as acceptance
import review_split as review
import run_baseline as rb
from test_review_split import envelope, judgment, packet


def historical_fixture():
    source = packet(attempt=2)
    source["case_id"] = "h3-dev-02"
    source["criteria"][0]["id"] = "h3-dev-02-E1"
    first = envelope(judgment(source, a="failed", b="passed"))
    history = {label: [{"attempt": attempt, "output": copy.deepcopy(source["outputs"][label])} for attempt in (1, 2, 3)] for label in ("a", "b")}
    independent = {**source, "review_mode": "independent-adjudication", "alleged_review": first["judgment"], "repetition_evidence": history}
    return first, independent


def link_fixture():
    return {name: {"path": name + ".json", "sha256": "a" * 64} for name in
            ("preparation", "launch", "fresh_manifest", "fresh_summary", "historical_packet", "historical_first", "historical_disposition", "historical_review", "runtime")}


def runtime_fixture():
    return {"valid": True, "omp_version": "omp v0.0.0-offline", "stdout": {"path": "version-stdout", "sha256": "a" * 64},
            "stderr": {"path": "version-stderr", "sha256": "b" * 64}}


class CombinedOutcomeTest(unittest.TestCase):
    def combine(self, historical, runtime=None, bindings=None, links=None, terminal=True):
        fresh = {"accepted": True, "gates": dict.fromkeys(acceptance.FRESH_GATES, True)}
        return acceptance.combined_outcome(fresh, historical, runtime_fixture() if runtime is None else runtime,
                                           dict.fromkeys(acceptance.BINDING_GATES, True) if bindings is None else bindings,
                                           link_fixture() if links is None else links, terminal_complete=terminal)

    def test_fresh_pass_without_historical_session_cannot_accept(self):
        self.assertFalse(self.combine(None)["accepted"])
        first, source = historical_fixture()
        missing = acceptance.historical_disposition(first, None, source)
        self.assertFalse(missing["complete"])
        self.assertFalse(self.combine(missing)["gates"]["mandatory_historical_disposition_complete"])

    def test_not_run_historical_side_blocks_even_with_valid_envelope(self):
        first, source = historical_fixture()
        incomplete = envelope(judgment(source, a="not-run", b="passed", adjudication=True))
        result = acceptance.historical_disposition(first, incomplete, source)
        self.assertTrue(result["unresolved"])
        self.assertFalse(self.combine(result)["accepted"])

    def test_baseline_only_confirmation_does_not_invent_candidate_regression(self):
        first, source = historical_fixture()
        confirmed = envelope(judgment(source, a="failed", b="passed", adjudication=True))
        result = acceptance.historical_disposition(first, confirmed, source)
        self.assertEqual(result["state"], "confirmed")
        self.assertEqual(result["allegations"][0]["side"], "baseline")
        self.assertEqual(result["new_candidate_contract_failures"], [])
        self.assertTrue(self.combine(result)["accepted"])

    def test_historical_candidate_novel_hard_failure_blocks(self):
        first, source = historical_fixture()
        value = judgment(source, a="failed", b="failed", adjudication=True)
        value["rationale"]["novel_contract_failures"] = [{
            "criterion_id": "h3-dev-02-E1", "label": "b", "category": "preservation",
            "reason": "Distinct candidate contract violation, absent from baseline evidence.",
            "observations": [{"path": "/outputs/b/final_output", "quote": "blue mug"}],
            "rules": [{"path": "/criteria/0/description", "quote": source["criteria"][0]["description"]}],
            "comparisons": [{"path": f"/repetition_evidence/a/{index}/output/final_output", "quote": "blue mug"} for index in range(3)],
        }]
        result = acceptance.historical_disposition(first, envelope(value), source)
        self.assertTrue(result["complete"])
        self.assertFalse(self.combine(result)["gates"]["no_historical_candidate_novel_hard_failures"])
        self.assertFalse(self.combine(result)["accepted"])

    def test_historical_candidate_failure_on_baseline_pass_also_blocks(self):
        first, source = historical_fixture()
        result = acceptance.historical_disposition(first, envelope(judgment(source, a="passed", b="failed", adjudication=True)), source)
        self.assertTrue(result["complete"])
        self.assertEqual(result["candidate_failure_on_baseline_pass"], ["h3-dev-02-E1"])
        self.assertFalse(self.combine(result)["accepted"])

    def test_malformed_supplemental_cannot_claim_complete(self):
        first, source = historical_fixture()
        value = judgment(source, a="failed", b="passed", adjudication=True)
        value["criteria"].pop()
        result = acceptance.historical_disposition(first, envelope(value), source)
        self.assertFalse(result["complete"])
        self.assertTrue(result["validation_error"])
        self.assertFalse(self.combine(result)["accepted"])

    def test_runtime_binding_link_and_terminal_omissions_block(self):
        first, source = historical_fixture()
        result = acceptance.historical_disposition(first, envelope(judgment(source, a="failed", b="passed", adjudication=True)), source)
        self.assertFalse(self.combine(result, runtime={})["accepted"])
        self.assertFalse(self.combine(result, bindings={})["accepted"])
        self.assertFalse(self.combine(result, links={})["accepted"])
        self.assertFalse(self.combine(result, terminal=False)["accepted"])


class LaunchClaimTest(unittest.TestCase):
    def test_drift_claims_failed_attempt_before_runtime_and_second_execute_refuses(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rb.save_json(root / "preparation.json", {"synthetic": True})
            with mock.patch.object(acceptance.preparation_api, "validate_preparation", side_effect=review.ReviewError("prepared input drift")) as validate, \
                    mock.patch.object(acceptance, "observe_runtime") as runtime, \
                    redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(acceptance.execute(root, "offline-test-handle"), 1)
                claim_hash = rb.digest(root / "launch.json")
                runtime.assert_not_called()
                with self.assertRaisesRegex(review.ReviewError, "already claimed"):
                    acceptance.execute(root, "offline-test-handle")
                self.assertEqual(validate.call_count, 1)
                self.assertEqual(rb.digest(root / "launch.json"), claim_hash)
            self.assertFalse(review.load_json(root / "combined-outcome.json")["accepted"])
            terminal = review.load_json(root / "execution.json")
            self.assertEqual(terminal["status"], "failed")
            self.assertIn("prepared input drift", terminal["error"])
            outcome = review.load_json(root / "combined-outcome.json")
            outcome["evidence"].pop("execution")
            self.assertEqual(terminal["combined_outcome_payload_sha256"], rb.manifest_identity(outcome))

    def test_nonfrozen_execution_refuses_before_version(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rb.save_json(root / "preparation.json", {"synthetic": True})
            validated = {"provenance": root / "ai-review/provenance", "preparation": {"gates": {}}}
            with mock.patch.object(acceptance.preparation_api, "validate_preparation", return_value=validated), \
                    mock.patch.object(acceptance, "observe_runtime") as runtime, \
                    redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(acceptance.execute(root, "offline-test-handle"), 1)
                runtime.assert_not_called()
            self.assertIn("frozen imported closure", review.load_json(root / "execution.json")["error"])

    def test_failed_runtime_observation_never_queues_paid_wave(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rb.save_json(root / "preparation.json", {"synthetic": True})
            validated = {"preparation": {"gates": dict.fromkeys(acceptance.BINDING_GATES, True)}}
            with mock.patch.object(acceptance.preparation_api, "validate_preparation", return_value=validated), \
                    mock.patch.object(acceptance, "_require_frozen_execution"), \
                    mock.patch.object(acceptance, "observe_runtime", return_value={"valid": False, "error": "runtime unavailable"}), \
                    mock.patch.object(acceptance, "_fresh_and_historical") as wave, \
                    redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                # The mocked observation still retains its required raw record.
                rb.save_json(root / "runtime-version.json", {"valid": False})
                self.assertEqual(acceptance.execute(root, "offline-test-handle"), 1)
                wave.assert_not_called()
            self.assertEqual(review.load_json(root / "execution.json")["status"], "failed")

    def test_abrupt_exception_never_manufactures_terminal_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rb.save_json(root / "preparation.json", {"synthetic": True})
            with mock.patch.object(acceptance.preparation_api, "validate_preparation", side_effect=KeyboardInterrupt), \
                    mock.patch.object(acceptance, "observe_runtime") as runtime, \
                    redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with self.assertRaises(KeyboardInterrupt):
                    acceptance.execute(root, "offline-test-handle")
                runtime.assert_not_called()
            self.assertTrue((root / "launch.json").is_file())
            self.assertFalse((root / "execution.json").exists())
            self.assertFalse((root / "combined-outcome.json").exists())

    def test_prepare_and_validate_cli_are_offline(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rb.save_json(root / "preparation.json", {})
            with mock.patch.object(acceptance.preparation_api, "prepare", return_value={"expected_packets": 411, "expected_capture_slots": 798}) as prepare, \
                    mock.patch.object(acceptance.preparation_api, "validate_preparation", return_value={"packets": [], "preparation": {"gates": {}}}), \
                    mock.patch.object(acceptance.subprocess, "Popen") as spawn, \
                    redirect_stdout(io.StringIO()):
                self.assertEqual(acceptance.main(["prepare", "--results", str(root), "--boundary-results", str(root), "--source-review", str(root),
                                                  "--candidate-root", str(root), "--out", str(root)]), 0)
                self.assertEqual(prepare.call_args.kwargs["evals"], acceptance.EVALS)
                self.assertEqual(acceptance.main(["validate", "--out", str(root)]), 0)
                spawn.assert_not_called()


class ObservedInterruptionTest(unittest.TestCase):
    def test_external_terminal_evidence_closes_unaccepted_without_execution_record(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "acceptance"
            root.mkdir()
            identity = {"pid": 999999999, "boot_id": "offline", "start_ticks": "1", "state": "T"}
            launch = {"started_at": acceptance.now(), "pid": identity["pid"], "process_identity": identity,
                      "preparation_sha256": "a" * 64, "managed_handle": "offline-stop"}
            acceptance.exclusive_json(root / "launch.json", launch)
            evidence = root.parent / "external-supervisor.txt"
            evidence.write_text("Synthetic observed SIGSTOP, empty worker inventory, runner SIGKILL terminal -9.\n")
            value = {"kind": "externally-observed-acceptance-interruption", "observed_at": acceptance.now(), "observer": "offline supervisor fixture",
                     "launch_sha256": rb.digest(root / "launch.json"), "preparation_sha256": launch["preparation_sha256"],
                     "managed_handle": launch["managed_handle"], "pid": launch["pid"], "process_identity": identity,
                     "runner": {"suspended_observed": True, "suspension_signal": "SIGSTOP", "terminal_observed": True,
                                "termination_signal": "SIGKILL", "returncode": -int(signal.SIGKILL)},
                     "worker_inventory_complete": True, "worker_groups": [],
                     "evidence": [{"path": str(evidence), "sha256": rb.digest(evidence)}]}
            observation = root.parent / "observed-stop.json"
            rb.save_json(observation, value)
            outcome = acceptance.observe_interruption(root, observation)
            self.assertFalse(outcome["accepted"])
            self.assertFalse((root / "execution.json").exists())
            self.assertTrue((root / "observed-interruption.json").is_file())
            with self.assertRaisesRegex(review.ReviewError, "already retained"):
                acceptance.observe_interruption(root, observation)


# The subprocess smoke deliberately replaces only fresh execute_wave with an
# explicitly synthetic offline writer. The supplemental uses real run_reviewer
# and a PATH containing only this fake executable, including its fixture copy.
SYNTHETIC_WAVE = '''

def _offline_wave(items, out, scratch, system_file, config_file, timeout, jobs, adjudication=False):
    results = {}
    group = "adjudications" if adjudication else "reviews"
    for item in items:
        packet = item["packet"]
        criteria = []
        for index, criterion in enumerate(packet["criteria"]):
            proof = lambda label: {"reason": "Synthetic offline proof.", "observations": [{"path": "/outputs/" + label + "/final_output", "quote": "blue mug"}], "rules": [{"path": "/criteria/" + str(index) + "/description", "quote": criterion["description"]}]}
            criteria.append({"id": criterion["id"], "a": "passed", "b": "passed" if packet["paired"] else None,
                             "evidence": {"a": proof("a"), "b": proof("b") if packet["paired"] else None}})
        value = {"case_id": packet["case_id"], "attempt": packet["attempt"], "reviewer_kind": "ai", "criteria": criteria,
                 "regression": False if packet["paired"] else None, "rationale": "Synthetic offline initial judgment."}
        validate_judgment(value, packet)
        if os.environ.get("OFFLINE_FRESH_NOTRUN") == "1":
            value = not_run_judgment(packet, "Synthetic unavailable initial session.")
        destination = out / group / packet["case_id"] / ("attempt-" + str(packet["attempt"]))
        destination.mkdir(parents=True, exist_ok=False)
        (destination / "synthetic.txt").write_text("Not real reviewer evidence; offline fixture only.\\n")
        result = {"valid": os.environ.get("OFFLINE_FRESH_NOTRUN") != "1", "judgment": value, "execution": {"status": "completed", "exit_code": 0, "error": None},
                  "packet_sha256": item["packet_sha256"], "raw_checksums": {"synthetic.txt": rb.digest(destination / "synthetic.txt")}}
        rb.save_json(destination / "review.json", result)
        results[(packet["case_id"], packet["attempt"])] = result
    return results

execute_wave = _offline_wave
'''

SYNTHETIC_PREPARATION = '''
from pathlib import Path
import review_acceptance_history
import review_split as review
import run_baseline as rb

def validate_preparation(out):
    out = Path(out)
    prepared = review.load_json(out / "preparation.json")
    review.verify_files(out, prepared["prepared_files"], "synthetic preparation")
    review.verify_files(out / "ai-review/provenance", prepared["provenance_files"], "synthetic closure")
    packets = [{"packet": review.load_json(out / row["path"]), "suite": row["suite"], "packet_path": row["path"].removeprefix("ai-review/"), "packet_sha256": row["sha256"], "run": {}} for row in prepared["packets"]]
    return {"preparation": prepared, "packets": packets, "mappings": review.load_json(out / "ai-review/label-map.json"),
            "historical_packet": review.load_json(out / "historical-packet.json"), "historical_first": review.load_json(out / "historical-first.json"),
            "provenance": out / "ai-review/provenance"}
'''

FAKE_OMP = '''
import hashlib, json, os, sys
from pathlib import Path
with Path(os.environ["OFFLINE_CALLS"]).open("a") as stream:
    stream.write(json.dumps(sys.argv[1:]) + "\\n")
if sys.argv[1:] == ["--help"]:
    print("omp v0.0.0-offline")
    raise SystemExit(0)
if os.environ.get("OFFLINE_HISTORICAL_FAIL") == "1":
    sys.stderr.write("synthetic historical session failed\\n")
    raise SystemExit(17)
source = json.loads(Path("packet.json").read_text())
for fixture in source["fixtures"]:
    path = Path(fixture["path"])
    assert hashlib.sha256(path.read_bytes()).hexdigest() == fixture["sha256"]
sys.stderr.write("synthetic supplemental fixture copied and verified\\n")
criteria = []
for index, criterion in enumerate(source["criteria"]):
    proof = lambda label: {"reason": "Synthetic offline fixture assessment.", "observations": [{"path": "/outputs/" + label + "/final_output", "quote": "blue mug"}], "rules": [{"path": "/criteria/" + str(index) + "/description", "quote": criterion["description"]}]}
    criteria.append({"id": criterion["id"], "a": "failed" if index == 0 else "passed", "b": "passed", "evidence": {"a": proof("a"), "b": proof("b")}})
value = {"case_id": source["case_id"], "attempt": source["attempt"], "reviewer_kind": "ai", "criteria": criteria, "regression": True,
         "rationale": {"explanation": "Synthetic baseline-only confirmation.", "novel_contract_failures": []}}
print(json.dumps({"type": "message_end", "message": {"role": "assistant", "stopReason": "stop", "provider": "openai-codex", "model": "gpt-6-astra", "content": [{"type": "text", "text": json.dumps(value)}]}}))
print(json.dumps({"type": "agent_end", "isTerminal": True}))
'''


def create_synthetic_preparation(root):
    """Build a full-count fixture; no legacy evidence or real provider is touched."""
    out = root / "prepared"
    provenance = out / "ai-review/provenance"
    provenance.mkdir(parents=True)
    for name in ("review_acceptance.py", "review_acceptance_history.py", "review_split.py", "run_split.py", "run_baseline.py", "evaluate.py"):
        shutil.copyfile(acceptance.EVALS / name, provenance / name)
    with (provenance / "review_split.py").open("a") as stream:
        stream.write(SYNTHETIC_WAVE)
    (provenance / "review_acceptance_prepare.py").write_text(SYNTHETIC_PREPARATION)
    (provenance / "reviewer-system.txt").write_text("Synthetic offline fixture, never a real review.\n")
    (provenance / "omp-config.json").write_text("{}\n")
    fixture = out / "ai-review/fixtures/nested/source.txt"
    fixture.parent.mkdir(parents=True)
    fixture.write_text("Synthetic supplemental fixture content.\n")
    packets, mappings = [], []
    for case_index in range(137):
        paired = case_index < 129
        for attempt in (1, 2, 3):
            value = packet(attempt=attempt, paired=paired)
            value["case_id"] = "h3-dev-02" if case_index == 0 else f"offline-{case_index:03d}"
            if case_index == 0:
                value["criteria"][0]["id"] = "h3-dev-02-E1"
            value["fixtures"] = [{"path": "fixtures/nested/source.txt", "sha256": rb.digest(fixture)}]
            path = out / "ai-review/packets" / value["case_id"] / f"attempt-{attempt}/packet.json"
            path.parent.mkdir(parents=True)
            rb.save_json(path, value)
            packets.append({"case_id": value["case_id"], "attempt": attempt, "suite": "corpus" if paired else "boundary",
                            "path": path.relative_to(out).as_posix(), "sha256": rb.digest(path)})
            mappings.append({"case_id": value["case_id"], "attempt": attempt, "a": "baseline" if paired else "candidate", "b": "candidate" if paired else None})
    first, history = historical_fixture()
    history["fixtures"] = [{"path": "fixtures/nested/source.txt", "sha256": rb.digest(fixture)}]
    rb.save_json(out / "historical-packet.json", history)
    rb.save_json(out / "historical-first.json", first)
    rb.save_json(out / "ai-review/label-map.json", mappings)
    handle = "offline-synthetic-managed-handle"
    meta = {"model_requested": acceptance.MODEL, "reasoning_requested": "high", "timeout_seconds": 900, "jobs": 3,
            "expected_packets": 411, "expected_capture_slots": 798,
            "gates": dict.fromkeys(acceptance.BINDING_GATES, True),
            "future_execution": {"managed_handle": handle, "argv": acceptance.future_command(out, handle)},
            "capture_manifest_hashes": {"corpus": "a" * 64, "boundary": "b" * 64},
            "baseline_revision": "offline-baseline", "candidate_revision": "offline-candidate",
            "provenance_files": rb.source_manifest(provenance), "packets": packets, "prepared_files": rb.source_manifest(out)}
    rb.save_json(out / "preparation.json", meta)
    rb.freeze_snapshot(out)
    executable = root / "bin/omp"
    executable.parent.mkdir()
    executable.write_text(f"#!{sys.executable}\n" + FAKE_OMP)
    executable.chmod(0o755)
    environment = {**os.environ, "PATH": str(executable.parent), "OFFLINE_CALLS": str(root / "fake-calls.jsonl"), "PYTHONDONTWRITEBYTECODE": "1"}
    return out, meta["future_execution"]["argv"], environment


@unittest.skipUnless(os.name == "posix", "isolated POSIX synthetic executable")
class FrozenSubprocessTest(unittest.TestCase):
    def test_complete_fresh_plus_one_real_helper_supplemental_fixture_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out, argv, environment = create_synthetic_preparation(root)
            process = subprocess.run(argv, env=environment, capture_output=True, timeout=30)
            self.assertEqual(process.returncode, 0, process.stderr.decode())
            fresh = review.load_json(out / "ai-review/summary.json")
            self.assertTrue(fresh["accepted"])
            self.assertEqual(fresh["raw_counts"]["initial_reviews"], 411)
            self.assertEqual(fresh["raw_counts"]["capture_slots"], 798)
            self.assertEqual(fresh["raw_counts"]["adjudications"], 0)
            historical = review.load_json(out / "historical-disposition.json")
            self.assertTrue(historical["complete"])
            self.assertEqual(historical["allegations"][0]["side"], "baseline")
            self.assertIn("fixture copied", (out / "ai-review/historical-adjudications/h3-dev-02/attempt-2/stderr.txt").read_text())
            combined = review.load_json(out / "combined-outcome.json")
            self.assertTrue(combined["accepted"])
            self.assertEqual(combined["evidence"]["fresh_summary"]["sha256"], rb.digest(out / "ai-review/summary.json"))
            self.assertEqual(combined["evidence"]["fresh_manifest"]["sha256"], rb.digest(out / "ai-review/manifest.json"))
            self.assertEqual(combined["evidence"]["historical_disposition"]["sha256"], rb.digest(out / "historical-disposition.json"))
            self.assertEqual(combined["evidence"]["execution"]["sha256"], rb.digest(out / "execution.json"))
            self.assertFalse(any((out / "ai-review/provenance").glob("__pycache__")))
            calls = [json.loads(line) for line in (root / "fake-calls.jsonl").read_text().splitlines()]
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0], ["--help"])
            self.assertIn("--model", calls[1])
            self.assertEqual(calls[1][calls[1].index("--model") + 1], acceptance.MODEL)
            before = rb.digest(out / "launch.json")
            refused = subprocess.run(argv, env=environment, capture_output=True, timeout=10)
            self.assertEqual(refused.returncode, 2)
            self.assertEqual(rb.digest(out / "launch.json"), before)
            self.assertEqual(len((root / "fake-calls.jsonl").read_text().splitlines()), 2)

    def test_unavailable_historical_blocks_without_rewriting_passing_fresh_summary(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out, argv, environment = create_synthetic_preparation(root)
            environment["OFFLINE_HISTORICAL_FAIL"] = "1"
            process = subprocess.run(argv, env=environment, capture_output=True, timeout=30)
            self.assertEqual(process.returncode, 1, process.stderr.decode())
            self.assertTrue(review.load_json(out / "ai-review/summary.json")["accepted"])
            historical = review.load_json(out / "historical-disposition.json")
            self.assertFalse(historical["complete"])
            combined = review.load_json(out / "combined-outcome.json")
            self.assertFalse(combined["accepted"])
            self.assertFalse(combined["gates"]["mandatory_historical_disposition_complete"])
            self.assertEqual(len((root / "fake-calls.jsonl").read_text().splitlines()), 2)

    def test_historical_session_is_mandatory_even_when_fresh_wave_is_unavailable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out, argv, environment = create_synthetic_preparation(root)
            environment["OFFLINE_FRESH_NOTRUN"] = "1"
            process = subprocess.run(argv, env=environment, capture_output=True, timeout=30)
            self.assertEqual(process.returncode, 1, process.stderr.decode())
            self.assertFalse(review.load_json(out / "ai-review/summary.json")["accepted"])
            self.assertTrue(review.load_json(out / "historical-disposition.json")["complete"])
            self.assertFalse(review.load_json(out / "combined-outcome.json")["accepted"])
            self.assertEqual(len((root / "fake-calls.jsonl").read_text().splitlines()), 2)

    def test_packet_drift_refuses_before_even_fake_runtime_observation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out, argv, environment = create_synthetic_preparation(root)
            path = out / "historical-packet.json"
            path.chmod(0o644)
            path.write_text("{}\n")
            process = subprocess.run(argv, env=environment, capture_output=True, timeout=10)
            self.assertEqual(process.returncode, 1, process.stderr.decode())
            self.assertFalse((root / "fake-calls.jsonl").exists())
            self.assertFalse(review.load_json(out / "combined-outcome.json")["accepted"])
            self.assertTrue((out / "execution.json").is_file())
            self.assertTrue((out / "launch.json").is_file())


if __name__ == "__main__":
    unittest.main()
