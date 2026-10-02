#!/usr/bin/env python3
"""Score Scenario Maker prompt-behavior captures without judging prompt semantics.

The evaluator recognizes only the mechanical checks declared by the Phase 1 case
schema. Semantic criteria remain ``not-run`` until an explicitly identified
human review is imported. Trace checks cover observable OMP tool-start events;
they do not prove that a shell command or hidden provider behavior was sandboxed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import random
import re
import shlex
import string
import sys
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

STATES = {"passed", "failed", "not-run"}
METHODS = {"mechanical", "maintainer"}
SEVERITIES = {"hard", "advisory"}
CHECK_TYPES = {"exact_text", "word_limit", "numbered_count", "export", "trace_policy"}
BASELINE_REVISION = "5fcc3d0eded83c6a9aaf472a1dc8d5ce24011d9d"
FORBIDDEN_TOOL_NAMES = {
    "agent",
    "browser",
    "completion",
    "generate_image",
    "generate_video",
    "image_generation",
    "judge",
    "task",
    "video_generation",
    "web_search",
    "skill",
    "switch_model",
    "use_skill",
}
FORBIDDEN_SHELL_COMMANDS = {
    "curl",
    "wget",
    "ssh",
    "scp",
    "omp",
    "openai",
}
LOCAL_FILE_COMMANDS = {"cat", "cp", "mkdir", "mv", "realpath", "touch", "wc"}
LIMITATIONS = [
    "Mechanical checks inspect captured final text/files only; they do not infer semantic preservation, exclusions, style, or relationships from keywords.",
    "Trace policy inspects observable OMP tool_execution_start events only. It is not an enforced shell sandbox and cannot establish hidden provider behavior.",
    "Unknown tool-event shapes and ambiguous shell commands are not-run; complete traces with observed forbidden tools/actions fail.",
    "Trace path checks recognize only selected-skill, fixtures, and outputs; direct raw Danbooru data access, URIs, and image ?q processing are prohibited.",
    "Human semantic passes require imported review records with human=true and a reviewer identifier beginning with 'human:'.",
]


class InputError(ValueError):
    pass


def _jsonl(path: Path) -> list[tuple[int, Any]]:
    rows: list[tuple[int, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    rows.append((number, json.loads(line)))
                except json.JSONDecodeError as exc:
                    raise InputError(f"{path}:{number}: invalid JSON: {exc.msg}") from exc
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc
    return rows


def _relative_path(value: Any, field: str) -> PurePosixPath:
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{field} must be a non-empty relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise InputError(f"{field} must stay beneath its declared root: {value!r}")
    return path


def _validate_check(check: Any, location: str) -> None:
    if not isinstance(check, dict) or set(check) - {"type", "value", "max", "count", "path", "lines"}:
        raise InputError(f"{location}: unsupported mechanical check fields")
    kind = check.get("type")
    if kind not in CHECK_TYPES:
        raise InputError(f"{location}: unsupported mechanical check type {kind!r}")
    if kind == "exact_text":
        if set(check) != {"type", "value"} or not isinstance(check["value"], str) or not check["value"]:
            raise InputError(f"{location}: exact_text requires a non-empty string value")
    elif kind == "word_limit":
        if set(check) != {"type", "max"} or type(check["max"]) is not int or check["max"] < 0:
            raise InputError(f"{location}: word_limit requires a non-negative integer max")
    elif kind == "numbered_count":
        if set(check) != {"type", "count"} or type(check["count"]) is not int or check["count"] < 0:
            raise InputError(f"{location}: numbered_count requires a non-negative integer count")
    elif kind == "export":
        if set(check) != {"type", "path", "lines"} or type(check["lines"]) is not int or check["lines"] < 0:
            raise InputError(f"{location}: export requires path and a non-negative integer lines")
        _relative_path(check["path"], f"{location}.path")
    elif set(check) != {"type"}:
        raise InputError(f"{location}: trace_policy takes no additional fields")


def load_cases(path: Path) -> list[dict[str, Any]]:
    required = {
        "id", "title", "request", "fixtures", "operation", "task", "scope",
        "target_profile", "required_details", "prohibited_changes", "output_contract", "criteria",
    }
    cases: list[dict[str, Any]] = []
    case_ids: set[str] = set()
    criterion_ids: set[str] = set()
    for line, case in _jsonl(path):
        location = f"{path}:{line}"
        if not isinstance(case, dict) or set(case) != required:
            raise InputError(f"{location}: case fields must be exactly {sorted(required)}")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip() or case_id in case_ids:
            raise InputError(f"{location}: case id must be a unique non-empty string")
        case_ids.add(case_id)
        for field in ("title", "request", "operation", "task", "scope", "target_profile", "output_contract"):
            if not isinstance(case[field], str):
                raise InputError(f"{location}: {field} must be a string")
        if not isinstance(case["fixtures"], list):
            raise InputError(f"{location}: fixtures must be a list")
        for fixture in case["fixtures"]:
            _relative_path(fixture, f"{location}.fixtures")
        for field in ("required_details", "prohibited_changes"):
            if not isinstance(case[field], list) or any(not isinstance(item, str) for item in case[field]):
                raise InputError(f"{location}: {field} must be a list of strings")
        if not isinstance(case["criteria"], list) or not case["criteria"]:
            raise InputError(f"{location}: criteria must be a non-empty list")
        for index, criterion in enumerate(case["criteria"]):
            cloc = f"{location}.criteria[{index}]"
            expected = {"id", "description", "method", "check", "severity", "mandatory_phase", "decision_url"}
            if not isinstance(criterion, dict) or set(criterion) != expected:
                raise InputError(f"{cloc}: criterion fields must be exactly {sorted(expected)}")
            criterion_id = criterion.get("id")
            if not isinstance(criterion_id, str) or not criterion_id.strip() or criterion_id in criterion_ids:
                raise InputError(f"{cloc}: criterion id must be globally unique and non-empty")
            criterion_ids.add(criterion_id)
            if criterion["method"] not in METHODS or criterion["severity"] not in SEVERITIES:
                raise InputError(f"{cloc}: invalid method or severity")
            if type(criterion["mandatory_phase"]) is not int or not 1 <= criterion["mandatory_phase"] <= 7:
                raise InputError(f"{cloc}: mandatory_phase must be an integer from 1 through 7")
            if not isinstance(criterion["description"], str) or not isinstance(criterion["decision_url"], str):
                raise InputError(f"{cloc}: description and decision_url must be strings")
            if criterion["method"] == "mechanical":
                _validate_check(criterion["check"], cloc)
            elif criterion["check"] is not None:
                raise InputError(f"{cloc}: maintainer criteria must have check=null")
        cases.append(case)
    if not cases:
        raise InputError(f"{path}: no cases found")
    return cases


def _safe_child(root: Path, relative: str | PurePosixPath) -> Path | None:
    try:
        candidate = (root / Path(str(relative))).resolve()
        candidate.relative_to(root.resolve())
        return candidate
    except (OSError, ValueError):
        return None


def _read_text(path: Path | None, *, allow_empty: bool = False) -> tuple[str | None, str | None]:
    if path is None:
        return None, "unsafe path"
    try:
        data = path.read_bytes()
    except OSError as exc:
        return None, f"unavailable: {exc}"
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None, "not UTF-8 text"
    if not allow_empty and not text.strip():
        return None, "empty output"
    return text, None


def _path_parts(manifest_path: Path, results: Path) -> tuple[str, str, int] | None:
    try:
        rel = manifest_path.relative_to(results)
    except ValueError:
        return None
    if len(rel.parts) < 3 or rel.name != "attempt.json":
        return None
    attempt_dir = rel.parts[-2]
    match = re.fullmatch(r"attempt-(\d+)", attempt_dir)
    if not match:
        return None
    cohort_parts = rel.parts[:-3]
    cohort = "/".join(cohort_parts) if cohort_parts else "."
    return cohort, rel.parts[-3], int(match.group(1))


def discover_attempts(results: Path, case_ids: set[str]) -> tuple[dict[tuple[str, str, str, int], dict[str, Any]], list[str]]:
    attempts: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    warnings: list[str] = []
    parsed: list[dict[str, Any]] = []
    if not results.is_dir():
        raise InputError(f"results directory does not exist: {results}")
    for manifest_path in sorted(results.rglob("attempt.json")):
        parts = _path_parts(manifest_path, results)
        if parts is None:
            warnings.append(f"ignored attempt manifest outside cohort/case-id/attempt-N shape: {manifest_path}")
            continue
        cohort, path_case_id, path_attempt = parts
        if path_case_id not in case_ids or path_attempt not in (1, 2, 3):
            warnings.append(f"ignored unknown case or non-Phase-1 slot: {manifest_path}")
            continue
        record: dict[str, Any] = {
            "path": manifest_path,
            "dir": manifest_path.parent,
            "cohort": cohort,
            "path_case_id": path_case_id,
            "path_attempt": path_attempt,
            "valid": False,
            "issues": [],
            "manifest": None,
            "revision": None,
        }
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            record["issues"].append(f"invalid attempt manifest: {exc}")
            parsed.append(record)
            continue
        record["manifest"] = manifest
        if not isinstance(manifest, dict):
            record["issues"].append("attempt manifest is not an object")
            parsed.append(record)
            continue
        revision = manifest.get("revision")
        if isinstance(revision, str) and revision.strip():
            record["revision"] = revision
        else:
            record["issues"].append("missing non-empty revision")
        if manifest.get("case_id") != path_case_id or type(manifest.get("attempt")) is not int or manifest.get("attempt") != path_attempt:
            record["issues"].append("manifest case_id/attempt does not match its path")
        execution = manifest.get("execution")
        if not isinstance(execution, dict) or execution.get("status") not in {"completed", "error", "timeout", "not-run"}:
            record["issues"].append("invalid execution object/status")
        elif type(execution.get("exit_code")) is not int and execution.get("exit_code") is not None:
            record["issues"].append("execution.exit_code must be an integer or null")
        raw = manifest.get("raw")
        if (
            not isinstance(raw, dict)
            or not {"output", "trace", "stderr"} <= set(raw)
            or (raw.get("output") is not None and not isinstance(raw.get("output"), str))
            or not isinstance(raw.get("trace"), str)
            or not isinstance(raw.get("stderr"), str)
        ):
            record["issues"].append("invalid raw evidence links")
        if type(manifest.get("trace_complete")) is not bool:
            record["issues"].append("trace_complete must be boolean")
        artifacts = manifest.get("artifacts")
        if not isinstance(artifacts, list):
            record["issues"].append("artifacts must be a list")
        else:
            for item in artifacts:
                if (
                    not isinstance(item, dict)
                    or not {"path", "stored_path", "sha256", "bytes"} <= set(item)
                    or not isinstance(item.get("path"), str)
                    or not isinstance(item.get("stored_path"), str)
                    or not isinstance(item.get("sha256"), str)
                    or type(item.get("bytes")) is not int
                    or item.get("bytes", -1) < 0
                ):
                    record["issues"].append("invalid artifact record")
                    break
        record["valid"] = not record["issues"]
        parsed.append(record)

    revisions_by_cohort: dict[str, set[str]] = defaultdict(set)
    for record in parsed:
        if record["revision"]:
            revisions_by_cohort[record["cohort"]].add(record["revision"])
    for record in parsed:
        revision = record["revision"]
        if revision is None:
            known = revisions_by_cohort[record["cohort"]]
            revision = next(iter(known)) if len(known) == 1 else "unknown"
        key = (record["cohort"], revision, record["path_case_id"], record["path_attempt"])
        if key in attempts:
            raise InputError(f"duplicate attempt slot for {key}: {record['path']} and {attempts[key]['path']}")
        attempts[key] = record
    return attempts, warnings


def _event_tool(event: Any) -> tuple[str, Any] | None | bool:
    if not isinstance(event, dict):
        return False
    event_type = event.get("type") or event.get("event")
    if not isinstance(event_type, str):
        return False
    if event_type != "tool_execution_start":
        return None
    name = event.get("toolName")
    args = event.get("args")
    if not isinstance(name, str) or not name.strip() or not isinstance(args, (dict, list, str)):
        return False
    return name, args


def _normalize_tool(name: str) -> str:
    return re.split(r"[./:]", name.strip().lower())[-1]


def _shell_command(args: Any) -> str | None:
    if isinstance(args, str):
        return args
    if not isinstance(args, dict):
        return None
    for key in ("command", "cmd", "script"):
        if isinstance(args.get(key), str):
            return args[key]
    return None


def _strip_selector(value: str) -> str:
    return re.sub(r":(?:raw(?::\d+(?:-\d+)?)?|\d+(?:[-+]\d+)?(?:,\d+(?:-\d+)?)*)$", "", value)


def _local_operand(value: str) -> bool:
    if not value or value.startswith("-"):
        return True
    lowered = value.lower()
    if "://" in lowered or "?q=" in lowered:
        return False
    path = PurePosixPath(_strip_selector(value))
    if path.is_absolute() or ".." in path.parts:
        return False
    parts = tuple(part for part in path.parts if part not in ("", "."))
    return bool(parts) and parts[0] in {"selected-skill", "fixtures", "outputs"}


def _classify_local_tool(name: str, args: Any) -> tuple[str, str]:
    if name == "edit":
        return "failed", "edit is not an available or permitted generator-session tool"
    if not isinstance(args, dict):
        return "not-run", f"{name} arguments are not an object"
    raw_paths = args.get("path")
    if isinstance(raw_paths, str):
        paths = [item for item in raw_paths.split(";") if item]
    elif isinstance(raw_paths, list) and all(isinstance(item, str) for item in raw_paths):
        paths = raw_paths
    else:
        return "not-run", f"{name} arguments do not expose path evidence"
    if not paths:
        return "not-run", f"{name} has no observable path"
    lowered_paths = [path.lower() for path in paths]
    if any("://" in path for path in lowered_paths):
        return "failed", f"{name} used a URI instead of the selected workspace"
    if any("?q=" in path for path in lowered_paths):
        return "failed", f"{name} invoked image question/model processing"
    stripped_paths = [_strip_selector(path) for path in paths]
    if any(".csv" in PurePosixPath(path).name.lower() or "docs/danbooru_tags" in path.lower() for path in stripped_paths):
        return "failed", f"{name} accessed the raw Danbooru dataset instead of the lookup script"
    if not all(_local_operand(path) for path in stripped_paths):
        return "failed", f"{name} accessed a path outside selected-skill, fixtures, or outputs"
    if name == "write" and any(tuple(part for part in PurePosixPath(path).parts if part not in ("", "."))[0] != "outputs" for path in stripped_paths):
        return "failed", "write targeted a path outside outputs"
    return "passed", f"recognized workspace-local {name}"


def _classify_shell(command: str, *, cwd: str | None = None, workspace: str | None = None, environment: Any = None) -> tuple[str, str]:
    if any(token in command for token in (";", "&&", "||", "|", "`", "$(", ">", "<", "\n")):
        return "not-run", "shell command contains composition or redirection"
    try:
        words = shlex.split(command)
    except ValueError:
        return "not-run", "shell command could not be parsed"
    if not words:
        return "not-run", "empty shell command"
    executable = PurePosixPath(words[0]).name.lower()
    if executable in FORBIDDEN_SHELL_COMMANDS:
        return "failed", f"observed prohibited shell action {executable!r}"
    if environment not in (None, {}):
        return "not-run", "shell environment overrides prevent conservative classification"
    root = PurePosixPath(workspace or ".")
    directory = PurePosixPath(cwd) if cwd else root
    if cwd and not directory.is_absolute():
        directory = root / directory
    if ".." in directory.parts:
        return "not-run", "shell cwd contains parent traversal"
    try:
        directory.relative_to(root)
    except ValueError:
        return "failed", "shell cwd is outside the captured workspace"
    if executable in {"python", "python3"}:
        script = ""
        if len(words) >= 2 and ".." not in PurePosixPath(words[1]).parts:
            try:
                script = (directory / words[1]).relative_to(root).as_posix()
            except ValueError:
                return "failed", "Python script is outside the captured workspace"
        if script == "selected-skill/scripts/danbooru_lookup.py":
            if any(".csv" in PurePosixPath(word).name.lower() for word in words[2:] if not word.startswith("-")):
                return "failed", "lookup script was directed to a raw CSV"
            return "passed", "recognized local Danbooru lookup"
        return "not-run", "Python shell command is not the selected local lookup script"
    if any(".csv" in PurePosixPath(word).name.lower() or "docs/danbooru_tags" in word.lower() for word in words[1:] if not word.startswith("-")):
        return "failed", "observed raw Danbooru dataset access instead of the lookup script"
    if executable in LOCAL_FILE_COMMANDS:
        operands = []
        for word in words[1:]:
            if word.startswith("-"):
                continue
            if ".." in PurePosixPath(word).parts:
                return "not-run", "shell operand contains parent traversal"
            try:
                operands.append((directory / word).relative_to(root).as_posix())
            except ValueError:
                return "failed", "shell operand is outside the captured workspace"
        if all(_local_operand(word) for word in operands):
            return "passed", f"recognized simple local file command {executable!r}"
    return "not-run", f"ambiguous shell command {executable!r}"


def check_trace(record: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    manifest = record["manifest"]
    trace_complete = manifest.get("trace_complete") is True
    trace_link = manifest["raw"].get("trace")
    if not isinstance(trace_link, str) or not trace_link:
        return "not-run", {"reason": "trace evidence link is unavailable"}
    trace_path = _safe_child(record["dir"], trace_link)
    if trace_path is None or not trace_path.is_file():
        return "not-run", {"reason": "trace evidence file is unavailable", "path": trace_link}
    observed: list[str] = []
    uncertain: list[str] = []
    forbidden: list[str] = []
    try:
        trace_text = trace_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return "not-run", {"reason": f"trace is unreadable: {exc}", "path": trace_link}
    expected_trace_hash = manifest.get("raw_checksums", {}).get(trace_link) if isinstance(manifest.get("raw_checksums"), dict) else None
    actual_trace_hash = hashlib.sha256(trace_text.encode("utf-8")).hexdigest()
    if expected_trace_hash is not None and expected_trace_hash != actual_trace_hash:
        return "not-run", {"reason": "trace checksum does not match its manifest", "path": trace_link}
    lines = trace_text.splitlines()
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            uncertain.append(f"line {number}: invalid JSON")
            continue
        tool = _event_tool(event)
        if tool is False:
            uncertain.append(f"line {number}: unknown tool-start event shape")
            continue
        if tool is None:
            continue
        name, args = tool
        normalized = _normalize_tool(name)
        observed.append(name)
        tool_components = set(re.split(r"[./:]", name.strip().lower()))
        if tool_components & FORBIDDEN_TOOL_NAMES or "browser" in tool_components or any("generation" in component for component in tool_components):
            forbidden.append(name)
            continue
        if normalized in {"bash", "shell", "terminal"}:
            command = _shell_command(args)
            if command is None:
                uncertain.append(f"line {number}: shell arguments do not expose a command")
                continue
            state, reason = _classify_shell(command, cwd=args.get("cwd") if isinstance(args, dict) else None,
                                            workspace=manifest.get("cwd"), environment=args.get("env") if isinstance(args, dict) else None)
            if state == "failed":
                forbidden.append(reason)
            elif state == "not-run":
                uncertain.append(f"line {number}: {reason}")
            continue
        if normalized in {"read", "write", "edit", "grep", "glob"}:
            state, reason = _classify_local_tool(normalized, args)
            if state == "failed":
                forbidden.append(f"line {number}: {reason}")
            elif state == "not-run":
                uncertain.append(f"line {number}: {reason}")
        else:
            uncertain.append(f"line {number}: unknown tool {name!r}")
    evidence = {"trace": trace_link, "trace_complete": trace_complete, "sha256": actual_trace_hash, "observed_tools": observed}
    if forbidden:
        evidence.update(reason="observed prohibited tool/action", violations=forbidden)
        return "failed", evidence
    if not trace_complete:
        evidence.update(reason="trace is marked incomplete; absence of further prohibited calls cannot be established", limitations=uncertain)
        return "not-run", evidence
    if uncertain:
        evidence.update(reason="trace contains calls that cannot be classified conservatively", limitations=uncertain)
        return "not-run", evidence
    evidence["reason"] = "complete observable trace contains no prohibited calls"
    return "passed", evidence

def _output(record: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    link = record["manifest"]["raw"].get("output")
    if not isinstance(link, str) or not link:
        return None, {"reason": "output evidence link is unavailable"}
    path = _safe_child(record["dir"], link)
    text, error = _read_text(path)
    if error:
        return None, {"reason": error, "output": link}
    actual_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    checksums = record["manifest"].get("raw_checksums")
    expected_hash = checksums.get(link) if isinstance(checksums, dict) else None
    if expected_hash is not None and expected_hash != actual_hash:
        return None, {"reason": "output checksum does not match its manifest", "output": link}
    return text, {"output": link, "sha256": actual_hash}


def _artifact(record: dict[str, Any], requested: str) -> tuple[dict[str, Any] | None, str | None]:
    matches = [item for item in record["manifest"]["artifacts"] if item.get("path") == requested]
    if len(matches) != 1:
        return None, "expected artifact is missing" if not matches else "duplicate artifact records"
    artifact = matches[0]
    stored = artifact.get("stored_path")
    if not isinstance(stored, str) or not stored:
        return None, "artifact stored_path is unavailable"
    path = _safe_child(record["dir"], stored)
    if path is None or not path.is_file():
        return None, "captured artifact file is unavailable"
    try:
        data = path.read_bytes()
    except OSError as exc:
        return None, f"captured artifact file is unreadable: {exc}"
    digest = hashlib.sha256(data).hexdigest()
    if artifact.get("sha256") != digest or artifact.get("bytes") != len(data):
        return None, "captured artifact checksum/size does not match its manifest"
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None, "captured artifact is not UTF-8 text"
    return {"manifest": artifact, "text": text, "sha256": digest}, None


def mechanical(criterion: dict[str, Any], record: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    check = criterion["check"]
    kind = check["type"]
    if kind == "trace_policy":
        return check_trace(record)
    if kind == "export":
        artifact, error = _artifact(record, check["path"])
        if error:
            completed = record["manifest"]["execution"].get("status") == "completed"
            state = "failed" if completed and error in {"expected artifact is missing", "duplicate artifact records"} else "not-run"
            return state, {"reason": error, "artifact_path": check["path"]}
        lines = artifact["text"].splitlines()
        nonblank = [line for line in lines if line.strip()]
        passed = bool(lines) and len(lines) == check["lines"] and len(nonblank) == check["lines"] and len(set(lines)) == len(lines)
        return ("passed" if passed else "failed"), {
            "artifact_path": check["path"],
            "stored_path": artifact["manifest"]["stored_path"],
            "sha256": artifact["sha256"],
            "expected_lines": check["lines"],
            "line_count": len(lines),
            "nonblank_line_count": len(nonblank),
            "duplicate_exact_lines": len(lines) - len(set(lines)),
        }
    text, evidence = _output(record)
    if text is None:
        return "not-run", evidence
    if kind == "exact_text":
        present = check["value"] in text
        evidence.update(literal=check["value"], present=present)
        return ("passed" if present else "failed"), evidence
    if kind == "word_limit":
        count = len(re.findall(r"\S+", text, flags=re.UNICODE))
        evidence.update(word_count=count, maximum=check["max"], method="Unicode whitespace-separated tokens over the entire final output")
        return ("passed" if count <= check["max"] else "failed"), evidence
    matches = re.findall(r"(?m)^\s*\d+[.)]\s+", text)
    evidence.update(numbered_line_count=len(matches), expected_count=check["count"], method="line starts matching optional whitespace, digits, '.' or ')', then whitespace")
    return ("passed" if len(matches) == check["count"] else "failed"), evidence


def load_reviews(path: Path | None, criteria: dict[str, tuple[str, dict[str, Any]]]) -> dict[tuple[str, int, str], dict[str, Any]]:
    if path is None:
        return {}
    reviews: dict[tuple[str, int, str], dict[str, Any]] = {}
    required = {"case_id", "attempt", "criterion_id", "state", "reviewer", "reviewed_at", "evidence", "human"}
    for line, review in _jsonl(path):
        location = f"{path}:{line}"
        if not isinstance(review, dict) or set(review) != required:
            raise InputError(f"{location}: review fields must be exactly {sorted(required)}")
        key = (review.get("case_id"), review.get("attempt"), review.get("criterion_id"))
        if key in reviews:
            raise InputError(f"{location}: duplicate review for {key}")
        if type(review.get("attempt")) is not int or review["attempt"] not in (1, 2, 3):
            raise InputError(f"{location}: attempt must be 1, 2, or 3")
        if review.get("state") not in STATES:
            raise InputError(f"{location}: review state must be passed, failed, or not-run")
        reviewer = review.get("reviewer")
        if review.get("human") is not True or not isinstance(reviewer, str) or not reviewer.startswith("human:") or not reviewer[6:].strip():
            raise InputError(f"{location}: reviewer must explicitly identify a human as 'human:<stable-id>' and human must be true")
        lowered = reviewer.lower()
        if any(word in lowered for word in ("anonymous", "model", "bot", "auto-judge", "llm")):
            raise InputError(f"{location}: anonymous/model reviewer identities are not accepted")
        if not isinstance(review.get("reviewed_at"), str):
            raise InputError(f"{location}: reviewed_at must be an ISO-8601 timestamp")
        try:
            reviewed_at = dt.datetime.fromisoformat(review["reviewed_at"].replace("Z", "+00:00"))
        except ValueError as exc:
            raise InputError(f"{location}: reviewed_at must be an ISO-8601 timestamp") from exc
        if reviewed_at.tzinfo is None:
            raise InputError(f"{location}: reviewed_at must include a UTC offset or Z")
        if not isinstance(review.get("evidence"), str) or not review["evidence"].strip():
            raise InputError(f"{location}: evidence must be a non-empty string")
        criterion_entry = criteria.get(review["criterion_id"])
        if criterion_entry is None or criterion_entry[0] != review["case_id"] or criterion_entry[1]["method"] != "maintainer":
            raise InputError(f"{location}: review does not match a maintainer criterion")
        reviews[key] = review
    return reviews


def _attempt_evidence(record: dict[str, Any] | None, results: Path) -> dict[str, Any]:
    if record is None:
        return {"reason": "attempt slot is absent; no attempt.json was captured"}
    return {
        "attempt_manifest": record["path"].relative_to(results).as_posix(),
        "manifest_valid": record["valid"],
        "issues": record["issues"],
    }


def score_all(cases: list[dict[str, Any]], attempts: dict[tuple[str, str, str, int], dict[str, Any]], reviews: dict[tuple[str, int, str], dict[str, Any]], results: Path) -> tuple[list[dict[str, Any]], list[tuple[str, str]]]:
    groups = sorted({(key[0], key[1]) for key in attempts})
    if not groups:
        groups = [(results.name, "unknown")]
    rows: list[dict[str, Any]] = []
    for cohort, revision in groups:
        for case in cases:
            for attempt_number in (1, 2, 3):
                record = attempts.get((cohort, revision, case["id"], attempt_number))
                scored: list[dict[str, Any]] = []
                for criterion in case["criteria"]:
                    evidence = _attempt_evidence(record, results)
                    if record is None or not record["valid"]:
                        state = "not-run"
                    elif criterion["method"] == "mechanical":
                        state, detail = mechanical(criterion, record)
                        evidence.update(detail)
                    else:
                        review = reviews.get((case["id"], attempt_number, criterion["id"]))
                        output_text, output_detail = _output(record)
                        reviewable_artifacts = []
                        for artifact_record in record["manifest"]["artifacts"]:
                            artifact_path = artifact_record.get("path")
                            if not isinstance(artifact_path, str):
                                continue
                            artifact, _ = _artifact(record, artifact_path)
                            if artifact is not None and artifact["text"].strip():
                                reviewable_artifacts.append(artifact_path)
                        lookup_evidence = _lookup_trace_evidence(record) if criterion["id"] == "C11-LOOKUP-EVIDENCE" else None
                        reviewable_lookup = bool(lookup_evidence and lookup_evidence["calls"])
                        if review is None:
                            state = "not-run"
                            evidence["reason"] = "required human review is missing"
                        elif output_text is None and not reviewable_artifacts and not reviewable_lookup:
                            state = "not-run"
                            evidence["submitted_human_review"] = {
                                "state": review["state"],
                                "reviewer": review["reviewer"],
                                "reviewed_at": review["reviewed_at"],
                                "evidence": review["evidence"],
                                "human": True,
                                "accepted": False,
                            }
                            evidence["reason"] = "human review has no available non-empty captured output, artifact, or applicable lookup trace to support it"
                            evidence["output_availability"] = output_detail["reason"]
                        else:
                            state = review["state"]
                            evidence["reviewed_raw_sources"] = {
                                "output": output_detail.get("output") if output_text is not None else None,
                                "artifacts": reviewable_artifacts,
                                "trace": record["manifest"]["raw"]["trace"] if reviewable_lookup else None,
                            }
                            if lookup_evidence is not None:
                                evidence["observable_lookup_trace"] = lookup_evidence
                            evidence["human_review"] = {
                                "reviewer": review["reviewer"],
                                "reviewed_at": review["reviewed_at"],
                                "evidence": review["evidence"],
                                "human": True,
                            }
                    scored.append({
                        "criterion_id": criterion["id"],
                        "state": state,
                        "method": criterion["method"],
                        "severity": criterion["severity"],
                        "mandatory_phase": criterion["mandatory_phase"],
                        "evidence": evidence,
                    })
                execution = record["manifest"].get("execution") if record and record["valid"] else None
                rows.append({
                    "cohort": cohort,
                    "revision": revision,
                    "case_id": case["id"],
                    "attempt": attempt_number,
                    "execution": execution,
                    "criteria": scored,
                })
    return rows, groups


def result_kinds(results: Path, groups: list[tuple[str, str]]) -> dict[tuple[str, str], str]:
    kinds: dict[tuple[str, str], str] = {}
    for group in groups:
        cohort, _ = group
        root = results if cohort == "." else _safe_child(results, cohort)
        manifest_path = root / "manifest.json" if root is not None else None
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path is not None else None
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            manifest = None
        kind = manifest.get("kind") if isinstance(manifest, dict) else None
        kinds[group] = kind if isinstance(kind, str) and kind else "unknown"
    return kinds


def summarize(cases: list[dict[str, Any]], rows: list[dict[str, Any]], groups: list[tuple[str, str]], kinds: dict[tuple[str, str], str], warnings: list[str]) -> dict[str, Any]:
    indexed = {(row["cohort"], row["revision"], row["case_id"], row["attempt"]): row for row in rows}
    group_summaries: list[dict[str, Any]] = []
    for cohort, revision in groups:
        result_kind = kinds[(cohort, revision)]
        case_summaries: list[dict[str, Any]] = []
        hard_gate_counts: Counter[str] = Counter()
        for case in cases:
            criterion_summaries: list[dict[str, Any]] = []
            case_states: Counter[str] = Counter()
            for criterion in case["criteria"]:
                states = [
                    next(item for item in indexed[(cohort, revision, case["id"], attempt)]["criteria"] if item["criterion_id"] == criterion["id"])["state"]
                    for attempt in (1, 2, 3)
                ]
                counts = Counter(states)
                passes = counts["passed"]
                classification = None
                if result_kind == "original-phase-one-baseline" and revision == BASELINE_REVISION and criterion["severity"] == "hard":
                    if passes == 3:
                        classification = "original-3-of-3-hard-gate"
                    elif passes:
                        classification = "unstable-baseline"
                    elif counts["failed"]:
                        classification = "zero-pass-baseline"
                    else:
                        classification = "unreviewed-baseline"
                    hard_gate_counts[classification] += 1
                criterion_summaries.append({
                    "criterion_id": criterion["id"],
                    "description": criterion["description"],
                    "method": criterion["method"],
                    "severity": criterion["severity"],
                    "mandatory_phase": criterion["mandatory_phase"],
                    "counts": {state: counts[state] for state in ("passed", "failed", "not-run")},
                    "mixed_outcomes": len({state for state in states}) > 1,
                    "unreviewed_or_unavailable": counts["not-run"] > 0,
                    "baseline_classification": classification,
                    "blocks_acceptance_when_due": criterion["severity"] == "hard" and (counts["failed"] > 0 or counts["not-run"] > 0),
                })
                case_states.update(states)
            hard = [entry for entry in criterion_summaries if entry["severity"] == "hard"]
            if any(entry["counts"]["failed"] for entry in hard):
                hard_outcome = "failed"
            elif any(entry["counts"]["not-run"] for entry in hard):
                hard_outcome = "not-run"
            else:
                hard_outcome = "passed"
            case_summaries.append({
                "case_id": case["id"],
                "title": case["title"],
                "slot_count": 3,
                "all_criterion_state_counts": {state: case_states[state] for state in ("passed", "failed", "not-run")},
                "hard_outcome": hard_outcome,
                "criteria": criterion_summaries,
            })
        group_summaries.append({
            "cohort": cohort,
            "revision": revision,
            "kind": result_kind,
            "attempt_slots_per_case": 3,
            "baseline_hard_gate_counts": dict(sorted(hard_gate_counts.items())),
            "cases": case_summaries,
        })
    return {
        "protocol": "Scenario Maker Phase 1 prompt-behavior evaluation",
        "states": ["passed", "failed", "not-run"],
        "limitations": LIMITATIONS,
        "warnings": warnings,
        "groups": group_summaries,
    }


def _fixture_entries(case: dict[str, Any], cases_path: Path) -> list[dict[str, Any]]:
    base = (cases_path.parent / "fixtures").resolve()
    entries: list[dict[str, Any]] = []
    for declared in case["fixtures"]:
        relative = PurePosixPath(declared)
        if relative.parts and relative.parts[0] == "fixtures":
            relative = PurePosixPath(*relative.parts[1:])
        path = _safe_child(base, relative)
        try:
            data = path.read_bytes() if path is not None else None
        except OSError as exc:
            entries.append({"path": declared, "text": None, "availability": f"unavailable: {exc}", "bytes": None, "sha256": None})
            continue
        if data is None:
            entries.append({"path": declared, "text": None, "availability": "unsafe path", "bytes": None, "sha256": None})
            continue
        try:
            text = data.decode("utf-8")
            availability = "available text"
        except UnicodeDecodeError:
            text = None
            availability = "available binary fixture; inspect the repository path"
        entries.append({
            "path": declared,
            "text": text,
            "availability": availability,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    return entries


def _artifact_texts(record: dict[str, Any] | None) -> list[dict[str, Any]]:
    if record is None or not record["valid"]:
        return []
    entries: list[dict[str, Any]] = []
    for artifact_record in record["manifest"]["artifacts"]:
        declared = artifact_record.get("path")
        artifact, error = _artifact(record, declared) if isinstance(declared, str) else (None, "artifact path unavailable")
        entries.append({
            "path": declared,
            "text": artifact["text"] if artifact is not None else None,
            "availability": "available" if error is None else error,
        })
    return entries


def _redact_review_value(value: Any, record: dict[str, Any]) -> Any:
    sensitive = [str(record["dir"])]
    cwd = record["manifest"].get("cwd")
    if isinstance(cwd, str):
        sensitive.append(cwd)
    if isinstance(value, str):
        for token in sensitive:
            value = value.replace(token, "<workspace>")
        return value
    if isinstance(value, list):
        return [_redact_review_value(item, record) for item in value]
    if isinstance(value, dict):
        return {key: ("<redacted>" if key in {"cwd", "env"} else _redact_review_value(item, record)) for key, item in value.items()}
    return value


def _lookup_trace_evidence(record: dict[str, Any] | None) -> dict[str, Any]:
    if record is None or not record["valid"]:
        return {"availability": "unavailable: attempt or manifest is missing", "calls": []}
    trace_link = record["manifest"]["raw"].get("trace")
    trace_path = _safe_child(record["dir"], trace_link) if isinstance(trace_link, str) else None
    if trace_path is None:
        return {"availability": "unavailable: trace link is missing or unsafe", "calls": []}
    try:
        trace_text = trace_path.read_text(encoding="utf-8")
        events = [json.loads(line) for line in trace_text.splitlines() if line.strip()]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"availability": f"unavailable: trace cannot be read: {exc}", "calls": []}
    checksums = record["manifest"].get("raw_checksums")
    expected_hash = checksums.get(trace_link) if isinstance(checksums, dict) else None
    if expected_hash is not None and expected_hash != hashlib.sha256(trace_text.encode("utf-8")).hexdigest():
        return {"availability": "unavailable: trace checksum does not match its manifest", "calls": []}
    calls: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("type") == "tool_execution_start" and _normalize_tool(str(event.get("toolName", ""))) == "bash":
            args = event.get("args")
            command = _shell_command(args)
            if command is None or _classify_shell(
                    command, cwd=args.get("cwd") if isinstance(args, dict) else None,
                    workspace=record["manifest"].get("cwd"), environment=args.get("env") if isinstance(args, dict) else None
            ) != ("passed", "recognized local Danbooru lookup"):
                continue
            entry = {"args": _redact_review_value(args, record), "result_content": None}
            calls.append(entry)
            call_id = event.get("toolCallId")
            if isinstance(call_id, str):
                by_id[call_id] = entry
        elif event.get("type") == "tool_execution_end":
            call_id = event.get("toolCallId")
            if isinstance(call_id, str) and call_id in by_id:
                result = event.get("result")
                content = result.get("content") if isinstance(result, dict) else None
                by_id[call_id]["result_content"] = _redact_review_value(content, record)
    if not calls:
        return {
            "availability": "unavailable: no observable exact selected-skill Danbooru lookup call",
            "trace_complete": record["manifest"]["trace_complete"],
            "calls": [],
        }
    return {
        "availability": "available",
        "trace_complete": record["manifest"]["trace_complete"],
        "calls": calls,
    }

def review_material(cases: list[dict[str, Any]], attempts: dict[tuple[str, str, str, int], dict[str, Any]], groups: list[tuple[str, str]], cases_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    rng = random.SystemRandom()
    alphabet = string.ascii_lowercase + string.digits
    used: set[str] = set()
    cards: list[dict[str, Any]] = []
    mappings: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []
    for cohort, revision in groups:
        for case in cases:
            semantic = [criterion for criterion in case["criteria"] if criterion["method"] == "maintainer"]
            if not semantic:
                continue
            fixtures = _fixture_entries(case, cases_path)
            for attempt_number in (1, 2, 3):
                while True:
                    card_id = "card-" + "".join(rng.choice(alphabet) for _ in range(12))
                    if card_id not in used:
                        used.add(card_id)
                        break
                record = attempts.get((cohort, revision, case["id"], attempt_number))
                output = None
                availability = "attempt slot unavailable"
                if record and record["valid"]:
                    output, detail = _output(record)
                    availability = "available" if output is not None else detail["reason"]
                cards.append({
                    "card_id": card_id,
                    "input": {
                        "title": case["title"],
                        "request": case["request"],
                        "fixtures": fixtures,
                        "operation": case["operation"],
                        "task": case["task"],
                        "scope": case["scope"],
                        "target_profile": case["target_profile"],
                        "required_details": case["required_details"],
                        "prohibited_changes": case["prohibited_changes"],
                        "output_contract": case["output_contract"],
                    },
                    "raw_output": output,
                    "output_availability": availability,
                    "generated_artifacts": _artifact_texts(record),
                    **({"observable_lookup_trace": _lookup_trace_evidence(record)} if case["id"] == "case-11" else {}),
                    "criteria": [
                        {
                            "criterion_id": criterion["id"],
                            "description": criterion["description"],
                            "severity": criterion["severity"],
                            "mandatory_phase": criterion["mandatory_phase"],
                            "decision_url": criterion["decision_url"],
                        }
                        for criterion in semantic
                    ],
                })
                mappings.append({
                    "card_id": card_id,
                    "cohort": cohort,
                    "revision": revision,
                    "case_id": case["id"],
                    "attempt": attempt_number,
                })
                for criterion in semantic:
                    pending.append({
                        "case_id": case["id"],
                        "attempt": attempt_number,
                        "criterion_id": criterion["id"],
                        "state": None,
                        "reviewer": "human:<stable-id>",
                        "reviewed_at": None,
                        "evidence": None,
                        "human": True,
                    })
    rng.shuffle(cards)
    return cards, mappings, pending


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score three-slot Scenario Maker captures with declared mechanical checks and explicit human reviews.",
        epilog=(
            "Coverage is intentionally conservative: semantic criteria are never inferred from keywords; missing/empty raw output and incomplete traces cannot pass; "
            "trace policy observes OMP tool-start events but does not sandbox shell or hidden provider activity. Reviews must identify reviewer='human:<stable-id>' and human=true."
        ),
    )
    parser.add_argument("--cases", type=Path, required=True, help="Phase 1 cases JSONL")
    parser.add_argument("--results", type=Path, required=True, help="capture root containing cohort/case-id/attempt-N/attempt.json")
    parser.add_argument("--out", type=Path, required=True, help="new evaluation output directory outside the immutable results tree")
    parser.add_argument("--reviews", type=Path, help="optional completed human review JSONL; pending template nulls must be filled/removed before import")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    cases_path = args.cases.resolve()
    results = args.results.resolve()
    out = args.out.resolve()
    try:
        out.relative_to(results)
    except ValueError:
        pass
    else:
        raise InputError("--out must not equal or reside inside the immutable --results tree")
    cases = load_cases(cases_path)
    criteria = {criterion["id"]: (case["id"], criterion) for case in cases for criterion in case["criteria"]}
    attempts, warnings = discover_attempts(results, {case["id"] for case in cases})
    groups = sorted({(key[0], key[1]) for key in attempts}) or [(results.name, "unknown")]
    if args.reviews and len(groups) != 1:
        raise InputError("--reviews is ambiguous across multiple cohort/revision groups; evaluate each group separately")
    reviews = load_reviews(args.reviews.resolve() if args.reviews else None, criteria)
    if reviews:
        valid_review_keys = {(case["id"], attempt, criterion["id"]) for case in cases for attempt in (1, 2, 3) for criterion in case["criteria"] if criterion["method"] == "maintainer"}
        extra = set(reviews) - valid_review_keys
        if extra:
            raise InputError(f"reviews reference unavailable slots: {sorted(extra)}")
    rows, groups = score_all(cases, attempts, reviews, results)
    summary = summarize(cases, rows, groups, result_kinds(results, groups), warnings)
    cards, mapping, pending = review_material(cases, attempts, groups, cases_path)
    out.mkdir(parents=True, exist_ok=True)
    _write_jsonl(out / "scores.jsonl", rows)
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_jsonl(out / "review-packet.jsonl", cards)
    _write_jsonl(out / "review-mapping.jsonl", mapping)
    _write_jsonl(out / "pending-reviews.jsonl", pending)
    print(json.dumps({
        "scores": str(out / "scores.jsonl"),
        "summary": str(out / "summary.json"),
        "review_packet": str(out / "review-packet.jsonl"),
        "review_mapping": str(out / "review-mapping.jsonl"),
        "pending_reviews": str(out / "pending-reviews.jsonl"),
        "limitations": LIMITATIONS,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except InputError as exc:
        print(f"evaluate.py: error: {exc}", file=sys.stderr)
        raise SystemExit(2)
