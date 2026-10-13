#!/usr/bin/env python3
"""Validate and prepare the mandatory historical allegation without any runtime calls."""
import hashlib
import json
from pathlib import Path
import re

import review_split as review
import run_baseline as rb
import run_split as rs

CASE_ID = "h3-dev-02"
ATTEMPT = 2
CRITERION_ID = "h3-dev-02-E1"
BASELINE_REVISION = "8c1db4ecf911696e5a7492cf07d67e101e538ebdf8d2f67eceb7c383dd9961da"
CANDIDATE_REVISION = "split-sha256-81a60df7cea26a553c679e4c72405ba3ab17defd615b6cff9b7e13140fac7f70"
TOOLS = ["read", "grep", "glob"]
PROVENANCE_FILES = {"review_split.py", "reviewer-system.txt", "omp-config.json"}
RAW_FILES = {"command.json", "request.txt", "trace.jsonl", "stderr.txt", "context.json", "output.txt"}
ReviewError = review.ReviewError
_UNBOUND = object()


def _root(path, label):
    path = Path(path).absolute()
    if any(parent.is_symlink() for parent in (path, *path.parents)):
        raise ReviewError(f"{label}: symlinked evidence is not allowed: {path}")
    try:
        return rs._root(path, label)
    except rs.InputError as exc:
        raise ReviewError(str(exc)) from exc


def _bind(root, name, bindings, expected=_UNBOUND):
    try:
        path, checksum = rs._file(root, name, "historical evidence")
    except rs.InputError as exc:
        raise ReviewError(str(exc)) from exc
    if expected is not _UNBOUND:
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ReviewError(f"historical evidence checksum is invalid: {path}")
        if checksum != expected:
            raise ReviewError(f"historical evidence hash mismatch: {path}")
    bindings[str(path)] = checksum
    return path, checksum


def _key(row):
    if not isinstance(row, dict) or not isinstance(row.get("case_id"), str) or type(row.get("attempt")) is not int or row["attempt"] not in (1, 2, 3):
        raise ReviewError("malformed historical packet/mapping identity")
    return row["case_id"], row["attempt"]


def _json_hash(value):
    return hashlib.sha256((json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")).hexdigest()


def _request(packet):
    return (
        "Perform independent review of the complete local packet.json and its declared fixtures. "
        f"Review identity: case_id={json.dumps(packet['case_id'])}; attempt={packet['attempt']}. "
        "Copy that exact case ID and integer attempt into the specified AI review JSON, with grounded citations."
    )


def _original_review(root, packet, packet_hash, bindings):
    directory = _root(root / "reviews" / CASE_ID / f"attempt-{ATTEMPT}", "original historical review")
    names = set()
    for path in directory.iterdir():
        if path.is_symlink() or not path.is_file():
            raise ReviewError(f"unexpected nested/unsafe historical review evidence: {path}")
        names.add(path.name)
    if not RAW_FILES.issubset(names) or names - (RAW_FILES | {"review.json", "partial-output.txt"}):
        raise ReviewError("original review raw evidence coverage mismatch")
    record_path, _ = _bind(directory, "review.json", bindings)
    record = review.load_json(record_path)
    if not isinstance(record, dict) or _key(record) != (CASE_ID, ATTEMPT) or record.get("reviewer_kind") != "ai" or record.get("mode") != "review":
        raise ReviewError("original review identity/kind/mode mismatch")
    if record.get("valid") is not True or record.get("validation_errors") != []:
        raise ReviewError("original review is not valid")
    execution = record.get("execution")
    if not isinstance(execution, dict) or execution.get("status") != "completed" or type(execution.get("exit_code")) is not int or execution["exit_code"] != 0 or execution.get("error") is not None:
        raise ReviewError("original review execution is not complete")
    if record.get("packet_sha256") != packet_hash:
        raise ReviewError("original review packet hash mismatch")
    hashes = record.get("raw_checksums")
    if not isinstance(hashes, dict) or set(hashes) != names - {"review.json"}:
        raise ReviewError("original review raw checksum coverage mismatch")
    for name, checksum in hashes.items():
        _bind(directory, name, bindings, checksum)
    command = review.load_json(directory / "command.json")
    workspace = record.get("cwd")
    if not isinstance(workspace, str) or not Path(workspace).is_absolute() or ".." in Path(workspace).parts or "\\" in workspace or "\x00" in workspace:
        raise ReviewError("original review workspace is invalid")
    workspace = Path(workspace)
    if workspace.parts[-2:] != (CASE_ID, f"attempt-{ATTEMPT}") or workspace == root or root in workspace.parents:
        raise ReviewError("original review workspace slot/overlap mismatch")
    expected_command = ["omp", "--cwd", str(workspace), "--print", "--mode", "json", "--model", rb.MODEL,
                        "--thinking", "high", "--no-session", "--no-title", "--no-prewalk", "--no-skills", "--no-rules",
                        "--no-extensions", "--no-lsp", "--no-pty", "--tools", "read,grep,glob", "--approval-mode", "yolo",
                        "--config", str(root / "provenance/omp-config.json"),
                        "--system-prompt", str(root / "provenance/reviewer-system.txt"), "--max-time", "900s", _request(packet)]
    if command != expected_command or record.get("command") != command or rs._text(directory / "request.txt") != _request(packet):
        raise ReviewError("original review command/request differs from approved controls")
    events, errors = review.read_events(directory / "trace.jsonl")
    if errors or not review.terminal_trace(events) or record.get("trace_complete") is not True:
        raise ReviewError("original review terminal trace is incomplete/malformed")
    violations = review.reviewer_tool_violations(events, workspace, packet)
    metadata = review.review_metadata(events)
    if any(model.get("provider") not in (None, "openai-codex") or model.get("model") not in (None, "gpt-6-astra") for model in metadata["models_resolved"]):
        violations.append("observed reviewer model differs from approved model")
    if any(event.get("type") == "message_end" and event.get("message", {}).get("role") == "assistant" and event["message"].get("stopReason") in {"error", "aborted"} for event in events):
        violations.append("reviewer model error/aborted trace")
    if violations:
        raise ReviewError("; ".join(violations))
    if record.get("model_metadata") != metadata:
        raise ReviewError("original review metadata differs from trace")
    expected_context = {"system_prompt": rs._text(root / "provenance/reviewer-system.txt"),
                        "system_sha256": rb.digest(root / "provenance/reviewer-system.txt"),
                        "config_sha256": rb.digest(root / "provenance/omp-config.json"), "tools_requested": TOOLS, **metadata}
    if review.load_json(directory / "context.json") != expected_context:
        raise ReviewError("original review context differs from provenance/trace")
    final, partial = review.final_messages(events)
    if final is None or rs._text(directory / "output.txt") != final:
        raise ReviewError("original review final output differs from terminal trace")
    if ("partial-output.txt" in names) != (partial is not None) or (partial is not None and rs._text(directory / "partial-output.txt") != partial):
        raise ReviewError("original review partial output differs from trace")
    parsed = rs._json(final, "original review final JSON")
    if record.get("parsed_output") != parsed or record.get("judgment") != parsed:
        raise ReviewError("original review judgment/parsed/final JSON mismatch")
    review.validate_judgment(parsed, packet)
    if any(item[label] == "not-run" for item in parsed["criteria"] for label in ("a", "b")):
        raise ReviewError("original review criterion assessment is incomplete")
    allegations = [item for item in parsed["criteria"] if item["id"] == CRITERION_ID]
    if len(allegations) != 1 or allegations[0]["a"] != "failed" or allegations[0]["b"] != "passed" or parsed["regression"] is not True:
        raise ReviewError("original baseline-only historical allegation has changed")
    return record


def _source_manifest(root, bindings):
    path, checksum = _bind(root, "manifest.json", bindings)
    try:
        content = path.read_bytes()
        text = content.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise ReviewError(str(exc)) from exc
    if hashlib.sha256(content).hexdigest() != checksum:
        raise ReviewError("historical source review manifest changed while reading")
    manifest = rs._json(text, path)
    if not isinstance(manifest, dict):
        raise ReviewError("historical source review manifest must be an object")
    controls = {"kind": "independent-blinded-ai-split-review", "reviewer_kind": "ai", "model_requested": rb.MODEL,
                "reasoning_requested": "high", "expected_packets": 411, "expected_capture_slots": 798,
                "timeout_seconds": 900, "jobs": 3, "tools_requested": TOOLS, "blinding_limits": review.BLINDING_LIMITS}
    for field, expected in controls.items():
        if manifest.get(field) != expected or (type(expected) is int and type(manifest.get(field)) is not int):
            raise ReviewError(f"historical source review control mismatch: {field}")
    if not isinstance(manifest.get("omp_version"), str) or not manifest["omp_version"].strip() or manifest.get("omp_version_error") is not None:
        raise ReviewError("historical source runtime provenance missing/failed")
    provenance = manifest.get("provenance_files")
    if not isinstance(provenance, dict) or set(provenance) != PROVENANCE_FILES:
        raise ReviewError("historical reviewer provenance coverage mismatch")
    return manifest, checksum


def prepare_source_history(source_review: Path) -> dict:
    """Rebuild historical evidence exclusively from its original capture roots."""
    root = _root(source_review, "historical source review")
    manifest, checksum = _source_manifest(root, {})
    roots = []
    for field in ("results", "boundary_results"):
        value = manifest.get(field)
        if not isinstance(value, str) or not value or not Path(value).is_absolute():
            raise ReviewError(f"historical source capture root is invalid: {field}")
        roots.append(_root(value, "historical " + field))
    corpus, boundary = review.preflight(*roots)
    packets, mappings = review.build_packets(corpus, boundary)
    result = prepare_history(root, packets, mappings, corpus, boundary)
    manifest_path, _ = _bind(root, "manifest.json", {}, checksum)
    if result["bindings"].get(str(manifest_path)) != checksum:
        raise ReviewError("historical source review manifest changed during preparation")
    return result


def prepare_history(source_review: Path, packets: list, mappings: list, corpus: dict, boundary: dict) -> dict:
    """Return a runnable independent packet, original envelope and external bindings.

    ``corpus`` and ``boundary`` are preflight results for the historical source
    review's original captures; packets/mappings are their complete deterministic
    rebuild. No old file is written and no runtime is invoked.
    """
    root = _root(source_review, "historical source review")
    bindings = {}
    manifest, _ = _source_manifest(root, bindings)
    provenance = manifest["provenance_files"]
    for name, checksum in provenance.items():
        _bind(root, "provenance/" + name, bindings, checksum)
    capture_hashes = {}
    for run, suite, field in ((corpus, "corpus", "results"), (boundary, "boundary", "boundary_results")):
        capture_root = _root(run["root"], "historical " + suite + " captures")
        if manifest.get(field) != str(capture_root):
            raise ReviewError(f"historical capture root mismatch: {suite}")
        path, checksum = _bind(capture_root, "manifest.json", bindings)
        if review.load_json(path) != run["manifest"] or run["manifest"].get("suite") != suite:
            raise ReviewError(f"historical capture manifest differs from preflight: {suite}")
        capture_hashes[suite] = checksum
        for field, identity in (("baseline_revision", BASELINE_REVISION), ("candidate_revision", CANDIDATE_REVISION)):
            if manifest.get(field) != identity or run["manifest"].get(field) != identity:
                raise ReviewError(f"historical capture identity mismatch: {field}")
    if manifest.get("capture_manifest_hashes") != capture_hashes:
        raise ReviewError("historical capture manifest hash mismatch")
    _bind(corpus["inputs"], "omp-config.json", bindings, provenance["omp-config.json"])
    for name, checksum in corpus["manifest"]["fixtures"].items():
        _bind(root, "fixtures/" + name, bindings, checksum)
    mapping_path, _ = _bind(root, "label-map.json", bindings)
    old_mappings = review.load_json(mapping_path)
    if old_mappings != mappings:
        raise ReviewError("historical label map differs from deterministic rebuild")
    by_key, mapping_by_key = {}, {}
    for item in packets:
        key = _key(item["packet"])
        if key in by_key:
            raise ReviewError("duplicate freshly rebuilt packet")
        by_key[key] = item
    for row in mappings:
        key = _key(row)
        if key in mapping_by_key or key not in by_key or row.get("suite") != by_key[key]["suite"]:
            raise ReviewError("historical label map coverage mismatch")
        sides = ("a", "b") if by_key[key]["packet"]["paired"] else ("a",)
        if set(row.get("raw_attempts", {})) != {row.get(label) for label in sides} or set(row.get(label) for label in sides) != ({"baseline", "candidate"} if len(sides) == 2 else {"candidate"}):
            raise ReviewError("historical label map side/raw-path mismatch")
        mapping_by_key[key] = row
    rows = manifest.get("packets")
    if len(by_key) != 411 or set(mapping_by_key) != set(by_key) or not isinstance(rows, list) or len(rows) != 411:
        raise ReviewError("complete 411-packet historical manifest/mapping coverage required")
    source_rows = {}
    for row in rows:
        key = _key(row)
        expected_path = f"packets/{key[0]}/attempt-{key[1]}/packet.json"
        if key in source_rows or key not in by_key or row.get("suite") != by_key[key]["suite"] or row.get("path") != expected_path or not re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256"))):
            raise ReviewError("historical source packet manifest coverage/binding mismatch")
        source_rows[key] = row
    target_keys = {(CASE_ID, attempt) for attempt in (1, 2, 3)}
    if not target_keys.issubset(by_key):
        raise ReviewError("historical adjudication requires all three repetitions")
    current = mapping_by_key[(CASE_ID, ATTEMPT)]
    if current["a"] != "baseline" or current["b"] != "candidate":
        raise ReviewError("original historical labels must remain A=baseline, B=candidate")
    target_packets, alignment = [], []
    case = corpus["cases"].get(CASE_ID)
    if case is None:
        raise ReviewError("historical case missing from captured corpus")
    for attempt in (1, 2, 3):
        key = CASE_ID, attempt
        item, labels, row = by_key[key], mapping_by_key[key], source_rows[key]
        packet_path, packet_hash = _bind(root, row["path"], bindings, row["sha256"])
        packet = review.load_json(packet_path)
        if item["suite"] != "corpus" or packet.get("paired") is not True or packet != item["packet"] or packet_hash != _json_hash(item["packet"]):
            raise ReviewError(f"historical packet differs from current complete rebuild: attempt {attempt}")
        captures = []
        for label in ("a", "b"):
            side = labels[label]
            slots = [slot for slot in corpus["manifest"]["schedule"] if review.slot_key(slot) == (CASE_ID, attempt, side)]
            records = [record for record in corpus["manifest"]["attempts"] if review.slot_key(record) == (CASE_ID, attempt, side)]
            if len(slots) != 1 or len(records) != 1:
                raise ReviewError("historical adjudication requires all three raw repetitions on both sides")
            capture = review.validate_attempt(corpus["root"], case, slots[0], records[0], corpus["manifest"])
            if not capture["available"]:
                raise ReviewError(f"historical raw repetition unavailable: {side} attempt {attempt}: {capture['issues']}")
            if labels["raw_attempts"][side] != str(capture["directory"]):
                raise ReviewError("historical label map capture path mismatch")
            _bind(capture["directory"], "attempt.json", bindings, records[0]["attempt_manifest_sha256"])
            for name, checksum in records[0]["raw_checksums"].items():
                _bind(capture["directory"], name, bindings, checksum)
            for artifact in records[0]["artifacts"]:
                _bind(capture["directory"], artifact["stored_path"], bindings, artifact["sha256"])
            captures.append(capture)
        clean = review.normalizer(corpus, captures)
        if packet["outputs"] != {"a": review.output_for(captures[0], clean), "b": review.output_for(captures[1], clean)}:
            raise ReviewError("historical packet output differs from complete retained raw evidence")
        target_packets.append({"packet": packet, "suite": "corpus", "run": corpus})
        alignment.append({"attempt": attempt, "original_labels": {label: labels[label] for label in ("a", "b")},
                          "history_labels": {label: "a" if labels["a"] == current[label] else "b" for label in ("a", "b")},
                          "raw_attempts": labels["raw_attempts"], "packet_sha256": packet_hash})
    original = target_packets[1]
    first = _original_review(root, original["packet"], source_rows[(CASE_ID, ATTEMPT)]["sha256"], bindings)
    packet = review.adjudication_packet(original, target_packets, mappings, first)
    return {"packet": packet, "first": first, "bindings": bindings,
            "label_alignment": {"case_id": CASE_ID, "attempt": ATTEMPT, "criterion_id": CRITERION_ID,
                                "source_review": str(root), "original_labels": {"a": "baseline", "b": "candidate"},
                                "allegation": {"criterion_id": CRITERION_ID, "label": "a", "comparison_side": "baseline",
                                               "state": "failed", "other_label": "b", "other_state": "passed", "candidate_regression": False},
                                "repetitions": alignment}}
