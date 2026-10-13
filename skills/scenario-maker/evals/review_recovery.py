#!/usr/bin/env python3
"""Plan and single-launch the authorized review-only recovery of frozen evidence.

Planning and status are offline. The source campaign is never written, resumed,
replaced, or used as a reviewer workspace. A launch claim is permanent, including
when execution is interrupted. Only the 211 unfinished initial reviews receive
fresh sessions; every concrete hard allegation receives independent adjudication.
"""
import argparse
from contextlib import redirect_stdout
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

import review_split as review

rb = review.rb
rs = review.rs
ReviewError = review.ReviewError
EVALS = Path(__file__).resolve().parent
KIND = "review-only-split-recovery"
TOOLS = ["read", "grep", "glob"]
TIMEOUT = 900
EXPECTED = {"total": 411, "reused": 200, "partial": 3, "unstarted": 208, "new": 211}
PROVENANCE = {"review_split.py", "reviewer-system.txt", "omp-config.json"}
PARTIAL_FILES = {"command.json", "request.txt", "trace.jsonl", "stderr.txt"}
RAW_FILES = PARTIAL_FILES | {"context.json", "output.txt"}
TOOL_FILES = ("review_recovery.py", "review_split.py", "run_split.py", "run_baseline.py", "reviewer-system.txt")


def _now():
    return datetime.now(timezone.utc).isoformat()


def _key(value):
    case, attempt = value.get("case_id"), value.get("attempt")
    if not isinstance(case, str) or not case or type(attempt) is not int or attempt not in (1, 2, 3):
        raise ReviewError("malformed review slot identity")
    rs._relative(case, "case ID")
    if "/" in case:
        raise ReviewError("case ID must be one path component")
    return case, attempt


def _root(path, label):
    path = Path(path).absolute()
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise ReviewError(f"{label}: symlinked path: {parent}")
    return rs._root(path, label)


def _inventory(root):
    """Hash every regular file and retain empty directories; reject unsafe trees."""
    root = _root(root, "evidence inventory")
    files, directories = {}, []

    def visit(directory):
        for path in sorted(directory.iterdir()):
            name = path.relative_to(root).as_posix()
            if path.is_symlink():
                raise ReviewError(f"symlinked evidence: {path}")
            if path.is_dir():
                directories.append(name)
                visit(path)
            elif path.is_file():
                files[name] = rs._file(root, name, "evidence inventory")[1]
            else:
                raise ReviewError(f"nonregular evidence: {path}")

    visit(root)
    return {"files": files, "directories": sorted(directories)}


def _json_hash(value):
    return hashlib.sha256((json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")).hexdigest()


def _same_json(left, right):
    return json.dumps(left, sort_keys=True, ensure_ascii=False) == json.dumps(right, sort_keys=True, ensure_ascii=False)


def _parents(files):
    return {parent.as_posix() for name in files for parent in Path(name).parents if parent.as_posix() != "."}


def _imported_tools():
    modules = {"review_recovery.py": Path(__file__), "review_split.py": Path(review.__file__),
               "run_split.py": Path(rs.__file__), "run_baseline.py": Path(rb.__file__)}
    for name, path in modules.items():
        if path.absolute() != EVALS / name or path.is_symlink():
            raise ReviewError(f"unexpected imported recovery module: {name}")
    return {name: rs._file(EVALS, name, "recovery tool code")[1] for name in TOOL_FILES}

def _request(packet):
    mode = "adjudication" if "alleged_review" in packet else "review"
    return (
        f"Perform independent {mode} of the complete local packet.json and its declared fixtures. "
        f"Review identity: case_id={json.dumps(packet['case_id'])}; attempt={packet['attempt']}. "
        "Copy that exact case ID and integer attempt into the specified AI review JSON, with grounded citations."
    )


def _command(command, packet, campaign, cwd=None):
    if not isinstance(command, list) or not all(isinstance(part, str) for part in command):
        raise ReviewError("review command must be an argument array")
    if len(command) < 3:
        raise ReviewError("review command missing workspace")
    workspace = command[2]
    if not Path(workspace).is_absolute() or (cwd is not None and workspace != cwd):
        raise ReviewError("review command/workspace mismatch")
    if ".." in Path(workspace).parts or "\x00" in workspace or "\\" in workspace:
        raise ReviewError("unsafe reviewer workspace")
    if Path(workspace) == campaign or campaign in Path(workspace).parents:
        raise ReviewError("reviewer workspace overlaps retained campaign evidence")
    if Path(workspace).parts[-2:] != (packet["case_id"], f"attempt-{packet['attempt']}"):
        raise ReviewError("review workspace slot mismatch")
    expected = ["omp", "--cwd", workspace, "--print", "--mode", "json", "--model", rb.MODEL,
                "--thinking", "high", "--no-session", "--no-title", "--no-prewalk", "--no-skills", "--no-rules",
                "--no-extensions", "--no-lsp", "--no-pty", "--tools", "read,grep,glob", "--approval-mode", "yolo",
                "--config", str(campaign / "provenance/omp-config.json"),
                "--system-prompt", str(campaign / "provenance/reviewer-system.txt"), "--max-time", "900s", _request(packet)]
    if command != expected:
        raise ReviewError("review command differs from approved model/high/900s/read-only controls")
    return Path(workspace)


def _trace_controls(events, workspace, packet):
    violations = review.reviewer_tool_violations(events, workspace, packet)
    metadata = review.review_metadata(events)
    if any(model.get("provider") not in (None, "openai-codex") or model.get("model") not in (None, "gpt-6-astra")
           for model in metadata["models_resolved"]):
        violations.append("observed reviewer model differs from approved model")
    if any(event.get("type") == "message_end" and event.get("message", {}).get("role") == "assistant"
           and event["message"].get("stopReason") in {"error", "aborted"} for event in events):
        violations.append("reviewer model error/aborted trace")
    if violations:
        raise ReviewError("; ".join(violations))
    return metadata


def _completed(directory, packet, packet_hash, campaign):
    """Revalidate a completed envelope, not merely its cached valid boolean."""
    inventory = _inventory(directory)
    if inventory["directories"]:
        raise ReviewError(f"nested reviewer raw evidence: {directory}")
    record = review.load_json(directory / "review.json")
    if not isinstance(record, dict) or _key(record) != _key(packet):
        raise ReviewError(f"review identity mismatch: {directory}")
    mode = "adjudication" if "alleged_review" in packet else "review"
    if record.get("reviewer_kind") != "ai" or record.get("mode") != mode:
        raise ReviewError(f"review kind/mode mismatch: {directory}")
    if record.get("valid") is not True or record.get("validation_errors") != []:
        raise ReviewError(f"completed review is invalid: {directory}")
    execution = record.get("execution")
    if not isinstance(execution, dict) or not {"status", "exit_code", "error"}.issubset(execution) or execution.get("status") != "completed" or type(execution.get("exit_code")) is not int or execution["exit_code"] != 0 or execution.get("error") is not None:
        raise ReviewError(f"completed review execution failed: {directory}")
    if record.get("packet_sha256") != packet_hash:
        raise ReviewError(f"completed review packet hash mismatch: {directory}")
    hashes = record.get("raw_checksums")
    actual = {name: checksum for name, checksum in inventory["files"].items() if name != "review.json"}
    if not isinstance(hashes, dict) or hashes != actual or not RAW_FILES.issubset(actual) or set(actual) - (RAW_FILES | {"partial-output.txt"}):
        raise ReviewError(f"completed review raw checksum coverage mismatch: {directory}")
    review.verify_files(directory, hashes, "review raw evidence")
    command = review.load_json(directory / "command.json")
    if record.get("command") != command:
        raise ReviewError("review command envelope differs from raw command")
    if not isinstance(record.get("cwd"), str):
        raise ReviewError("review envelope lacks exact working directory")
    workspace = _command(command, packet, campaign, record.get("cwd"))
    if rs._text(directory / "request.txt") != _request(packet):
        raise ReviewError("review request differs from approved request")
    events, errors = review.read_events(directory / "trace.jsonl")
    if errors or not review.terminal_trace(events) or record.get("trace_complete") is not True:
        raise ReviewError("completed reviewer trace incomplete/malformed")
    metadata = _trace_controls(events, workspace, packet)
    if not _same_json(record.get("model_metadata"), metadata):
        raise ReviewError("review metadata differs from observed trace")
    context = review.load_json(directory / "context.json")
    expected_context = {"system_prompt": rs._text(campaign / "provenance/reviewer-system.txt"),
                        "system_sha256": rb.digest(campaign / "provenance/reviewer-system.txt"),
                        "config_sha256": rb.digest(campaign / "provenance/omp-config.json"),
                        "tools_requested": TOOLS, **metadata}
    if not _same_json(context, expected_context):
        raise ReviewError("review context differs from frozen controls/system/config/trace")
    final, partial = review.final_messages(events)
    if final is None or rs._text(directory / "output.txt") != final:
        raise ReviewError("review final output differs from terminal trace")
    if ("partial-output.txt" in actual) != (partial is not None):
        raise ReviewError("review partial-output coverage differs from trace")
    if partial is not None and rs._text(directory / "partial-output.txt") != partial:
        raise ReviewError("review partial output differs from trace")
    parsed = rs._json(final, "review final JSON")
    if not _same_json(record.get("parsed_output"), parsed) or not _same_json(record.get("judgment"), parsed):
        raise ReviewError("review judgment/parsed/final JSON mismatch")
    review.validate_judgment(parsed, packet)
    if any(criterion[label] == "not-run" for criterion in parsed["criteria"]
           for label in (("a", "b") if packet["paired"] else ("a",))):
        raise ReviewError("completed review is not fully assessed")
    return record


def _partial(directory, packet, campaign):
    inventory = _inventory(directory)
    if inventory["directories"] or not inventory["files"] or set(inventory["files"]) - PARTIAL_FILES:
        raise ReviewError("interrupted slot has completed/unknown review evidence")
    if "command.json" not in inventory["files"] or "request.txt" not in inventory["files"]:
        raise ReviewError("interrupted slot lacks launch command/request")
    command = review.load_json(directory / "command.json")
    workspace = _command(command, packet, campaign)
    if rs._text(directory / "request.txt") != _request(packet):
        raise ReviewError("interrupted review request mismatch")
    if "trace.jsonl" in inventory["files"]:
        events, errors = review.read_events(directory / "trace.jsonl")
        if errors or review.terminal_trace(events) or review.final_messages(events)[0] is not None:
            raise ReviewError("interrupted slot has malformed or terminal completed evidence")
        _trace_controls(events, workspace, packet)
    return inventory


def inspect_source(source_review: Path) -> dict:
    """Perform all offline evidence checks for the one authorized narrow source."""
    root = _root(source_review, "source review")
    inventory = _inventory(root)
    manifest = review.load_json(root / "manifest.json")
    if not isinstance(manifest, dict) or manifest.get("kind") != "independent-blinded-ai-split-review":
        raise ReviewError("source must be an original independent split review campaign, not a recovery")
    expected_controls = {"reviewer_kind": "ai", "model_requested": rb.MODEL, "reasoning_requested": "high",
                         "expected_packets": 411, "expected_capture_slots": 798, "timeout_seconds": 900,
                         "tools_requested": TOOLS, "acceptance": "not assessed",
                         "permissions": "declared local read-only tool access; not an OS sandbox",
                         "retry_policy": "none; fresh sessions, no resume/replacements/best-of selection",
                         "label_policy": "random.Random(0), sorted (case_id, attempt); label-map.json outside packets/raw sessions",
                         "blinding_limits": review.BLINDING_LIMITS}
    for name, expected in expected_controls.items():
        if manifest.get(name) != expected or (name in {"expected_packets", "expected_capture_slots", "timeout_seconds"} and type(manifest.get(name)) is not int):
            raise ReviewError(f"source review control mismatch: {name}")
    if type(manifest.get("jobs")) is not int or manifest["jobs"] <= 0:
        raise ReviewError("source reviewer jobs must be positive")
    if not isinstance(manifest.get("omp_version"), str) or not manifest["omp_version"] or manifest.get("omp_version_error") is not None:
        raise ReviewError("source review runtime provenance missing/failed")
    if any(name in manifest for name in ("finished_at", "reviews", "adjudications", "adjudication_packets", "recovery", "source_review")):
        raise ReviewError("source campaign is finalized, failed, adjudicated, or recovered")
    allowed_roots = {"manifest.json", "label-map.json", "packets", "fixtures", "provenance", "reviews"}
    if any(name.split("/", 1)[0] not in allowed_roots for name in (*inventory["files"], *inventory["directories"])):
        raise ReviewError("unknown/final/failed source campaign evidence")
    provenance = manifest.get("provenance_files")
    if not isinstance(provenance, dict) or set(provenance) != PROVENANCE:
        raise ReviewError("source review provenance coverage mismatch")
    if {name.removeprefix("provenance/") for name in inventory["files"] if name.startswith("provenance/")} != PROVENANCE:
        raise ReviewError("source review has unknown provenance")
    review.verify_files(root / "provenance", provenance, "source reviewer provenance")
    for name in ("review_split.py", "reviewer-system.txt"):
        if rs._file(EVALS, name, "current reviewer provenance")[1] != provenance[name]:
            raise ReviewError(f"current reviewer differs from retained source: {name}")
    corpus_root = _root(manifest.get("results"), "source corpus")
    boundary_root = _root(manifest.get("boundary_results"), "source boundary")
    capture_hashes = {"corpus": rs._file(corpus_root, "manifest.json", "corpus manifest")[1],
                      "boundary": rs._file(boundary_root, "manifest.json", "boundary manifest")[1]}
    if manifest.get("capture_manifest_hashes") != capture_hashes:
        raise ReviewError("source capture manifest hash mismatch")
    corpus, boundary = review.preflight(corpus_root, boundary_root)
    tools = _imported_tools()
    for name in ("run_baseline.py", "run_split.py"):
        if corpus["manifest"].get("evaluation_files", {}).get(name) != tools[name]:
            raise ReviewError(f"current imported runner differs from frozen capture provenance: {name}")
    for field in ("baseline_revision", "candidate_revision"):
        if manifest.get(field) != corpus["manifest"][field]:
            raise ReviewError(f"source capture revision mismatch: {field}")
    if provenance["omp-config.json"] != rs._file(corpus["inputs"], "omp-config.json", "frozen config")[1]:
        raise ReviewError("retained reviewer config differs from frozen captures")
    packets, mappings = review.build_packets(corpus, boundary)
    if len(packets) != 411 or sum(item["suite"] == "corpus" for item in packets) != 372 or sum(item["suite"] == "boundary" for item in packets) != 39:
        raise ReviewError("exactly 372 corpus plus 39 boundary packets required")
    if sum(len(run["captures"]) for run in (corpus, boundary)) != 798 or any(not capture["available"] for run in (corpus, boundary) for capture in run["captures"].values()):
        raise ReviewError("all 798 original captures must be fully available")
    if review.load_json(root / "label-map.json") != mappings:
        raise ReviewError("source label mapping differs from deterministic rebuild")
    expected_rows, by_key = [], {}
    for item in packets:
        packet = item["packet"]
        key = _key(packet)
        if key in by_key:
            raise ReviewError("duplicate rebuilt packet")
        name = f"packets/{key[0]}/attempt-{key[1]}/packet.json"
        path, checksum = rs._file(root, name, "source packet")
        if review.load_json(path) != packet or checksum != _json_hash(packet):
            raise ReviewError(f"source packet differs from deterministic rebuild: {name}")
        item.update(packet_path=name, packet_sha256=checksum)
        by_key[key] = item
        expected_rows.append({"case_id": key[0], "attempt": key[1], "suite": item["suite"], "path": name, "sha256": checksum})
    if manifest.get("packets") != expected_rows:
        raise ReviewError("source packet manifest differs from complete deterministic packet list")
    expected_packet_files = {row["path"] for row in expected_rows}
    if {name for name in inventory["files"] if name.startswith("packets/")} != expected_packet_files:
        raise ReviewError("unknown source packet evidence")
    expected_fixture_files = {"fixtures/" + name: checksum for name, checksum in corpus["manifest"]["fixtures"].items()}
    actual_fixture_files = {name: checksum for name, checksum in inventory["files"].items() if name.startswith("fixtures/")}
    if actual_fixture_files != expected_fixture_files:
        raise ReviewError("source fixture bytes/coverage differ from frozen captures")
    if set(inventory["directories"]) != _parents(inventory["files"]):
        raise ReviewError("source contains empty/unmanifested evidence directories")
    for name in inventory["directories"]:
        if name.startswith("reviews/"):
            parts = name.split("/")
            if len(parts) == 2:
                if parts[1] not in {key[0] for key in by_key}:
                    raise ReviewError("unknown review evidence case")
            elif len(parts) == 3 and parts[2] in {"attempt-1", "attempt-2", "attempt-3"}:
                if (parts[1], int(parts[2][-1])) not in by_key:
                    raise ReviewError("unknown review evidence slot")
            else:
                raise ReviewError("unknown nested review evidence directory")
    for name in inventory["files"]:
        if name.startswith("reviews/"):
            parts = name.split("/")
            if len(parts) != 4 or parts[2] not in {"attempt-1", "attempt-2", "attempt-3"} or (parts[1], int(parts[2][-1])) not in by_key:
                raise ReviewError("unknown review evidence slot")
    reviews, slots = {}, []
    counts = {"total": 411, "reused": 0, "partial": 0, "unstarted": 0, "new": 0}
    for key, item in by_key.items():
        directory = root / f"reviews/{key[0]}/attempt-{key[1]}"
        source_files = {str(root / name): checksum for name, checksum in inventory["files"].items()
                        if name.startswith(f"reviews/{key[0]}/attempt-{key[1]}/")}
        record_path = directory / "review.json"
        if record_path.exists():
            reviews[key] = _completed(directory, item["packet"], item["packet_sha256"], root)
            state, origin = "completed", "reused"
            counts["reused"] += 1
            source_record = {"path": str(record_path), "sha256": rb.digest(record_path)}
        elif directory.exists():
            _partial(directory, item["packet"], root)
            state, origin, source_record = "interrupted", "new", None
            counts["partial"] += 1
        else:
            state, origin, source_record = "unstarted", "new", None
            counts["unstarted"] += 1
        slots.append({"case_id": key[0], "attempt": key[1], "suite": item["suite"],
                      "source_state": state, "origin": origin, "packet_path": item["packet_path"],
                      "packet_sha256": item["packet_sha256"], "source_record": source_record,
                      "source_files": source_files,
                      "new_record_path": f"reviews/{key[0]}/attempt-{key[1]}/review.json" if origin == "new" else None})
    counts["new"] = counts["partial"] + counts["unstarted"]
    if counts != EXPECTED:
        raise ReviewError(f"source is outside authorized 200/3/208 recovery exception: {counts}")
    allegations = [key for key, record in reviews.items() if review.needs_adjudication(record["judgment"], by_key[key]["packet"])]
    if allegations != [("h3-dev-02", 2)]:
        raise ReviewError("retained source must have exactly the h3-dev-02 attempt-2 hard allegation")
    labels = next(row for row in mappings if _key(row) == allegations[0])
    allegation = reviews[allegations[0]]["judgment"]
    hard = {row["id"] for row in by_key[allegations[0]]["packet"]["criteria"] if row.get("severity", "hard") != "advisory"}
    failing_sides = {labels[label] for row in allegation["criteria"] if row["id"] in hard
                     for label in ("a", "b") if row[label] == "failed"}
    if failing_sides != {"baseline"}:
        raise ReviewError("retained h3-dev-02 allegation must be baseline-only")
    # Detect changes while inspecting, including partial processes still writing.
    if _inventory(root) != inventory:
        raise ReviewError("source evidence changed during offline inspection")
    return {"root": root, "manifest": manifest, "packets": packets, "mappings": mappings,
            "reviews": reviews, "corpus": corpus, "boundary": boundary, "inventory": inventory,
            "source_files": inventory["files"], "slots": slots, "counts": counts}


def plan(source_review: Path, out: Path, jobs=3) -> dict:
    if type(jobs) is not int or jobs <= 0:
        raise ReviewError("jobs must be a positive integer")
    out = Path(out).absolute()
    if out.exists() or out.is_symlink():
        raise ReviewError(f"out must be a new directory: {out}")
    if ".." in out.parts or "\x00" in str(out) or "\\" in str(out):
        raise ReviewError("unsafe recovery output path")
    for parent in out.parents:
        if parent.is_symlink():
            raise ReviewError(f"symlinked output parent: {parent}")
    source = inspect_source(source_review)
    evidence_roots = [source["root"]]
    for run in (source["corpus"], source["boundary"]):
        evidence_roots.extend((run["root"], run["inputs"], run["baseline"]))
    if any(out == root or root in out.parents or out in root.parents for root in evidence_roots):
        raise ReviewError("recovery output must not overlap source review/capture/evaluation evidence")
    capture_inventories = {suite: _inventory(source[suite]["root"]) for suite in ("corpus", "boundary")}
    out.mkdir(parents=True, exist_ok=False)
    review.retain_preparation(source["packets"], source["mappings"], out, source["corpus"])
    for name in ("review_recovery.py", "run_split.py", "run_baseline.py"):
        shutil.copyfile(EVALS / name, out / "provenance" / name)
    rb.freeze_snapshot(out / "provenance")
    frozen = _inventory(out)["files"]
    for item in source["packets"]:
        if frozen[item["packet_path"]] != item["packet_sha256"]:
            raise ReviewError("new preparation did not retain exact source packet bytes")
    if frozen["label-map.json"] != source["source_files"]["label-map.json"]:
        raise ReviewError("new preparation did not retain exact source label map bytes")
    if _inventory(source["root"]) != source["inventory"]:
        raise ReviewError("source evidence changed during planning")
    manifest = {"kind": KIND, "created_at": _now(), "state": "planned", "acceptance": "not assessed",
                "reviewer_kind": "ai", "model_requested": rb.MODEL, "reasoning_requested": "high",
                "timeout_seconds": TIMEOUT, "jobs": jobs, "tools_requested": TOOLS,
                "expected_packets": 411, "expected_capture_slots": 798, "counts": source["counts"],
                "source_review": str(source["root"]), "source_manifest_sha256": source["source_files"]["manifest.json"],
                "source_inventory": source["inventory"], "source_files": source["source_files"],
                "label_map_sha256": frozen["label-map.json"], "source_label_map_sha256": source["source_files"]["label-map.json"],
                "source_provenance_files": source["manifest"]["provenance_files"],
                "provenance_files": {name.removeprefix("provenance/"): checksum for name, checksum in frozen.items() if name.startswith("provenance/")},
                "tool_files": _imported_tools(),
                "frozen_files": frozen, "captures": {suite: {"root": str(source[suite]["root"]),
                    "manifest_sha256": source["manifest"]["capture_manifest_hashes"][suite],
                    "inventory": capture_inventories[suite]} for suite in ("corpus", "boundary")},
                "baseline_revision": source["manifest"]["baseline_revision"], "candidate_revision": source["manifest"]["candidate_revision"],
                "packets": source["manifest"]["packets"],
                "slots": [{**slot, "packet_physical_path": str(out / slot["packet_path"]),
                           "new_record_physical_path": str(out / slot["new_record_path"]) if slot["new_record_path"] else None}
                          for slot in source["slots"]],
                "required_reused_adjudications": [{"case_id": "h3-dev-02", "attempt": 2}],
                "retry_policy": "single-use recovery; no resume, retries, replacements, or automatic repeats",
                "permissions": source["manifest"]["permissions"], "blinding_limits": review.BLINDING_LIMITS,
                "provider_metadata": review.review_metadata([])}
    rb.save_json(out / "plan.json", manifest)
    (out / "plan.json").chmod(0o444)
    manifest = {**manifest, "plan_sha256": rb.digest(out / "plan.json")}
    rb.save_json(out / "manifest.json", manifest)
    return manifest


def _load_plan(out):
    out = _root(out, "recovery output")
    rs._file(out, "manifest.json", "recovery manifest")
    plan_file, checksum = rs._file(out, "plan.json", "sealed recovery plan")
    manifest, planned = review.load_json(out / "manifest.json"), review.load_json(plan_file)
    if not isinstance(manifest, dict) or not isinstance(planned, dict) or manifest.get("kind") != KIND or planned.get("kind") != KIND:
        raise ReviewError("not a planned recovery output")
    if manifest.get("plan_sha256") != checksum:
        raise ReviewError("sealed recovery plan hash mismatch")
    mutable = {"state", "acceptance"}
    if any(manifest.get(name) != value for name, value in planned.items() if name not in mutable):
        raise ReviewError("recovery manifest differs from sealed plan")
    if planned.get("state") != "planned" or planned.get("counts") != EXPECTED or planned.get("timeout_seconds") != TIMEOUT or type(planned.get("timeout_seconds")) is not int or planned.get("model_requested") != rb.MODEL or planned.get("reasoning_requested") != "high" or planned.get("tools_requested") != TOOLS:
        raise ReviewError("recovery plan controls outside authorized exception")
    if type(planned.get("jobs")) is not int or planned["jobs"] <= 0:
        raise ReviewError("planned jobs must be positive")
    if set(planned.get("tool_files", {})) != set(TOOL_FILES):
        raise ReviewError("planned tool provenance coverage mismatch")
    for name in ("packets", "slots"):
        rows = planned.get(name)
        if not isinstance(rows, list) or len(rows) != 411 or any(not isinstance(row, dict) for row in rows):
            raise ReviewError(f"planned {name} requires all 411 slot objects")
        if len({_key(row) for row in rows}) != 411:
            raise ReviewError(f"planned {name} contains duplicate slots")
    if [_key(row) for row in planned["packets"]] != [_key(row) for row in planned["slots"]]:
        raise ReviewError("planned packet and recovery slot order/identity mismatch")
    for slot in planned["slots"]:
        key = _key(slot)
        packet_name = f"packets/{key[0]}/attempt-{key[1]}/packet.json"
        record_name = f"reviews/{key[0]}/attempt-{key[1]}/review.json"
        if slot.get("packet_path") != packet_name or slot.get("packet_physical_path") != str(out / packet_name):
            raise ReviewError("planned packet physical path mismatch")
        if slot.get("origin") == "new":
            if slot.get("source_state") not in {"interrupted", "unstarted"} or slot.get("new_record_path") != record_name or slot.get("new_record_physical_path") != str(out / record_name):
                raise ReviewError("planned fresh record physical path/state mismatch")
        elif slot.get("origin") == "reused":
            if slot.get("source_state") != "completed" or slot.get("new_record_path") is not None or slot.get("new_record_physical_path") is not None:
                raise ReviewError("planned reused record must not have a replacement destination")
        else:
            raise ReviewError("unknown recovery record origin")
    return out, manifest, planned


def _verify_frozen(out, planned):
    review.verify_files(out, planned["frozen_files"], "planned frozen preparation")
    actual = _inventory(out)
    runtime_files = {"launch.json", "execution.json", "summary.json", "completion-stdout.txt"}
    allowed_files = set(planned["frozen_files"]) | {"plan.json", "manifest.json"}
    allowed_dirs = _parents(allowed_files)
    if (out / "launch.json").exists():
        allowed_files |= runtime_files
        new_keys = {_key(slot) for slot in planned["slots"] if slot["origin"] == "new"}
        all_keys = {_key(slot) for slot in planned["slots"]}
        for name in actual["files"]:
            if name.split("/", 1)[0] not in {"reviews", "adjudications", "adjudication-packets"}:
                continue
            parts = name.split("/")
            group = parts[0]
            if len(parts) != 4 or parts[2] not in {"attempt-1", "attempt-2", "attempt-3"}:
                raise ReviewError("unknown recovery evidence slot")
            key = parts[1], int(parts[2][-1])
            if key not in (new_keys if group == "reviews" else all_keys):
                raise ReviewError("unknown recovery slot or replacement of reused judgment")
            allowed_names = {"packet.json"} if group == "adjudication-packets" else RAW_FILES | {"review.json", "partial-output.txt"}
            if parts[3] not in allowed_names:
                raise ReviewError("unknown recovery reviewer evidence file")
            allowed_files.add(name)
        allowed_dirs |= _parents(allowed_files)
        # Workers can create sparse slot directories before their first file.
        for group in ("reviews", "adjudications", "adjudication-packets"):
            keys = new_keys if group == "reviews" else all_keys
            allowed_dirs.add(group)
            for case, attempt in keys:
                allowed_dirs.update((f"{group}/{case}", f"{group}/{case}/attempt-{attempt}"))
    if set(actual["files"]) - allowed_files or set(actual["directories"]) - allowed_dirs:
        raise ReviewError("unmanifested recovery output evidence additions")
    for prefix in ("packets/", "fixtures/", "provenance/"):
        if {name: checksum for name, checksum in actual["files"].items() if name.startswith(prefix)} != {name: checksum for name, checksum in planned["frozen_files"].items() if name.startswith(prefix)}:
            raise ReviewError(f"unplanned frozen preparation files: {prefix}")
    if _imported_tools() != planned["tool_files"]:
        raise ReviewError("planned imported recovery tool code changed")
    source_root = _root(planned["source_review"], "planned source review")
    if _inventory(source_root) != planned["source_inventory"]:
        raise ReviewError("source evidence inventory/hash drift after planning")
    for suite in ("corpus", "boundary"):
        capture = planned["captures"][suite]
        if _inventory(_root(capture["root"], "planned captures")) != capture["inventory"]:
            raise ReviewError(f"{suite} frozen capture inventory/hash drift after planning")


def _planned_packets(out, planned):
    packets = []
    for row in planned["packets"]:
        packet = review.load_json(out / row["path"])
        if _key(row) != _key(packet) or rb.digest(out / row["path"]) != row["sha256"]:
            raise ReviewError("planned packet identity/hash mismatch")
        packets.append({"packet": packet, "suite": row["suite"], "packet_path": row["path"], "packet_sha256": row["sha256"]})
    mappings = review.load_json(out / "label-map.json")
    if rb.digest(out / "label-map.json") != planned["label_map_sha256"]:
        raise ReviewError("planned label map hash mismatch")
    return packets, mappings


def _invalid(packet, error):
    return {"case_id": packet["case_id"], "attempt": packet["attempt"], "valid": False,
            "judgment": review.not_run_judgment(packet, error), "validation_errors": [error],
            "execution": {"status": "error", "exit_code": None, "error": error}}


def _new_record(out, name, packet, packet_hash):
    path = out / name
    if not path.exists():
        return None, None
    _, checksum = rs._file(out, name, "new reviewer record")
    record = None
    errors = []
    try:
        record = review.load_json(path)
        if not isinstance(record, dict) or _key(record) != _key(packet):
            raise ReviewError("new record identity mismatch")
        if record.get("valid") is True:
            record = _completed(path.parent, packet, packet_hash, out)
        else:
            raw = _inventory(path.parent)
            actual = {key: value for key, value in raw["files"].items() if key != "review.json"}
            if raw["directories"] or record.get("valid") is not False or record.get("raw_checksums") != actual:
                raise ReviewError("invalid new record raw coverage or validity flag mismatch")
            if actual:
                review.verify_files(path.parent, actual, "failed reviewer raw evidence")
            if not record.get("validation_errors") or record.get("execution", {}).get("status") not in {"error", "timeout", "completed"}:
                raise ReviewError("new failure lacks retained execution/validation errors")
            # Invalid execution never supplies semantic conclusions to aggregate.
            record = _invalid(packet, "; ".join(str(error) for error in record["validation_errors"]))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        errors.append(str(exc))
        record = _invalid(packet, f"retained new record validation failed: {exc}")
    reference = {"case_id": packet["case_id"], "attempt": packet["attempt"], "origin": "new",
                 "path": name, "physical_path": str(path), "sha256": checksum, "valid": record["valid"],
                 "packet_sha256": packet_hash, "validation_errors": errors or record.get("validation_errors", []),
                 "raw_files": {str(path.parent / raw_name): raw_hash
                               for raw_name, raw_hash in _inventory(path.parent)["files"].items()
                               if raw_name != "review.json"}}
    return record, reference


def _collect(out, planned, packets):
    by_key = {_key(item["packet"]): item for item in packets}
    records, references = {}, []
    for slot in planned["slots"]:
        key = _key(slot)
        item = by_key[key]
        if slot["origin"] == "reused":
            reference = slot["source_record"]
            source_path = Path(reference["path"])
            if rb.digest(source_path) != reference["sha256"]:
                raise ReviewError("reused completed judgment changed")
            record = _completed(source_path.parent, item["packet"], item["packet_sha256"], Path(planned["source_review"]))
            references.append({"case_id": key[0], "attempt": key[1], "origin": "reused", "path": reference["path"],
                               "physical_path": reference["path"], "sha256": reference["sha256"], "valid": True,
                               "packet_sha256": item["packet_sha256"], "validation_errors": [],
                               "raw_files": {name: checksum for name, checksum in slot["source_files"].items()
                                             if name != reference["path"]}})
        else:
            record, reference = _new_record(out, slot["new_record_path"], item["packet"], item["packet_sha256"])
            if record is None:
                continue
            references.append(reference)
        records[key] = record
    return records, references


def _verify_record_refs(references):
    for reference in references:
        path = Path(reference["physical_path"])
        root = _root(path.parent, "retained reviewer record")
        if rs._file(root, path.name, "retained reviewer record")[1] != reference["sha256"]:
            raise ReviewError("completed reviewer record was replaced")
        for name, checksum in reference["raw_files"].items():
            raw_path = Path(name)
            if raw_path.parent != path.parent or rs._file(root, raw_path.name, "retained reviewer raw evidence")[1] != checksum:
                raise ReviewError("completed reviewer raw evidence changed")


def _adjudication_items(out, packets, mappings, reviews, create=False):
    items = []
    required = {_key(item["packet"]) for item in packets if _key(item["packet"]) in reviews
                and reviews[_key(item["packet"])]["valid"]
                and review.needs_adjudication(reviews[_key(item["packet"])]["judgment"], item["packet"])}
    for group in ("adjudications", "adjudication-packets"):
        directory = out / group
        if directory.exists():
            inventory = _inventory(directory)
            for name in (*inventory["files"], *inventory["directories"]):
                parts = name.split("/")
                if len(parts) >= 2 and (parts[1] not in {"attempt-1", "attempt-2", "attempt-3"}
                                       or (parts[0], int(parts[1][-1])) not in required):
                    raise ReviewError("unrequired or unknown adjudication evidence slot")
    for item in packets:
        key = _key(item["packet"])
        first = reviews.get(key)
        if first is None or not first["valid"] or not review.needs_adjudication(first["judgment"], item["packet"]):
            continue
        packet = review.adjudication_packet(item, packets, mappings, first)
        name = f"adjudication-packets/{key[0]}/attempt-{key[1]}/packet.json"
        path = out / name
        if create:
            path.parent.mkdir(parents=True, exist_ok=False)
            rb.save_json(path, packet)
            rb.freeze_snapshot(path.parent)
        elif path.exists() and (review.load_json(rs._file(out, name, "adjudication packet")[0]) != packet or rb.digest(path) != _json_hash(packet)):
            raise ReviewError("adjudication packet differs from independently aligned frozen history")
        elif not path.exists() and (out / f"adjudications/{key[0]}/attempt-{key[1]}/review.json").exists():
            raise ReviewError("adjudication record lacks retained independent packet")
        items.append({**item, "packet": packet, "adjudication_packet_path": name, "adjudication_packet_sha256": _json_hash(packet)})
    return items


def _adjudications(out, items):
    records, references = {}, []
    for item in items:
        key = _key(item["packet"])
        name = f"adjudications/{key[0]}/attempt-{key[1]}/review.json"
        record, reference = _new_record(out, name, item["packet"], item["adjudication_packet_sha256"])
        if record is not None:
            records[key] = record
            references.append(reference)
    return records, references


class _Tee:
    def __init__(self, output, retained):
        self.output, self.retained = output, retained

    def write(self, text):
        self.output.write(text)
        self.retained.write(text)
        return len(text)

    def flush(self):
        self.output.flush()
        self.retained.flush()


def run(out: Path) -> int:
    out = _root(out, "recovery output")
    if (out / "launch.json").exists() or (out / "launch.json").is_symlink():
        raise ReviewError("recovery is single-use: launch already claimed, including interrupted launches")
    out, manifest, planned = _load_plan(out)
    if manifest.get("state") != "planned" or any((out / name).exists() for name in ("reviews", "adjudications", "adjudication-packets", "execution.json", "summary.json", "completion-stdout.txt")):
        raise ReviewError("planned output already contains launch/completed reviewer evidence")
    _verify_frozen(out, planned)
    source = inspect_source(Path(planned["source_review"]))
    source_slots = [{name: slot[name] for name in source["slots"][index]}
                    for index, slot in enumerate(planned["slots"])]
    if source["slots"] != source_slots or source["manifest"]["packets"] != planned["packets"] or source["mappings"] != review.load_json(out / "label-map.json"):
        raise ReviewError("planned packet/mapping/source slot mismatch")
    packets, mappings = _planned_packets(out, planned)
    missing = [item for item in packets if _key(item["packet"]) not in source["reviews"]]
    if len(missing) != 211:
        raise ReviewError("recovery must launch exactly 211 missing initial sessions")
    version, version_error = rs._version()
    launch = {"kind": KIND, "pid": os.getpid(), "ppid": os.getppid(), "started_at": _now(),
              "argv": [os.fsdecode(part) for part in Path("/proc/self/cmdline").read_bytes().split(b"\0") if part],
              "python_argv": list(sys.argv), "python_executable": sys.executable, "out": str(out),
              "model_requested": rb.MODEL, "reasoning_requested": "high", "timeout_seconds": TIMEOUT,
              "jobs": planned["jobs"], "initial_sessions": 211, "omp_version": version,
              "omp_version_error": version_error, "plan_sha256": manifest["plan_sha256"]}
    try:
        with (out / "launch.json").open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(launch, indent=2, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise ReviewError("recovery launch already claimed by another process") from exc
    (out / "launch.json").chmod(0o444)
    manifest.update(state="started", started_at=launch["started_at"], launch_sha256=rb.digest(out / "launch.json"))
    rb.save_json(out / "manifest.json", manifest)
    error, result, summary = None, 1, None
    reviews, adjudications, review_refs, adjudication_refs, items = {}, {}, [], [], []
    with (out / "completion-stdout.txt").open("x", encoding="utf-8") as retained:
        with redirect_stdout(_Tee(sys.stdout, retained)):
            print(json.dumps({"event": "recovery_started", **launch}), flush=True)
            try:
                if version_error or not version:
                    raise ReviewError(f"review runtime provenance unavailable: {version_error or 'empty version'}")
                with tempfile.TemporaryDirectory(prefix="scenario-maker-review-recovery-") as temporary:
                    scratch = Path(temporary)
                    system = out / "provenance/reviewer-system.txt"
                    config = out / "provenance/omp-config.json"
                    review.execute_wave(missing, out, scratch / "initial", system, config, TIMEOUT, planned["jobs"])
                    _verify_frozen(out, planned)
                    reviews, review_refs = _collect(out, planned, packets)
                    items = _adjudication_items(out, packets, mappings, reviews, create=True)
                    review.execute_wave(items, out, scratch / "adjudication", system, config, TIMEOUT, planned["jobs"], adjudication=True)
                    adjudications, adjudication_refs = _adjudications(out, items)
                    _verify_frozen(out, planned)
                    _verify_record_refs(review_refs + adjudication_refs)
                    final_reviews, final_refs = _collect(out, planned, packets)
                    final_items = _adjudication_items(out, packets, mappings, final_reviews)
                    final_adjudications, final_adjudication_refs = _adjudications(out, final_items)
                    if final_refs != review_refs or final_adjudication_refs != adjudication_refs:
                        raise ReviewError("completed reviewer envelope/raw coverage changed before aggregation")
                    reviews, adjudications, items = final_reviews, final_adjudications, final_items
                    summary = review.aggregate(packets, mappings, reviews, adjudications)
                    manifest.update(omp_version=version, omp_version_error=version_error)
                    result = 0 if summary["accepted"] else 1
            except (Exception, KeyboardInterrupt) as exc:
                error = f"{type(exc).__name__}: {exc}"
                # Do not replace a completed judgment or manufacture partial judgments.
                # aggregate's own absent-slot convention retains all 411 gates closed.
                try:
                    reviews, review_refs = _collect(out, planned, packets)
                    items = _adjudication_items(out, packets, mappings, reviews)
                    adjudications, adjudication_refs = _adjudications(out, items)
                    summary = review.aggregate(packets, mappings, reviews, adjudications)
                    summary.update(accepted=False, recovery_error=error)
                    summary["gates"]["recovery_execution_complete"] = False
                    manifest.update(reviews=review_refs, adjudications=adjudication_refs)
                except (ValueError, OSError, KeyError, TypeError) as evidence_error:
                    summary = review.aggregate(packets, mappings, {}, {})
                    summary.update(accepted=False, recovery_error=error, evidence_error=str(evidence_error))
                    summary["gates"]["recovery_execution_complete"] = False
                result = 1
            finished = _now()
            if summary is None:
                summary = review.aggregate(packets, mappings, {}, {})
                summary["accepted"] = False
                summary["gates"]["recovery_execution_complete"] = False
            summary["recovery"] = {"kind": KIND, "source_review": planned["source_review"],
                "source_manifest_sha256": planned["source_manifest_sha256"], "plan_sha256": manifest["plan_sha256"],
                "source_inventory": planned["source_inventory"], "source_files": planned["source_files"],
                "captures": planned["captures"], "provenance_files": planned["provenance_files"],
                "label_map_sha256": planned["label_map_sha256"], "coverage": planned["counts"],
                "slots": planned["slots"], "reviews": review_refs, "adjudications": adjudication_refs,
                "adjudication_packets": [{"case_id": item["packet"]["case_id"], "attempt": item["packet"]["attempt"],
                    "path": item["adjudication_packet_path"], "sha256": item["adjudication_packet_sha256"]}
                    for item in items if (out / item["adjudication_packet_path"]).is_file()]}
            manifest.update(reviews=review_refs, adjudications=adjudication_refs,
                            adjudication_packets=summary["recovery"]["adjudication_packets"])
            rb.save_json(out / "summary.json", summary)
            manifest.update(state="finished", finished_at=finished, acceptance="passed" if result == 0 else "blocked",
                            summary_sha256=rb.digest(out / "summary.json"), execution_error=error)
            execution = {"status": "completed" if error is None else "error", "exit_code": result,
                         "error": error, "started_at": launch["started_at"], "finished_at": finished,
                         "pid": launch["pid"], "ppid": launch["ppid"], "launch_sha256": manifest["launch_sha256"],
                         "summary_sha256": manifest["summary_sha256"]}
            rb.save_json(out / "execution.json", execution)
            manifest["execution_sha256"] = rb.digest(out / "execution.json")
            rb.save_json(out / "manifest.json", manifest)
            print(json.dumps({"event": "recovery_finished", "accepted": result == 0, "exit_code": result,
                              "status": execution["status"], "finished_at": finished, "error": error}), flush=True)
    manifest["completion_stdout_sha256"] = rb.digest(out / "completion-stdout.txt")
    rb.save_json(out / "manifest.json", manifest)
    rb.freeze_snapshot(out)
    return result


def status(out: Path) -> dict:
    """Observe retained evidence without invoking OMP or interpreting partial text."""
    root = _root(out, "recovery output")
    response = {"kind": KIND, "out": str(root), "state": "planned", "accepted": False,
                "counts": {"reused": 0, "new": 0, "partial": 0, "missing": 411, "valid_initial": 0,
                           "planned_new": 211, "source_partial": 3, "unstarted": 208, "invalid": 0},
                "adjudications": {"required": 0, "valid": 0, "missing": 0},
                "summary_status": "not assessed", "validation_errors": []}
    launched = (root / "launch.json").exists() or (root / "launch.json").is_symlink()
    finished = (root / "execution.json").exists()
    response["state"] = "finished" if finished else "started" if launched else "planned"
    try:
        root, manifest, planned = _load_plan(root)
        required_reused = len(planned["required_reused_adjudications"])
        response["adjudications"].update(required=required_reused, missing=required_reused)
        _verify_frozen(root, planned)
        packets, mappings = _planned_packets(root, planned)
        reviews, refs = _collect(root, planned, packets)
        valid_reused = sum(row["origin"] == "reused" and row["valid"] for row in refs)
        valid_new = sum(row["origin"] == "new" and row["valid"] for row in refs)
        invalid = sum(not row["valid"] for row in refs)
        partial = sum(slot["origin"] == "new" and _key(slot) not in reviews and
                      ((root / slot["new_record_path"]).parent.exists() or slot["source_state"] == "interrupted")
                      for slot in planned["slots"])
        response["counts"].update(reused=valid_reused, new=valid_new, valid_initial=valid_reused + valid_new,
                                  missing=411 - valid_reused - valid_new, partial=partial, invalid=invalid)
        items = _adjudication_items(root, packets, mappings, reviews)
        adjudications, adjudication_refs = _adjudications(root, items)
        valid_adjudications = sum(row["valid"] for row in adjudication_refs)
        response["adjudications"] = {"required": len(items), "valid": valid_adjudications,
                                    "missing": len(items) - valid_adjudications}
        response.update(source_review=planned["source_review"], plan_sha256=manifest["plan_sha256"],
                        started_at=manifest.get("started_at"), finished_at=manifest.get("finished_at"))
        if launched:
            launch_path, checksum = rs._file(root, "launch.json", "recovery launch")
            if checksum != manifest.get("launch_sha256"):
                raise ReviewError("launch evidence hash mismatch")
            launch = review.load_json(launch_path)
            response["process"] = {name: launch.get(name) for name in ("pid", "ppid", "started_at", "argv", "omp_version")}
        if finished:
            _, checksum = rs._file(root, "execution.json", "recovery execution")
            if checksum != manifest.get("execution_sha256"):
                raise ReviewError("execution evidence hash mismatch")
            response["execution"] = review.load_json(root / "execution.json")
            _verify_record_refs(manifest.get("reviews", []) + manifest.get("adjudications", []))
            if manifest.get("reviews") != refs or manifest.get("adjudications") != adjudication_refs:
                raise ReviewError("finished reviewer references differ from retained records")
            if "completion_stdout_sha256" in manifest:
                if rs._file(root, "completion-stdout.txt", "retained completion stdout")[1] != manifest["completion_stdout_sha256"]:
                    raise ReviewError("retained completion stdout hash mismatch")
        if (root / "summary.json").exists():
            _, checksum = rs._file(root, "summary.json", "recovery summary")
            if checksum != manifest.get("summary_sha256"):
                raise ReviewError("summary evidence hash mismatch")
            summary = review.load_json(root / "summary.json")
            current = review.aggregate(packets, mappings, reviews, adjudications)
            if summary.get("accepted") is True and not current["accepted"]:
                raise ReviewError("retained summary acceptance differs from original aggregate gates")
            response["summary_status"] = "passed" if summary.get("accepted") is True else "blocked"
            response["accepted"] = bool(finished and summary.get("accepted") is True and
                                        response["counts"]["valid_initial"] == 411 and
                                        response["adjudications"]["missing"] == 0 and
                                        response.get("execution", {}).get("exit_code") == 0 and current["accepted"])
            response["gates"] = summary.get("gates", {})
    except (ValueError, OSError, KeyError, TypeError) as exc:
        response["accepted"] = False
        response["summary_status"] = "blocked"
        response["validation_errors"].append(f"{type(exc).__name__}: {exc}")
    return response


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="operation", required=True)
    planning = subparsers.add_parser("plan", help="validate and freeze a new offline recovery plan")
    planning.add_argument("--source-review", type=Path, required=True)
    planning.add_argument("--out", type=Path, required=True)
    planning.add_argument("--jobs", type=int, default=3)
    for operation in ("run", "status"):
        command = subparsers.add_parser(operation)
        command.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.operation == "plan":
            value = plan(args.source_review, args.out, args.jobs)
            print(json.dumps(value, indent=2, ensure_ascii=False))
            return 0
        if args.operation == "status":
            print(json.dumps(status(args.out), indent=2, ensure_ascii=False))
            return 0
        return run(args.out)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        claimed = (args.out / "launch.json").exists() or (args.out / "launch.json").is_symlink()
        evidence = {"error": f"{type(exc).__name__}: {exc}", "launch_claimed": claimed}
        if not claimed:
            evidence["paid_reviews_started"] = False
        print(json.dumps(evidence), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
