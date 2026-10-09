#!/usr/bin/env python3
"""Measure ordinary source-instruction bytes and independently inspect split traces.

No model calls, token estimates, semantic review, or host-selection claims are made.
An absent or incomplete corpus/boundary capture cannot pass the trace gate.
"""
import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import shlex

import run_baseline as rb
import run_split as rs

COMMON = (
    "SKILL.md", "references/routing.md", "references/output-contracts.md",
    "references/scene-composition.md", "references/constraints-and-revisions.md",
    "references/prompt-types.md",
)
CATALOG = "references/model-prompts.md"
VIDEO = "references/video-prompts.md"
PROFILES = {skill: paths[0] for skill, paths in rs.MODEL_FILES.items() if skill != "scenario-maker"}
GENERIC_TARGETS = {
    "case-10": (PROFILES["scenario-maker-sdxl"], PROFILES["scenario-maker-krea-2"]),
    "p4-dev-10": (PROFILES["scenario-maker-krea-2"],),
    "split-compare": (PROFILES["scenario-maker-sdxl"], PROFILES["scenario-maker-pony"], PROFILES["scenario-maker-minimax-h3"]),
    "split-shared": (PROFILES["scenario-maker-sdxl"], PROFILES["scenario-maker-krea-2"]),
    "split-explicit-generic": (PROFILES["scenario-maker-minimax-h3"],),
}
# These are hints for inspecting observed consultation, not a semantic classifier or
# a declaration that either complete guide is mandatory for every matching request.
GUIDE_HINTS = {
    "official examples": r"official.{0,20}example",
    "extended camera": r"optical zoom|camera truck|dolly|camera movement",
    "vocal events": r"voiceover|says exactly|spoken line|singing|narrator|timbre|dialogue",
    "cross-cut": r"across.{0,15}cut|cross.cut|uninterrupted|scenetrans|interrup",
    "visible text": r"sign.{0,30}read|lettering|visible text",
    "sound placement": r"audience.only|diegetic|room tone|soundscape",
    "multi-reference / storyboard": r"picture [2-9]|video [1-3]|storyboard|composition and order",
    "copied / referenced audio": r"audio [1-3]|reuse.{0,30}(?:audio|soundtrack|score)|fully.copy|partially.copy",
    "one-image anchor": r"FL2VA|I2VA|one.opening.image|opening image",
}
SELECTOR = re.compile(r":(?=(?:raw|img|conflicts|[0-9,-]))")
REFERENCE_PATH = re.compile(r"(?:[^\s\"'`;()]*[/\\])?references[/\\][^\s\"'`;()]+")


def _json(path):
    value = rs._json(rs._text(path), path)
    if not isinstance(value, dict):
        raise rs.InputError(f"{path}: an object is required")
    return value


def _descriptor(root, name):
    path, checksum = rs._file(root, name, "instruction source")
    return {"path": name, "bytes": path.stat().st_size, "sha256": checksum}


def _description(root, skill):
    path, checksum = rs._file(root, "SKILL.md", "catalog description")
    lines = path.read_bytes().splitlines(keepends=True)
    if not lines or lines[0].strip() != b"---":
        raise rs.InputError(f"{path}: YAML frontmatter is required")
    values = []
    for index, line in enumerate(lines[1:], 1):
        if line.strip() == b"---":
            break
        if line.startswith(b"description:"):
            value = line[len(b"description:"):].lstrip(b" \t").rstrip(b"\r\n")
            if value in (b"|", b">", b"|-", b">-", b"|+", b">+"):
                body = []
                for following in lines[index + 1:]:
                    if following.strip() and not following.startswith((b" ", b"\t")):
                        break
                    body.append(following)
                value += b"\n" + b"".join(body)
            values.append(value)
    else:
        raise rs.InputError(f"{path}: unterminated YAML frontmatter")
    if len(values) != 1 or not values[0].strip():
        raise rs.InputError(f"{path}: exactly one nonempty description is required")
    value = values[0]
    return {"skill": skill, "path": "SKILL.md", "skill_md_sha256": checksum,
            "description_source": value.decode("utf-8"), "description_bytes": len(value),
            "description_sha256": hashlib.sha256(value).hexdigest()}


def _ordinary_files(skill, baseline):
    names = list(COMMON)
    if skill == "scenario-maker":
        return names
    if skill == "scenario-maker-wan":
        # The frozen entry does not route Wan through the old image/H3 index.
        # Its entire Wan contract is in shared video, not a nonexistent profile.
        return names + ([VIDEO] if baseline else [PROFILES[skill], VIDEO])
    names.extend(([CATALOG, PROFILES[skill]] if baseline else [PROFILES[skill]]))
    if skill == "scenario-maker-minimax-h3":
        names.append(VIDEO)
    return names


def _path_bytes(root, names):
    files, unique = [], {}
    for name in names:
        row = _descriptor(root, name)
        key = (row["sha256"], row["bytes"])
        row["counted"] = key not in unique
        row["identical_to"] = unique.get(key)
        unique.setdefault(key, name)
        files.append(row)
    return {"root": str(root), "files": files,
            "instruction_bytes": sum(row["bytes"] for row in files if row["counted"])}


def measure_bytes(baseline, candidate_root):
    baseline = rs._root(baseline, "frozen baseline")
    candidate_root = rs._root(candidate_root, "candidate root")
    roots = {skill: rs._root(candidate_root / skill, skill) for skill in rs.SKILLS}
    sources = {"baseline": rs._source_files(baseline, baseline=True),
               "candidate": {skill: rs._source_files(root, skill=skill) for skill, root in roots.items()}}
    old_description = _description(baseline, "scenario-maker")
    new_descriptions = [_description(roots[skill], skill) for skill in rs.SKILLS]
    installed = sum(row["description_bytes"] for row in new_descriptions)
    descriptions = {row["skill"]: row["description_bytes"] for row in new_descriptions}
    paths = []
    for skill in rs.SKILLS:
        old = _path_bytes(baseline, _ordinary_files(skill, True))
        new = _path_bytes(roots[skill], _ordinary_files(skill, False))
        old_total = old["instruction_bytes"] + old_description["description_bytes"]
        full_total = new["instruction_bytes"] + installed
        standalone_total = new["instruction_bytes"] + descriptions[skill]
        paths.append({
            "path": "generic-no-model" if skill == "scenario-maker" else skill,
            "selected_skill": skill, "baseline": old, "candidate": new,
            "baseline_one_description_total_bytes": old_total,
            "candidate_eight_descriptions_total_bytes": full_total,
            "candidate_standalone_description_total_bytes": standalone_total,
            "instruction_reduction_bytes": old["instruction_bytes"] - new["instruction_bytes"],
            "full_catalog_reduction_bytes": old_total - full_total,
            "standalone_reduction_bytes": old_total - standalone_total,
            "lower_instruction_bytes": new["instruction_bytes"] < old["instruction_bytes"],
            "lower_with_full_catalog": full_total < old_total,
            "lower_standalone": standalone_total < old_total,
        })
    failing = [row["path"] for row in paths if not all(row[key] for key in
               ("lower_instruction_bytes", "lower_with_full_catalog", "lower_standalone"))]
    guides = {}
    for side, root in (("baseline", baseline), ("candidate", roots["scenario-maker-minimax-h3"])):
        profile = PROFILES["scenario-maker-minimax-h3"]
        text = rs._text(root / profile)
        section = re.search(r"^## Official Guides[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
        guides[side] = {"profile": _descriptor(root, profile),
                        "conditional_contract_source": section.group(0) if section else None,
                        "excluded_from_ordinary_paths": [_descriptor(root, name) for name in rs.H3_GUIDES]}
        if section is None:
            raise rs.InputError(f"{root / profile}: conditional official-guide contract is missing")
    return {
        "unit": "bytes", "paths": paths, "status": "failed" if failing else "passed",
        "failing_paths": failing,
        "catalog": {"baseline_descriptions": [old_description], "baseline_description_bytes": old_description["description_bytes"],
                    "candidate_descriptions": new_descriptions, "candidate_full_description_bytes": installed},
        "conditional_h3_guides": guides,
        "accounting": [
            "Exact source-file bytes (including frontmatter and line endings), not tokens or delivered tool-result bytes.",
            "An ordinary path reads entry, four mandatory common references, prompt-types, and only its selected model/video rules.",
            "Five old image paths read catalog plus profile; old H3 reads catalog, profile, video; old Wan reads shared video only.",
            "Identical complete file content is counted once per path, keyed by SHA-256 and byte length.",
            "Catalog overhead counts description value source bytes, excluding the key/separator and final line ending; block scalar source is not YAML-decoded.",
            "Discovery descriptions and entry-file reads are separate context surfaces; all eight installed description entries count, even though the selected entry also includes its description.",
            "Optional characters, tags, wildcard references, utilities, data, and H3 official guides are excluded from ordinary paths, not removed from packages.",
            "All eight paths must be strictly smaller both before and after full eight-description overhead; standalone totals are also reported and checked.",
        ],
    }, sources


def _normalize_path(value, cwd, tool_cwd=None):
    """Retain the selector while resolving dot segments against actual capture cwd."""
    if not isinstance(value, str) or not value:
        raise rs.InputError("read/search path is not a nonempty string")
    match = SELECTOR.search(value)
    path, selector = (value[:match.start()], value[match.start():]) if match else (value, "")
    if "://" in path and not path.startswith("file://"):
        return {"original_path": value, "path": path, "selector": selector, "local": False, "selected_skill_relative": None}
    path = path.removeprefix("file://").replace("\\", "/")
    if not isinstance(cwd, str) or not os.path.isabs(cwd):
        return {"original_path": value, "path": path, "selector": selector, "local": None,
                "selected_skill_relative": None, "workspace_normalization": "unavailable"}
    base = os.path.normpath(cwd)
    if tool_cwd:
        base = os.path.normpath(tool_cwd if os.path.isabs(tool_cwd) else os.path.join(base, tool_cwd))
    resolved = os.path.normpath(path if os.path.isabs(path) else os.path.join(base, path))
    workspace = os.path.normpath(cwd)
    selected = os.path.join(workspace, "selected-skill")
    relative = os.path.relpath(resolved, selected)
    inside = relative != ".." and not relative.startswith("../")
    workspace_relative = os.path.relpath(resolved, workspace)
    normalized = ("selected-skill" + ("/" + relative if relative != "." else "")) if inside else (
        workspace_relative if workspace_relative != ".." and not workspace_relative.startswith("../") else resolved)
    return {"original_path": value, "path": normalized, "selector": selector, "local": True,
            "selected_skill_relative": relative if inside else None}


def _read_paths(args):
    value = args.get("path", args.get("paths"))
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and value and all(isinstance(item, str) for item in value):
        return value
    raise rs.InputError("read tool_execution_start has no usable path argument")


def _resource(path):
    value = path.replace("\\", "/")
    match = re.search(r"(?:^|/)references/(.+)$", value)
    return "references/" + match.group(1) if match else None


def _generator_activation(command):
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        tokens = command.split()
    segment = []
    for token in tokens:
        if token in {"&&", ";", "|", "||", "&"}:
            segment = []
            continue
        if token.endswith("character_generator.py"):
            if not segment:
                return "direct character_generator.py command"
            if any(re.fullmatch(r"(?:.*/)?(?:python(?:3(?:\.\d+)?)?|pypy3?)", item) for item in segment):
                return "Python character_generator.py invocation"
        segment.append(token)
    if any(re.fullmatch(r"(?:.*/)?(?:python(?:3(?:\.\d+)?)?|pypy3?)", item) for item in tokens):
        if re.search(r"\b-m\s+(?:scripts\.)?character_generator\b", command):
            return "character_generator module invocation"
        if "-c" in tokens and re.search(r"\b(?:import|from)\s+(?:scripts\.)?character_generator\b", command):
            return "character_generator module import in Python command"
    return None


def _random_authorization(request):
    # Requests, not expectations or Wild/Unbound labels, are the authority.
    for clause in re.split(r"[.!?;\n]", request):
        if re.search(r"\b(?:random(?:ized|ised|ize|ise|ly)?|shuffle)\b", clause, re.I) and re.search(r"character|profile|design|batch", clause, re.I):
            if not re.search(r"\b(?:no|not|never|without|don't)\b", clause, re.I):
                return clause.strip()
    return None


def _trace_events(path):
    events, errors = [], []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                event = rs._json(line, f"{path}:{line_number}")
                if not isinstance(event, dict):
                    raise rs.InputError("event is not an object")
                events.append((line_number, event))
            except ValueError as exc:
                errors.append(str(exc))
    return events, errors


def inspect_trace(record, case, events, sources):
    side, skill = record["comparison_side"], record["selected_skill"]
    errors = []
    cwd = record.get("cwd")
    if not isinstance(cwd, str) or not os.path.isabs(cwd):
        errors.append("attempt has no absolute workspace cwd; path normalization is unavailable")
    ends = {event.get("toolCallId"): event for _, event in events if event.get("type") == "tool_execution_end"}
    starts = [(line, event) for line, event in events if event.get("type") == "tool_execution_start"]
    start_ids = [event.get("toolCallId") for _, event in starts]
    if any(not isinstance(value, str) or not value for value in start_ids) or len(start_ids) != len(set(start_ids)):
        errors.append("missing/duplicate tool_execution_start IDs")
    end_ids = [event.get("toolCallId") for _, event in events if event.get("type") == "tool_execution_end"]
    if len(end_ids) != len(set(end_ids)) or set(start_ids) != set(end_ids):
        errors.append("tool start/end coverage is incomplete or duplicated")
    if not any(event.get("type") == "agent_end" and event.get("isTerminal") is True for _, event in events):
        errors.append("terminal agent_end event is absent")
    reads, accesses, utilities, generators, usage = [], [], [], [], []
    for line, event in starts:
        tool = str(event.get("toolName", "")).rsplit(".", 1)[-1]
        args = event.get("args")
        if not isinstance(args, dict):
            errors.append(f"trace line {line}: tool args are not an object")
            continue
        ended = ends.get(event.get("toolCallId"), {})
        failed = ended.get("isError") is True or (isinstance(ended.get("result"), dict) and ended["result"].get("isError") is True)
        action = {"trace_line": line, "tool_call_id": event.get("toolCallId"), "tool": tool,
                  "args": args, "ended": bool(ended), "is_error": failed}
        if tool in {"read", "grep", "glob"}:
            try:
                paths = _read_paths(args) if tool == "read" else ([args["path"]] if isinstance(args.get("path"), str) else [])
                if tool != "read":
                    paths = [item for value in paths for item in value.split(";") if item]
                for value in paths:
                    normalized = _normalize_path(value, cwd, args.get("cwd"))
                    row = {**action, **normalized}
                    if tool == "read":
                        reads.append(row)
                    if _resource(normalized["path"]):
                        accesses.append(row)
            except (ValueError, TypeError) as exc:
                errors.append(f"trace line {line}: {exc}")
        if tool == "bash":
            command = args.get("command")
            if not isinstance(command, str):
                errors.append(f"trace line {line}: bash command is missing")
                continue
            actual_cwd = args.get("cwd") or cwd
            normalized_cwd = _normalize_path(actual_cwd, cwd)["path"] if actual_cwd else None
            if "danbooru_lookup" in command or "character_generator" in command:
                utilities.append({**action, "normalized_cwd": normalized_cwd})
            activation = _generator_activation(command)
            if activation:
                generators.append({**action, "normalized_cwd": normalized_cwd, "detection": activation})
            # Utility scripts read their own data internally; that is not a prompt
            # reference read. Literal reference-reading shell commands are retained.
            if re.search(r"\b(?:cat|sed|head|tail|less|more|grep|rg)\b|read_text|read_bytes|\bopen\s*\(", command):
                for value in REFERENCE_PATH.findall(command):
                    normalized = _normalize_path(value, cwd, args.get("cwd"))
                    accesses.append({**action, **normalized, "shell_path_detection": "literal reference path in reading command"})
    for line, event in events:
        message = event.get("message")
        if event.get("type") == "message_end" and isinstance(message, dict) and message.get("role") == "assistant" and isinstance(message.get("usage"), dict):
            usage.append({"trace_line": line, "provider": message.get("provider"), "model": message.get("model"),
                          "api": message.get("api"), "usage": message["usage"]})
    target_skill = case["selected_skill"]
    allowed = set(GENERIC_TARGETS.get(case["id"], ())) if target_skill == "scenario-maker" else {PROFILES[target_skill]}
    h3 = PROFILES["scenario-maker-minimax-h3"] in allowed
    violations = []
    for row in accesses:
        resource = _resource(row["path"])
        catalog = resource == CATALOG
        model = resource and resource.startswith("references/models/")
        if side != "candidate" or row["tool"] == "glob":
            continue
        local = row["selected_skill_relative"] == resource
        reason = None
        if catalog and (skill != "scenario-maker" or not allowed):
            reason = "specialist all-model catalog access" if skill != "scenario-maker" else "unnamed generic catalog access"
        elif model and resource not in allowed and not (h3 and resource in rs.H3_GUIDES):
            reason = "unrelated model resource access" if allowed else "unnamed generic model resource access"
        elif (catalog or model) and not local:
            reason = "model resource read outside the isolated selected package"
        if reason:
            violations.append({"rule": reason, "action": row})
    if side == "candidate" and case["id"] == "split-wrong-family":
        for row in reads:
            if "krea" in row["original_path"].lower():
                violations.append({"rule": "wrong-family guard reads unavailable Krea guidance", "action": row})
        for row in accesses:
            if row["tool"] != "read" and "krea" in row["original_path"].lower():
                violations.append({"rule": "wrong-family guard accesses unavailable Krea guidance", "action": row})
    authorization = _random_authorization(case["request"])
    unexpected = [] if authorization else generators
    if side == "candidate":
        violations.extend({"rule": "unexpected character_generator activation on nonrandom request", "action": row} for row in unexpected)
    successful_local = {row["selected_skill_relative"] for row in accesses if row["tool"] != "glob" and row["ended"] and not row["is_error"]}
    required_models = set(allowed) if case["id"] != "split-wrong-family" else set()
    if side == "baseline":
        required_models.discard(PROFILES["scenario-maker-wan"])
    if required_models and (target_skill == "scenario-maker" or side == "baseline"):
        required_models.add(CATALOG)
    if side == "candidate":
        for name in sorted(required_models - successful_local):
            violations.append({"rule": "selected local model contract not observed", "path": name})
    source_files = sources["baseline"] if side == "baseline" else sources["candidate"][skill]
    observed_files = sorted({row["selected_skill_relative"] for row in accesses if row["selected_skill_relative"] in source_files})
    guides = [row for row in accesses if _resource(row["path"]) in rs.H3_GUIDES]
    hints = [{"feature": name, "request_excerpt": match.group(0)} for name, pattern in GUIDE_HINTS.items()
             if (match := re.search(pattern, case["request"], re.I))] if h3 else []
    return {
        "case_id": case["id"], "attempt": record["attempt"], "side": side, "selected_skill": skill,
        "case_source": case["case_source"], "request": case["request"],
        "read_actions": reads, "actual_reference_reads": [row for row in reads if _resource(row["path"])],
        "reference_accesses": accesses, "distinct_local_reference_paths": observed_files,
        "ordinary_contract_files_not_observed": sorted(set(_ordinary_files(case["selected_skill"], side == "baseline")) - successful_local - {"SKILL.md"}),
        "allowed_candidate_profiles": sorted(allowed), "required_model_contracts": sorted(required_models),
        "h3_guides": {"conditional": True, "automatically_required": False, "request_feature_hints": hints,
                      "actual_accesses": guides, "condition_assessment": "semantic judgment not inferred from hints or read counts"},
        "utility_actions": utilities, "character_generator_actions": generators,
        "randomized_character_authorization_clause": authorization,
        "unexpected_character_generator_actions": unexpected,
        "usage_messages": usage, "trace_errors": errors, "violations": violations,
    }


def _verify_files(root, declared, label):
    if not isinstance(declared, dict):
        raise rs.InputError(f"{label}: hash mapping is missing")
    for name, expected in declared.items():
        _, actual = rs._file(root, name, label)
        if not isinstance(expected, str) or actual != expected:
            raise rs.InputError(f"{label}: hash mismatch for {root / name}")


def _attempt_location(suite, case, slot):
    group = "boundary" if suite == "boundary" else "formal" if case["case_source"] == "cases.jsonl" else "probes"
    return f"{group}/{slot['side']}/{case['id']}/attempt-{slot['attempt']}"


def _verify_attempt(root, manifest, case, slot, listed):
    name = _attempt_location(manifest["suite"], case, slot) + "/attempt.json"
    if listed.get("attempt_manifest") != name:
        raise rs.InputError(f"attempt manifest path differs from scheduled slot: {name}")
    path, checksum = rs._file(root, name, "attempt manifest")
    if checksum != listed.get("attempt_manifest_sha256"):
        raise rs.InputError(f"attempt manifest hash mismatch: {name}")
    record = _json(path)
    if record != {key: value for key, value in listed.items() if key != "attempt_manifest_sha256"}:
        raise rs.InputError(f"manifest attempt differs from immutable attempt.json: {name}")
    selected = "scenario-maker" if slot["side"] == "baseline" else case["selected_skill"]
    files = manifest["source_manifests"]["baseline"] if slot["side"] == "baseline" else manifest["source_manifests"]["candidate"][selected]
    for key, expected in {"case_id": case["id"], "attempt": slot["attempt"], "comparison_side": slot["side"],
                          "selected_skill": selected, "selected_skill_sha256": rb.manifest_identity(files),
                          "case_source": case["case_source"], "revision": manifest[slot["side"] + "_revision"],
                          "model_requested": manifest["model_requested"], "reasoning_requested": manifest["reasoning_requested"]}.items():
        if record.get(key) != expected:
            raise rs.InputError(f"{name}: inconsistent {key}")
    evidence = path.parent
    _verify_files(evidence, record.get("raw_checksums"), "raw evidence")
    actual_raw = {item.name for item in evidence.iterdir() if item.is_file() and item.name != "attempt.json"}
    if actual_raw != set(record["raw_checksums"]):
        raise rs.InputError(f"{name}: raw evidence file coverage differs from declared hashes")
    raw = record.get("raw")
    if not isinstance(raw, dict) or raw.get("trace") != "trace.jsonl":
        raise rs.InputError(f"{name}: trace declaration is missing or unexpected")
    for filename in raw.values():
        if filename is not None and filename not in record["raw_checksums"]:
            if record["execution"].get("status") == "completed" or (evidence / filename).exists():
                raise rs.InputError(f"{name}: unhashed raw file {filename!r}")
    prefix = "Use the explicitly selected Scenario Maker skill in ./selected-skill/SKILL.md.\n\n" + case["request"]
    if case["fixtures"]:
        prefix += "\n\nSupplied local fixtures: " + ", ".join("fixtures/" + value for value in case["fixtures"])
    if "request.txt" in record["raw_checksums"]:
        if rs._text(evidence / "request.txt") != prefix:
            raise rs.InputError(f"{name}: captured request differs from the frozen case")
    elif record["execution"].get("status") == "completed":
        raise rs.InputError(f"{name}: completed capture has no retained request")
    artifacts = record.get("artifacts")
    if not isinstance(artifacts, list):
        raise rs.InputError(f"{name}: artifact declarations are missing")
    stored_paths = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise rs.InputError(f"{name}: malformed artifact declaration")
        stored = artifact.get("stored_path")
        if not isinstance(stored, str) or not stored.startswith("artifacts/") or stored in stored_paths:
            raise rs.InputError(f"{name}: invalid/duplicate artifact path")
        stored_paths.add(stored)
        artifact_path, actual = rs._file(evidence, stored, "exported artifact")
        if actual != artifact.get("sha256") or artifact_path.stat().st_size != artifact.get("bytes"):
            raise rs.InputError(f"{name}: artifact hash/byte mismatch: {stored}")
    artifacts_root = evidence / "artifacts"
    actual_artifacts = {item.relative_to(evidence).as_posix() for item in rs._walk_source(artifacts_root)} if artifacts_root.exists() else set()
    if actual_artifacts != stored_paths:
        raise rs.InputError(f"{name}: exported artifact coverage differs from declared hashes")
    if record.get("model_metadata") != rs._model_metadata(record, evidence):
        raise rs.InputError(f"{name}: model metadata differs from captured context")
    return record, evidence


def assess_suite(path, suite, source_manifests):
    report = {"suite": suite, "root": str(path.absolute()), "integrity_status": "not-run", "complete": False,
              "integrity_errors": [], "incomplete_evidence": [], "attempts": [], "manifest_sha256": None}
    try:
        root = rs._root(path, suite + " results")
        manifest_path, manifest_hash = rs._file(root, "manifest.json", "capture manifest")
        report["manifest_sha256"] = manifest_hash
        manifest = _json(manifest_path)
        if manifest.get("kind") != "current-monolith-versus-model-split" or manifest.get("suite") != suite:
            raise rs.InputError(f"{manifest_path}: wrong capture kind or suite")
        snapshots = manifest.get("candidate_snapshots")
        if not isinstance(snapshots, dict) or set(snapshots) != set(rs.SKILLS):
            raise rs.InputError("manifest must declare all eight candidate snapshots")
        if snapshots != {skill: "snapshots/candidate/" + skill for skill in rs.SKILLS} or manifest.get("baseline_snapshot") != "snapshots/baseline":
            raise rs.InputError("snapshot paths differ from the runner layout")
        if manifest.get("evaluation_inputs") != "evaluation-inputs":
            raise rs.InputError("frozen evaluation input root differs from runner layout")
        checked = rs.preflight(root / manifest["baseline_snapshot"], root / "snapshots/candidate", suite, evals=root / "evaluation-inputs")
        actual_sources = {"baseline": checked["baseline_files"], "candidate": checked["candidate_files"]}
        if manifest.get("source_manifests") != actual_sources or actual_sources != source_manifests:
            raise rs.InputError("capture snapshots differ from declared or measured source manifests")
        expected_fields = {
            "baseline_revision": rb.manifest_identity(actual_sources["baseline"]),
            "candidate_revision": "split-sha256-" + rb.manifest_identity(actual_sources["candidate"]),
            "cases": checked["cases"], "schedule": checked["schedule"],
            "evaluation_files": checked["evaluation_files"], "fixtures": checked["fixture_files"],
            "route_ownership": checked["routes"], "attempts_per_case": 3, "expected_attempts": len(checked["schedule"]),
            "model_requested": rb.MODEL, "reasoning_requested": "high",
        }
        for key, expected in expected_fields.items():
            if manifest.get(key) != expected:
                raise rs.InputError(f"capture manifest has inconsistent {key}")
        report.update(candidate_revision=manifest["candidate_revision"], baseline_revision=manifest["baseline_revision"],
                      evaluation_files=manifest["evaluation_files"], fixtures=manifest["fixtures"],
                      expected_attempts=manifest["expected_attempts"], model_requested=manifest["model_requested"],
                      reasoning_requested=manifest["reasoning_requested"], omp_version=manifest.get("omp_version"))
        if not manifest.get("finished_at") or manifest.get("omp_version_error") or not manifest.get("omp_version"):
            report["incomplete_evidence"].append("capture run lacks completed execution provenance")
        listed = manifest.get("attempts", [])
        if not isinstance(listed, list):
            raise rs.InputError("manifest attempts must be a list")
        index = {}
        scheduled = {(slot["case_id"], slot["attempt"], slot["side"]) for slot in checked["schedule"]}
        for record in listed:
            if not isinstance(record, dict):
                raise rs.InputError("manifest attempt is not an object")
            key = (record.get("case_id"), record.get("attempt"), record.get("comparison_side"))
            if key not in scheduled or key in index:
                raise rs.InputError(f"duplicate/unscheduled attempt {key}")
            index[key] = record
        case_index = {case["id"]: case for case in checked["cases"]}
        for slot in checked["schedule"]:
            key = (slot["case_id"], slot["attempt"], slot["side"])
            if key not in index:
                report["incomplete_evidence"].append({"slot": slot, "reason": "missing attempt"})
                continue
            case = case_index[slot["case_id"]]
            try:
                record, evidence = _verify_attempt(root, manifest, case, slot, index[key])
                trace_path = evidence / record["raw"]["trace"]
                events, parse_errors = _trace_events(trace_path) if trace_path.is_file() else ([], ["missing trace.jsonl"])
                attempt = inspect_trace(record, case, events, actual_sources)
                attempt.update(attempt_manifest=index[key]["attempt_manifest"], attempt_manifest_sha256=index[key]["attempt_manifest_sha256"],
                               raw_checksums=record["raw_checksums"], execution=record["execution"],
                               model_metadata=record["model_metadata"])
                attempt["trace_errors"].extend(parse_errors)
                output = record["raw"].get("output")
                complete = (record["execution"].get("status") == "completed" and record.get("trace_complete") is True
                            and not record.get("evidence_errors") and not attempt["trace_errors"]
                            and output is not None and (evidence / output).stat().st_size > 0)
                attempt["complete"] = bool(complete)
                if not complete:
                    report["incomplete_evidence"].append({"slot": slot, "reason": "failed/partial execution, output, or trace", "trace_errors": attempt["trace_errors"]})
                report["attempts"].append(attempt)
            except (ValueError, OSError, KeyError, TypeError) as exc:
                report["integrity_errors"].append({"slot": slot, "error": str(exc)})
        report["integrity_status"] = "failed" if report["integrity_errors"] else "passed"
        report["complete"] = not report["integrity_errors"] and not report["incomplete_evidence"] and len(report["attempts"]) == len(scheduled)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        report["integrity_errors"].append(str(exc))
        report["integrity_status"] = "not-run" if isinstance(exc, (FileNotFoundError, NotADirectoryError)) or report["manifest_sha256"] is None else "failed"
    return report


def _numeric_usage(value, prefix=""):
    result = {}
    for name, item in value.items():
        key = prefix + name
        if isinstance(item, dict):
            result.update(_numeric_usage(item, key + "."))
        elif isinstance(item, (int, float)) and not isinstance(item, bool):
            result[key] = item
    return result


def aggregate_usage(suites):
    groups = {}
    available, missing = [], []
    for suite in suites:
        for attempt in suite["attempts"]:
            identity = {key: attempt[key] for key in ("case_id", "attempt", "side", "selected_skill")}
            identity["suite"] = suite["suite"]
            if not attempt["usage_messages"]:
                missing.append(identity)
            else:
                available.append(identity)
            for message in attempt["usage_messages"]:
                key = (attempt["side"], attempt["selected_skill"], message["provider"], message["model"], message["api"])
                if key not in groups:
                    groups[key] = {"side": key[0], "skill": key[1], "provider": key[2], "model": key[3], "api": key[4],
                                   "usage_messages": 0, "reported_numeric_totals": defaultdict(int)}
                row = groups[key]
                row["usage_messages"] += 1
                for field, value in _numeric_usage(message["usage"]).items():
                    row["reported_numeric_totals"][field] += value
    rows = []
    for key in sorted(groups, key=lambda value: tuple(str(part) for part in value)):
        row = groups[key]
        row["reported_numeric_totals"] = dict(sorted(row["reported_numeric_totals"].items()))
        rows.append(row)
    return {"status": "available" if available else "unknown", "by_model_side_skill": rows,
            "attempts_with_usage": available, "attempts_without_usage": missing,
            "source": "actual assistant message_end.usage only; stream updates, turn_end and agent_end copies are not counted",
            "interpretation": "Provider field names and cost fields are retained, not converted or used to prove context savings; totals include the complete capture conversation, tools/output and cache accounting, not just instructions."}


def assess_traces(results, boundary_results, sources):
    suites = []
    absent = []
    for path, suite in ((results, "corpus"), (boundary_results, "boundary")):
        if path is None:
            absent.append(suite)
        else:
            suites.append(assess_suite(path, suite, sources))
    consistency_errors = []
    if len(suites) == 2 and all("evaluation_files" in suite for suite in suites):
        for key in ("baseline_revision", "candidate_revision", "evaluation_files", "fixtures", "model_requested", "reasoning_requested", "omp_version"):
            if suites[0][key] != suites[1][key]:
                consistency_errors.append(f"corpus/boundary {key} differs")
    violations = [{"suite": suite["suite"], **{key: attempt[key] for key in ("case_id", "attempt", "side", "selected_skill")},
                   **violation} for suite in suites for attempt in suite["attempts"] for violation in attempt["violations"]]
    all_complete = not absent and len(suites) == 2 and all(suite["complete"] for suite in suites) and not consistency_errors
    integrity_failed = any(suite["integrity_status"] == "failed" for suite in suites) or bool(consistency_errors)
    status = "not-run" if not all_complete else "failed" if violations else "passed"
    return {
        "status": status, "captures_complete": all_complete, "absent_suites": absent,
        "integrity_status": "failed" if integrity_failed else "passed" if all_complete else "not-run",
        "consistency_errors": consistency_errors, "observed_rules_status": "failed" if violations else "passed" if all_complete else "not-run",
        "violations": violations, "suites": suites,
        "unexpected_character_generator": [{"suite": suite["suite"], **{key: attempt[key] for key in ("case_id", "attempt", "side", "selected_skill")},
                                             "actions": attempt["unexpected_character_generator_actions"]}
                                            for suite in suites for attempt in suite["attempts"] if attempt["unexpected_character_generator_actions"]],
        "rules": [
            "Unnamed generic candidate requests read no model catalog/profile/guide; the five declared named-generic exceptions read only their relevant local profiles and catalog.",
            "Specialists access only their own local profile (and H3's conditional guides); no unrelated profiles or all-model catalog, including external/sibling resources.",
            "Selected local profiles/catalog must be observed in completed candidate traces, except the wrong-family guard which must never read Krea guidance.",
            "H3 guide consultation is visible per attempt with request-feature hints; neither guide is made automatically mandatory by this measurement.",
            "Unexpected character_generator execution/import on a nonrandom request is separately reported on both sides; candidate activation blocks the trace gate.",
            "Read selectors and workspace-relative paths are normalized without deleting original arguments, calls, failed reads, or external paths.",
            "Both complete suites, unchanged frozen inputs/snapshots, every scheduled attempt, and verified attempt/raw/artifact hashes are required for a trace pass.",
        ],
        "limits": [
            "Instruction source bytes are not exact bytes delivered by ranged, truncated, rendered or repeated read results.",
            "Direct read/grep access and literal reference-reading shell commands are inspected; arbitrary dynamically computed shell/code reads cannot be fully reconstructed.",
            "Glob listings are retained but are not treated as reads of file contents or proof that a profile was consulted.",
            "Read presence does not prove understanding, output correctness, or all shared preservation semantics; independent semantic review remains required.",
            "Top-level manifest hashes are recorded here; internal consistency is verified, not an externally signed provenance chain.",
        ],
    }, aggregate_usage(suites)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--candidate-root", required=True, type=Path)
    parser.add_argument("--results", type=Path)
    parser.add_argument("--boundary-results", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.out.exists() or args.out.is_symlink():
        parser.error(f"--out must be a new JSON file: {args.out}")
    out = args.out.resolve(strict=False)
    for root in (args.baseline, args.results, args.boundary_results):
        if root is not None and out.is_relative_to(root.resolve(strict=False)):
            parser.error("--out must not be inside a snapshot or capture directory")
    for skill in rs.SKILLS:
        package = (args.candidate_root / skill).resolve(strict=False)
        if not out.is_relative_to(package):
            continue
        evidence = package / "evals" / "comparisons"
        if skill != "scenario-maker" or not out.is_relative_to(evidence):
            parser.error("--out must not modify a measured runtime package")
    try:
        byte_gate, sources = measure_bytes(args.baseline, args.candidate_root)
        trace_gate, usage = assess_traces(args.results, args.boundary_results, sources)
        report = {
            "kind": "scenario-maker-model-split-context-assessment", "schema_version": 1,
            "baseline": str(args.baseline.absolute()), "candidate_root": str(args.candidate_root.absolute()),
            "source_manifests": sources, "baseline_identity": rb.manifest_identity(sources["baseline"]),
            "candidate_identity": "split-sha256-" + rb.manifest_identity(sources["candidate"]),
            "measurement_script_sha256": rb.digest(Path(__file__).resolve()),
            "byte_gate": byte_gate, "trace_gate": trace_gate, "actual_usage": usage,
            "context_assessment": "failed" if "failed" in (byte_gate["status"], trace_gate["status"]) else
                                  "passed" if trace_gate["status"] == "passed" else "not-run",
            "semantic_migration_acceptance": "not assessed by byte/trace measurement",
            "host_automatic_skill_selection": "unverified; captures explicitly invoke an isolated package with host skills disabled",
            "limits": ["No tokens are inferred from source bytes.", "No model-backed captures or reviews are launched.",
                       "Smaller package/directory/entry alone is not context or prompt-quality acceptance.",
                       "Absent/failed/partial captures remain visible and cannot become a trace pass."],
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps({"out": str(out), "byte_gate": byte_gate["status"], "trace_gate": trace_gate["status"],
                      "context_assessment": report["context_assessment"]}, sort_keys=True))
    return 1 if report["context_assessment"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
