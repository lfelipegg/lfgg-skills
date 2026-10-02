#!/usr/bin/env python3
"""Capture the fixed Phase 1 baseline or a paired baseline/worktree cohort."""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import tarfile
import tempfile
import time
from datetime import datetime, timezone

BASELINE = "5fcc3d0eded83c6a9aaf472a1dc8d5ce24011d9d"
MODEL = "openai-codex/gpt-6-astra"
ROOT = Path(__file__).resolve().parent.parent
EVALS = ROOT / "evals"
TOOLS = "read,grep,glob,bash,write"
PROVENANCE_FILES = [
    "generator-system.txt",
    "omp-config.json",
    "capture.ts",
    "run_baseline.py",
    "cases.jsonl",
    "rubric.md",
    "evaluate.py",
]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def source_manifest(snapshot):
    return {
        path.relative_to(snapshot).as_posix(): digest(path)
        for path in sorted(snapshot.rglob("*"))
        if path.is_file()
    }


def manifest_identity(files):
    encoded = json.dumps(files, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def freeze_snapshot(snapshot):
    for path in snapshot.rglob("*"):
        if path.is_file():
            path.chmod(0o444)


def extract_baseline(snapshot, scratch, baseline_repo):
    snapshot.mkdir()
    archive = scratch / "baseline.tar"
    with archive.open("wb") as stream:
        subprocess.run(
            ["git", "archive", BASELINE, "SKILL.md", "references", "scripts", "docs/danbooru_tags"],
            cwd=baseline_repo,
            stdout=stream,
            check=True,
        )
    with tarfile.open(archive) as bundle:
        bundle.extractall(snapshot, filter="data")
    archive.unlink()
    freeze_snapshot(snapshot)
    return source_manifest(snapshot)


def worktree_source_files():
    files = [ROOT / "SKILL.md"]
    for directory in (ROOT / "references", ROOT / "scripts"):
        files.extend(
            path
            for path in directory.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".pyo"}
        )
    files.extend(path for path in (ROOT / "docs" / "danbooru_tags").glob("*.csv") if path.is_file())
    return sorted(set(files))


def retain_worktree_snapshot(snapshot):
    snapshot.mkdir(parents=True)
    for source in worktree_source_files():
        relative = source.relative_to(ROOT)
        target = snapshot / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    files = source_manifest(snapshot)
    identity = manifest_identity(files)
    freeze_snapshot(snapshot)
    return files, identity


def capture(case, repetition, snapshot, destination, timeout, scratch, revision, side=None):
    evidence = destination / case["id"] / f"attempt-{repetition}"
    evidence.mkdir(parents=True)
    workspace = scratch / (side or "baseline") / case["id"] / f"attempt-{repetition}"
    workspace.mkdir(parents=True)
    # Each attempt has independent script/cache paths. Large immutable CSVs use
    # hardlinks; the selected skill is never an authorized write destination.
    shutil.copytree(snapshot, workspace / "selected-skill", copy_function=os.link)
    for fixture in case["fixtures"]:
        source = EVALS / "fixtures" / fixture
        target = workspace / "fixtures" / fixture
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    prompt = "Use the explicitly selected Scenario Maker skill in ./selected-skill/SKILL.md.\n\n" + case["request"]
    if case["fixtures"]:
        prompt += "\n\nSupplied local fixtures: " + ", ".join("fixtures/" + name for name in case["fixtures"])
    (evidence / "request.txt").write_text(prompt, encoding="utf-8")
    command = [
        "omp",
        "--cwd",
        str(workspace),
        "--print",
        "--mode",
        "json",
        "--model",
        MODEL,
        "--thinking",
        "high",
        "--no-session",
        "--no-title",
        "--no-prewalk",
        "--no-skills",
        "--no-rules",
        "--no-extensions",
        "--no-lsp",
        "--no-pty",
        "--tools",
        TOOLS,
        "--approval-mode",
        "yolo",
        "--config",
        str(EVALS / "omp-config.json"),
        "--system-prompt",
        str(EVALS / "generator-system.txt"),
        "--extension",
        str(EVALS / "capture.ts"),
        "--max-time",
        f"{timeout}s",
        prompt,
    ]
    environment = os.environ.copy()
    environment.update(
        EVAL_CONTEXT_FILE=str(evidence / "context.jsonl"),
        EVAL_SYSTEM_FILE=str(EVALS / "generator-system.txt"),
        PYTHONDONTWRITEBYTECODE="1",
        TZ="UTC",
        LC_ALL="C.UTF-8",
    )
    started = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()
    status, exit_code, error = "error", None, None
    with (evidence / "trace.jsonl").open("wb") as stdout, (evidence / "stderr.txt").open("wb") as stderr:
        try:
            process = subprocess.Popen(
                command,
                cwd=workspace,
                env=environment,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
            )
            try:
                exit_code = process.wait(timeout=timeout + 30)
                status = "completed" if exit_code == 0 else "error"
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                exit_code, status, error = process.returncode, "timeout", "outer capture deadline"
        except OSError as exc:
            error = str(exc)
    events, malformed = [], []
    for index, line in enumerate(
        (evidence / "trace.jsonl").read_text(encoding="utf-8", errors="replace").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            malformed.append(index)
    messages = [event.get("message", {}) for event in events if event.get("type") == "message_end"]
    assistant = [message for message in messages if message.get("role") == "assistant"]
    text_messages = [
        message
        for message in assistant
        if any(content.get("type") == "text" for content in message.get("content", []))
        and not any(content.get("type") == "toolCall" for content in message.get("content", []))
    ]
    final = [message for message in text_messages if message.get("stopReason") == "stop"]
    output_path, partial_path = None, None
    if final:
        output_path = "output.txt"
        (evidence / output_path).write_text(
            "".join(content["text"] for content in final[-1]["content"] if content.get("type") == "text"),
            encoding="utf-8",
        )
    elif text_messages:
        partial_path = "partial-output.txt"
        (evidence / partial_path).write_text(
            "".join(
                content["text"]
                for content in text_messages[-1]["content"]
                if content.get("type") == "text"
            ),
            encoding="utf-8",
        )
    model_errors = [
        message.get("errorMessage", message.get("stopReason"))
        for message in assistant
        if message.get("stopReason") in ("error", "aborted")
    ]
    if model_errors and status == "completed":
        status = "error"
    started_calls = {
        event.get("toolCallId") for event in events if event.get("type") == "tool_execution_start"
    }
    ended_calls = {
        event.get("toolCallId") for event in events if event.get("type") == "tool_execution_end"
    }
    trace_complete = bool(
        not malformed
        and started_calls == ended_calls
        and any(event.get("type") == "agent_end" and event.get("isTerminal") is True for event in events)
    )
    artifacts = []
    fixture_set = {"fixtures/" + name for name in case["fixtures"]}
    for path in sorted(workspace.rglob("*")):
        relative = path.relative_to(workspace)
        if (
            not path.is_file()
            or path.is_symlink()
            or relative.parts[0] in ("selected-skill", ".omp", ".git")
            or relative.as_posix() in fixture_set
        ):
            continue
        stored = Path("artifacts") / relative
        target = evidence / stored
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        artifacts.append(
            {
                "path": relative.as_posix(),
                "stored_path": stored.as_posix(),
                "sha256": digest(target),
                "bytes": target.stat().st_size,
            }
        )
    contexts = []
    context_file = evidence / "context.jsonl"
    if context_file.exists():
        for line in context_file.read_text(encoding="utf-8").splitlines():
            contexts.append(json.loads(line))
    actual = [context for context in contexts if context.get("type") == "eval_context"]
    record = {
        "case_id": case["id"],
        "attempt": repetition,
        "revision": revision,
        "started_at": started,
        "elapsed_seconds": round(time.monotonic() - start, 3),
        "command": command,
        "cwd": str(workspace),
        "execution": {
            "status": status,
            "exit_code": exit_code,
            "error": error,
            "model_errors": model_errors,
            "malformed_trace_lines": malformed,
        },
        "raw": {
            "output": output_path,
            "partial_output": partial_path,
            "trace": "trace.jsonl",
            "stderr": "stderr.txt",
            "context": "context.jsonl" if context_file.exists() else None,
        },
        "trace_complete": trace_complete,
        "artifacts": artifacts,
        "observed_context": actual,
        "raw_checksums": {path.name: digest(path) for path in evidence.iterdir() if path.is_file()},
    }
    if side is not None:
        record["comparison_side"] = side
    save_json(evidence / "attempt.json", record)
    progress = {
        "case": case["id"],
        "attempt": repetition,
        "status": status,
        "output": output_path is not None,
        "trace_complete": trace_complete,
    }
    if side is not None:
        progress["side"] = side
    print(json.dumps(progress), flush=True)
    return record


def capture_manifest(kind, args, version, cases, provenance_files, candidate_revision=None):
    return {
        "kind": kind,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "baseline_revision": BASELINE,
        "candidate_revision": candidate_revision,
        "omp_version": version,
        "model_requested": MODEL,
        "reasoning_requested": "high",
        "resolved_immutable_snapshot": None,
        "unknown_metadata": [
            "immutable provider snapshot",
            "provider seed",
            "system fingerprint",
            "hidden provider instructions",
        ],
        "tools_requested": TOOLS.split(","),
        "permissions": "auto-approved local tools; not an OS sandbox",
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "TZ": "UTC",
            "LC_ALL": "C.UTF-8",
        },
        "timeout_seconds": args.timeout,
        "jobs": args.jobs,
        "scheduling": "case-major submission, repetition ascending; completion order may differ",
        "attempts_per_case": 1 if args.smoke else 3,
        "evaluation_files": {name: digest(EVALS / name) for name in provenance_files},
        "fixtures": {
            name: digest(EVALS / "fixtures" / name)
            for case in cases
            for name in case["fixtures"]
        },
        "redactions": [],
        "trace_boundary": (
            "OMP client JSON events and allowlisted provider request body fields; no headers/credentials"
        ),
    }


def save_summary(destination, records):
    save_json(
        destination / "execution-summary.json",
        {
            "attempts": len(records),
            "completed": sum(record["execution"]["status"] == "completed" for record in records),
            "errors": sum(record["execution"]["status"] == "error" for record in records),
            "timeouts": sum(record["execution"]["status"] == "timeout" for record in records),
            "outputs": sum(record["raw"]["output"] is not None for record in records),
            "trace_complete": sum(record["trace_complete"] for record in records),
            "semantic_review": "not-run",
            "acceptance": "not assessed",
        },
    )


def validate_cases(parser, cases, smoke):
    if not smoke and (len(cases) != 16 or len({case["id"] for case in cases}) != 16):
        parser.error("capture requires exactly sixteen distinct reviewed cases")
    for case in cases:
        if Path(case["id"]).name != case["id"] or case["id"] in (".", ".."):
            parser.error("unsafe case id")
        for fixture in case["fixtures"]:
            path = Path(fixture)
            if not path.parts or path.is_absolute() or ".." in path.parts:
                parser.error("fixtures must be inside evals/fixtures")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="New evidence directory; existing paths are refused")
    parser.add_argument(
        "--baseline-repo",
        type=Path,
        required=True,
        help="Clone of scenario-maker-skill containing the fixed historical baseline commit",
    )
    parser.add_argument(
        "--candidate-worktree",
        action="store_true",
        help="Capture an immutable current-worktree snapshot paired with a fresh fixed-baseline rerun",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="One separate capture exercise (or pair), never acceptance evidence",
    )
    parser.add_argument("--timeout", type=int, default=300, help="OMP deadline per attempt in seconds")
    parser.add_argument("--jobs", type=int, default=3, help="Maximum concurrent fresh OMP sessions")
    args = parser.parse_args()
    if args.timeout < 1 or args.jobs < 1:
        parser.error("timeout and jobs must be positive")
    cases = (
        [
            {
                "id": "capture-smoke",
                "request": (
                    "Read the selected skill and its applicable prompt-type reference. Write one very "
                    "short still-image prompt about a red cube on a gray surface to outputs/smoke.txt. "
                    "Report the saved path."
                ),
                "fixtures": [],
            }
        ]
        if args.smoke
        else [
            json.loads(line)
            for line in (EVALS / "cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    )
    validate_cases(parser, cases, args.smoke)
    destination = args.out.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    version = subprocess.run(
        ["omp", "--help"], text=True, capture_output=True, check=True
    ).stdout.splitlines()[0]

    with tempfile.TemporaryDirectory(prefix="scenario-maker-eval-") as temp:
        scratch = Path(temp)
        baseline_snapshot = scratch / "baseline-snapshot"
        baseline_files = extract_baseline(baseline_snapshot, scratch, args.baseline_repo.resolve())
        repetitions = range(1, 2 if args.smoke else 4)

        if not args.candidate_worktree:
            provenance_files = PROVENANCE_FILES[:4] if args.smoke else PROVENANCE_FILES
            manifest = capture_manifest(
                "capture-smoke" if args.smoke else "original-phase-one-baseline",
                args,
                version,
                cases,
                provenance_files,
            )
            save_json(destination / "manifest.json", manifest)
            save_json(destination / "selected-skill-files.json", baseline_files)
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
                futures = [
                    pool.submit(
                        capture,
                        case,
                        repetition,
                        baseline_snapshot,
                        destination,
                        args.timeout,
                        scratch,
                        BASELINE,
                    )
                    for case in cases
                    for repetition in repetitions
                ]
                records = [future.result() for future in concurrent.futures.as_completed(futures)]
            save_summary(destination, records)
            return

        retained_candidate = destination / "candidate-source-snapshot"
        candidate_files, candidate_hash = retain_worktree_snapshot(retained_candidate)
        candidate_revision = f"worktree-sha256-{candidate_hash}"
        baseline_destination = destination / "baseline"
        candidate_destination = destination / "candidate"
        baseline_destination.mkdir()
        candidate_destination.mkdir()
        save_json(baseline_destination / "selected-skill-files.json", baseline_files)
        save_json(candidate_destination / "selected-skill-files.json", candidate_files)
        baseline_manifest = capture_manifest(
            "paired-smoke-baseline" if args.smoke else "paired-baseline-rerun",
            args,
            version,
            cases,
            PROVENANCE_FILES,
            candidate_revision,
        )
        candidate_manifest = capture_manifest(
            "paired-smoke-candidate" if args.smoke else "paired-candidate-worktree",
            args,
            version,
            cases,
            PROVENANCE_FILES,
            candidate_revision,
        )
        baseline_manifest["selected_skill"] = {
            "kind": "git-revision",
            "identity": BASELINE,
            "files_manifest": "selected-skill-files.json",
        }
        candidate_manifest["selected_skill"] = {
            "kind": "retained-worktree-snapshot",
            "identity": candidate_revision,
            "files_manifest": "selected-skill-files.json",
            "snapshot": "../candidate-source-snapshot",
        }
        save_json(baseline_destination / "manifest.json", baseline_manifest)
        save_json(candidate_destination / "manifest.json", candidate_manifest)
        schedule = [
            {"position": position, "case_id": case["id"], "attempt": repetition, "side": side}
            for position, (case, repetition, side) in enumerate(
                (
                    item
                    for case in cases
                    for repetition in repetitions
                    for item in ((case, repetition, "baseline"), (case, repetition, "candidate"))
                ),
                1,
            )
        ]
        comparison_manifest = capture_manifest(
            "paired-candidate-comparison-smoke" if args.smoke else "paired-candidate-comparison",
            args,
            version,
            cases,
            PROVENANCE_FILES,
            candidate_revision,
        )
        comparison_manifest.update(
            {
                "acceptance_eligible": False if args.smoke else "requires mechanical and human review",
                "candidate_snapshot": {
                    "identity": candidate_revision,
                    "path": "candidate-source-snapshot",
                    "files": candidate_files,
                },
                "baseline_source": {
                    "kind": "git-revision",
                    "identity": BASELINE,
                    "files": baseline_files,
                },
                "controlled_equal": [
                    "cases and requests",
                    "fixtures",
                    "system instructions",
                    "OMP configuration and capture extension",
                    "model and reasoning request",
                    "tools and permissions",
                    "timeout and concurrency limit",
                ],
                "environment_differences": [
                    {
                        "field": "selected skill source",
                        "baseline": f"git revision {BASELINE}",
                        "candidate": candidate_revision,
                        "purpose": "the sole intentional treatment difference",
                    }
                ],
                "schedule": schedule,
                "schedule_policy": (
                    "adjacent baseline/candidate submissions for each case and repetition; "
                    "at most jobs processes in flight; completion order may differ"
                ),
                "retry_policy": "none; every error and timeout is retained in its original slot",
                "side_results": {"baseline": "baseline", "candidate": "candidate"},
            }
        )
        save_json(destination / "manifest.json", comparison_manifest)
        work = [
            (
                case,
                repetition,
                side,
                baseline_snapshot if side == "baseline" else retained_candidate,
                baseline_destination if side == "baseline" else candidate_destination,
                BASELINE if side == "baseline" else candidate_revision,
            )
            for case in cases
            for repetition in repetitions
            for side in ("baseline", "candidate")
        ]
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = [
                pool.submit(
                    capture,
                    case,
                    repetition,
                    snapshot,
                    side_destination,
                    args.timeout,
                    scratch,
                    revision,
                    side,
                )
                for case, repetition, side, snapshot, side_destination, revision in work
            ]
            records = [future.result() for future in concurrent.futures.as_completed(futures)]
        comparison_manifest["completion_order"] = [
            {
                "position": position,
                "case_id": record["case_id"],
                "attempt": record["attempt"],
                "side": record["comparison_side"],
                "status": record["execution"]["status"],
            }
            for position, record in enumerate(records, 1)
        ]
        save_json(destination / "manifest.json", comparison_manifest)
        baseline_records = [record for record in records if record["comparison_side"] == "baseline"]
        candidate_records = [record for record in records if record["comparison_side"] == "candidate"]
        save_summary(baseline_destination, baseline_records)
        save_summary(candidate_destination, candidate_records)
        save_summary(destination, records)


if __name__ == "__main__":
    main()
