#!/usr/bin/env python3
"""Independently review frozen split captures; never supply AI scores to evaluate.py.

All integrity checks finish before any paid session. Missing/failed slots remain
not-run. Labels are deterministic side-label blinding, not perfect anonymity.
The only additional rubric is the approved explicit specialist invocation rule.
"""
import argparse
import base64
import concurrent.futures
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import random
import re
import shutil
import signal
import subprocess
import tempfile
import time

import run_baseline as rb
import run_split as rs

EVALS = Path(__file__).resolve().parent
STATES = {"passed", "failed", "not-run"}
COMMON_REFERENCES = (
    "references/routing.md", "references/output-contracts.md",
    "references/scene-composition.md", "references/constraints-and-revisions.md",
    "references/prompt-types.md",
)
SPECIAL_PROFILES = {
    "case-10": ("sdxl", "krea-2"), "split-shared": ("sdxl", "krea-2"),
    "p4-dev-10": ("krea-2",), "split-compare": ("sdxl", "pony-v6", "minimax-h3"),
    "split-explicit-generic": ("minimax-h3",),
}
PROFILE_NAMES = {
    "scenario-maker-sdxl": "sdxl", "scenario-maker-krea-2": "krea-2",
    "scenario-maker-illustrious": "illustrious", "scenario-maker-noobai": "noobai",
    "scenario-maker-pony": "pony-v6", "scenario-maker-minimax-h3": "minimax-h3",
}
INVOCATION_CONTRACT = (
    "Explicitly invoking a specialist supplies its family as Target when the request omits a model. "
    "It does not supply Task, choose a checkpoint variant, broaden Scope, or release locks. "
    "H3 invocation still does not invent a native route or resolve consequential hosted/local ambiguity; "
    "the user's media/task context may resolve it under the existing rules. A different explicitly "
    "requested family overrides the implied target. Never output the invoked specialist's dialect "
    "for that conflicting request. Explain that the requested profile belongs to the appropriate "
    "named specialist or scenario-maker; do not guess another model's contract or read a hardcoded "
    "sibling path. Supported standalone requests have no sibling dependency."
)
BLINDING_LIMITS = (
    "Deterministic A/B side-label blinding only: dialect, wording, selected-profile reads, "
    "and the explicit invocation contract may reveal identity. Mapping and original capture "
    "paths/revisions are outside reviewer packets and reviewer raw sessions."
)


class ReviewError(ValueError):
    """Invalid capture provenance or invalid reviewer judgment."""


def load_json(path):
    return rs._json(rs._text(path), path)


def safe_directory(root, name):
    relative = rs._relative(name, "retained directory")
    path = root
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise ReviewError(f"symlinked retained directory: {path}")
    return rs._root(path, "retained directory")


def verify_files(root, checksums, label):
    if not isinstance(checksums, dict) or not checksums:
        raise ReviewError(f"{label}: nonempty checksum mapping required")
    for name, expected in checksums.items():
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ReviewError(f"{label}: invalid checksum for {name}")
        _, actual = rs._file(root, name, label)
        if actual != expected:
            raise ReviewError(f"{label}: hash mismatch: {name}")


def slot_key(row):
    return row.get("case_id"), row.get("attempt"), row.get("side", row.get("comparison_side"))


def attempt_directory(root, case, attempt, side, suite):
    group = "boundary" if suite == "boundary" else "formal" if case["case_source"] == "cases.jsonl" else "probes"
    return root / group / side / case["id"] / f"attempt-{attempt}"


def read_events(path):
    events, errors = [], []
    if path is None or not path.is_file():
        return events, ["trace missing"]
    for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = rs._json(line, f"{path}:{number}")
            if not isinstance(value, dict):
                raise ValueError("event is not an object")
            events.append(value)
        except ValueError as exc:
            errors.append(f"line {number}: {exc}")
    return events, errors


def terminal_trace(events):
    starts = [event.get("toolCallId") for event in events if event.get("type") == "tool_execution_start"]
    ends = [event.get("toolCallId") for event in events if event.get("type") == "tool_execution_end"]
    return sorted(starts, key=str) == sorted(ends, key=str) and any(
        event.get("type") == "agent_end" and event.get("isTerminal") is True for event in events
    )


def final_messages(events):
    messages = [event.get("message", {}) for event in events if event.get("type") == "message_end"]
    assistants = [message for message in messages if message.get("role") == "assistant"]
    text = [message for message in assistants if any(item.get("type") == "text" for item in message.get("content", []))
            and not any(item.get("type") == "toolCall" for item in message.get("content", []))]
    final = [message for message in text if message.get("stopReason") == "stop"]
    rendered = lambda message: "".join(item["text"] for item in message.get("content", []) if item.get("type") == "text")
    return rendered(final[-1]) if final else None, rendered(text[-1]) if text and not final else None


def validate_attempt(root, case, slot, record, manifest):
    """Return retained availability; never turn absent slots into replacement runs."""
    directory = attempt_directory(root, case, slot["attempt"], slot["side"], manifest["suite"])
    if record is None:
        if (directory / "attempt.json").exists():
            raise ReviewError(f"attempt exists outside manifest attempts: {directory}")
        return {"record": None, "directory": directory, "available": False, "issues": ["scheduled capture missing"], "events": []}
    side = slot["side"]
    selected = "scenario-maker" if side == "baseline" else case["selected_skill"]
    sources = manifest["source_manifests"][side]
    files = sources if side == "baseline" else sources[selected]
    expected = {
        "case_id": case["id"], "attempt": slot["attempt"], "comparison_side": side,
        "selected_skill": selected, "selected_skill_sha256": rb.manifest_identity(files),
        "case_source": case["case_source"], "revision": manifest[side + "_revision"],
        "model_requested": rb.MODEL, "reasoning_requested": "high",
        "attempt_manifest": (directory / "attempt.json").relative_to(root).as_posix(),
    }
    for field, value in expected.items():
        if record.get(field) != value or (field == "attempt" and type(record.get(field)) is not int):
            raise ReviewError(f"{directory}: inconsistent {field}")
    issues = []
    attempt_file = directory / "attempt.json"
    if not attempt_file.exists():
        issues.append("retained attempt manifest missing")
    else:
        rs._file(root, expected["attempt_manifest"], "attempt manifest")
        checksum = record.get("attempt_manifest_sha256")
        if checksum != rb.digest(attempt_file):
            raise ReviewError(f"{directory}: attempt manifest hash mismatch")
        retained = load_json(attempt_file)
        comparison = {key: value for key, value in record.items() if key != "attempt_manifest_sha256"}
        if retained != comparison:
            raise ReviewError(f"{directory}: attempt manifest differs from suite manifest")
    raw = record.get("raw")
    hashes = record.get("raw_checksums")
    if not isinstance(raw, dict) or not isinstance(hashes, dict):
        raise ReviewError(f"{directory}: raw evidence/hash mappings required")
    for name, checksum in hashes.items():
        rs._relative(name, "raw evidence")
        if not re.fullmatch(r"[0-9a-f]{64}", str(checksum)):
            raise ReviewError(f"{directory}: invalid raw checksum: {name}")
        if not (directory / name).exists():
            issues.append(f"raw evidence missing: {name}")
        else:
            verify_files(directory, {name: checksum}, "raw evidence")
    if directory.is_dir():
        for path in directory.iterdir():
            if path.is_file() and path.name != "attempt.json" and path.name not in hashes:
                raise ReviewError(f"{directory}: unhashed raw evidence: {path.name}")
    for name in raw.values():
        if name is not None:
            rs._relative(name, "raw evidence reference")
            if name not in hashes:
                issues.append(f"raw evidence reference has no retained hash: {name}")
    artifacts = record.get("artifacts")
    if not isinstance(artifacts, list):
        raise ReviewError(f"{directory}: artifact list required")
    artifact_names = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise ReviewError(f"{directory}: malformed artifact")
        name, stored = artifact.get("path"), artifact.get("stored_path")
        rs._relative(name, "artifact path")
        rs._relative(stored, "stored artifact path")
        if stored != "artifacts/" + name or name in artifact_names:
            raise ReviewError(f"{directory}: inconsistent/duplicate artifact {name}")
        artifact_names.add(name)
        if not (directory / stored).exists():
            issues.append(f"artifact missing: {name}")
        else:
            verify_files(directory, {stored: artifact.get("sha256")}, "artifact")
            if (directory / stored).stat().st_size != artifact.get("bytes"):
                raise ReviewError(f"{directory}: artifact size mismatch: {name}")
    artifacts_root = directory / "artifacts"
    if artifacts_root.exists():
        actual = {path.relative_to(artifacts_root).as_posix() for path in rs._walk_source(artifacts_root)}
        if actual - artifact_names:
            raise ReviewError(f"{directory}: unrecorded artifacts: {sorted(actual - artifact_names)}")
    execution = record.get("execution", {})
    if execution.get("status") != "completed" or execution.get("exit_code") != 0:
        issues.append("capture did not complete successfully")
    if record.get("evidence_errors"):
        issues.extend(record["evidence_errors"])
    trace = directory / raw["trace"] if raw.get("trace") and (directory / raw["trace"]).is_file() else None
    events, trace_errors = read_events(trace)
    if trace_errors or not terminal_trace(events) or record.get("trace_complete") is not True:
        issues.append("capture trace incomplete/malformed")
    final, _ = final_messages(events)
    output = directory / raw["output"] if raw.get("output") and (directory / raw["output"]).is_file() else None
    if output is None:
        issues.append("final output missing")
    elif final is None or output.read_text(encoding="utf-8") != final or not final.strip():
        issues.append("final output absent/empty or inconsistent with trace")
    request = directory / "request.txt"
    prompt = "Use the explicitly selected Scenario Maker skill in ./selected-skill/SKILL.md.\n\n" + case["request"]
    if case["fixtures"]:
        prompt += "\n\nSupplied local fixtures: " + ", ".join("fixtures/" + name for name in case["fixtures"])
    if not request.is_file():
        issues.append("captured request missing")
    elif request.read_text(encoding="utf-8") != prompt:
        raise ReviewError(f"{directory}: captured request differs from case/fixtures")
    metadata = record.get("model_metadata", {})
    for model in metadata.get("models_resolved", []):
        if model.get("provider") not in (None, "openai-codex") or model.get("id") not in (None, "gpt-6-astra"):
            raise ReviewError(f"{directory}: observed capture model differs from approved model")
    if any(value != "high" for value in metadata.get("reasoning_resolved", [])):
        raise ReviewError(f"{directory}: observed capture reasoning differs")
    return {"record": record, "directory": directory, "available": not issues, "issues": issues, "events": events}


def validate_run(root, suite):
    root = rs._root(root, suite + " results")
    manifest = load_json(root / "manifest.json")
    if not isinstance(manifest, dict) or manifest.get("kind") != "current-monolith-versus-model-split" or manifest.get("suite") != suite:
        raise ReviewError(f"{root}: not a {suite} split capture manifest")
    if manifest.get("model_requested") != rb.MODEL or manifest.get("reasoning_requested") != "high":
        raise ReviewError(f"{root}: approved model/high reasoning required")
    if type(manifest.get("attempts_per_case")) is not int or manifest["attempts_per_case"] != 3:
        raise ReviewError(f"{root}: three repetitions required")
    if not isinstance(manifest.get("schedule"), list) or any(
        not isinstance(slot, dict) or type(slot.get("attempt")) is not int or type(slot.get("position")) is not int
        for slot in manifest["schedule"]
    ):
        raise ReviewError(f"{root}: schedule requires integer repetitions and positions")
    inputs = safe_directory(root, manifest.get("evaluation_inputs"))
    baseline = safe_directory(root, manifest.get("baseline_snapshot"))
    snapshots = manifest.get("candidate_snapshots")
    if not isinstance(snapshots, dict) or set(snapshots) != set(rs.SKILLS):
        raise ReviewError(f"{root}: snapshots for all eight candidate packages required")
    roots = {skill: safe_directory(root, name) for skill, name in snapshots.items()}
    parent = roots[rs.SKILLS[0]].parent
    if any(path != parent / skill for skill, path in roots.items()):
        raise ReviewError(f"{root}: candidate snapshot mapping differs from runner layout")
    checked = rs.preflight(baseline, parent, suite, evals=inputs)
    required = {
        "source_manifests": {"baseline": checked["baseline_files"], "candidate": checked["candidate_files"]},
        "baseline_revision": rb.manifest_identity(checked["baseline_files"]),
        "candidate_revision": "split-sha256-" + rb.manifest_identity(checked["candidate_files"]),
        "evaluation_files": checked["evaluation_files"], "fixtures": checked["fixture_files"],
        "cases": checked["cases"], "route_ownership": checked["routes"],
        "schedule": checked["schedule"], "expected_attempts": 744 if suite == "corpus" else 54,
    }
    for field, expected in required.items():
        if manifest.get(field) != expected:
            raise ReviewError(f"{root}: inconsistent {field}")
    for skill, snapshot in roots.items():
        actual_files = {path.relative_to(snapshot).as_posix(): rb.digest(path) for path in rs._walk_source(snapshot)}
        if actual_files != checked["candidate_files"][skill]:
            raise ReviewError(f"{root}: candidate snapshot contains unmanifested files: {skill}")
    actual_inputs = {path.relative_to(inputs).as_posix(): rb.digest(path) for path in rs._walk_source(inputs)}
    expected_inputs = {**checked["evaluation_files"], **{"fixtures/" + name: checksum for name, checksum in checked["fixture_files"].items()}}
    if actual_inputs != expected_inputs:
        raise ReviewError(f"{root}: frozen evaluation inputs contain unmanifested files")
    if checked["fixture_files"].get("case15-geometric-source.png") != "96d3453296fdd1239b21aeda140412632b643d96cb3980986739da4470bd8ded":
        raise ReviewError(f"{root}: original case-15 image fixture required")
    attempts = manifest.get("attempts", [])
    if not isinstance(attempts, list):
        raise ReviewError(f"{root}: attempt list required")
    records, slots = {}, {slot_key(slot) for slot in checked["schedule"]}
    for record in attempts:
        if not isinstance(record, dict):
            raise ReviewError(f"{root}: attempt must be an object")
        key = slot_key(record)
        if key not in slots or key in records or type(record.get("attempt")) is not int:
            raise ReviewError(f"{root}: duplicate/unknown/malformed attempt slot: {key}")
        records[key] = record
    cases = {case["id"]: case for case in checked["cases"]}
    captures = {}
    for slot in checked["schedule"]:
        key = slot_key(slot)
        captures[key] = validate_attempt(root, cases[slot["case_id"]], slot, records.get(key), manifest)
    return {"root": root, "manifest": manifest, "inputs": inputs, "baseline": baseline, "cases": cases, "captures": captures}


def preflight(results, boundary_results):
    corpus, boundary = validate_run(results, "corpus"), validate_run(boundary_results, "boundary")
    for field in ("baseline_revision", "candidate_revision", "source_manifests", "evaluation_files", "fixtures", "route_ownership", "model_requested", "reasoning_requested"):
        if corpus["manifest"][field] != boundary["manifest"][field]:
            raise ReviewError(f"corpus/boundary provenance differs: {field}")
    return corpus, boundary


def criteria_for(case):
    if "criteria" in case:
        criteria = case["criteria"]
    else:
        criteria = [{"id": f"{case['id']}-E{index}", "description": text, "severity": "hard", "method": "ai-supplemental"}
                    for index, text in enumerate(case["expected_behavior"], 1)]
    ids = [criterion["id"] for criterion in criteria]
    if not ids or len(set(ids)) != len(ids):
        raise ReviewError(f"{case['id']}: criteria require distinct IDs")
    return criteria


def rubric_for(case, baseline):
    profiles = SPECIAL_PROFILES.get(case["id"], ())
    if case["selected_skill"] in PROFILE_NAMES:
        profiles = (PROFILE_NAMES[case["selected_skill"]],)
    paths = list(COMMON_REFERENCES)
    paths.extend("references/models/" + profile + ".md" for profile in profiles)
    text = case["request"].lower()
    h3 = "minimax-h3" in profiles
    video = h3 or case["selected_skill"] == "scenario-maker-wan" or bool(re.search(r"\b(video|t2v|i2v|cinematic paragraph|wan)\b", text))
    if video:
        paths.append("references/video-prompts.md")
    if re.search(r"\b(character|characters|randomized|randomised)\b", text) or case.get("scope") == "character-design":
        paths.append("references/characters.md")
    if re.search(r"\b(tag|tags|danbooru|canonical|underscore|underscores|snake_case)\b", text) or any(profile in {"illustrious", "noobai", "pony-v6"} for profile in profiles):
        paths.append("references/danbooru-tags.md")
    if re.search(r"\b(wildcard|wildcards|comfyui|fragment|fragments)\b", text):
        paths.append("references/wildcards.md")
    if h3:
        paths.extend(rs.H3_GUIDES)
    references = []
    for name in dict.fromkeys(paths):
        path, checksum = rs._file(baseline, name, "frozen reviewer rubric")
        references.append({"path": name, "sha256": checksum, "text": rs._text(path)})
    invocation = INVOCATION_CONTRACT if case.get("paired") is False else None
    return {"source": "frozen current-monolith runtime references, complete and unsummarized", "references": references,
            "invocation_contract": invocation, "invoked_family": case["selected_skill"].removeprefix("scenario-maker-") if invocation else None}


def normalizer(run, captures):
    replacements = []
    for capture in captures:
        record = capture["record"]
        if record and record.get("cwd"):
            replacements.append((record["cwd"], "."))
    manifest = run["manifest"]
    for name in ("baseline_supplied", "candidate_root_supplied"):
        if manifest.get(name):
            replacements.append((manifest[name], "<source-root>"))
    replacements.extend((str(run["root"] / path), "<package>") for path in manifest["candidate_snapshots"].values())
    replacements.append((str(run["baseline"]), "<package>"))
    replacements.extend((manifest[name], "<revision>") for name in ("baseline_revision", "candidate_revision"))
    replacements.sort(key=lambda item: len(item[0]), reverse=True)

    def clean(value):
        if isinstance(value, str):
            for old, new in replacements:
                value = value.replace(old, new)
            value = value.replace("./selected-skill", "./supplied-package").replace("selected-skill/", "supplied-package/")
            # Strip only identity-bearing workspace path prefixes, never plain
            # side words or model names in authored prompt/artifact content.
            value = re.sub(r"(?:/[^\s\"'<>]*)?/(?:baseline|candidate)/" + re.escape(captures[0]["directory"].parent.name) + r"/attempt-[123](?=/|\b)", ".", value)
            return value
        if isinstance(value, list):
            return [clean(item) for item in value]
        if isinstance(value, dict):
            return {key: clean(item) for key, item in value.items()}
        return value
    return clean


def normalized_evidence(events, clean):
    evidence = []
    for event in events:
        kind = event.get("type", "")
        if kind.startswith("tool_execution_"):
            evidence.append(clean({key: value for key, value in event.items() if key not in {"timestamp", "elapsedMs", "durationMs"}}))
        elif kind == "message_end":
            message = event.get("message", {})
            if message.get("role") in {"user", "assistant", "toolResult", "tool"}:
                # Preserve complete calls/results and user-visible interaction;
                # provider, revisions, usage and timestamps are not evidence.
                fields = ("role", "content", "toolCallId", "toolName", "isError", "details", "stopReason", "errorMessage")
                content = {key: message[key] for key in fields if key in message}
                if message.get("role") == "assistant":
                    content["content"] = [item for item in message.get("content", []) if item.get("type") != "thinking"]
                evidence.append(clean({"type": "message_end", "message": content}))
    return evidence


def output_for(capture, clean):
    record, directory = capture["record"], capture["directory"]
    result = {"available": capture["available"], "capture_status": record.get("execution", {}).get("status", "error") if record else "missing",
              "capture_issues": clean(capture["issues"]), "final_output": None,
              "partial_output": None, "artifacts": [], "tool_evidence": normalized_evidence(capture["events"], clean)}
    if not record:
        return result
    for field, raw_field in (("final_output", "output"), ("partial_output", "partial_output")):
        name = record["raw"].get(raw_field)
        if name and (directory / name).is_file():
            result[field] = clean(rs._text(directory / name))
    for artifact in record["artifacts"]:
        path = directory / artifact["stored_path"]
        if not path.is_file():
            result["artifacts"].append({"path": clean(artifact["path"]), "missing": True})
            continue
        content = path.read_bytes()
        try:
            text = content.decode("utf-8")
            body = {"encoding": "utf-8", "content": clean(text)}
        except UnicodeError:
            body = {"encoding": "base64", "content": base64.b64encode(content).decode("ascii")}
        result["artifacts"].append({"path": clean(artifact["path"]), "bytes": len(content), **body})
    return result


def build_packets(corpus, boundary):
    rng, packets, mappings = random.Random(0), [], []
    pairs = sorted((case_id, attempt, run) for run in (corpus, boundary) for case_id in run["cases"] for attempt in (1, 2, 3))
    for case_id, attempt, run in pairs:
        case = run["cases"][case_id]
        paired = run["manifest"]["suite"] == "corpus" or case["paired"]
        sides = ["baseline", "candidate"] if paired else ["candidate"]
        if paired:
            rng.shuffle(sides)
        captures = [run["captures"][(case_id, attempt, side)] for side in sides]
        clean = normalizer(run, captures)
        packet = {"case_id": case_id, "attempt": attempt, "paired": paired, "request": case["request"],
                  "case_contract": {key: value for key, value in case.items() if key not in {"selected_skill", "skill", "case_source", "criteria", "fixtures", "request", "paired", "id"}},
                  "fixtures": [{"path": "fixtures/" + name, "sha256": run["manifest"]["fixtures"][name]} for name in case["fixtures"]],
                  "criteria": criteria_for(case), "rubric": rubric_for(case, run["baseline"]),
                  "outputs": {"a": output_for(captures[0], clean), "b": output_for(captures[1], clean) if paired else None},
                  "blinding_limits": BLINDING_LIMITS}
        packets.append({"packet": packet, "run": run, "suite": run["manifest"]["suite"]})
        mappings.append({"case_id": case_id, "attempt": attempt, "suite": run["manifest"]["suite"],
                         "a": sides[0], "b": sides[1] if paired else None,
                         "raw_attempts": {side: str(capture["directory"]) for side, capture in zip(sides, captures)}})
    if len(packets) != 411 or sum(item["suite"] == "corpus" for item in packets) != 372:
        raise ReviewError("exactly 372 corpus plus 39 boundary packets required")
    return packets, mappings


def pointer_value(packet, path):
    if not isinstance(path, str) or not path.startswith("/"):
        raise ReviewError("citation must use a JSON pointer")
    value = packet
    try:
        for part in path[1:].split("/"):
            if re.search(r"~(?![01])", part):
                raise ReviewError("invalid JSON pointer escape")
            key = part.replace("~1", "/").replace("~0", "~")
            value = value[int(key)] if isinstance(value, list) and re.fullmatch(r"0|[1-9][0-9]*", key) else value[key]
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise ReviewError(f"invalid citation path: {path}") from exc
    return value


def validate_citation(citation, packet, label, rule, history=False):
    if not isinstance(citation, dict) or set(citation) != {"path", "quote"}:
        raise ReviewError("citation requires exactly path and quote")
    path, quote = citation["path"], citation["quote"]
    if not isinstance(path, str):
        raise ReviewError("citation path must be a string")
    if rule:
        permitted = path == "/rubric/invocation_contract" or path == "/request" or bool(re.fullmatch(
            r"/(?:rubric/references/[0-9]+/text|criteria/[0-9]+/description)", path))
    else:
        permitted = bool(re.match(r"^/outputs/" + label + r"/(final_output|partial_output|artifacts|tool_evidence)(?:/|$)", path))
        if history:
            permitted = permitted or bool(re.match(r"^/repetition_evidence/" + label + r"/[0-9]+/output/(final_output|partial_output|artifacts|tool_evidence)(?:/|$)", path))
    if not permitted:
        raise ReviewError(f"citation points outside {'rules' if rule else label + ' observations'}: {path}")
    value = pointer_value(packet, path)
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    if not isinstance(quote, str) or not quote.strip() or quote not in text:
        raise ReviewError(f"citation is not a literal evidence quote: {path}")


def validate_judgment(value, packet):
    fields = {"case_id", "attempt", "reviewer_kind", "criteria", "regression", "rationale"}
    if not isinstance(value, dict) or set(value) != fields:
        raise ReviewError(f"review requires exactly {sorted(fields)}")
    if value["case_id"] != packet["case_id"] or type(value["attempt"]) is not int or value["attempt"] != packet["attempt"]:
        raise ReviewError("review case ID/attempt mismatch")
    if value["reviewer_kind"] != "ai":
        raise ReviewError("independent reviewer_kind must be ai, never human")
    rationale = value["rationale"]
    if packet.get("review_mode") == "independent-adjudication":
        if not isinstance(rationale, dict) or set(rationale) != {"explanation", "novel_contract_failures"}:
            raise ReviewError("adjudication rationale requires explanation and novel_contract_failures")
        if not isinstance(rationale["explanation"], str) or not rationale["explanation"].strip() or not isinstance(rationale["novel_contract_failures"], list):
            raise ReviewError("adjudication explanation and novelty list required")
    elif not isinstance(rationale, str) or not rationale.strip():
        raise ReviewError("initial review rationale must be a nonempty string")
    if type(value["regression"]) is not bool and value["regression"] is not None:
        raise ReviewError("regression must be boolean or null")
    criteria = value["criteria"]
    if not isinstance(criteria, list) or not all(isinstance(item, dict) for item in criteria):
        raise ReviewError("review criteria must be objects")
    ids = [item.get("id") for item in criteria]
    expected = [item["id"] for item in packet["criteria"]]
    if any(not isinstance(item, str) for item in ids) or len(set(ids)) != len(ids) or set(ids) != set(expected):
        raise ReviewError("review criteria coverage must match every original ID exactly once")
    for criterion in criteria:
        if set(criterion) != {"id", "a", "b", "evidence"}:
            raise ReviewError("criterion requires exactly id, a, b, evidence")
        evidence = criterion["evidence"]
        if not isinstance(evidence, dict) or set(evidence) != {"a", "b"}:
            raise ReviewError("criterion evidence requires both a/b keys")
        for label in ("a", "b"):
            state, proof = criterion[label], evidence[label]
            if label == "b" and not packet["paired"]:
                if state is not None or proof is not None:
                    raise ReviewError("single-output b and evidence.b must be null")
                continue
            if not isinstance(state, str) or state not in STATES:
                raise ReviewError("invalid criterion state")
            if not packet["outputs"][label]["available"] and state != "not-run":
                raise ReviewError("missing/failed capture cannot pass or fail semantic review")
            if not isinstance(proof, dict) or set(proof) != {"reason", "observations", "rules"}:
                raise ReviewError("side evidence requires reason, observations, rules")
            if not isinstance(proof["reason"], str) or not proof["reason"].strip():
                raise ReviewError("side evidence reason required")
            for key in ("observations", "rules"):
                if not isinstance(proof[key], list) or (state != "not-run" and not proof[key]):
                    raise ReviewError("passed/failed criteria need artifact and rule citations")
                for citation in proof[key]:
                    validate_citation(citation, packet, label, key == "rules")
    hard_ids = {item["id"] for item in packet["criteria"] if item.get("severity", "hard") != "advisory"}
    hard = [item for item in criteria if item["id"] in hard_ids]
    difference = packet["paired"] and any({item["a"], item["b"]} == {"passed", "failed"} for item in hard)
    incomplete = any(item[label] == "not-run" for item in hard for label in (("a", "b") if packet["paired"] else ("a",)))
    required = None if not packet["paired"] else True if difference else None if incomplete else False
    if value["regression"] is not required:
        raise ReviewError("regression inconsistent with hard criterion states/coverage")
    if packet.get("review_mode") == "independent-adjudication":
        validate_novelty(rationale["novel_contract_failures"], criteria, packet)
    return value


def validate_novelty(claims, criteria, packet):
    """Novelty is a separate independently grounded three-repetition decision."""
    hard = {item["id"] for item in packet["criteria"] if item.get("severity", "hard") != "advisory"}
    states = {item["id"]: item for item in criteria}
    categories = {"preservation", "scope/invention permission", "task/model boundaries", "requested artifact shape",
                  "utility evidence", "self-contained execution", "invocation/format/packaging"}
    seen = set()
    for claim in claims:
        if not isinstance(claim, dict) or set(claim) != {"criterion_id", "label", "category", "reason", "observations", "rules", "comparisons"}:
            raise ReviewError("novel contract failure requires criterion_id, label, category, reason, observations, rules, comparisons")
        criterion_id, label = claim["criterion_id"], claim["label"]
        if not isinstance(criterion_id, str) or not isinstance(label, str) or (criterion_id, label) in seen:
            raise ReviewError("invalid or duplicate novel contract failure")
        seen.add((criterion_id, label))
        if criterion_id not in hard or label not in (("a", "b") if packet["paired"] else ("a",)) or states[criterion_id][label] != "failed":
            raise ReviewError("novel failure must identify a hard criterion and its actually failing side")
        if claim["category"] not in categories or not isinstance(claim["reason"], str) or not claim["reason"].strip():
            raise ReviewError("novelty requires a concrete contract category and explanation")
        for field in ("observations", "rules", "comparisons"):
            if not isinstance(claim[field], list) or (field != "comparisons" and not claim[field]):
                raise ReviewError("novelty requires grounded artifact/rule citations")
        for citation in claim["observations"]:
            validate_citation(citation, packet, label, False, history=True)
        if not any(citation["path"].startswith("/outputs/" + label + "/") for citation in claim["observations"]):
            raise ReviewError("novelty must cite the currently failing raw output")
        for citation in claim["rules"]:
            validate_citation(citation, packet, label, True)
        if packet["paired"]:
            if not claim["comparisons"]:
                raise ReviewError("paired novelty requires opposite-side raw comparison evidence across repetitions")
            opposite = "b" if label == "a" else "a"
            for citation in claim["comparisons"]:
                validate_citation(citation, packet, opposite, False, history=True)
        elif claim["comparisons"]:
            raise ReviewError("single-output novelty cannot invent comparison evidence")


def not_run_judgment(packet, reason):
    proof = {"reason": reason, "observations": [], "rules": []}
    return {"case_id": packet["case_id"], "attempt": packet["attempt"], "reviewer_kind": "ai",
            "criteria": [{"id": item["id"], "a": "not-run", "b": "not-run" if packet["paired"] else None,
                          "evidence": {"a": dict(proof), "b": dict(proof) if packet["paired"] else None}} for item in packet["criteria"]],
            "regression": None, "rationale": reason}


def review_metadata(events):
    models, usage = [], []
    for event in events:
        if event.get("type") != "message_end":
            continue
        message = event.get("message", {})
        if message.get("role") != "assistant":
            continue
        observed = {key: message.get(key) for key in ("provider", "model", "api")}
        if any(value is not None for value in observed.values()) and observed not in models:
            models.append(observed)
        if isinstance(message.get("usage"), dict):
            usage.append(message["usage"])
    return {"model_requested": rb.MODEL, "reasoning_requested": "high", "models_resolved": models,
            "usage_observed": usage, "reasoning_resolved": None, "provider_request_metadata": None,
            "immutable_provider_snapshot": None, "provider_seed": None, "system_fingerprint": None,
            "hidden_provider_instructions": None,
            "unknown_metadata": ["resolved reasoning", "provider request body/settings", "immutable provider snapshot",
                                 "provider seed", "system fingerprint", "hidden provider instructions"] + ([] if models else ["resolved model"])}


def reviewer_tool_violations(events, workspace, packet):
    violations, calls = [], []
    for event in events:
        if event.get("type") == "tool_execution_start":
            calls.append((event.get("toolName"), event.get("args", event.get("arguments", {}))))
        if event.get("type") == "message_end":
            calls.extend((item.get("name"), item.get("arguments", {})) for item in event.get("message", {}).get("content", []) if item.get("type") == "toolCall")
    allowed_files = {"packet.json", *(fixture["path"] for fixture in packet["fixtures"])}
    for name, args in calls:
        if name not in {"read", "grep", "glob"} or not isinstance(args, dict):
            violations.append(f"prohibited reviewer tool: {name}")
            continue
        paths = args.get("path", "." if name != "read" else None)
        if not isinstance(paths, str):
            violations.append(f"invalid {name} path")
            continue
        for raw in ([paths] if name == "read" else paths.split(";")):
            # Read's JSON queries and line/image selectors still address the
            # same declared file; queries can themselves contain semicolons.
            raw = re.split(r":(?=\d|raw\b|img\b|-\d)", raw.split("?", 1)[0])[0]
            if "://" in raw or "\x00" in raw or "\\" in raw:
                violations.append(f"nonlocal reviewer path: {raw}")
                continue
            absolute = Path(raw) if Path(raw).is_absolute() else workspace / raw
            try:
                relative = absolute.resolve().relative_to(workspace.resolve()).as_posix()
            except ValueError:
                violations.append(f"reviewer path escapes declared workspace: {raw}")
                continue
            if name == "read" and relative not in allowed_files:
                violations.append(f"undeclared reviewer read: {relative}")
            elif name != "read":
                # glob/grep may search this sparse declared tree, not parents.
                if ".." in Path(raw).parts:
                    violations.append(f"reviewer search escapes declaration: {raw}")
    return sorted(set(violations))


def run_reviewer(packet, destination, scratch, system_file, config_file, timeout):
    """One fresh real OMP process, no extensions, no retry or replacement."""
    destination.mkdir(parents=True, exist_ok=False)
    workspace = scratch / packet["case_id"] / f"attempt-{packet['attempt']}"
    workspace.mkdir(parents=True, exist_ok=False)
    rb.save_json(workspace / "packet.json", packet)
    fixture_root = destination.parent.parent.parent / "fixtures"
    for fixture in packet["fixtures"]:
        target = workspace / fixture["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(fixture_root / fixture["path"].removeprefix("fixtures/"), target)
        if rb.digest(target) != fixture["sha256"]:
            raise ReviewError(f"fixture changed before reviewer session: {fixture['path']}")
    rb.freeze_snapshot(workspace)
    mode = "adjudication" if "alleged_review" in packet else "review"
    request = (
        f"Perform independent {mode} of the complete local packet.json and its declared fixtures. "
        f"Review identity: case_id={json.dumps(packet['case_id'])}; attempt={packet['attempt']}. "
        "Copy that exact case ID and integer attempt into the specified AI review JSON, with grounded citations."
    )
    (destination / "request.txt").write_text(request, encoding="utf-8")
    command = ["omp", "--cwd", str(workspace), "--print", "--mode", "json", "--model", rb.MODEL,
               "--thinking", "high", "--no-session", "--no-title", "--no-prewalk", "--no-skills", "--no-rules",
               "--no-extensions", "--no-lsp", "--no-pty", "--tools", "read,grep,glob", "--approval-mode", "yolo",
               "--config", str(config_file), "--system-prompt", str(system_file), "--max-time", f"{timeout}s", request]
    rb.save_json(destination / "command.json", command)
    environment = os.environ.copy()
    environment.update(PYTHONDONTWRITEBYTECODE="1", TZ="UTC", LC_ALL="C.UTF-8")
    environment.pop("EVAL_CONTEXT_FILE", None)
    environment.pop("EVAL_SYSTEM_FILE", None)
    started, start = datetime.now(timezone.utc).isoformat(), time.monotonic()
    status, exit_code, error = "error", None, None
    with (destination / "trace.jsonl").open("wb") as stdout, (destination / "stderr.txt").open("wb") as stderr:
        try:
            # The request is in argv; inherited pipes must not delay OMP startup.
            process = subprocess.Popen(command, cwd=workspace, env=environment, stdin=subprocess.DEVNULL,
                                       stdout=stdout, stderr=stderr, start_new_session=True)
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
                status, exit_code, error = "timeout", process.returncode, "outer reviewer deadline"
        except OSError as exc:
            error = f"{type(exc).__name__}: {exc}"
    events, malformed = read_events(destination / "trace.jsonl")
    final, partial = final_messages(events)
    if final is not None:
        (destination / "output.txt").write_text(final, encoding="utf-8")
    if partial is not None:
        (destination / "partial-output.txt").write_text(partial, encoding="utf-8")
    metadata = review_metadata(events)
    rb.save_json(destination / "context.json", {"system_prompt": rs._text(system_file), "system_sha256": rb.digest(system_file),
                                                "config_sha256": rb.digest(config_file), "tools_requested": ["read", "grep", "glob"], **metadata})
    violations = reviewer_tool_violations(events, workspace, packet)
    model_errors = [event["message"].get("errorMessage", event["message"].get("stopReason")) for event in events
                    if event.get("type") == "message_end" and event.get("message", {}).get("role") == "assistant"
                    and event["message"].get("stopReason") in {"error", "aborted"}]
    wrong_model = any(model.get("provider") not in (None, "openai-codex") or model.get("model") not in (None, "gpt-6-astra") for model in metadata["models_resolved"])
    errors = list(malformed) + violations + model_errors
    if wrong_model:
        errors.append("observed reviewer model differs from approved model")
    if not terminal_trace(events):
        errors.append("reviewer trace incomplete")
    if status != "completed":
        errors.append(error or f"reviewer process {status}: exit {exit_code}")
    if final is None:
        errors.append("reviewer final output missing")
    parsed, judgment = None, None
    if final is not None:
        try:
            parsed = rs._json(final, "reviewer final output")
            if not errors:
                judgment = validate_judgment(parsed, packet)
        except ValueError as exc:
            errors.append(str(exc))
    if judgment is None:
        judgment = not_run_judgment(packet, "; ".join(str(item) for item in errors) or "reviewer judgment unavailable")
    result = {"case_id": packet["case_id"], "attempt": packet["attempt"], "reviewer_kind": "ai", "mode": mode,
              "valid": not errors and parsed is not None, "judgment": judgment, "parsed_output": parsed,
              "validation_errors": errors, "execution": {"status": status, "exit_code": exit_code, "error": error},
              "started_at": started, "elapsed_seconds": round(time.monotonic() - start, 3),
              "command": command, "cwd": str(workspace), "packet_sha256": rb.digest(workspace / "packet.json"),
              "model_metadata": metadata, "trace_complete": terminal_trace(events),
              "raw_checksums": {path.name: rb.digest(path) for path in destination.iterdir() if path.is_file()}}
    rb.save_json(destination / "review.json", result)
    rb.freeze_snapshot(destination)
    return result


def needs_adjudication(judgment, packet):
    hard = {item["id"] for item in packet["criteria"] if item.get("severity", "hard") != "advisory"}
    # Reassess any concrete hard failure, including paired both-failed cases:
    # one broad criterion can hide different violations on the two sides.
    return judgment["regression"] is True or any(
        item["id"] in hard and any(item[label] == "failed" for label in (("a", "b") if packet["paired"] else ("a",)))
        for item in judgment["criteria"]
    )


def disposition(first, adjudication, packet):
    if not first["valid"]:
        return {"state": "not-run", "judgment": first["judgment"], "unresolved": True, "allegations": []}
    if not needs_adjudication(first["judgment"], packet):
        return {"state": "no-alleged-regression", "judgment": first["judgment"], "unresolved": False, "allegations": []}
    alleged = []
    hard = {item["id"] for item in packet["criteria"] if item.get("severity", "hard") != "advisory"}
    for item in first["judgment"]["criteria"]:
        if item["id"] not in hard:
            continue
        for label in (("a", "b") if packet["paired"] else ("a",)):
            if item[label] == "failed" and (not packet["paired"] or item["b" if label == "a" else "a"] == "passed"):
                alleged.append({"criterion_id": item["id"], "label": label, "state": "unresolved"})
    if adjudication is None or not adjudication["valid"]:
        return {"state": "unresolved", "judgment": first["judgment"], "unresolved": True, "allegations": alleged}
    independent = adjudication["judgment"]
    by_id = {item["id"]: item for item in independent["criteria"]}
    for allegation in alleged:
        state = by_id[allegation["criterion_id"]][allegation["label"]]
        allegation["state"] = "confirmed" if state == "failed" else "rejected-on-evidence" if state == "passed" else "unresolved"
    incomplete = any(item[label] == "not-run" for item in independent["criteria"] for label in (("a", "b") if packet["paired"] else ("a",)))
    overall = "unresolved" if incomplete else "confirmed" if any(item["state"] == "confirmed" for item in alleged) else "rejected-on-evidence" if alleged else "contract-failures-reassessed"
    return {"state": overall, "judgment": independent, "unresolved": incomplete, "allegations": alleged}


def aggregate(packets, mappings, reviews, adjudications):
    mapping = {(item["case_id"], item["attempt"]): item for item in mappings}
    counts, failures, not_run, advisory, dispositions = {}, [], [], [], []
    capture_failures = []
    review_complete, adjudication_complete, captures_complete = True, True, True
    boundary_pass, unresolved_new = True, []
    raw_counts = {"capture_slots": 0, "completed_captures": 0, "initial_reviews": len(reviews),
                  "valid_initial_reviews": 0, "adjudications": len(adjudications), "valid_adjudications": 0,
                  "alleged_regressions": 0, "required_adjudications": 0,
                  "capture_statuses": {state: 0 for state in ("completed", "error", "timeout", "missing", "other")},
                  "initial_criterion_states": {side: {state: 0 for state in STATES} for side in ("baseline", "candidate")},
                  "adjudication_criterion_states": {side: {state: 0 for state in STATES} for side in ("baseline", "candidate")},
                  "criterion_states": {side: {state: 0 for state in STATES} for side in ("baseline", "candidate")}}
    for item in packets:
        packet, suite = item["packet"], item["suite"]
        key = packet["case_id"], packet["attempt"]
        labels = mapping[key]
        for label in (("a", "b") if packet["paired"] else ("a",)):
            raw_counts["capture_slots"] += 1
            available = packet["outputs"][label]["available"]
            raw_counts["completed_captures"] += int(available)
            captures_complete = captures_complete and available
            status = packet["outputs"][label].get("capture_status", "completed" if available else "missing")
            raw_counts["capture_statuses"][status if status in raw_counts["capture_statuses"] else "other"] += 1
            if not available:
                capture_failures.append({"case_id": key[0], "attempt": key[1], "side": labels[label], "status": status,
                                         "issues": packet["outputs"][label]["capture_issues"]})
        first = reviews.get(key, {"valid": False, "judgment": not_run_judgment(packet, "initial review missing")})
        second = adjudications.get(key)
        raw_counts["valid_initial_reviews"] += int(first["valid"])
        raw_counts["valid_adjudications"] += int(second is not None and second["valid"])
        for result, field in ((first, "initial_criterion_states"), (second, "adjudication_criterion_states")):
            if result is not None:
                for criterion in result["judgment"]["criteria"]:
                    for label in (("a", "b") if packet["paired"] else ("a",)):
                        raw_counts[field][labels[label]][criterion[label]] += 1
        raw_counts["alleged_regressions"] += int(first["judgment"]["regression"] is True)
        raw_counts["required_adjudications"] += int(first["valid"] and needs_adjudication(first["judgment"], packet))
        final = disposition(first, second, packet)
        review_complete = review_complete and first["valid"]
        adjudication_complete = adjudication_complete and not (needs_adjudication(first["judgment"], packet) and final["unresolved"])
        dispositions.append({"case_id": key[0], "attempt": key[1], "state": final["state"], "unresolved": final["unresolved"],
                             "allegations": final["allegations"], "initial_judgment": first["judgment"],
                             "adjudication_judgment": second["judgment"] if second else None})
        definitions = {criterion["id"]: criterion for criterion in packet["criteria"]}
        if second and second["valid"] and isinstance(second["judgment"]["rationale"], dict):
            for claim in second["judgment"]["rationale"]["novel_contract_failures"]:
                if labels[claim["label"]] == "candidate":
                    unresolved_new.append({"case_id": key[0], "attempt": key[1], "disposition": final["state"], **claim})
        for criterion in final["judgment"]["criteria"]:
            criterion_id = criterion["id"]
            hard = definitions[criterion_id].get("severity", "hard") != "advisory"
            cohort = counts.setdefault((key[0], criterion_id), {"case_id": key[0], "criterion_id": criterion_id, "suite": suite,
                "severity": "hard" if hard else "advisory", "paired": packet["paired"],
                "baseline": {state: 0 for state in STATES}, "candidate": {state: 0 for state in STATES}})
            by_side = {}
            for label in (("a", "b") if packet["paired"] else ("a",)):
                side, state = labels[label], criterion[label]
                by_side[side] = state
                cohort[side][state] += 1
                raw_counts["criterion_states"][side][state] += 1
                detail = {"case_id": key[0], "attempt": key[1], "criterion_id": criterion_id, "side": side,
                          "severity": cohort["severity"], "evidence": criterion["evidence"][label], "disposition": final["state"]}
                if state == "failed":
                    (failures if hard else advisory).append(detail)
                if state == "not-run":
                    not_run.append(detail)
                    review_complete = False
                if suite == "boundary" and side == "candidate" and state != "passed":
                    boundary_pass = False
    count_failures, always_pass = [], []
    for cohort in counts.values():
        if not cohort["paired"] or cohort["severity"] == "advisory":
            continue
        if cohort["candidate"]["failed"] > cohort["baseline"]["failed"]:
            count_failures.append(cohort)
        if cohort["baseline"]["passed"] == 3 and cohort["candidate"]["failed"]:
            always_pass.append(cohort)
    gates = {"captures_complete": captures_complete and raw_counts["capture_slots"] == 798,
             "reviews_complete": review_complete and len(reviews) == 411,
             "adjudications_complete": adjudication_complete,
             "all_boundary_checks_pass": boundary_pass,
             "no_new_candidate_contract_failures": not unresolved_new,
             "candidate_per_criterion_failures_not_above_baseline": not count_failures,
             "baseline_always_pass_protected": not always_pass}
    return {"reviewer_kind": "ai", "assessment": "separate AI-reviewed migration assessment, not legacy human/phase acceptance",
            "accepted": all(gates.values()), "gates": gates, "raw_counts": raw_counts,
            "criterion_counts": sorted(counts.values(), key=lambda row: (row["case_id"], row["criterion_id"])),
            "failures": failures, "not_run": not_run, "capture_failures": capture_failures, "advisory_preferences": advisory,
            "new_candidate_contract_failures": unresolved_new, "excess_candidate_failures": count_failures,
            "baseline_always_pass_violations": always_pass, "dispositions": dispositions,
            "preexisting_baseline_failures": [item for item in failures if item["side"] == "baseline"],
            "blinding_limits": BLINDING_LIMITS,
            "limitations": ["Prompt-authoring review, not rendered-media quality", "Not proof of native host automatic selection",
                            "Read-only tools and declared local access are not an OS sandbox",
                            "Legacy mechanical evaluation must be run separately; no AI judgments enter --reviews"]}


def retain_preparation(packets, mappings, out, corpus):
    provenance = out / "provenance"
    provenance.mkdir()
    for name in ("review_split.py", "reviewer-system.txt"):
        shutil.copyfile(EVALS / name, provenance / name)
    shutil.copyfile(corpus["inputs"] / "omp-config.json", provenance / "omp-config.json")
    fixtures = out / "fixtures"
    fixtures.mkdir()
    for name, checksum in corpus["manifest"]["fixtures"].items():
        target = fixtures / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(corpus["inputs"] / "fixtures" / name, target)
        if rb.digest(target) != checksum:
            raise ReviewError(f"fixture changed after preflight: {name}")
    for item in packets:
        packet = item["packet"]
        directory = out / "packets" / packet["case_id"] / f"attempt-{packet['attempt']}"
        directory.mkdir(parents=True)
        rb.save_json(directory / "packet.json", packet)
        item["packet_path"] = (directory / "packet.json").relative_to(out).as_posix()
        item["packet_sha256"] = rb.digest(directory / "packet.json")
    rb.save_json(out / "label-map.json", mappings)
    rb.freeze_snapshot(provenance)
    rb.freeze_snapshot(fixtures)
    rb.freeze_snapshot(out / "packets")


def failed_review(packet, destination, error):
    """Retain operational preparation/runner failures without a replacement."""
    destination.mkdir(parents=True, exist_ok=True)
    result = {"case_id": packet["case_id"], "attempt": packet["attempt"], "reviewer_kind": "ai",
              "mode": "adjudication" if "alleged_review" in packet else "review", "valid": False,
              "judgment": not_run_judgment(packet, error), "parsed_output": None, "validation_errors": [error],
              "execution": {"status": "error", "exit_code": None, "error": error},
              "model_metadata": review_metadata([]),
              "raw_checksums": {path.name: rb.digest(path) for path in destination.iterdir() if path.is_file() and path.name != "review.json"}}
    rb.save_json(destination / "review.json", result)
    rb.freeze_snapshot(destination)
    return result


def execute_wave(items, out, scratch, system_file, config_file, timeout, jobs, adjudication=False):
    results = {}
    group = "adjudications" if adjudication else "reviews"
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = {}
        for item in items:
            packet = item["packet"]
            destination = out / group / packet["case_id"] / f"attempt-{packet['attempt']}"
            futures[pool.submit(run_reviewer, packet, destination, scratch, system_file, config_file, timeout)] = packet, destination
        for future in concurrent.futures.as_completed(futures):
            packet, destination = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                result = failed_review(packet, destination, f"review runner failure: {type(exc).__name__}: {exc}")
            key = packet["case_id"], packet["attempt"]
            results[key] = result
            print(json.dumps({"mode": group, "case_id": key[0], "attempt": key[1], "valid": result["valid"], "status": result["execution"]["status"]}), flush=True)
    return results


def adjudication_packet(item, packets, mappings, first):
    """Align histories to this packet's labels without naming either side."""
    packet = item["packet"]
    mapping = {(row["case_id"], row["attempt"]): row for row in mappings}
    current = mapping[(packet["case_id"], packet["attempt"])]
    history = {"a": [], "b": [] if packet["paired"] else None}
    for other in packets:
        evidence = other["packet"]
        if evidence["case_id"] != packet["case_id"]:
            continue
        labels = mapping[(evidence["case_id"], evidence["attempt"])]
        for label in (("a", "b") if packet["paired"] else ("a",)):
            history_label = "a" if labels["a"] == current[label] else "b"
            history[label].append({"attempt": evidence["attempt"], "output": evidence["outputs"][history_label]})
    if any([row["attempt"] for row in history[label]] != [1, 2, 3] for label in (("a", "b") if packet["paired"] else ("a",))):
        raise ReviewError("adjudication requires all three anonymized repetitions")
    return {**packet, "alleged_review": first["judgment"], "review_mode": "independent-adjudication", "repetition_evidence": history}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--boundary-results", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=900, help="Fresh reviewer deadline in seconds (default: 900); no retries")
    parser.add_argument("--jobs", type=int, default=3)
    args = parser.parse_args(argv)
    if args.timeout <= 0 or args.jobs <= 0:
        parser.error("--timeout and --jobs must be positive")
    if args.out.exists() or args.out.is_symlink():
        parser.error(f"--out must not exist: {args.out}")
    try:
        corpus, boundary = preflight(args.results, args.boundary_results)
        packets, mappings = build_packets(corpus, boundary)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    out = args.out.absolute()
    out.mkdir(parents=True, exist_ok=False)
    try:
        retain_preparation(packets, mappings, out, corpus)
    except (ValueError, OSError) as exc:
        rb.save_json(out / "preparation-error.json", {"error": str(exc), "paid_reviews_started": False})
        parser.error(str(exc))
    version, version_error = rs._version()
    manifest = {"kind": "independent-blinded-ai-split-review", "created_at": datetime.now(timezone.utc).isoformat(),
                "reviewer_kind": "ai", "model_requested": rb.MODEL, "reasoning_requested": "high",
                "results": str(corpus["root"]), "boundary_results": str(boundary["root"]),
                "capture_manifest_hashes": {"corpus": rb.digest(corpus["root"] / "manifest.json"), "boundary": rb.digest(boundary["root"] / "manifest.json")},
                "baseline_revision": corpus["manifest"]["baseline_revision"], "candidate_revision": corpus["manifest"]["candidate_revision"],
                "expected_packets": 411, "expected_capture_slots": 798, "jobs": args.jobs, "timeout_seconds": args.timeout,
                "omp_version": version, "omp_version_error": version_error,
                "tools_requested": ["read", "grep", "glob"], "permissions": "declared local read-only tool access; not an OS sandbox",
                "retry_policy": "none; fresh sessions, no resume/replacements/best-of selection",
                "label_policy": "random.Random(0), sorted (case_id, attempt); label-map.json outside packets/raw sessions",
                "blinding_limits": BLINDING_LIMITS,
                "provenance_files": rb.source_manifest(out / "provenance"),
                "packets": [{"case_id": item["packet"]["case_id"], "attempt": item["packet"]["attempt"], "suite": item["suite"],
                             "path": item["packet_path"], "sha256": item["packet_sha256"]} for item in packets],
                "provider_metadata": review_metadata([]), "acceptance": "not assessed"}
    rb.save_json(out / "manifest.json", manifest)
    system_file, config_file = out / "provenance/reviewer-system.txt", out / "provenance/omp-config.json"
    with tempfile.TemporaryDirectory(prefix="scenario-maker-independent-review-") as temporary:
        scratch = Path(temporary)
        reviews = execute_wave(packets, out, scratch / "initial", system_file, config_file, args.timeout, args.jobs)
        allegations = []
        for item in packets:
            packet = item["packet"]
            first = reviews[(packet["case_id"], packet["attempt"])]
            if first["valid"] and needs_adjudication(first["judgment"], packet):
                independent_packet = adjudication_packet(item, packets, mappings, first)
                path = out / "adjudication-packets" / packet["case_id"] / f"attempt-{packet['attempt']}"
                path.mkdir(parents=True)
                rb.save_json(path / "packet.json", independent_packet)
                rb.freeze_snapshot(path)
                allegations.append({**item, "packet": independent_packet, "adjudication_packet_path": (path / "packet.json").relative_to(out).as_posix(),
                                    "adjudication_packet_sha256": rb.digest(path / "packet.json")})
        adjudications = execute_wave(allegations, out, scratch / "adjudication", system_file, config_file, args.timeout, args.jobs, adjudication=True)
    summary = aggregate(packets, mappings, reviews, adjudications)
    if version_error:
        summary["gates"]["review_runtime_provenance_recorded"] = False
        summary["accepted"] = False
    manifest.update(finished_at=datetime.now(timezone.utc).isoformat(), acceptance="passed" if summary["accepted"] else "blocked",
                    reviews=[{"case_id": key[0], "attempt": key[1], "path": f"reviews/{key[0]}/attempt-{key[1]}/review.json",
                              "sha256": rb.digest(out / f"reviews/{key[0]}/attempt-{key[1]}/review.json"), "valid": value["valid"]} for key, value in sorted(reviews.items())],
                    adjudications=[{"case_id": key[0], "attempt": key[1], "path": f"adjudications/{key[0]}/attempt-{key[1]}/review.json",
                                    "sha256": rb.digest(out / f"adjudications/{key[0]}/attempt-{key[1]}/review.json"), "valid": value["valid"]} for key, value in sorted(adjudications.items())],
                    adjudication_packets=[{"case_id": item["packet"]["case_id"], "attempt": item["packet"]["attempt"], "path": item["adjudication_packet_path"],
                                           "sha256": item["adjudication_packet_sha256"]} for item in allegations])
    rb.save_json(out / "summary.json", summary)
    rb.save_json(out / "manifest.json", manifest)
    rb.freeze_snapshot(out)
    return 0 if summary["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
