"""Offline review-only recovery regressions using disposable retained evidence.

``make_synthetic_source(Path(...))`` is also the disposable smoke fixture: use
``fixture.mock_capture_preflight()`` around recovery.plan/run, and patch
``review.run_reviewer`` with ``fixture.synthetic_reviewer()``.  The real
execute_wave, retained-envelope validators, adjudication builder and aggregate
are deliberately not mocked.  No helper launches OMP.
"""
import contextlib
import copy
import io
import json
from pathlib import Path
import shutil
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest import mock

import review_recovery as recovery
import review_split as review


RETAINED_ALLEGATION = ("h3-dev-02", 2)
FIXTURE_NAME = "case15-geometric-source.png"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.chmod(0o644)
    review.rb.save_json(path, value)


def write_text(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.chmod(0o644)
    path.write_text(value, encoding="utf-8")


def tree_bytes(root):
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*")) if path.is_file()}


@contextlib.contextmanager
def restored_evidence(root):
    """Undo a subtest's deliberate corruption, without rewriting unchanged bytes."""
    original = tree_bytes(root)
    directories = {path for path in root.rglob("*") if path.is_dir()}
    try:
        yield
    finally:
        for path in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
            relative = path.relative_to(root).as_posix()
            if path.is_symlink() or (path.is_file() and relative not in original):
                path.unlink()
            elif path.is_dir() and path not in directories:
                path.rmdir()
        for relative, content in original.items():
            path = root / relative
            if not path.exists() or path.read_bytes() != content:
                path.parent.mkdir(parents=True, exist_ok=True)
                if path.exists():
                    path.chmod(0o644)
                path.write_bytes(content)


def synthetic_judgment(packet, failed_label=None):
    """A complete, grounded verdict, optionally alleging one hard failure."""
    criteria = []
    for index, criterion in enumerate(packet["criteria"]):
        states, proofs = {}, {}
        for label in ("a", "b"):
            if label == "b" and not packet["paired"]:
                states[label], proofs[label] = None, None
                continue
            states[label] = "failed" if label == failed_label and index == 0 else "passed"
            proofs[label] = {
                "reason": "The supplied output is compared with the original preservation contract.",
                "observations": [{"path": f"/outputs/{label}/final_output", "quote": "blue mug"}],
                "rules": [{"path": f"/criteria/{index}/description", "quote": criterion["description"]}],
            }
        criteria.append({"id": criterion["id"], "a": states["a"], "b": states["b"], "evidence": proofs})
    independent = packet.get("review_mode") == "independent-adjudication"
    return {
        "case_id": packet["case_id"], "attempt": packet["attempt"], "reviewer_kind": "ai",
        "criteria": criteria, "regression": bool(failed_label) if packet["paired"] else None,
        "rationale": {"explanation": "All three repetitions were independently reassessed.",
                      "novel_contract_failures": []} if independent else "Original contract and retained output assessed.",
    }


def reviewer_request(packet):
    mode = "adjudication" if "alleged_review" in packet else "review"
    return (
        f"Perform independent {mode} of the complete local packet.json and its declared fixtures. "
        f"Review identity: case_id={json.dumps(packet['case_id'])}; attempt={packet['attempt']}. "
        "Copy that exact case ID and integer attempt into the specified AI review JSON, with grounded citations."
    )


def reviewer_command(packet, workspace, system_file, config_file, timeout=900):
    return [
        "omp", "--cwd", str(workspace), "--print", "--mode", "json", "--model", review.rb.MODEL,
        "--thinking", "high", "--no-session", "--no-title", "--no-prewalk", "--no-skills", "--no-rules",
        "--no-extensions", "--no-lsp", "--no-pty", "--tools", "read,grep,glob", "--approval-mode", "yolo",
        "--config", str(config_file), "--system-prompt", str(system_file), "--max-time", f"{timeout}s",
        reviewer_request(packet),
    ]


def reviewer_events(value):
    return [
        {"type": "tool_execution_start", "toolCallId": "read-packet", "toolName": "read",
         "args": {"path": "packet.json"}},
        {"type": "tool_execution_end", "toolCallId": "read-packet", "toolName": "read",
         "isError": False, "result": "The declared packet was read completely."},
        {"type": "message_end", "message": {
            "role": "assistant", "content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}],
            "stopReason": "stop", "provider": "openai-codex", "model": "gpt-6-astra",
            "api": "openai-codex-responses", "usage": {"input": 10, "output": 20},
        }},
        {"type": "agent_end", "isTerminal": True},
    ]


def write_trace(path, events):
    write_text(path, "".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events))


def write_completed_review(packet, destination, scratch, system_file, config_file, timeout=900,
                           failed_label=None, invalid=False):
    """Write the same physical evidence envelope a real reviewer retains."""
    destination.mkdir(parents=True, exist_ok=False)
    workspace = scratch / packet["case_id"] / f"attempt-{packet['attempt']}"
    workspace.mkdir(parents=True, exist_ok=False)
    write_json(workspace / "packet.json", packet)
    fixture_root = destination.parent.parent.parent / "fixtures"
    for fixture in packet["fixtures"]:
        target = workspace / fixture["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(fixture_root / fixture["path"].removeprefix("fixtures/"), target)
    command = reviewer_command(packet, workspace, system_file, config_file, timeout)
    write_text(destination / "request.txt", reviewer_request(packet))
    write_json(destination / "command.json", command)
    value = synthetic_judgment(packet, failed_label)
    events = reviewer_events(value)
    write_trace(destination / "trace.jsonl", events)
    final, _ = review.final_messages(events)
    write_text(destination / "output.txt", final)
    write_text(destination / "stderr.txt", "")
    metadata = review.review_metadata(events)
    write_json(destination / "context.json", {
        "system_prompt": system_file.read_text(encoding="utf-8"), "system_sha256": review.rb.digest(system_file),
        "config_sha256": review.rb.digest(config_file), "tools_requested": ["read", "grep", "glob"], **metadata,
    })
    result = {
        "case_id": packet["case_id"], "attempt": packet["attempt"], "reviewer_kind": "ai",
        "mode": "adjudication" if "alleged_review" in packet else "review", "valid": not invalid,
        "judgment": review.not_run_judgment(packet, "synthetic execution failure") if invalid else value,
        "parsed_output": value, "validation_errors": ["synthetic execution failure"] if invalid else [],
        "execution": {"status": "error" if invalid else "completed", "exit_code": 1 if invalid else 0,
                      "error": "synthetic execution failure" if invalid else None},
        "started_at": "2026-10-09T00:00:00+00:00", "elapsed_seconds": 0.01,
        "command": command, "cwd": str(workspace), "packet_sha256": review.rb.digest(workspace / "packet.json"),
        "model_metadata": metadata, "trace_complete": True,
        "raw_checksums": {path.name: review.rb.digest(path) for path in destination.iterdir() if path.is_file()},
    }
    write_json(destination / "review.json", result)
    review.rb.freeze_snapshot(destination)
    return result


class SyntheticRecoverySource:
    """An interrupted source campaign with 411 packets and 798 frozen captures."""

    def __init__(self, root):
        self.root = Path(root).absolute()
        self.root.mkdir(parents=True, exist_ok=False)
        self.source_review = self.root / "ai-review"
        self.source_review.mkdir()
        self.calls = []
        self._call_lock = threading.Lock()
        self.corpus, self.boundary = self._capture_runs()
        packets, mappings = review.build_packets(self.corpus, self.boundary)
        self.packets = packets
        self.mappings = mappings
        self.rebuilt_packets = copy.deepcopy(packets)
        self.rebuilt_mappings = copy.deepcopy(mappings)
        review.retain_preparation(packets, mappings, self.source_review, self.corpus)
        all_keys = [(item["packet"]["case_id"], item["packet"]["attempt"]) for item in packets]
        self.reused_keys = set(all_keys[:199]) | {RETAINED_ALLEGATION}
        remaining = [key for key in all_keys if key not in self.reused_keys]
        self.partial_keys = set(remaining[:3])
        self.unstarted_keys = set(remaining[3:])
        self.new_keys = self.partial_keys | self.unstarted_keys
        self.packet_by_key = {(item["packet"]["case_id"], item["packet"]["attempt"]): item["packet"] for item in packets}
        self.mapping_by_key = {(row["case_id"], row["attempt"]): row for row in mappings}
        system = self.source_review / "provenance/reviewer-system.txt"
        config = self.source_review / "provenance/omp-config.json"
        for key in sorted(self.reused_keys):
            packet = self.packet_by_key[key]
            failed = self.label_for(key, "baseline") if key == RETAINED_ALLEGATION else None
            write_completed_review(packet, self.review_directory(key), self.root / "old-scratch",
                                   system, config, failed_label=failed)
        for key in sorted(self.partial_keys):
            packet = self.packet_by_key[key]
            destination = self.review_directory(key)
            destination.mkdir(parents=True)
            workspace = self.root / "old-scratch" / key[0] / f"attempt-{key[1]}"
            write_text(destination / "request.txt", reviewer_request(packet))
            write_json(destination / "command.json", reviewer_command(packet, workspace, system, config))
            # This is reasoning, not a judgment or a final assistant message.
            write_trace(destination / "trace.jsonl", [{"type": "message_end", "message": {
                "role": "assistant", "content": [{"type": "thinking", "thinking": "Tentative pass; still examining."}],
                "stopReason": "toolUse", "provider": "openai-codex", "model": "gpt-6-astra",
            }}])
            write_text(destination / "stderr.txt", "")
        self.source_manifest = {
            "kind": "independent-blinded-ai-split-review", "created_at": "2026-10-08T00:00:00+00:00",
            "reviewer_kind": "ai", "model_requested": review.rb.MODEL, "reasoning_requested": "high",
            "results": str(self.corpus["root"]), "boundary_results": str(self.boundary["root"]),
            "capture_manifest_hashes": {
                "corpus": review.rb.digest(self.corpus["root"] / "manifest.json"),
                "boundary": review.rb.digest(self.boundary["root"] / "manifest.json"),
            },
            "baseline_revision": self.corpus["manifest"]["baseline_revision"],
            "candidate_revision": self.corpus["manifest"]["candidate_revision"],
            "expected_packets": 411, "expected_capture_slots": 798, "jobs": 3, "timeout_seconds": 900,
            "omp_version": "omp synthetic-offline-fixture", "omp_version_error": None,
            "tools_requested": ["read", "grep", "glob"],
            "permissions": "declared local read-only tool access; not an OS sandbox",
            "retry_policy": "none; fresh sessions, no resume/replacements/best-of selection",
            "label_policy": "random.Random(0), sorted (case_id, attempt); label-map.json outside packets/raw sessions",
            "blinding_limits": review.BLINDING_LIMITS,
            "provenance_files": review.rb.source_manifest(self.source_review / "provenance"),
            "packets": [{"case_id": item["packet"]["case_id"], "attempt": item["packet"]["attempt"],
                         "suite": item["suite"], "path": item["packet_path"], "sha256": item["packet_sha256"]}
                        for item in packets],
            "provider_metadata": review.review_metadata([]), "acceptance": "not assessed",
        }
        write_json(self.source_review / "manifest.json", self.source_manifest)
        review.rb.freeze_snapshot(self.source_review)

    def _capture_runs(self):
        inputs = self.root / "evaluation-inputs"
        inputs.mkdir()
        (inputs / "fixtures").mkdir()
        evaluation_files = {}
        for name in ("omp-config.json", "run_baseline.py", "run_split.py"):
            shutil.copyfile(review.EVALS / name, inputs / name)
            evaluation_files[name] = review.rb.digest(inputs / name)
        shutil.copyfile(review.EVALS / "fixtures" / FIXTURE_NAME, inputs / "fixtures" / FIXTURE_NAME)
        fixtures = {FIXTURE_NAME: review.rb.digest(inputs / "fixtures" / FIXTURE_NAME)}
        baseline = self.root / "baseline"
        baseline.mkdir()
        reference_names = {*review.COMMON_REFERENCES, "references/models/sdxl.md", "references/models/minimax-h3.md",
                           "references/video-prompts.md", *review.rs.H3_GUIDES}
        for name in sorted(reference_names):
            target = baseline / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(review.EVALS.parent / name, target)
        source_files = review.rb.source_manifest(baseline)
        baseline_revision = review.rb.manifest_identity(source_files)
        candidate_files = {skill: {"SKILL.md": "1" * 64} for skill in review.rs.SKILLS}
        candidate_revision = "split-sha256-" + review.rb.manifest_identity(candidate_files)
        runs = []
        for suite, identifiers in (
            ("corpus", [f"corpus-{index:03}" for index in range(123)] + ["h3-dev-02"]),
            ("boundary", [f"zz-boundary-{index:02}" for index in range(13)]),
        ):
            root = self.root / suite
            root.mkdir()
            cases, captures, schedule, attempts = {}, {}, [], []
            for index, case_id in enumerate(identifiers):
                paired = suite == "corpus" or index < 5
                case = {"id": case_id, "request": "Preserve the blue mug on the white shelf.",
                        "criteria": [{"id": f"{case_id}-PRESERVE", "description": "Preserve all supplied facts.",
                                      "severity": "hard", "method": "ai"}],
                        "fixtures": [FIXTURE_NAME] if index == 0 else [], "paired": paired,
                        "case_source": "cases.jsonl",
                        "selected_skill": "scenario-maker-minimax-h3" if case_id == "h3-dev-02" else "scenario-maker-sdxl"}
                cases[case_id] = case
                for attempt in (1, 2, 3):
                    for side in (("baseline", "candidate") if paired else ("candidate",)):
                        directory = root / "captures" / side / case_id / f"attempt-{attempt}"
                        directory.mkdir(parents=True)
                        output = f"A blue mug remains on a white shelf. Repetition {attempt}."
                        write_text(directory / "output.txt", output)
                        events = [{"type": "message_end", "message": {
                            "role": "assistant", "content": [{"type": "text", "text": output}], "stopReason": "stop",
                        }}, {"type": "agent_end", "isTerminal": True}]
                        write_trace(directory / "trace.jsonl", events)
                        record = {"case_id": case_id, "attempt": attempt, "comparison_side": side,
                                  "cwd": str(directory / "workspace"), "raw": {"output": "output.txt", "trace": "trace.jsonl"},
                                  "raw_checksums": {name: review.rb.digest(directory / name) for name in ("output.txt", "trace.jsonl")},
                                  "artifacts": [], "execution": {"status": "completed", "exit_code": 0, "error": None}}
                        write_json(directory / "attempt.json", record)
                        captures[(case_id, attempt, side)] = {"record": record, "directory": directory,
                                                            "available": True, "issues": [], "events": events}
                        schedule.append({"case_id": case_id, "attempt": attempt, "side": side, "position": len(schedule)})
                        attempts.append(record)
            manifest = {
                "kind": "current-monolith-versus-model-split", "suite": suite, "model_requested": review.rb.MODEL,
                "reasoning_requested": "high", "attempts_per_case": 3, "baseline_revision": baseline_revision,
                "candidate_revision": candidate_revision,
                "source_manifests": {"baseline": source_files, "candidate": candidate_files},
                "candidate_snapshots": {skill: f"snapshots/{skill}" for skill in review.rs.SKILLS},
                "baseline_snapshot": "baseline", "evaluation_inputs": "evaluation-inputs",
                "fixtures": fixtures, "evaluation_files": evaluation_files,
                "route_ownership": {}, "cases": list(cases.values()), "schedule": schedule, "attempts": attempts,
                "expected_attempts": 744 if suite == "corpus" else 54,
            }
            write_json(root / "manifest.json", manifest)
            runs.append({"root": root, "manifest": manifest, "inputs": inputs, "baseline": baseline,
                         "cases": cases, "captures": captures})
        for frozen in (inputs, baseline, *(run["root"] for run in runs)):
            review.rb.freeze_snapshot(frozen)
        return tuple(runs)

    def label_for(self, key, side):
        mapping = self.mapping_by_key[key]
        return "a" if mapping["a"] == side else "b"

    def review_directory(self, key):
        return self.source_review / "reviews" / key[0] / f"attempt-{key[1]}"

    @contextlib.contextmanager
    def mock_capture_preflight(self):
        # Only reconstruction of the expensive capture corpus is replaced.
        with mock.patch.object(review, "preflight", return_value=(self.corpus, self.boundary)), \
                mock.patch.object(review, "build_packets", side_effect=lambda *_: (
                    copy.deepcopy(self.rebuilt_packets), copy.deepcopy(self.rebuilt_mappings))):
            yield self

    def synthetic_reviewer(self, *, outcomes=None, initial_failures=None, adjudication_failures=None,
                           entered=None, release=None):
        """Return a no-model run_reviewer replacement writing real destination files.

        outcomes maps (mode, case_id, attempt) to invalid, missing, raise,
        forged-valid, citation, or novelty.  Failure maps bind slot keys to A/B labels.
        Optional events pause paid-session stand-ins to exercise the launch lock.
        """
        outcomes = outcomes or {}
        initial_failures = initial_failures or {}
        adjudication_failures = adjudication_failures or {}

        def run(packet, destination, scratch, system_file, config_file, timeout):
            mode = "adjudication" if "alleged_review" in packet else "review"
            key = packet["case_id"], packet["attempt"]
            with self._call_lock:
                self.calls.append({"mode": mode, "key": key, "destination": destination, "scratch": scratch,
                                   "timeout": timeout, "packet": copy.deepcopy(packet)})
            if entered is not None:
                entered.set()
            if release is not None and not release.wait(20):
                raise RuntimeError("synthetic launch coordination timed out")
            outcome = outcomes.get((mode, *key))
            if outcome == "raise":
                raise OSError("synthetic unavailable reviewer")
            failed = initial_failures.get(key) if mode == "review" else adjudication_failures.get(
                key, self.label_for(key, "baseline") if key == RETAINED_ALLEGATION else None)
            result = write_completed_review(packet, destination, scratch, system_file, config_file, timeout,
                                            failed_label=failed, invalid=outcome == "invalid")
            if outcome == "missing":
                (destination / "review.json").unlink()
            elif outcome == "forged-valid":
                result["execution"]["exit_code"] = 1
                write_json(destination / "review.json", result)
            elif outcome == "citation":
                result["judgment"]["criteria"][0]["evidence"]["a"]["observations"][0]["quote"] = "invented evidence"
                rewrite_completed_judgment(destination, result)
            elif outcome == "novelty":
                opposite = "b" if failed == "a" else "a"
                result["judgment"]["rationale"]["novel_contract_failures"] = [{
                    "criterion_id": packet["criteria"][0]["id"], "label": failed, "category": "preservation",
                    "reason": "The candidate introduces a preservation violation absent from the opposite repetitions.",
                    "observations": [{"path": f"/outputs/{failed}/final_output", "quote": "blue mug"}],
                    "rules": [{"path": "/criteria/0/description", "quote": packet["criteria"][0]["description"]}],
                    "comparisons": [{"path": f"/repetition_evidence/{opposite}/0/output/final_output", "quote": "blue mug"}],
                }]
                rewrite_completed_judgment(destination, result)
            return result

        return run


def make_synthetic_source(root):
    """Create a disposable source; root must not already exist."""
    return SyntheticRecoverySource(root)


def rehash_review(directory, record=None):
    record = read_json(directory / "review.json") if record is None else record
    record["raw_checksums"] = {path.name: review.rb.digest(path) for path in directory.iterdir()
                               if path.is_file() and path.name != "review.json"}
    write_json(directory / "review.json", record)
    return record


def rewrite_completed_judgment(directory, record):
    """Keep output/parsed/trace/hash coherence while deliberately corrupting semantics."""
    record["parsed_output"] = copy.deepcopy(record["judgment"])
    events = reviewer_events(record["judgment"])
    write_trace(directory / "trace.jsonl", events)
    write_text(directory / "output.txt", review.final_messages(events)[0])
    rehash_review(directory, record)


class ReviewRecoveryTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="review-recovery-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.fixture = make_synthetic_source(self.root / "source")
        self.out = self.root / "recovery"
        self.capture_patch = self.fixture.mock_capture_preflight()
        self.capture_patch.__enter__()
        self.addCleanup(self.capture_patch.__exit__, None, None, None)
        # Any accidental model process is a regression, not a fallback.
        self.launch = self.enterContext(mock.patch("subprocess.Popen", side_effect=AssertionError("No models in regression tests")))
        self.version = self.enterContext(mock.patch.object(review.rs, "_version", return_value=("omp synthetic-offline-fixture", None)))

    def plan(self, out=None):
        return recovery.plan(self.fixture.source_review, self.out if out is None else out)

    def run_recovery(self, runner=None):
        with mock.patch.object(review, "run_reviewer", side_effect=runner or self.fixture.synthetic_reviewer()), \
                contextlib.redirect_stdout(io.StringIO()):
            return recovery.run(self.out)

    def assert_prelaunch_rejected(self, operation):
        with mock.patch.object(review, "run_reviewer", side_effect=AssertionError("Tamper must be rejected before launch")) as runner:
            with self.assertRaises((ValueError, OSError)):
                operation()
            runner.assert_not_called()
        self.launch.assert_not_called()

    def test_inspection_and_offline_plan_preserve_all_old_bytes_and_classify_slots(self):
        original = tree_bytes(self.fixture.source_review)
        with mock.patch.object(review.rs, "_version", side_effect=AssertionError("Offline planning must not probe OMP")):
            inspection = recovery.inspect_source(self.fixture.source_review)
            manifest = self.plan()
            planned = recovery.status(self.out)
        self.assertEqual(inspection["counts"], {"total": 411, "reused": 200, "partial": 3, "unstarted": 208, "new": 211})
        self.assertEqual(manifest["counts"], inspection["counts"])
        self.assertEqual(len(inspection["packets"]), 411)
        self.assertEqual(len(inspection["reviews"]), 200)
        self.assertEqual(len(inspection["corpus"]["captures"]), 744)
        self.assertEqual(len(inspection["boundary"]["captures"]), 54)
        self.assertEqual({row["attempt"] for row in inspection["mappings"]}, {1, 2, 3})
        self.assertEqual(len({row["case_id"] for row in inspection["mappings"]}), 137)
        slots = {(row["case_id"], row["attempt"]): row for row in manifest["slots"]}
        self.assertEqual({key for key, row in slots.items() if row["origin"] == "reused"}, self.fixture.reused_keys)
        self.assertEqual({key for key, row in slots.items() if row["source_state"] == "interrupted"}, self.fixture.partial_keys)
        self.assertEqual({key for key, row in slots.items() if row["origin"] == "new"}, self.fixture.new_keys)
        for key in self.fixture.partial_keys:
            self.assertIsNone(slots[key]["source_record"])
            self.assertEqual(len(slots[key]["source_files"]), 4)
            self.assertFalse((self.fixture.review_directory(key) / "review.json").exists())
            for path, checksum in slots[key]["source_files"].items():
                self.assertTrue(Path(path).is_relative_to(self.fixture.source_review))
                self.assertEqual(review.rb.digest(Path(path)), checksum)
        for key in self.fixture.reused_keys:
            retained = slots[key]["source_record"]
            expected = self.fixture.review_directory(key) / "review.json"
            self.assertEqual(Path(retained["path"]), expected)
            self.assertEqual(retained["sha256"], review.rb.digest(expected))
        self.assertEqual(planned["state"], "planned")
        self.assertEqual(planned["counts"]["reused"], 200)
        self.assertEqual(planned["counts"]["partial"], 3)
        self.assertEqual(planned["counts"]["missing"], 211)
        self.assertEqual(planned["counts"]["new"], 0)
        self.assertEqual(planned["counts"]["valid_initial"], 200)
        self.assertEqual(planned["adjudications"], {"required": 1, "valid": 0, "missing": 1})
        self.assertFalse(planned["accepted"])
        for item in manifest["slots"]:
            path = self.out / item["packet_path"]
            source_path = self.fixture.source_review / item["packet_path"]
            self.assertEqual(path.read_bytes(), source_path.read_bytes())
            self.assertEqual(review.rb.digest(path), item["packet_sha256"])
        for relative in ("label-map.json", "fixtures/" + FIXTURE_NAME,
                         "provenance/review_split.py", "provenance/reviewer-system.txt", "provenance/omp-config.json"):
            self.assertEqual((self.out / relative).read_bytes(), (self.fixture.source_review / relative).read_bytes())
        self.assertEqual(tree_bytes(self.fixture.source_review), original)
        self.assertFalse((self.out / "launch.json").exists())
        self.version.assert_not_called()
        self.launch.assert_not_called()

    def test_success_uses_only_missing_destinations_and_mandatory_retained_adjudication(self):
        original = tree_bytes(self.fixture.source_review)
        self.plan()
        self.assertEqual(self.run_recovery(), 0)
        initial = [call for call in self.fixture.calls if call["mode"] == "review"]
        independent = [call for call in self.fixture.calls if call["mode"] == "adjudication"]
        self.assertEqual(len(initial), 211)
        self.assertEqual({call["key"] for call in initial}, self.fixture.new_keys)
        self.assertEqual([call["key"] for call in independent], [RETAINED_ALLEGATION])
        for call in self.fixture.calls:
            self.assertEqual(call["timeout"], 900)
            self.assertTrue(call["destination"].is_relative_to(self.out))
            self.assertFalse(call["destination"].is_relative_to(self.fixture.source_review))
            self.assertTrue((call["destination"] / "review.json").is_file())
        adjudication = independent[0]["packet"]
        baseline = self.fixture.label_for(RETAINED_ALLEGATION, "baseline")
        candidate = "b" if baseline == "a" else "a"
        self.assertEqual(adjudication["alleged_review"]["criteria"][0][baseline], "failed")
        self.assertEqual(adjudication["alleged_review"]["criteria"][0][candidate], "passed")
        for label in ("a", "b"):
            self.assertEqual([row["attempt"] for row in adjudication["repetition_evidence"][label]], [1, 2, 3])
        summary = read_json(self.out / "summary.json")
        self.assertTrue(summary["accepted"])
        self.assertTrue(all(summary["gates"].values()))
        self.assertEqual(summary["raw_counts"]["capture_slots"], 798)
        self.assertEqual(summary["raw_counts"]["completed_captures"], 798)
        self.assertEqual(summary["raw_counts"]["initial_reviews"], 411)
        self.assertEqual(summary["raw_counts"]["valid_initial_reviews"], 411)
        self.assertEqual(summary["raw_counts"]["required_adjudications"], 1)
        self.assertEqual(summary["raw_counts"]["valid_adjudications"], 1)
        self.assertEqual(len(summary["preexisting_baseline_failures"]), 1)
        self.assertEqual(summary["new_candidate_contract_failures"], [])
        boundaries = [row for row in summary["criterion_counts"] if row["suite"] == "boundary"]
        self.assertEqual(len(boundaries), 13)
        self.assertTrue(all(row["candidate"]["passed"] == 3 for row in boundaries))
        manifest = read_json(self.out / "manifest.json")
        self.assertEqual(manifest["state"], "finished")
        self.assertEqual(manifest["acceptance"], "passed")
        references = manifest["reviews"]
        self.assertEqual(len(references), 411)
        self.assertEqual({(row["case_id"], row["attempt"]) for row in references},
                         self.fixture.reused_keys | self.fixture.new_keys)
        for row in references:
            key = row["case_id"], row["attempt"]
            reused = key in self.fixture.reused_keys
            self.assertEqual(row["origin"], "reused" if reused else "new")
            expected = self.fixture.review_directory(key) / "review.json" if reused else (
                self.out / "reviews" / key[0] / f"attempt-{key[1]}" / "review.json")
            self.assertEqual(Path(row["physical_path"]), expected)
            self.assertEqual(Path(row["path"]), expected if reused else expected.relative_to(self.out))
            self.assertEqual(row["sha256"], review.rb.digest(expected))
            self.assertEqual(row["packet_sha256"],
                             review.rb.digest(self.out / "packets" / key[0] / f"attempt-{key[1]}" / "packet.json"))
            self.assertTrue(row["valid"])
        self.assertEqual(len(summary["recovery"]["reviews"]), 411)
        for row in summary["recovery"]["reviews"]:
            self.assertEqual(row["sha256"], review.rb.digest(Path(row["physical_path"])))
        self.assertEqual(len(manifest["adjudications"]), 1)
        self.assertEqual(len(manifest["adjudication_packets"]), 1)
        adjudication_record = manifest["adjudications"][0]
        adjudication_packet = manifest["adjudication_packets"][0]
        self.assertEqual(adjudication_record["origin"], "new")
        self.assertEqual(adjudication_record["sha256"], review.rb.digest(Path(adjudication_record["physical_path"])))
        self.assertEqual(adjudication_packet["sha256"], review.rb.digest(self.out / adjudication_packet["path"]))
        self.assertEqual(adjudication_record["packet_sha256"], adjudication_packet["sha256"])
        completions = [json.loads(line) for line in (self.out / "completion-stdout.txt").read_text().splitlines()]
        initial_completions = [row for row in completions if row.get("mode") == "reviews"]
        self.assertEqual({(row["case_id"], row["attempt"]) for row in initial_completions}, self.fixture.new_keys)
        self.assertTrue(all(row["valid"] and row["status"] == "completed" for row in initial_completions))
        self.assertEqual(manifest["completion_stdout_sha256"], review.rb.digest(self.out / "completion-stdout.txt"))
        self.assertEqual(manifest["execution_sha256"], review.rb.digest(self.out / "execution.json"))
        finished = recovery.status(self.out)
        self.assertEqual(finished["counts"]["valid_initial"], 411)
        self.assertEqual(finished["counts"]["reused"], 200)
        self.assertEqual(finished["counts"]["new"], 211)
        self.assertEqual(finished["counts"]["missing"], 0)
        self.assertEqual(finished["adjudications"], {"required": 1, "valid": 1, "missing": 0})
        self.assertTrue(finished["accepted"])
        self.assertEqual(tree_bytes(self.fixture.source_review), original)
        self.assertTrue((self.out / "launch.json").is_file())
        # No copied/referenced completed record may be replaced by a fresh run.
        self.assertTrue(self.fixture.reused_keys.isdisjoint({call["key"] for call in initial}))

    def test_every_new_hard_allegation_is_independently_reassessed(self):
        self.plan()
        corpus_key = next(key for key in sorted(self.fixture.new_keys)
                          if self.fixture.packet_by_key[key]["paired"] and key != RETAINED_ALLEGATION)
        single_key = next(key for key in sorted(self.fixture.new_keys)
                          if not self.fixture.packet_by_key[key]["paired"])
        failures = {corpus_key: self.fixture.label_for(corpus_key, "candidate"), single_key: "a"}
        self.assertEqual(self.run_recovery(self.fixture.synthetic_reviewer(initial_failures=failures)), 0)
        independent = [call for call in self.fixture.calls if call["mode"] == "adjudication"]
        self.assertEqual({call["key"] for call in independent}, {RETAINED_ALLEGATION, corpus_key, single_key})
        self.assertEqual(len(independent), 3)
        summary = read_json(self.out / "summary.json")
        self.assertEqual(summary["raw_counts"]["required_adjudications"], 3)
        self.assertEqual(summary["raw_counts"]["valid_adjudications"], 3)
        self.assertEqual(summary["new_candidate_contract_failures"], [])

    def test_confirmed_failures_keep_the_original_acceptance_gates(self):
        corpus_key = next(key for key in sorted(self.fixture.new_keys) if key[0].startswith("corpus-"))
        boundary_key = next(key for key in sorted(self.fixture.new_keys)
                            if not self.fixture.packet_by_key[key]["paired"])
        for index, (name, key, novelty, blocked_gates) in enumerate((
            ("paired", corpus_key, False, ("candidate_per_criterion_failures_not_above_baseline", "baseline_always_pass_protected")),
            ("boundary", boundary_key, False, ("all_boundary_checks_pass",)),
            ("novel-contract", corpus_key, True, ("no_new_candidate_contract_failures",)),
        )):
            with self.subTest(name=name):
                self.out = self.root / f"confirmed-failure-{index}"
                self.fixture.calls.clear()
                self.plan()
                label = self.fixture.label_for(key, "candidate")
                runner = self.fixture.synthetic_reviewer(
                    initial_failures={key: label}, adjudication_failures={key: label},
                    outcomes={("adjudication", *key): "novelty"} if novelty else {})
                self.assertEqual(self.run_recovery(runner), 1)
                summary = read_json(self.out / "summary.json")
                self.assertFalse(summary["accepted"])
                self.assertTrue(summary["gates"]["reviews_complete"])
                self.assertTrue(summary["gates"]["adjudications_complete"])
                for gate in blocked_gates:
                    self.assertFalse(summary["gates"][gate])
                self.assertEqual(summary["raw_counts"]["valid_initial_reviews"], 411)
                self.assertEqual(summary["raw_counts"]["valid_adjudications"], 2)
                if novelty:
                    self.assertEqual(len(summary["new_candidate_contract_failures"]), 1)

    def test_missing_or_invalid_new_reviews_and_adjudications_block_without_retry(self):
        key = sorted(self.fixture.new_keys)[0]
        for index, (mode, outcome) in enumerate((
            ("review", "invalid"), ("review", "missing"), ("review", "raise"),
            ("review", "forged-valid"), ("review", "citation"),
            ("adjudication", "invalid"), ("adjudication", "missing"),
            ("adjudication", "forged-valid"), ("adjudication", "citation"),
        )):
            with self.subTest(mode=mode, outcome=outcome):
                self.out = self.root / f"failed-recovery-{index}"
                self.fixture.calls.clear()
                self.plan()
                target = RETAINED_ALLEGATION if mode == "adjudication" else key
                runner = self.fixture.synthetic_reviewer(outcomes={(mode, *target): outcome})
                self.assertEqual(self.run_recovery(runner), 1)
                summary = read_json(self.out / "summary.json")
                self.assertFalse(summary["accepted"])
                self.assertFalse(summary["gates"]["adjudications_complete" if mode == "adjudication" else "reviews_complete"])
                blocked = recovery.status(self.out)
                self.assertFalse(blocked["accepted"])
                self.assertEqual(blocked["state"], "finished")
                if mode == "adjudication":
                    self.assertEqual(blocked["adjudications"], {"required": 1, "valid": 0, "missing": 1})
                self.assertEqual(sum(call["mode"] == mode and call["key"] == target for call in self.fixture.calls), 1)
                self.assertEqual(sum(call["mode"] == "review" for call in self.fixture.calls), 211)
                target_file = self.out / ("adjudications" if mode == "adjudication" else "reviews") / target[0] / f"attempt-{target[1]}" / "review.json"
                if outcome != "missing":
                    self.assertTrue(target_file.is_file())
                count = len(self.fixture.calls)
                self.assert_prelaunch_rejected(lambda: recovery.run(self.out))
                self.assertEqual(len(self.fixture.calls), count)

    def test_repeat_and_concurrent_runs_are_prevented_even_before_first_completion(self):
        self.plan()
        entered, release = threading.Event(), threading.Event()
        runner = self.fixture.synthetic_reviewer(entered=entered, release=release)
        with mock.patch.object(review, "run_reviewer", side_effect=runner), contextlib.redirect_stdout(io.StringIO()), \
                ThreadPoolExecutor(max_workers=1) as pool:
            first = pool.submit(recovery.run, self.out)
            try:
                self.assertTrue(entered.wait(20))
                self.assertTrue((self.out / "launch.json").is_file())
                active = recovery.status(self.out)
                self.assertEqual(active["state"], "started")
                self.assertFalse(active["accepted"])
                with self.assertRaises((ValueError, OSError)):
                    recovery.run(self.out)
            finally:
                release.set()
            self.assertEqual(first.result(timeout=30), 0)
        self.assertEqual(sum(call["mode"] == "review" for call in self.fixture.calls), 211)
        self.assert_prelaunch_rejected(lambda: recovery.run(self.out))
        interrupted_out = self.root / "interrupted-recovery"
        self.plan(interrupted_out)
        write_json(interrupted_out / "launch.json", {"started_at": "2026-10-09T00:00:00+00:00", "pid": 999999})
        self.assert_prelaunch_rejected(lambda: recovery.run(interrupted_out))

    def test_status_and_cli_status_are_read_only_and_never_treat_partial_reasoning_as_review(self):
        self.plan()
        original = tree_bytes(self.out)
        with mock.patch.object(review.rs, "_version", side_effect=AssertionError("Status is offline")), \
                mock.patch.object(review, "run_reviewer", side_effect=AssertionError("Status never launches")) as runner:
            status = recovery.status(self.out)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(recovery.main(["status", "--out", str(self.out)]), 0)
            self.assertEqual(json.loads(stdout.getvalue()), status)
            runner.assert_not_called()
        self.assertEqual(status["counts"]["valid_initial"], 200)
        self.assertEqual(status["counts"]["partial"], 3)
        self.assertEqual(status["counts"]["missing"], 211)
        self.assertEqual(tree_bytes(self.out), original)

    def test_existing_output_and_finished_failed_or_recovered_source_campaigns_are_rejected(self):
        self.out.mkdir()
        write_text(self.out / "keep.txt", "existing user-owned output")
        self.assert_prelaunch_rejected(self.plan)
        self.assertEqual((self.out / "keep.txt").read_text(encoding="utf-8"), "existing user-owned output")
        for change in ({"acceptance": "passed"}, {"acceptance": "blocked"},
                       {"finished_at": "2026-10-09T00:00:00+00:00"}, {"kind": "review-only-split-recovery"}):
            with self.subTest(change=change), restored_evidence(self.fixture.source_review):
                manifest = read_json(self.fixture.source_review / "manifest.json")
                manifest.update(change)
                write_json(self.fixture.source_review / "manifest.json", manifest)
                self.assert_prelaunch_rejected(lambda: recovery.plan(self.fixture.source_review, self.root / "new-output"))

    def test_rebuilt_packets_and_mappings_must_equal_retained_evidence(self):
        for field in ("packet", "mapping"):
            with self.subTest(field=field):
                if field == "packet":
                    original = self.fixture.rebuilt_packets[0]["packet"]["request"]
                    self.fixture.rebuilt_packets[0]["packet"]["request"] = "A changed request from frozen captures"
                else:
                    original = copy.deepcopy(self.fixture.rebuilt_mappings[0])
                    row = self.fixture.rebuilt_mappings[0]
                    row["a"], row["b"] = row["b"], row["a"]
                try:
                    self.assert_prelaunch_rejected(lambda: recovery.plan(self.fixture.source_review, self.root / f"mismatch-{field}"))
                finally:
                    if field == "packet":
                        self.fixture.rebuilt_packets[0]["packet"]["request"] = original
                    else:
                        self.fixture.rebuilt_mappings[0] = original

    def test_source_tampering_is_rejected_before_any_recovery_session(self):
        key = sorted(self.fixture.reused_keys)[0]
        directory = self.fixture.review_directory(key)
        partial = self.fixture.review_directory(sorted(self.fixture.partial_keys)[0])
        mutations = (
            "raw-hash", "unhashed-raw", "missing-raw-hash", "packet-hash", "record-identity", "judgment-identity",
            "judgment-disagrees", "malformed-review", "invalid-review", "citation", "not-assessed",
            "trace-terminal", "trace-malformed", "tool", "model",
            "command-model", "command-thinking", "command-deadline", "command-tools", "command-system",
            "context-system", "context-config", "execution", "errors", "provenance", "config-provenance",
            "provenance-resealed", "system-provenance-resealed",
            "partial-terminal", "partial-command", "partial-model", "partial-judgment", "unknown-slot", "symlink",
            "manifest-model", "manifest-thinking", "manifest-deadline", "unsafe-packet-path", "mapping",
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation), restored_evidence(self.fixture.source_review):
                record = read_json(directory / "review.json")
                if mutation == "raw-hash":
                    write_text(directory / "stderr.txt", "unrecorded changed bytes")
                elif mutation == "unhashed-raw":
                    write_text(directory / "extra.txt", "unhashed evidence")
                elif mutation == "missing-raw-hash":
                    record["raw_checksums"].pop("stderr.txt")
                    write_json(directory / "review.json", record)
                elif mutation == "packet-hash":
                    record["packet_sha256"] = "0" * 64
                    write_json(directory / "review.json", record)
                elif mutation == "record-identity":
                    record["attempt"] = 2 if key[1] != 2 else 1
                    write_json(directory / "review.json", record)
                elif mutation in {"judgment-identity", "citation", "not-assessed"}:
                    if mutation == "judgment-identity":
                        record["judgment"]["case_id"] = "wrong-case"
                    elif mutation == "citation":
                        record["judgment"]["criteria"][0]["evidence"]["a"]["observations"][0]["quote"] = "invented evidence"
                    else:
                        record["judgment"]["criteria"][0]["a"] = "not-run"
                        record["judgment"]["regression"] = None
                    rewrite_completed_judgment(directory, record)
                elif mutation == "judgment-disagrees":
                    record["judgment"]["rationale"] = "A replacement judgment, unlike the final output."
                    write_json(directory / "review.json", record)
                elif mutation == "malformed-review":
                    write_text(directory / "review.json", "{not json}\n")
                elif mutation == "invalid-review":
                    record["valid"] = False
                    write_json(directory / "review.json", record)
                elif mutation in {"trace-terminal", "trace-malformed", "tool", "model"}:
                    events = [json.loads(line) for line in (directory / "trace.jsonl").read_text().splitlines()]
                    if mutation == "trace-terminal":
                        events.pop()
                    elif mutation == "tool":
                        events[0]["toolName"] = "bash"
                        events[1]["toolName"] = "bash"
                    elif mutation == "model":
                        events[2]["message"]["model"] = "unapproved-model"
                        metadata = review.review_metadata(events)
                        record["model_metadata"] = metadata
                        context = read_json(directory / "context.json")
                        context.update(metadata)
                        write_json(directory / "context.json", context)
                    write_trace(directory / "trace.jsonl", events)
                    if mutation == "trace-malformed":
                        write_text(directory / "trace.jsonl", "{not json}\n")
                    rehash_review(directory, record)
                elif mutation.startswith("command-"):
                    flag, value = {
                        "command-model": ("--model", "unapproved-model"), "command-thinking": ("--thinking", "low"),
                        "command-deadline": ("--max-time", "899s"), "command-tools": ("--tools", "read,grep,glob,bash"),
                        "command-system": ("--system-prompt", str(self.root / "other-system.txt")),
                    }[mutation]
                    command = read_json(directory / "command.json")
                    command[command.index(flag) + 1] = value
                    write_json(directory / "command.json", command)
                    record["command"] = command
                    rehash_review(directory, record)
                elif mutation in {"context-system", "context-config"}:
                    context = read_json(directory / "context.json")
                    context["system_prompt" if mutation == "context-system" else "config_sha256"] = "changed system" if mutation == "context-system" else "0" * 64
                    write_json(directory / "context.json", context)
                    rehash_review(directory)
                elif mutation == "execution":
                    record["execution"]["exit_code"] = 1
                    write_json(directory / "review.json", record)
                elif mutation == "errors":
                    record["validation_errors"] = ["ignored failure"]
                    write_json(directory / "review.json", record)
                elif mutation in {"provenance", "config-provenance", "provenance-resealed", "system-provenance-resealed"}:
                    name = ("omp-config.json" if mutation == "config-provenance" else
                            "reviewer-system.txt" if mutation == "system-provenance-resealed" else "review_split.py")
                    path = self.fixture.source_review / "provenance" / name
                    write_text(path, path.read_text() + "\nchanged provenance\n")
                    if mutation.endswith("-resealed"):
                        manifest = read_json(self.fixture.source_review / "manifest.json")
                        manifest["provenance_files"][name] = review.rb.digest(path)
                        write_json(self.fixture.source_review / "manifest.json", manifest)
                elif mutation == "partial-terminal":
                    write_trace(partial / "trace.jsonl", reviewer_events(synthetic_judgment(self.fixture.packet_by_key[sorted(self.fixture.partial_keys)[0]])))
                elif mutation == "partial-command":
                    command = read_json(partial / "command.json")
                    command[command.index("--thinking") + 1] = "low"
                    write_json(partial / "command.json", command)
                elif mutation == "partial-model":
                    events = [json.loads(line) for line in (partial / "trace.jsonl").read_text().splitlines()]
                    events[0]["message"]["model"] = "unapproved-model"
                    write_trace(partial / "trace.jsonl", events)
                elif mutation == "partial-judgment":
                    write_json(partial / "review.json", record)
                elif mutation == "unknown-slot":
                    write_text(self.fixture.source_review / "reviews/unknown-case/attempt-1/request.txt", "unknown slot")
                elif mutation == "symlink":
                    path = directory / "stderr.txt"
                    path.unlink()
                    path.symlink_to(self.root / "outside-stderr.txt")
                    write_text(self.root / "outside-stderr.txt", "")
                elif mutation.startswith("manifest-"):
                    manifest = read_json(self.fixture.source_review / "manifest.json")
                    field, value = {"manifest-model": ("model_requested", "unapproved-model"),
                                    "manifest-thinking": ("reasoning_requested", "low"),
                                    "manifest-deadline": ("timeout_seconds", 901)}[mutation]
                    manifest[field] = value
                    write_json(self.fixture.source_review / "manifest.json", manifest)
                elif mutation == "unsafe-packet-path":
                    manifest = read_json(self.fixture.source_review / "manifest.json")
                    manifest["packets"][0]["path"] = "../outside-packet.json"
                    write_json(self.fixture.source_review / "manifest.json", manifest)
                elif mutation == "mapping":
                    mappings = read_json(self.fixture.source_review / "label-map.json")
                    mappings[0]["a"], mappings[0]["b"] = mappings[0]["b"], mappings[0]["a"]
                    write_json(self.fixture.source_review / "label-map.json", mappings)
                self.assert_prelaunch_rejected(lambda: recovery.plan(self.fixture.source_review, self.root / f"tampered-{mutation}"))

    def test_source_and_planned_preparation_drift_block_before_launch(self):
        self.plan()
        source_directory = self.fixture.review_directory(sorted(self.fixture.reused_keys)[0])
        partial_directory = self.fixture.review_directory(sorted(self.fixture.partial_keys)[0])
        targets = (
            source_directory / "review.json", partial_directory / "stderr.txt",
            self.fixture.source_review / "label-map.json", self.fixture.source_review / "provenance/review_split.py",
            self.out / "packets/corpus-000/attempt-1/packet.json", self.out / "label-map.json",
            self.out / "provenance/review_recovery.py", self.out / "provenance/review_split.py",
            self.out / "provenance/reviewer-system.txt", self.out / "provenance/omp-config.json",
            self.out / "fixtures" / FIXTURE_NAME,
        )
        for target in targets:
            with self.subTest(target=str(target)), restored_evidence(self.fixture.source_review), restored_evidence(self.out):
                target.chmod(0o644)
                target.write_bytes(target.read_bytes() + b"\nchanged after planning\n")
                self.assert_prelaunch_rejected(lambda: recovery.run(self.out))
                self.assertFalse((self.out / "launch.json").exists())
        with restored_evidence(self.out):
            key = sorted(self.fixture.reused_keys)[0]
            replacement = self.out / "reviews" / key[0] / f"attempt-{key[1]}" / "review.json"
            write_json(replacement, read_json(self.fixture.review_directory(key) / "review.json"))
            self.assert_prelaunch_rejected(lambda: recovery.run(self.out))


if __name__ == "__main__":
    unittest.main()
