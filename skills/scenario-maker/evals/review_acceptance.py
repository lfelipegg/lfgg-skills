#!/usr/bin/env python3
"""Prepare/validate offline; execute a separately authorized frozen assessment once.

Only ``execute`` invokes OMP. Invoke it from the retained provenance directory in
one managed process, without an enclosing shell deadline. launch.json permanently
claims the attempt, including failed binding/version checks. Readiness proves
runner startup, never provider success. There is no retry, resume, canary, or
automatic stop-on-first-failure policy.

An abrupt stop leaves no terminal execution record and cannot be accepted. The
``record-interruption`` command accepts only externally observed terminal stop
evidence: suspend this runner first, inventory and terminate isolated reviewer
process groups, then terminate the runner. It does not signal processes, invent
execution.json, or authorize another launch. See observe_interruption's schema.
"""
import argparse
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time

import review_acceptance_prepare as preparation_api
import review_split as review
import run_baseline as rb
import run_split as rs

EVALS = Path(__file__).resolve().parent
MODEL = "openai-codex/gpt-6-astra"
TIMEOUT = 900
JOBS = 3
FRESH_GATES = (
    "captures_complete", "reviews_complete", "adjudications_complete",
    "all_boundary_checks_pass", "no_new_candidate_contract_failures",
    "candidate_per_criterion_failures_not_above_baseline", "baseline_always_pass_protected",
)
BINDING_GATES = (
    "capture_bindings_valid", "current_runtime_inputs_match", "packet_coverage_complete",
    "historical_packet_complete", "context_evidence_applicable", "packaging_evidence_applicable",
)


def now():
    return datetime.now(timezone.utc).isoformat()


def future_command(out, managed_handle):
    """Exact future argv; a retained recommendation, not execution authorization."""
    out = Path(out).absolute()
    return [sys.executable, "-B", "-u", str(out / "ai-review/provenance/review_acceptance.py"),
            "execute", "--out", str(out), "--managed-handle", managed_handle]


def exclusive_json(path, value):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    path.chmod(0o444)


def file_binding(root, path):
    path = Path(path)
    return {"path": path.relative_to(root).as_posix(), "sha256": rb.digest(path)}


def process_identity(pid):
    """Observed Linux start identity prevents confusing a recycled PID."""
    identity = {"pid": pid, "boot_id": None, "start_ticks": None, "state": None}
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(") ", 1)[1].split()
        identity.update(state=fields[0], start_ticks=fields[19],
                        boot_id=Path("/proc/sys/kernel/random/boot_id").read_text().strip())
    except (OSError, IndexError):
        pass
    return identity


def _require_frozen_execution(out, validated, managed_handle):
    provenance = Path(validated["provenance"]).resolve()
    if provenance != (out / "ai-review/provenance").resolve():
        raise review.ReviewError("validated evaluator is not this acceptance's frozen provenance")
    names = ("review_acceptance", "review_acceptance_prepare", "review_acceptance_history",
             "review_split", "run_split", "run_baseline", "evaluate")
    for name in names:
        module = sys.modules.get(name)
        path = Path(__file__).resolve() if name == "review_acceptance" else Path(module.__file__).resolve() if module else None
        if path != provenance / (name + ".py"):
            raise review.ReviewError(f"execute must use the frozen imported closure: {name}")
    prepared = validated["preparation"]
    controls = {"model_requested": MODEL, "reasoning_requested": "high", "timeout_seconds": TIMEOUT,
                "jobs": JOBS, "expected_packets": 411, "expected_capture_slots": 798}
    for key, value in controls.items():
        if prepared.get(key) != value:
            raise review.ReviewError(f"prepared execution control differs: {key}")
    if rb.MODEL != MODEL or len(validated["packets"]) != 411:
        raise review.ReviewError("frozen model or packet coverage differs from authorized controls")
    future = prepared.get("future_execution", {})
    if future.get("managed_handle") != managed_handle or future.get("argv") != future_command(out, managed_handle):
        raise review.ReviewError("managed handle/exact future argv differs from the prepared supervision binding")
    if list(getattr(sys, "orig_argv", [])) != future["argv"]:
        raise review.ReviewError("observed interpreter argv differs from the prepared exact launch command")
    gates = prepared.get("gates", {})
    if not all(gates.get(name) is True for name in BINDING_GATES):
        raise review.ReviewError("required source, context, packaging, or packet binding gate is not passing")


class _Tee:
    def __init__(self, retained, original):
        self.retained, self.original = retained, original

    def write(self, text):
        self.retained.write(text)
        self.retained.flush()
        # A supervisor disappearing must not discard the retained wave evidence.
        try:
            self.original.write(text)
            self.original.flush()
        except (OSError, ValueError):
            pass
        return len(text)

    def flush(self):
        self.retained.flush()
        try:
            self.original.flush()
        except (OSError, ValueError):
            pass


def observe_runtime(out):
    """Observe the existing OMP help/version banner once, only after binding checks."""
    argv = ["omp", "--help"]
    started, start = now(), time.monotonic()
    exit_code, error, pid = None, None, None
    stdout_path, stderr_path = out / "omp-version-stdout.txt", out / "omp-version-stderr.txt"
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        try:
            process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                       start_new_session=True,
                                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "TZ": "UTC", "LC_ALL": "C.UTF-8"})
            pid = process.pid
            try:
                exit_code = process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(pid, signal.SIGKILL)
                process.wait()
                exit_code, error = process.returncode, "runtime version observation timed out"
        except OSError as exc:
            error = f"{type(exc).__name__}: {exc}"
    lines = stdout_path.read_text(encoding="utf-8", errors="replace").splitlines()
    version = lines[0].strip() if lines else None
    if exit_code != 0 or not isinstance(version, str) or not re.fullmatch(r"omp v\d+\.\d+\.\d+\S*", version):
        error = error or "runtime version command failed or OMP version banner is missing"
    runtime = {"argv": argv, "started_at": started, "elapsed_seconds": round(time.monotonic() - start, 3),
               "pid": pid, "exit_code": exit_code, "omp_version": version, "error": error,
               "valid": error is None, "stdout": file_binding(out, stdout_path), "stderr": file_binding(out, stderr_path)}
    exclusive_json(out / "runtime-version.json", runtime)
    stdout_path.chmod(0o444)
    stderr_path.chmod(0o444)
    return runtime


def historical_disposition(first, independent, packet):
    """Use original A=baseline/B=candidate; regression:true alone has no direction."""
    if (packet.get("case_id"), packet.get("attempt")) != ("h3-dev-02", 2):
        raise review.ReviewError("historical supplemental identity differs")
    original_packet = {key: value for key, value in packet.items() if key not in {"alleged_review", "review_mode", "repetition_evidence"}}
    review.validate_judgment(first["judgment"], original_packet)
    original = next((row for row in first["judgment"]["criteria"] if row["id"] == "h3-dev-02-E1"), None)
    if not first.get("valid") or original is None or (original["a"], original["b"]) != ("failed", "passed"):
        raise review.ReviewError("historical original allegation must remain baseline-only")
    validation_error = None
    if independent is not None and independent.get("valid"):
        try:
            review.validate_judgment(independent["judgment"], packet)
        except (ValueError, KeyError, TypeError) as exc:
            validation_error = str(exc)
            independent = {**independent, "valid": False}
    final = review.disposition(first, independent, packet)
    complete = independent is not None and independent.get("valid") is True and not final["unresolved"]
    novel, candidate_differences = [], []
    if complete:
        novel = [claim for claim in final["judgment"]["rationale"]["novel_contract_failures"] if claim["label"] == "b"]
        hard = {criterion["id"] for criterion in packet["criteria"] if criterion.get("severity", "hard") != "advisory"}
        candidate_differences = [row["id"] for row in final["judgment"]["criteria"]
                                 if row["id"] in hard and row["b"] == "failed" and row["a"] == "passed"]
    return {"kind": "supplemental-historical-independent-disposition", "case_id": "h3-dev-02", "attempt": 2,
            "label_alignment": {"a": "baseline", "b": "candidate"},
            "original_allegation": {"criterion_id": "h3-dev-02-E1", "label": "a", "side": "baseline"},
            "independent_session_present": independent is not None, "complete": complete,
            "state": final["state"], "unresolved": final["unresolved"], "judgment": final["judgment"],
            "allegations": [{**item, "side": "baseline" if item["label"] == "a" else "candidate"} for item in final["allegations"]],
            "new_candidate_contract_failures": novel, "candidate_failure_on_baseline_pass": candidate_differences,
            "validation_error": validation_error,
            "scope": "one supplemental session, separate from all 411 fresh initial slots"}


def combined_outcome(fresh, historical, runtime, binding_gates, links, terminal_complete=True):
    """Never accept a standalone fresh pass without independent historical coverage."""
    fresh_gates = fresh.get("gates", {}) if isinstance(fresh, dict) else {}
    gates = {f"fresh_{name}": fresh_gates.get(name) is True for name in FRESH_GATES}
    gates.update({name: binding_gates.get(name) is True for name in BINDING_GATES})
    gates.update(fresh_aggregate_accepted=isinstance(fresh, dict) and fresh.get("accepted") is True,
                 mandatory_historical_disposition_complete=isinstance(historical, dict) and historical.get("complete") is True,
                 no_historical_candidate_novel_hard_failures=isinstance(historical, dict) and historical.get("complete") is True and not historical.get("new_candidate_contract_failures"),
                 historical_candidate_baseline_pass_protected=isinstance(historical, dict) and historical.get("complete") is True and not historical.get("candidate_failure_on_baseline_pass"),
                 review_runtime_provenance_recorded=isinstance(runtime, dict) and runtime.get("valid") is True and bool(runtime.get("omp_version")) and bool(runtime.get("stdout")) and bool(runtime.get("stderr")),
                 retained_outcome_links_complete=all(isinstance(links.get(name), dict) and links[name].get("path") and links[name].get("sha256")
                                                   for name in ("preparation", "launch", "fresh_manifest", "fresh_summary", "historical_packet", "historical_first", "historical_disposition", "historical_review", "runtime")),
                 terminal_execution_observed=terminal_complete is True)
    accepted = all(gates.values())
    return {"kind": "combined-fresh-and-historical-ai-acceptance", "reviewer_kind": "ai",
            "accepted": accepted, "outcome": "passed" if accepted else "not-accepted", "gates": gates,
            "evidence": links, "historical_original_allegation_side": "baseline",
            "limitations": ["Separate AI assessment, not legacy human sign-off or rendered-media proof",
                            "Side-label blinding is not identity-proof anonymity; declared read-only tools are not an OS sandbox",
                            "Prior context/packaging evidence is bound, not claimed as rerun"]}


def _review_records(ai, group, results):
    rows = []
    for (case_id, attempt), value in sorted(results.items()):
        path = ai / group / case_id / f"attempt-{attempt}" / "review.json"
        if value["raw_checksums"]:
            review.verify_files(path.parent, value["raw_checksums"], "new reviewer raw evidence")
        elif value["valid"]:
            raise review.ReviewError("valid new review has no retained raw evidence")
        rows.append({"case_id": case_id, "attempt": attempt, "valid": value["valid"],
                     **file_binding(ai, path), "packet_sha256": value.get("packet_sha256"),
                     "execution": value["execution"], "raw_checksums": value["raw_checksums"]})
    return rows


def _fresh_and_historical(out, validated, runtime, launch):
    prepared, packets, mappings = validated["preparation"], validated["packets"], validated["mappings"]
    ai, provenance = out / "ai-review", Path(validated["provenance"])
    system_file, config_file = provenance / "reviewer-system.txt", provenance / "omp-config.json"
    manifest = {"kind": "fresh-independent-ai-acceptance-review", "created_at": now(),
                "reviewer_kind": "ai", "model_requested": MODEL, "reasoning_requested": "high",
                "timeout_seconds": TIMEOUT, "jobs": JOBS, "expected_packets": 411, "expected_capture_slots": 798,
                "reused_initial_judgments": 0, "supplemental_historical_sessions_in_fresh_summary": 0,
                "omp_version": runtime["omp_version"], "runtime": file_binding(out, out / "runtime-version.json"),
                "preparation": file_binding(out, out / "preparation.json"), "launch": file_binding(out, out / "launch.json"),
                "capture_manifest_hashes": prepared["capture_manifest_hashes"],
                "baseline_revision": prepared["baseline_revision"], "candidate_revision": prepared["candidate_revision"],
                "provenance_files": prepared["provenance_files"], "packets": prepared["packets"],
                "retry_policy": "none; no resume/replacement/reused judgments/best-of aggregation", "acceptance": "not assessed"}
    rb.save_json(ai / "manifest.json", manifest)
    with tempfile.TemporaryDirectory(prefix="scenario-maker-fresh-acceptance-") as temporary:
        scratch = Path(temporary)
        reviews = review.execute_wave(packets, ai, scratch / "initial", system_file, config_file, TIMEOUT, JOBS)
        allegations = []
        for item in packets:
            packet = item["packet"]
            first = reviews[(packet["case_id"], packet["attempt"])]
            if first["valid"] and review.needs_adjudication(first["judgment"], packet):
                independent = review.adjudication_packet(item, packets, mappings, first)
                directory = ai / "adjudication-packets" / packet["case_id"] / f"attempt-{packet['attempt']}"
                directory.mkdir(parents=True, exist_ok=False)
                rb.save_json(directory / "packet.json", independent)
                rb.freeze_snapshot(directory)
                allegations.append({**item, "packet": independent, "adjudication_packet": file_binding(ai, directory / "packet.json")})
        adjudications = review.execute_wave(allegations, ai, scratch / "adjudication", system_file, config_file, TIMEOUT, JOBS, adjudication=True)
        summary = review.aggregate(packets, mappings, reviews, adjudications)
        manifest.update(finished_at=now(), acceptance="passed" if summary["accepted"] else "blocked",
                        reviews=_review_records(ai, "reviews", reviews), adjudications=_review_records(ai, "adjudications", adjudications),
                        adjudication_packets=[{"case_id": item["packet"]["case_id"], "attempt": item["packet"]["attempt"], **item["adjudication_packet"]} for item in allegations])
        exclusive_json(ai / "summary.json", summary)
        manifest["summary"] = file_binding(ai, ai / "summary.json")
        rb.save_json(ai / "manifest.json", manifest)
        (ai / "manifest.json").chmod(0o444)
        # Mandatory even when all fresh judgments pass or the fresh aggregate fails.
        packet = validated["historical_packet"]
        destination = ai / "historical-adjudications/h3-dev-02/attempt-2"
        try:
            independent = review.run_reviewer(packet, destination, scratch / "historical", system_file, config_file, TIMEOUT)
        except Exception as exc:
            independent = review.failed_review(packet, destination, f"historical reviewer failure: {type(exc).__name__}: {exc}")
        historical = historical_disposition(validated["historical_first"], independent, packet)
        record = _review_records(ai, "historical-adjudications", {("h3-dev-02", 2): independent})[0]
        historical.update(packet=file_binding(out, out / "historical-packet.json"),
                          first=file_binding(out, out / "historical-first.json"), independent_review=record)
        exclusive_json(out / "historical-disposition.json", historical)
    links = {"preparation": file_binding(out, out / "preparation.json"), "launch": file_binding(out, out / "launch.json"),
             "fresh_manifest": file_binding(out, ai / "manifest.json"), "fresh_summary": file_binding(out, ai / "summary.json"),
             "historical_packet": file_binding(out, out / "historical-packet.json"), "historical_first": file_binding(out, out / "historical-first.json"),
             "historical_disposition": file_binding(out, out / "historical-disposition.json"),
             "historical_review": file_binding(out, destination / "review.json"), "runtime": file_binding(out, out / "runtime-version.json")}
    return combined_outcome(summary, historical, runtime, prepared["gates"], links)


def execute(out, managed_handle):
    """Consume the prepared attempt once; explicit execution is separately authorized."""
    out = rs._root(Path(out), "prepared acceptance")
    if not isinstance(managed_handle, str) or not managed_handle.strip():
        raise review.ReviewError("a real managed process handle is required")
    preparation_path = out / "preparation.json"
    try:
        preparation_sha256 = rb.digest(preparation_path)
    except OSError:
        preparation_sha256 = None
    launch = {"kind": "permanent-single-launch-acceptance-claim", "started_at": now(),
              "pid": os.getpid(), "ppid": os.getppid(), "process_identity": process_identity(os.getpid()),
              "managed_handle": managed_handle, "argv": list(getattr(sys, "orig_argv", [sys.executable, *sys.argv])),
              "python_argv": list(sys.argv), "future_argv": future_command(out, managed_handle),
              "cwd": str(Path.cwd()), "python_executable": sys.executable,
              "preparation_sha256": preparation_sha256,
              "model_requested": MODEL, "reasoning_requested": "high", "timeout_seconds": TIMEOUT, "jobs": JOBS,
              "stdout": "runner-stdout.txt", "stderr": "runner-stderr.txt",
              "retry_policy": "none; this claim remains permanent after failure or interruption"}
    try:
        exclusive_json(out / "launch.json", launch)
    except FileExistsError as exc:
        raise review.ReviewError("acceptance launch already claimed; second execution/resume is forbidden") from exc
    runtime, validated, outcome, error = None, None, None, None
    start = time.monotonic()
    with (out / "runner-stdout.txt").open("x", encoding="utf-8") as stdout, (out / "runner-stderr.txt").open("x", encoding="utf-8") as stderr:
        with redirect_stdout(_Tee(stdout, sys.stdout)), redirect_stderr(_Tee(stderr, sys.stderr)):
            print(json.dumps({"event": "acceptance_started", **launch}), flush=True)
            try:
                validated = preparation_api.validate_preparation(out)
                _require_frozen_execution(out, validated, managed_handle)
                if rb.digest(preparation_path) != launch["preparation_sha256"]:
                    raise review.ReviewError("preparation changed after launch claim")
                runtime = observe_runtime(out)
                if not runtime["valid"]:
                    raise review.ReviewError(runtime["error"])
                outcome = _fresh_and_historical(out, validated, runtime, launch)
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                print(error, file=sys.stderr, flush=True)
                outcome = combined_outcome(None, None, runtime, validated["preparation"].get("gates", {}) if validated else {},
                                           {"preparation": file_binding(out, preparation_path)} if preparation_path.is_file() else {})
                outcome["error"] = error
            # KeyboardInterrupt, SIGTERM/SIGKILL, and other abrupt exits deliberately
            # have no invented terminal record. External observation closes them.
            print(json.dumps({"event": "acceptance_terminal", "accepted": outcome["accepted"], "error": error}), flush=True)
    stdout_path, stderr_path = out / "runner-stdout.txt", out / "runner-stderr.txt"
    outcome["evidence"].update(runner_stdout=file_binding(out, stdout_path), runner_stderr=file_binding(out, stderr_path))
    code = 0 if outcome["accepted"] else 1
    terminal = {"kind": "observed-runner-terminal-execution", "finished_at": now(), "pid": launch["pid"],
                "managed_handle": managed_handle, "launch": file_binding(out, out / "launch.json"),
                "preparation_sha256": launch["preparation_sha256"], "elapsed_seconds": round(time.monotonic() - start, 3),
                "exit_code": code, "status": "completed" if error is None else "failed", "error": error,
                "combined_outcome_path": "combined-outcome.json",
                "combined_outcome_payload_sha256": rb.manifest_identity(outcome),
                "stdout": file_binding(out, stdout_path), "stderr": file_binding(out, stderr_path),
                "runtime": file_binding(out, out / "runtime-version.json") if runtime else None}
    exclusive_json(out / "execution.json", terminal)
    # Store the terminal record before publishing any passing combined outcome.
    # Its payload hash omits only this terminal backlink, avoiding a hash cycle.
    outcome["evidence"]["execution"] = file_binding(out, out / "execution.json")
    exclusive_json(out / "combined-outcome.json", outcome)
    stdout_path.chmod(0o444)
    stderr_path.chmod(0o444)
    return code


def observe_interruption(out, observation_path):
    """Retain externally observed stop, never manufacture runner finalization.

    JSON has exactly: kind='externally-observed-acceptance-interruption',
    observed_at (ISO timestamp), observer (nonempty), launch_sha256,
    preparation_sha256, managed_handle, pid, process_identity (from launch),
    runner={suspended_observed:true, suspension_signal:'SIGSTOP',
            terminal_observed:true, termination_signal:'SIGTERM'|'SIGKILL',
            returncode:<negative signal number>},
    worker_inventory_complete:true,
    worker_groups=[{pgid:<positive int>, signals:['SIGTERM'|'SIGKILL',...],
                    terminal_observed:true},...],
    evidence=[{path:<absolute external file>, sha256:<observed hash>},...].

    Evidence must contain retained supervisor observations of the inventory,
    signals and terminal outcomes; this command validates bindings, not whether
    an external observer is truthful. Empty worker inventory requires explicit
    complete-inventory evidence, not inference from an absent runner record.
    """
    out = rs._root(Path(out), "interrupted acceptance")
    if (out / "execution.json").exists() or (out / "combined-outcome.json").exists():
        raise review.ReviewError("terminal/combined record already retained; no external rewrite allowed")
    observation_path = Path(observation_path).absolute()
    value, launch = review.load_json(observation_path), review.load_json(out / "launch.json")
    fields = {"kind", "observed_at", "observer", "launch_sha256", "preparation_sha256", "managed_handle", "pid",
              "process_identity", "runner", "worker_inventory_complete", "worker_groups", "evidence"}
    if not isinstance(value, dict) or set(value) != fields or value["kind"] != "externally-observed-acceptance-interruption":
        raise review.ReviewError("explicit external observed-interruption schema required")
    if value["launch_sha256"] != rb.digest(out / "launch.json") or any(value[key] != launch[key] for key in ("preparation_sha256", "managed_handle", "pid", "process_identity")):
        raise review.ReviewError("external interruption evidence differs from launch identity")
    try:
        timestamp = datetime.fromisoformat(value["observed_at"])
        if timestamp.tzinfo is None or timestamp < datetime.fromisoformat(launch["started_at"]):
            raise ValueError("timestamp must follow launch and include timezone")
    except (ValueError, TypeError) as exc:
        raise review.ReviewError("invalid external observation timestamp") from exc
    if not isinstance(value["observer"], str) or not value["observer"].strip():
        raise review.ReviewError("external observer identity required")
    runner = value["runner"]
    if (not isinstance(runner, dict) or set(runner) != {"suspended_observed", "suspension_signal", "terminal_observed", "termination_signal", "returncode"}
            or runner["suspended_observed"] is not True or runner["suspension_signal"] != "SIGSTOP"
            or runner["terminal_observed"] is not True or runner["termination_signal"] not in {"SIGTERM", "SIGKILL"}
            or type(runner["returncode"]) is not int or runner["returncode"] != -getattr(signal, runner["termination_signal"])):
        raise review.ReviewError("observed runner suspension and signal-terminal outcome required")
    current = process_identity(value["pid"])
    if (current["start_ticks"] is not None and current["start_ticks"] == launch["process_identity"]["start_ticks"]
            and current["boot_id"] == launch["process_identity"]["boot_id"] and current["state"] != "Z"):
        raise review.ReviewError("claimed interrupted runner is still live")
    groups = value["worker_groups"]
    if value["worker_inventory_complete"] is not True or not isinstance(groups, list):
        raise review.ReviewError("complete externally observed worker inventory required")
    seen = set()
    for group in groups:
        if (not isinstance(group, dict) or set(group) != {"pgid", "signals", "terminal_observed"}
                or type(group["pgid"]) is not int or group["pgid"] <= 0 or group["pgid"] in seen
                or group["terminal_observed"] is not True or not isinstance(group["signals"], list)
                or not group["signals"] or any(item not in {"SIGTERM", "SIGKILL"} for item in group["signals"])):
            raise review.ReviewError("invalid observed worker process-group termination")
        seen.add(group["pgid"])
    if not isinstance(value["evidence"], list) or not value["evidence"]:
        raise review.ReviewError("retained external supervisor evidence required")
    for binding in value["evidence"]:
        if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
            raise review.ReviewError("invalid supervisor evidence binding")
        path = Path(binding["path"])
        if not path.is_absolute() or path.is_symlink() or rb.digest(path) != binding["sha256"]:
            raise review.ReviewError("supervisor evidence binding mismatch")
    exclusive_json(out / "observed-interruption.json", {**value, "observation_source": {"path": str(observation_path), "sha256": rb.digest(observation_path)}})
    outcome = combined_outcome(None, None, None, {}, {"launch": file_binding(out, out / "launch.json"),
                               "observed_interruption": file_binding(out, out / "observed-interruption.json")}, terminal_complete=False)
    outcome["reason"] = "externally observed terminal interruption; no synthesized execution.json and no resume"
    exclusive_json(out / "combined-outcome.json", outcome)
    return outcome


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="offline only; no OMP/provider invocation")
    for flag in ("results", "boundary-results", "source-review", "candidate-root", "out"):
        prepare.add_argument("--" + flag, type=Path, required=True)
    prepare.add_argument("--evals", type=Path, default=EVALS)
    prepare.add_argument("--capture-preparation", type=Path,
                         help="frozen preparation for a separately authorized fresh capture wave")
    prepare.add_argument("--package-smoke-proof", type=Path,
                         help="isolated package proof bound to the fresh capture runtime sources")
    validate = commands.add_parser("validate", help="offline binding/coverage check only")
    validate.add_argument("--out", type=Path, required=True)
    run = commands.add_parser("execute", help="separately authorized paid execution; single permanent claim")
    run.add_argument("--out", type=Path, required=True)
    run.add_argument("--managed-handle", required=True)
    interrupted = commands.add_parser("record-interruption", help="retain explicit external stop evidence; never invoke OMP")
    interrupted.add_argument("--out", type=Path, required=True)
    interrupted.add_argument("--observation", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            value = preparation_api.prepare(
                args.results, args.boundary_results, args.source_review, args.candidate_root,
                args.out, evals=args.evals, capture_preparation=args.capture_preparation,
                package_smoke_proof=args.package_smoke_proof)
            print(json.dumps({"prepared": str(args.out.absolute()), "expected_packets": value["expected_packets"],
                              "expected_capture_slots": value["expected_capture_slots"], "paid_execution_started": False}), flush=True)
            return 0
        if args.command == "validate":
            value = preparation_api.validate_preparation(args.out)
            print(json.dumps({"valid": True, "expected_packets": len(value["packets"]), "gates": value["preparation"]["gates"],
                              "preparation_sha256": rb.digest(args.out / "preparation.json"), "paid_execution_started": False}), flush=True)
            return 0
        if args.command == "record-interruption":
            observe_interruption(args.out, args.observation)
            return 1
        return execute(args.out, args.managed_handle)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"acceptance error: {exc}", file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
