#!/usr/bin/env python3
"""Capture the frozen current monolith against eight isolated split packages.

This records execution evidence only, not semantic or migration acceptance.
Every scheduled slot is attempted once; operational failures remain evidence.
"""
import argparse
import concurrent.futures
from datetime import datetime, timezone
import json
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import subprocess
import tempfile
import time

import evaluate
import run_baseline as rb

EVALS = Path(__file__).resolve().parent
CASE_FILES = (
    "cases.jsonl", "phase-three-probes.jsonl", "phase-four-probes.jsonl",
    "h3-probes.jsonl", "h3-guide-probes.jsonl", "wild-probes.jsonl", "unbound-probes.jsonl",
)
SKILLS = (
    "scenario-maker", "scenario-maker-sdxl", "scenario-maker-krea-2",
    "scenario-maker-illustrious", "scenario-maker-noobai", "scenario-maker-pony",
    "scenario-maker-wan", "scenario-maker-minimax-h3",
)
COMMON_RUNTIME_FILES = (
    "SKILL.md", "references/routing.md", "references/output-contracts.md",
    "references/scene-composition.md", "references/constraints-and-revisions.md",
    "references/prompt-types.md", "references/video-prompts.md", "references/characters.md",
    "references/danbooru-tags.md", "references/wildcards.md",
    "scripts/character_generator.py", "scripts/danbooru_lookup.py",
    "scripts/build_danbooru_index.py", "docs/danbooru_tags/danbooru_tags.csv",
    "docs/danbooru_tags/danbooru_tags_cooccurrence.csv",
)
PACKAGE_FILES = ("README.md", "CONTEXT.md", "agents/openai.yaml")
H3_GUIDES = (
    "references/models/minimax_h3/VIDEO_PROMPT_WRITING_GUIDE_base_en.md",
    "references/models/minimax_h3/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md",
)
MODEL_FILES = {
    "scenario-maker-sdxl": ("references/models/sdxl.md",),
    "scenario-maker-krea-2": ("references/models/krea-2.md",),
    "scenario-maker-illustrious": ("references/models/illustrious.md",),
    "scenario-maker-noobai": ("references/models/noobai.md",),
    "scenario-maker-pony": ("references/models/pony-v6.md",),
    "scenario-maker-wan": ("references/models/wan.md",),
    "scenario-maker-minimax-h3": ("references/models/minimax-h3.md",) + H3_GUIDES,
}
MODEL_FILES["scenario-maker"] = (
    "references/model-prompts.md",
    *(name for paths in MODEL_FILES.values() for name in paths),
)
EVALUATION_FILES = CASE_FILES + (
    "split-routes.json", "split-boundaries.jsonl", "rubric.md", "evaluate.py",
    "run_baseline.py", "run_split.py", "omp-config.json", "generator-system.txt", "capture.ts",
)
BOUNDARY_SKILLS = {
    **{"split-invoke-" + skill.removeprefix("scenario-maker-"): skill for skill in SKILLS[1:]},
    "split-wrong-family": "scenario-maker-pony",
    "split-prose-pony": "scenario-maker-pony",
    "split-format-noobai": "scenario-maker-noobai",
    "split-compare": "scenario-maker",
    "split-shared": "scenario-maker",
    "split-explicit-generic": "scenario-maker",
}
PAIRED_BOUNDARIES = {
    "split-prose-pony", "split-format-noobai", "split-compare", "split-shared", "split-explicit-generic",
}


class InputError(ValueError):
    """An invalid or unreadable source, evaluation input, or package."""


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _json(text, location):
    try:
        return json.loads(text, object_pairs_hook=_unique_object)
    except (ValueError, TypeError) as exc:
        raise InputError(f"{location}: {exc}") from exc


def _root(path, label):
    path = Path(path).absolute()
    if path.is_symlink():
        raise InputError(f"{label}: symlinked root is not allowed: {path}")
    try:
        if not path.is_dir():
            raise InputError(f"{label}: directory does not exist: {path}")
        return path.resolve(strict=True)
    except OSError as exc:
        raise InputError(f"{label}: {path}: {exc}") from exc


def _relative(name, label):
    if not isinstance(name, str) or not name or "\\" in name or "\x00" in name:
        raise InputError(f"{label}: unsafe relative path {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute() or path.as_posix() != name or any(part in (".", "..") for part in path.parts):
        raise InputError(f"{label}: unsafe relative path {name!r}")
    if not path.parts or ":" in path.parts[0]:
        raise InputError(f"{label}: unsafe relative path {name!r}")
    return path


def _file(root, name, label):
    relative = _relative(name, label)
    path = root
    try:
        for part in relative.parts:
            path = path / part
            if path.is_symlink():
                raise InputError(f"{label}: symlink is not allowed: {path}")
        path.resolve(strict=True).relative_to(root.resolve(strict=True))
        if not path.is_file():
            raise InputError(f"{label}: not a regular file: {path}")
        # Hashing reads all bytes, including the large optional lookup datasets.
        checksum = rb.digest(path)
    except (OSError, ValueError) as exc:
        if isinstance(exc, InputError):
            raise
        raise InputError(f"{label}: unavailable or escaping file {path}: {exc}") from exc
    return path, checksum


def _text(path):
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise InputError(f"{path}: unreadable UTF-8 input: {exc}") from exc


def _jsonl(path):
    rows = []
    for line, text in enumerate(_text(path).splitlines(), 1):
        if not text.strip():
            continue
        row = _json(text, f"{path}:{line}")
        if not isinstance(row, dict):
            raise InputError(f"{path}:{line}: expected a JSON object")
        rows.append(row)
    if not rows:
        raise InputError(f"{path}: empty case selection")
    return rows


def _case(row, location):
    case_id = row.get("id")
    if not isinstance(case_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", case_id):
        raise InputError(f"{location}: invalid case ID {case_id!r}")
    if not isinstance(row.get("request"), str) or not row["request"].strip():
        raise InputError(f"{location}: request must be a non-empty string")
    if not isinstance(row.get("fixtures"), list):
        raise InputError(f"{location}: fixtures must be a list")
    for name in row["fixtures"]:
        _relative(name, f"{location}.fixtures")
    if len(set(row["fixtures"])) != len(row["fixtures"]):
        raise InputError(f"{location}: duplicate fixture")


def _expectations(row, location):
    values = row.get("expected_behavior")
    if not isinstance(values, list) or not values or any(not isinstance(value, str) or not value.strip() for value in values):
        raise InputError(f"{location}: expected_behavior must be a non-empty list of strings")


def _walk_source(directory):
    if directory.is_symlink():
        raise InputError(f"source symlink is not allowed: {directory}")
    files = []
    # Unlike glob traversal, iterdir propagates an unreadable directory error.
    for path in sorted(directory.iterdir()):
        if path.is_symlink():
            raise InputError(f"source symlink is not allowed: {path}")
        if path.is_dir():
            files.extend(_walk_source(path))
        elif path.is_file():
            files.append(path)
        else:
            raise InputError(f"source is not a regular file or directory: {path}")
    return files


def _source_files(root, *, baseline=False, skill=None):
    required = COMMON_RUNTIME_FILES + (
        tuple(name for name in MODEL_FILES["scenario-maker"] if name != "references/models/wan.md")
        if baseline else MODEL_FILES[skill] + PACKAGE_FILES
    )
    directories = (root,) if baseline else (root / "references", root / "scripts", root / "docs" / "danbooru_tags")
    try:
        enumerated = [path for directory in directories for path in _walk_source(directory)]
        paths = enumerated if baseline else rb.worktree_source_files(root) + [root / name for name in PACKAGE_FILES]
        names = {path.relative_to(root).as_posix() for path in paths} | set(required)
        files = {name: _file(root, name, "source manifest")[1] for name in sorted(names)}
    except OSError as exc:
        raise InputError(f"{root}: source manifest unavailable: {exc}") from exc
    return files


def _schedule(cases, suite):
    schedule = []
    for case in cases:
        for attempt in (1, 2, 3):
            sides = ("baseline", "candidate") if suite == "corpus" or case["paired"] else ("candidate",)
            for side in sides:
                schedule.append({"position": len(schedule) + 1, "case_id": case["id"], "attempt": attempt, "side": side})
    return schedule


def preflight(baseline, candidate_root, suite, evals=EVALS):
    """Validate every source/input without creating output or invoking capture."""
    if suite not in {"corpus", "boundary"}:
        raise InputError(f"unknown suite {suite!r}")
    baseline = _root(baseline, "baseline")
    candidate_root = _root(candidate_root, "candidate root")
    evals = _root(evals, "evaluation inputs")
    evaluation_files = {name: _file(evals, name, "evaluation input")[1] for name in EVALUATION_FILES}
    config = _json(_text(evals / "omp-config.json"), evals / "omp-config.json")
    if not isinstance(config, dict) or not isinstance(config.get("retry"), dict):
        raise InputError("omp-config.json: a configuration object with explicit retry settings is required")
    if any(config["retry"].get(name) is not False for name in ("enabled", "modelFallback", "usageAwareFallback")):
        raise InputError("omp-config.json: retries and model fallbacks must be disabled")

    corpus, source_ids = [], set()
    for name in CASE_FILES:
        rows = _jsonl(evals / name)
        if name == "cases.jsonl":
            try:
                evaluate.load_cases(evals / name)
            except ValueError as exc:
                raise InputError(str(exc)) from exc
            if {row.get("id") for row in rows} != {f"case-{number:02}" for number in range(1, 17)}:
                raise InputError("cases.jsonl: the sixteen formal case IDs are required")
        for row in rows:
            _case(row, name)
            if name != "cases.jsonl":
                _expectations(row, name)
            if row["id"] in source_ids:
                raise InputError(f"duplicate source case ID {row['id']!r}")
            source_ids.add(row["id"])
            corpus.append({**row, "case_source": name})
    if len(corpus) != 124:
        raise InputError(f"corpus requires all 124 distinct source IDs, found {len(corpus)}")
    routes = _json(_text(evals / "split-routes.json"), evals / "split-routes.json")
    if not isinstance(routes, dict) or set(routes) != source_ids:
        missing = sorted(source_ids - set(routes)) if isinstance(routes, dict) else sorted(source_ids)
        extra = sorted(set(routes) - source_ids) if isinstance(routes, dict) else []
        raise InputError(f"split-routes.json: exact ownership of all 124 IDs required; missing={missing}, unknown={extra}")
    for case_id, skill in routes.items():
        if not isinstance(skill, str) or skill not in SKILLS:
            raise InputError(f"split-routes.json: unknown skill for {case_id}: {skill!r}")
    corpus = [{**row, "selected_skill": routes[row["id"]]} for row in corpus]

    boundaries, boundary_ids = [], set()
    fields = {"id", "skill", "request", "fixtures", "expected_behavior", "paired"}
    for row in _jsonl(evals / "split-boundaries.jsonl"):
        if set(row) != fields:
            raise InputError(f"split-boundaries.jsonl: fields must be exactly {sorted(fields)}")
        _case(row, "split-boundaries.jsonl")
        _expectations(row, "split-boundaries.jsonl")
        case_id = row["id"]
        if case_id in boundary_ids or case_id not in BOUNDARY_SKILLS:
            raise InputError(f"split-boundaries.jsonl: duplicate or unknown ID {case_id!r}")
        if row["skill"] != BOUNDARY_SKILLS[case_id]:
            raise InputError(f"split-boundaries.jsonl: wrong selected skill for {case_id}")
        if type(row["paired"]) is not bool or row["paired"] != (case_id in PAIRED_BOUNDARIES):
            raise InputError(f"split-boundaries.jsonl: invalid paired field for {case_id}")
        if row["fixtures"]:
            raise InputError(f"split-boundaries.jsonl: {case_id} requires fixtures=[]")
        boundary_ids.add(case_id)
        boundaries.append({**row, "case_source": "split-boundaries.jsonl", "selected_skill": row["skill"]})
    if boundary_ids != set(BOUNDARY_SKILLS):
        raise InputError(f"split-boundaries.jsonl: all thirteen boundary IDs required; missing={sorted(set(BOUNDARY_SKILLS) - boundary_ids)}")

    fixtures = {name for row in corpus + boundaries for name in row["fixtures"]}
    fixture_files = {name: _file(evals, "fixtures/" + name, "fixture")[1] for name in sorted(fixtures)}
    baseline_files = _source_files(baseline, baseline=True)
    candidate_roots = {skill: _root(candidate_root / skill, f"selected package {skill}") for skill in SKILLS}
    candidate_files = {skill: _source_files(root, skill=skill) for skill, root in candidate_roots.items()}
    cases = corpus if suite == "corpus" else boundaries
    if not cases:
        raise InputError("empty case selection")
    schedule = _schedule(cases, suite)
    expected = 744 if suite == "corpus" else 54
    if len(schedule) != expected:
        raise InputError(f"{suite}: requires {expected} scheduled slots, found {len(schedule)}")
    return {
        "baseline": baseline, "candidate_root": candidate_root, "candidate_roots": candidate_roots,
        "evals": evals, "cases": cases, "routes": routes, "corpus": corpus, "boundaries": boundaries,
        "baseline_files": baseline_files, "candidate_files": candidate_files,
        "evaluation_files": evaluation_files, "fixture_files": fixture_files, "schedule": schedule,
    }


def _retain_files(root, destination, files):
    destination.mkdir(parents=True, exist_ok=False)
    for name, checksum in files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, target)
        if rb.digest(target) != checksum:
            raise InputError(f"source changed after preflight: {root / name}")
    rb.freeze_snapshot(destination)


def _retain_sources(checked, out):
    _retain_files(checked["baseline"], out / "snapshots/baseline", checked["baseline_files"])
    for skill in SKILLS:
        snapshot = out / "snapshots/candidate" / skill
        rb.retain_worktree_snapshot(snapshot, checked["candidate_roots"][skill])
        for name in PACKAGE_FILES:
            target = snapshot / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(checked["candidate_roots"][skill] / name, target)
        if rb.source_manifest(snapshot) != checked["candidate_files"][skill]:
            raise InputError(f"source changed after preflight: {checked['candidate_roots'][skill]}")
        rb.freeze_snapshot(snapshot)
    inputs = {**checked["evaluation_files"], **{"fixtures/" + name: checksum for name, checksum in checked["fixture_files"].items()}}
    _retain_files(checked["evals"], out / "evaluation-inputs", inputs)


def _model_metadata(record, evidence):
    contexts, errors = [], []
    path = evidence / "context.jsonl"
    if path.is_file():
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if not line.strip():
                continue
            try:
                context = json.loads(line)
                if isinstance(context, dict):
                    contexts.append(context)
                else:
                    errors.append(f"context line {number}: not an object")
            except ValueError as exc:
                errors.append(f"context line {number}: {exc}")
    resolved, reasoning, requests = [], [], []
    for context in contexts:
        if context.get("type") == "eval_context":
            model = context.get("model")
            if isinstance(model, dict):
                model = {key: model.get(key) for key in ("provider", "id", "name")}
                if model not in resolved:
                    resolved.append(model)
            thinking = context.get("thinking")
            if thinking is not None and thinking not in reasoning:
                reasoning.append(thinking)
        elif context.get("type") == "provider_request":
            observed = context.get("observed")
            if isinstance(observed, dict):
                requests.append({key: observed[key] for key in ("model", "reasoning", "seed", "service_tier", "temperature", "top_p") if key in observed})
    unknown = ["immutable provider snapshot", "system fingerprint", "hidden provider instructions"]
    if not resolved:
        unknown.append("resolved model")
    for key in ("provider", "id", "name"):
        if any(model[key] is None for model in resolved):
            unknown.append(f"resolved model {key}")
    if not reasoning:
        unknown.append("resolved reasoning")
    seeds = [request["seed"] for request in requests if "seed" in request]
    if not seeds:
        unknown.append("provider seed")
    if not requests:
        unknown.append("provider request metadata")
    return {
        "model_requested": rb.MODEL, "reasoning_requested": "high",
        "models_resolved": resolved, "reasoning_resolved": reasoning,
        "provider_requests": requests, "provider_seeds": seeds or None,
        "resolved_immutable_snapshot": None, "system_fingerprint": None,
        "hidden_provider_instructions": None, "unknown_metadata": unknown, "metadata_errors": errors,
    }


def _failed_capture(case, slot, evidence, revision, started, elapsed, error):
    record = {
        "case_id": case["id"], "attempt": slot["attempt"], "revision": revision,
        "comparison_side": slot["side"], "started_at": started, "elapsed_seconds": round(elapsed, 3) if elapsed is not None else None,
        "command": None, "cwd": None,
        "execution": {"status": "error", "exit_code": None, "error": error, "model_errors": [], "malformed_trace_lines": []},
        "raw": {}, "trace_complete": False, "artifacts": [], "observed_context": [], "raw_checksums": {},
    }
    previous = evidence / "attempt.json"
    if previous.is_file():
        try:
            value = json.loads(previous.read_text(encoding="utf-8"))
            if isinstance(value, dict):
                record.update(value)
                record["execution"] = {**record.get("execution", {}), "status": "error", "error": error}
        except (OSError, ValueError):
            pass
    for field, name in (("output", "output.txt"), ("partial_output", "partial-output.txt"), ("trace", "trace.jsonl"), ("stderr", "stderr.txt"), ("context", "context.jsonl")):
        record["raw"][field] = name if field in {"trace", "stderr"} or (evidence / name).is_file() else None
    record["artifacts"] = []
    record["evidence_errors"] = []
    try:
        for path in sorted((evidence / "artifacts").rglob("*")):
            if path.is_file() and not path.is_symlink():
                try:
                    record["artifacts"].append({"path": path.relative_to(evidence / "artifacts").as_posix(), "stored_path": path.relative_to(evidence).as_posix(), "sha256": rb.digest(path), "bytes": path.stat().st_size})
                except OSError as exc:
                    record["evidence_errors"].append(f"{path}: {exc}")
    except OSError as exc:
        record["evidence_errors"].append(f"artifact enumeration: {exc}")
    return record


def _retain_attempt(record, case, slot, checked, evidence, out):
    selected = "scenario-maker" if slot["side"] == "baseline" else case["selected_skill"]
    files = checked["baseline_files"] if slot["side"] == "baseline" else checked["candidate_files"][selected]
    record.update(selected_skill=selected, selected_skill_sha256=rb.manifest_identity(files), case_source=case["case_source"])
    record["model_requested"], record["reasoning_requested"] = rb.MODEL, "high"
    record.setdefault("evidence_errors", [])
    record["attempt_manifest"] = (evidence / "attempt.json").relative_to(out).as_posix()
    try:
        evidence.mkdir(parents=True, exist_ok=True)
        record["model_metadata"] = _model_metadata(record, evidence)
    except Exception as exc:
        record["model_metadata"] = {
            "model_requested": rb.MODEL, "reasoning_requested": "high",
            "models_resolved": [], "reasoning_resolved": [], "provider_requests": [],
            "provider_seeds": None, "resolved_immutable_snapshot": None,
            "system_fingerprint": None, "hidden_provider_instructions": None,
            "unknown_metadata": ["resolved/provider metadata unavailable after evidence failure"],
            "metadata_errors": [f"{type(exc).__name__}: {exc}"],
        }
        record["evidence_errors"].append(f"{type(exc).__name__}: {exc}")
    record["raw_checksums"] = {}
    try:
        for path in sorted(evidence.iterdir()):
            if path.is_file() and path.name != "attempt.json":
                try:
                    record["raw_checksums"][path.name] = rb.digest(path)
                except OSError as exc:
                    record["evidence_errors"].append(f"{path}: {exc}")
    except OSError as exc:
        record["evidence_errors"].append(f"raw evidence enumeration: {exc}")
    if record["evidence_errors"]:
        record["execution"] = {**record["execution"], "status": "error", "error": "failed to retain complete attempt evidence"}
    try:
        rb.save_json(evidence / "attempt.json", record)
        # Metadata is added first. Retained capture raw files are never rewritten.
        rb.freeze_snapshot(evidence)
        record["attempt_manifest_sha256"] = rb.digest(evidence / "attempt.json")
    except Exception as exc:
        record["evidence_errors"].append(f"{type(exc).__name__}: {exc}")
        record["execution"] = {**record["execution"], "status": "error", "error": "failed to retain complete attempt evidence"}
    return record


def _capture_slot(case, slot, checked, out, scratch, timeout, baseline_revision, candidate_revision):
    side, attempt = slot["side"], slot["attempt"]
    group = "boundary" if case["case_source"] == "split-boundaries.jsonl" else "formal" if case["case_source"] == "cases.jsonl" else "probes"
    destination = out / group / side
    evidence = destination / case["id"] / f"attempt-{attempt}"
    selected = "scenario-maker" if side == "baseline" else case["selected_skill"]
    revision = baseline_revision if side == "baseline" else candidate_revision
    snapshot = out / "snapshots/baseline" if side == "baseline" else out / "snapshots/candidate" / selected
    started, start = datetime.now(timezone.utc).isoformat(), time.monotonic()
    try:
        record = rb.capture(case, attempt, snapshot, destination, timeout, scratch, revision, side)
    except Exception as exc:
        record = _failed_capture(case, slot, evidence, revision, started, time.monotonic() - start, f"{type(exc).__name__}: {exc}")
    return _retain_attempt(record, case, slot, checked, evidence, out)


def _successful(record):
    return record["execution"]["status"] == "completed" and bool(record["raw"]["output"]) and record["trace_complete"] and not record.get("evidence_errors")


def _version():
    try:
        process = subprocess.run(["omp", "--help"], text=True, capture_output=True, timeout=30, check=True)
        return (process.stdout.splitlines()[0] if process.stdout.splitlines() else None), None
    except (OSError, subprocess.SubprocessError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--suite", choices=("corpus", "boundary"), required=True)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--jobs", type=int, default=3)
    args = parser.parse_args(argv)
    if args.timeout <= 0 or args.jobs <= 0:
        parser.error("--timeout and --jobs must be positive")
    if args.out.exists() or args.out.is_symlink():
        parser.error(f"--out must not exist: {args.out}")
    try:
        checked = preflight(args.baseline, args.candidate_root, args.suite, evals=EVALS)
    except (InputError, OSError) as exc:
        parser.error(str(exc))
    out = args.out.absolute()
    out.mkdir(parents=True, exist_ok=False)
    try:
        _retain_sources(checked, out)
    except (InputError, OSError) as exc:
        rb.save_json(out / "preparation-error.json", {"error": str(exc), "paid_captures_started": False})
        parser.error(str(exc))
    version, version_error = _version()
    baseline_revision = rb.manifest_identity(checked["baseline_files"])
    candidate_revision = "split-sha256-" + rb.manifest_identity(checked["candidate_files"])
    manifest = {
        "kind": "current-monolith-versus-model-split", "suite": args.suite,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_requested": rb.MODEL, "reasoning_requested": "high",
        "baseline_revision": baseline_revision, "candidate_revision": candidate_revision,
        "baseline_snapshot": "snapshots/baseline",
        "candidate_snapshots": {skill: "snapshots/candidate/" + skill for skill in SKILLS},
        "source_manifests": {"baseline": checked["baseline_files"], "candidate": checked["candidate_files"]},
        "cases": checked["cases"], "schedule": checked["schedule"],
        "evaluation_inputs": "evaluation-inputs", "evaluation_files": checked["evaluation_files"],
        "fixtures": checked["fixture_files"], "route_ownership": checked["routes"],
        "baseline_supplied": str(checked["baseline"]), "candidate_root_supplied": str(checked["candidate_root"]),
        "attempts_per_case": 3, "expected_attempts": len(checked["schedule"]),
        "timeout_seconds": args.timeout, "jobs": args.jobs,
        "omp_version": version, "omp_version_error": version_error,
        "tools_requested": rb.TOOLS.split(","), "permissions": "auto-approved local tools; not an OS sandbox",
        "environment": {"platform": platform.platform(), "python": platform.python_version(), "TZ": "UTC", "LC_ALL": "C.UTF-8"},
        "schedule_policy": "case-major, repetition ascending, adjacent baseline/candidate submissions; completion order may differ",
        "retry_policy": "none; no resume, replacements, or best-of selection",
        "controlled_equal": ["requests and fixtures", "system instructions", "OMP config and capture extension", "model and reasoning request", "tools and permissions", "timeout and concurrency limit"],
        "trace_boundary": "OMP client JSON events and allowlisted provider request body fields; no headers/credentials",
        "resolved_immutable_snapshot": None,
        "unknown_metadata": ["immutable provider snapshot", "provider seed unless observed", "system fingerprint", "hidden provider instructions"],
        "redactions": [], "acceptance": "not assessed", "semantic_review": "not-run",
    }
    rb.save_json(out / "manifest.json", manifest)
    cases = {case["id"]: case for case in checked["cases"]}
    records = []
    original_evals = rb.EVALS
    try:
        # Unchanged capture() uses these exact frozen config, system, extension, and fixtures.
        rb.EVALS = out / "evaluation-inputs"
        with tempfile.TemporaryDirectory(prefix="scenario-maker-split-") as temporary:
            scratch = Path(temporary)
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
                futures = {
                    pool.submit(_capture_slot, cases[slot["case_id"]], slot, checked, out, scratch, args.timeout, baseline_revision, candidate_revision): slot
                    for slot in checked["schedule"]
                }
                for future in concurrent.futures.as_completed(futures):
                    slot = futures[future]
                    try:
                        record = future.result()
                    except Exception as exc:
                        # Even a runner failure remains an explicit slot, never a skipped row.
                        case = cases[slot["case_id"]]
                        group = "boundary" if args.suite == "boundary" else "formal" if case["case_source"] == "cases.jsonl" else "probes"
                        evidence = out / group / slot["side"] / case["id"] / f"attempt-{slot['attempt']}"
                        revision = baseline_revision if slot["side"] == "baseline" else candidate_revision
                        record = _failed_capture(case, slot, evidence, revision, None, None, f"runner failure: {type(exc).__name__}: {exc}")
                        record = _retain_attempt(record, case, slot, checked, evidence, out)
                    records.append(record)
    finally:
        rb.EVALS = original_evals
    manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
    manifest["completion_order"] = [
        {"position": position, "case_id": record["case_id"], "attempt": record["attempt"], "side": record["comparison_side"], "status": record["execution"]["status"]}
        for position, record in enumerate(records, 1)
    ]
    records.sort(key=lambda record: (record["case_id"], record["attempt"], record["comparison_side"]))
    manifest["attempts"] = records
    manifest["model_metadata"] = {
        "per_attempt": [{"case_id": record["case_id"], "attempt": record["attempt"], "side": record["comparison_side"], **record.get("model_metadata", {"models_resolved": [], "unknown_metadata": ["all resolved/provider metadata unavailable after runner failure"]})} for record in records],
        "resolved_immutable_snapshot": None, "system_fingerprint": None, "hidden_provider_instructions": None,
    }
    summary = {
        "expected_attempts": len(checked["schedule"]), "attempts": len(records),
        "successful": sum(_successful(record) for record in records),
        "completed": sum(record["execution"]["status"] == "completed" for record in records),
        "errors": sum(record["execution"]["status"] == "error" for record in records),
        "timeouts": sum(record["execution"]["status"] == "timeout" for record in records),
        "outputs": sum(bool(record["raw"]["output"]) for record in records),
        "trace_complete": sum(bool(record["trace_complete"]) for record in records),
        "semantic_review": "not-run", "acceptance": "not assessed",
    }
    rb.save_json(out / "manifest.json", manifest)
    rb.save_json(out / "execution-summary.json", summary)
    rb.freeze_snapshot(out)
    return 0 if len(records) == len(checked["schedule"]) and all(_successful(record) for record in records) and version_error is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
