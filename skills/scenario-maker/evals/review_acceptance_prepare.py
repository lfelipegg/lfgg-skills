"""Freeze one fresh acceptance assessment without invoking OMP or providers."""
import ast
from datetime import datetime, timezone
from pathlib import Path
import platform
import shutil
import sys

import review_acceptance_history as history
import review_split as review
import run_baseline as rb
import run_split as rs

EVALS = Path(__file__).resolve().parent
BASELINE = "8c1db4ecf911696e5a7492cf07d67e101e538ebdf8d2f67eceb7c383dd9961da"
CANDIDATE = "split-sha256-81a60df7cea26a553c679e4c72405ba3ab17defd615b6cff9b7e13140fac7f70"


def dependency_closure(evals):
    """Enumerate local static imports; reject unbound third-party dependencies."""
    pending, files, imports = ["review_acceptance"], {}, {}
    while pending:
        name = pending.pop()
        filename = name + ".py"
        if filename in files:
            continue
        path, checksum = rs._file(evals, filename, "evaluator dependency")
        files[filename] = checksum
        names = set()
        for node in ast.walk(ast.parse(rs._text(path), filename=filename)):
            if isinstance(node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.level or not node.module:
                    raise review.ReviewError(f"unbound relative evaluator import: {filename}")
                names.add(node.module.split(".")[0])
        imports[filename] = sorted(names)
        for imported in names:
            if (evals / (imported + ".py")).exists():
                pending.append(imported)
            elif imported not in sys.stdlib_module_names:
                raise review.ReviewError(f"unbound evaluator dependency: {imported}")
    required = {"review_acceptance.py", "review_acceptance_prepare.py", "review_acceptance_history.py",
                "review_split.py", "run_split.py", "run_baseline.py", "evaluate.py"}
    if set(files) != required:
        raise review.ReviewError(f"unexpected evaluator closure: {sorted(files)}")
    return files, imports


def current_bindings(corpus, boundary, candidate_root, evals, scope=None):
    live = rs.preflight(corpus["baseline"], candidate_root, "corpus", evals=evals)
    manifest = corpus["manifest"]
    candidate = scope["candidate_revision"] if scope else CANDIDATE
    if manifest["baseline_revision"] != BASELINE or manifest["candidate_revision"] != candidate:
        raise review.ReviewError("capture identities differ from approved unchanged-capture scope" if not scope
                                 else "capture identities differ from frozen fresh-capture scope")
    expected = {"candidate_files": manifest["source_manifests"]["candidate"],
                "evaluation_files": manifest["evaluation_files"], "fixture_files": manifest["fixtures"]}
    for field, captured in expected.items():
        if live[field] != captured:
            raise review.ReviewError(f"current {field} drift; no synchronization or prompt repair authorized")
    unavailable = [(run["manifest"]["suite"], slot, value["issues"])
                   for run in (corpus, boundary) for slot, value in run["captures"].items() if not value["available"]]
    if unavailable or sum(len(run["captures"]) for run in (corpus, boundary)) != 798:
        raise review.ReviewError(f"all 798 unchanged captures must be available: {unavailable}")
    return live


def ancillary_evidence(corpus):
    """Bind prior context/packaging proof, without claiming those checks ran again."""
    round_root = corpus["root"].parent
    comparison = round_root.parent
    context_path = round_root / "context-final.json"
    proof_path = round_root / "capture-and-context-proof.json"
    packaging_path = comparison / "packaging-proof.json"
    checks_path = comparison / "offline-checks-v2.json"
    original_path = comparison / "corpus/manifest.json"
    context, proof = review.load_json(context_path), review.load_json(proof_path)
    packaging, checks = review.load_json(packaging_path), review.load_json(checks_path)
    original = review.load_json(original_path)
    manifest = corpus["manifest"]
    if (context.get("baseline_identity"), context.get("candidate_identity")) != (BASELINE, CANDIDATE):
        raise review.ReviewError("prior context proof has different source identities")
    if context.get("source_manifests") != manifest["source_manifests"]:
        raise review.ReviewError("prior context source manifests differ")
    if (proof.get("baseline_revision"), proof.get("candidate_revision")) != (BASELINE, CANDIDATE):
        raise review.ReviewError("capture/context proof identities differ")
    context_ok = (context.get("context_assessment") == "passed"
                  and context["byte_gate"].get("status") == "passed"
                  and context["trace_gate"].get("status") == "passed"
                  and context["trace_gate"].get("integrity_status") == "passed")
    # Packaging exercised utilities, local resources, discovery and installation.
    # Later prompt-wording repairs are not new utility/packaging implementations.
    packaging_changes = []
    for skill in rs.SKILLS:
        before = original["source_manifests"]["candidate"][skill]
        after = manifest["source_manifests"]["candidate"][skill]
        if set(before) != set(after):
            raise review.ReviewError(f"prior packaging file inventory no longer applies: {skill}")
        for name in before:
            if before[name] != after[name]:
                if name != "SKILL.md" and not (name.startswith("references/") and name.endswith(".md")):
                    raise review.ReviewError(f"prior packaging runtime implementation changed: {skill}/{name}")
                packaging_changes.append(skill + "/" + name)
    packaging_ok = (packaging["discovery"].get("count") == 10
                    and packaging["isolated_utilities"].get("packages") == 8
                    and packaging["isolated_utilities"].get("runtime_links") == "all resolved"
                    and packaging["synchronization"].get("check") == "passed"
                    and all(value == 0 for value in checks["exit_codes"]))
    if not context_ok or not packaging_ok:
        raise review.ReviewError("prior context/packaging evidence is not applicable passing evidence")
    bindings = {str(path): rb.digest(path) for path in (context_path, proof_path, packaging_path, checks_path, original_path)}
    return {"bindings": bindings, "gates": {"context_evidence_applicable": context_ok,
            "packaging_evidence_applicable": packaging_ok}, "packaging_prompt_only_changes": packaging_changes,
            "verification_origin": "prior retained proof; not rerun utilities, installation or context measurement"}


def capture_scope(corpus, boundary, capture_preparation=None, package_smoke_proof=None):
    """Select fresh scope only through both explicit, externally bound inputs."""
    if (capture_preparation is None) != (package_smoke_proof is None):
        raise review.ReviewError("capture_preparation and package_smoke_proof must be supplied together")
    if capture_preparation is None:
        return None
    paths = []
    for value in (capture_preparation, package_smoke_proof):
        path = Path(value).absolute()
        if path.is_symlink() or path.resolve() != path or not path.is_file():
            raise review.ReviewError(f"regular absolute frozen scope input required: {path}")
        paths.append(path)
    capture_path, smoke_path = paths
    frozen = review.load_json(capture_path)
    candidate = frozen.get("candidate_identity")
    if (frozen.get("baseline_identity") != BASELINE
            or candidate != "split-sha256-" + rb.manifest_identity(frozen.get("source_manifests", {}).get("candidate", {}))
            or rb.manifest_identity(frozen.get("source_manifests", {}).get("baseline", {})) != BASELINE
            or candidate != "split-sha256-26055f990f2e24b85a268819c555bb67e79c3328db7fff9ffa02bfdc997fa74b"
            or frozen.get("scheduled_slots") != {"corpus": 744, "boundary": 54}
            or frozen.get("original_requests_expectations_routes_rubric_and_fixtures_unchanged") is not True
            or frozen.get("semantic_acceptance") != "not assessed"):
        raise review.ReviewError("frozen capture preparation identity/control differs")
    for run in (corpus, boundary):
        manifest, suite = run["manifest"], run["manifest"]["suite"]
        if (run["root"] != capture_path.parent / suite
                or manifest.get("baseline_supplied") != str(capture_path.parent / "before")
                or manifest.get("candidate_root_supplied") != str(capture_path.parent / "skills")
                or manifest.get("expected_attempts") != {"corpus": 744, "boundary": 54}[suite]
                or manifest["baseline_revision"] != BASELINE or manifest["candidate_revision"] != candidate
                or manifest["source_manifests"] != frozen["source_manifests"]
                or manifest["evaluation_files"] != frozen.get("evaluation_files")
                or manifest["fixtures"] != frozen.get("fixture_files")):
            raise review.ReviewError("fresh capture preparation/source bindings differ")
    return {"kind": "frozen-fresh-capture", "capture_preparation": str(capture_path),
            "package_smoke_proof": str(smoke_path), "baseline_revision": BASELINE,
            "candidate_revision": candidate,
            "bindings": {str(path): rb.digest(path) for path in paths}}


def fresh_ancillary_evidence(corpus, boundary, scope):
    root = Path(scope["capture_preparation"]).parent
    names = ("context-proof.json", "packaging-proof-binding.json", "authorization.json",
             "capture-outcome.json", "managed-terminal.json")
    paths = [root / name for name in names]
    for path in paths:
        if path.is_symlink() or path.resolve() != path or not path.is_file():
            raise review.ReviewError(f"regular frozen ancillary proof required: {path}")
    context, binder, authorization, outcome, terminal = [review.load_json(path) for path in paths]
    frozen = review.load_json(Path(scope["capture_preparation"]))
    smoke = review.load_json(Path(scope["package_smoke_proof"]))
    candidate = scope["candidate_revision"]
    manifest = corpus["manifest"]
    if (context.get("baseline_identity"), context.get("candidate_identity")) != (BASELINE, candidate):
        raise review.ReviewError("fresh context proof identities differ")
    if (context.get("source_manifests") != manifest["source_manifests"]
            or context.get("baseline") != str(root / "before")
            or context.get("candidate_root") != str(root / "skills")):
        raise review.ReviewError("fresh context source bindings differ")
    byte, trace = context.get("byte_gate", {}), context.get("trace_gate", {})
    if (context.get("context_assessment") != "passed" or byte.get("status") != "passed"
            or byte.get("failing_paths") != [] or trace.get("status") != "passed"
            or trace.get("captures_complete") is not True or trace.get("integrity_status") != "passed"
            or trace.get("observed_rules_status") != "passed"
            or any(trace.get(key) != [] for key in ("absent_suites", "consistency_errors", "violations",
                                                  "unexpected_character_generator"))):
        raise review.ReviewError("fresh context byte/trace/integrity gates are not complete passing evidence")
    suites = trace.get("suites", [])
    if len(suites) != 2 or {item.get("suite") for item in suites} != {"corpus", "boundary"}:
        raise review.ReviewError("fresh context trace suites differ")
    for run in (corpus, boundary):
        m = run["manifest"]
        item = next(item for item in suites if item["suite"] == m["suite"])
        expected = {"root": str(run["root"]), "manifest_sha256": rb.digest(run["root"] / "manifest.json"),
                    "baseline_revision": BASELINE, "candidate_revision": candidate,
                    "evaluation_files": m["evaluation_files"], "fixtures": m["fixtures"],
                    "expected_attempts": m["expected_attempts"], "model_requested": m["model_requested"],
                    "reasoning_requested": m["reasoning_requested"], "integrity_status": "passed",
                    "complete": True, "integrity_errors": [], "incomplete_evidence": []}
        if any(item.get(key) != value for key, value in expected.items()):
            raise review.ReviewError("fresh context trace root/manifest bindings differ")
    controls = {"model": rb.MODEL, "reasoning_requested": "high", "generator_timeout_seconds": 300,
                "jobs": 3, "expected_corpus": 744, "expected_boundary": 54, "retries": False,
                "replacements": False, "reuse": False, "paid_assessment_authorized": False,
                "adjudications_authorized": False, "prior_campaigns_non_resumable": True}
    if any(authorization.get(key) != value for key, value in controls.items()):
        raise review.ReviewError("fresh capture authorization controls differ")
    if (outcome.get("candidate_identity") != candidate or outcome.get("exit_code") != 0
            or outcome.get("validation_errors") != [] or outcome.get("paid_assessment_authorized") is not False
            or outcome.get("semantic_review") != "not-run" or outcome.get("acceptance") != "not assessed"):
        raise review.ReviewError("fresh capture outcome differs")
    for suite, count in (("corpus", 744), ("boundary", 54)):
        summary = outcome.get("execution_summaries", {}).get(suite, {})
        record = outcome.get("suites", {}).get(suite, {})
        if (any(summary.get(key) != count for key in ("expected_attempts", "attempts", "successful",
                                                     "completed", "outputs", "trace_complete"))
                or summary.get("errors") != 0 or summary.get("timeouts") != 0
                or record.get("exit_code") != 0 or record.get("command") != frozen["commands"][suite]):
            raise review.ReviewError("fresh capture completion controls differ")
    terminal_controls = {"state": "exited", "ready": True, "exit_code": 0, "corpus_runner_exit_code": 0,
                         "boundary_runner_exit_code": 0, "capture_outcome_exit_code": 0,
                         "terminal_matches_recorded_outcome": True, "paid_assessment_authorized": False,
                         "semantic_review": "not-run", "acceptance": "not assessed"}
    if any(terminal.get(key) != value for key, value in terminal_controls.items()):
        raise review.ReviewError("fresh managed terminal controls differ")
    extras = {"README.md", "CONTEXT.md", "agents/openai.yaml"}
    if (binder.get("status") != "passed" or binder.get("candidate_identity") != candidate
            or set(binder.get("packages", [])) != set(rs.SKILLS)
            or binder.get("runtime_hashes_match_isolated_smoke") is not True
            or set(binder.get("additional_capture_files", [])) != extras
            or smoke.get("kind") != "offline-source-repair" or smoke.get("paid_execution") is not False
            or set(smoke.get("packages", {})) != set(rs.SKILLS)):
        raise review.ReviewError("fresh packaging proof controls differ")
    proof_reference = binder.get("offline_package_proof")
    smoke_path = Path(scope["package_smoke_proof"])
    if (not isinstance(proof_reference, str) or ".." in Path(proof_reference).parts
            or not (str(smoke_path) == proof_reference
                    or (not Path(proof_reference).is_absolute()
                        and str(smoke_path).endswith("/" + proof_reference)))):
        raise review.ReviewError("fresh packaging explicit smoke path differs from binder")
    runtime = {}
    for skill in rs.SKILLS:
        full = manifest["source_manifests"]["candidate"][skill]
        package = smoke["packages"][skill]
        runtime[skill] = {name: checksum for name, checksum in full.items() if name not in extras}
        if (not extras <= set(full) or package.get("manifest") != runtime[skill]
                or package.get("identity") != rb.manifest_identity(runtime[skill])
                or package.get("terminal_exit") != 0 or package.get("stderr") != ""
                or not package.get("cold_hits") or package.get("resolved_runtime_links", 0) <= 0
                or any(package.get(key) is not True for key in ("character_matches_frozen",
                                                               "local_index_created", "alias_and_search_passed"))):
            raise review.ReviewError(f"fresh packaging runtime manifest/smoke differs: {skill}")
    identity = "split-sha256-" + rb.manifest_identity(runtime)
    guides = {"skills/" + skill + "/" + name: checksum for skill, files in runtime.items()
              for name, checksum in files.items() if name.startswith("references/models/minimax_h3/")}
    if (smoke.get("candidate_identity") != identity or frozen.get("offline_runtime_only_identity") != identity
            or smoke.get("guide_hashes") != guides):
        raise review.ReviewError("fresh packaging runtime identity/guide hashes differ")
    bindings = {str(path): rb.digest(path) for path in paths}
    bindings.update(scope["bindings"])
    return {"bindings": bindings, "gates": {"context_evidence_applicable": True,
            "packaging_evidence_applicable": True}, "capture_controls": controls,
            "verification_origin": "fresh retained capture/context and explicit offline package smoke proof; not rerun"}


def _outside(out, roots):
    if out.exists() or out.is_symlink() or out.resolve() != out.absolute():
        raise review.ReviewError(f"fresh non-symlink output required: {out}")
    for root in roots:
        if out == root or out in root.parents or root in out.parents:
            raise review.ReviewError(f"output overlaps retained evidence: {root}")


def _historical_provenance(source_review, provenance):
    original = source_review / "provenance"
    changes = {}
    for name in ("review_split.py", "reviewer-system.txt", "omp-config.json"):
        old, new = rb.digest(original / name), rb.digest(provenance / name)
        changes[name] = {"historical_path": str(original / name), "historical_sha256": old,
                         "prepared_sha256": new, "changed": old != new}
    return changes


def prepare(results, boundary_results, source_review, candidate_root, out, evals=EVALS, *,
            capture_preparation=None, package_smoke_proof=None):
    results, boundary_results, source_review, candidate_root, evals = (
        rs._root(path, label) for path, label in ((results, "corpus"), (boundary_results, "boundary"),
        (source_review, "historical review"), (candidate_root, "candidate root"), (evals, "live evaluation inputs")))
    out = Path(out).absolute()
    _outside(out, (results.parent, source_review))
    corpus, boundary = review.preflight(results, boundary_results)
    scope = capture_scope(corpus, boundary, capture_preparation, package_smoke_proof)
    current_bindings(corpus, boundary, candidate_root, evals, scope)
    packets, mappings = review.build_packets(corpus, boundary)
    if len(packets) != 411:
        raise review.ReviewError("all 411 acceptance packets must be prepared")
    supplemental = history.prepare_source_history(source_review)
    ancillary = fresh_ancillary_evidence(corpus, boundary, scope) if scope else ancillary_evidence(corpus)
    dependencies, imports = dependency_closure(evals)
    out.mkdir(parents=True, exist_ok=False)
    fresh = out / "ai-review"
    fresh.mkdir()
    review.retain_preparation(packets, mappings, fresh, corpus)
    provenance = fresh / "provenance"
    for name, checksum in dependencies.items():
        target = provenance / name
        if not target.exists():
            shutil.copyfile(evals / name, target)
        if rb.digest(target) != checksum:
            raise review.ReviewError(f"evaluator changed during preparation: {name}")
    if rb.digest(provenance / "reviewer-system.txt") != rb.digest(evals / "reviewer-system.txt"):
        raise review.ReviewError("reviewer system changed during preparation")
    rb.save_json(out / "historical-packet.json", supplemental["packet"])
    rb.save_json(out / "historical-first.json", supplemental["first"])
    external = {str(run["root"] / "manifest.json"): rb.digest(run["root"] / "manifest.json") for run in (corpus, boundary)}
    external.update(supplemental["bindings"])
    external.update(ancillary["bindings"])
    provenance_changes = _historical_provenance(source_review, provenance)
    for value in provenance_changes.values():
        external[value["historical_path"]] = value["historical_sha256"]
    provenance_files = rb.source_manifest(provenance)
    from review_acceptance import future_command
    managed_handle = "scenario-" + out.name
    preparation = {"kind": "fresh-split-acceptance-offline-preparation", "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(), "acceptance": "not assessed",
        "paid_execution_authorized": False, "results": str(results), "boundary_results": str(boundary_results),
        "source_review": str(source_review), "candidate_root": str(candidate_root), "live_evals": str(evals),
        "baseline_revision": BASELINE, "candidate_revision": corpus["manifest"]["candidate_revision"],
        "capture_scope": scope, "historical_bindings": supplemental["bindings"],
        "model_requested": rb.MODEL, "reasoning_requested": "high", "timeout_seconds": 900, "jobs": 3,
        "expected_packets": 411, "expected_capture_slots": 798, "reused_initial_judgments": 0,
        "paired_packets": sum(item["packet"]["paired"] for item in packets),
        "candidate_only_packets": sum(not item["packet"]["paired"] for item in packets),
        "historical_sessions": 1, "historical_label_alignment": supplemental["label_alignment"],
        "capture_manifest_hashes": {run["manifest"]["suite"]: rb.digest(run["root"] / "manifest.json") for run in (corpus, boundary)},
        "source_manifests": corpus["manifest"]["source_manifests"],
        "evaluation_files": corpus["manifest"]["evaluation_files"], "fixtures": corpus["manifest"]["fixtures"],
        "provenance_files": provenance_files, "dependency_imports": imports,
        "historical_provenance_difference": provenance_changes, "external_files": external,
        "ancillary_evidence": ancillary,
        "gates": {"capture_bindings_valid": True, "current_runtime_inputs_match": True,
                  "packet_coverage_complete": True, "historical_packet_complete": True, **ancillary["gates"]},
        "future_execution": {"managed_handle": managed_handle, "argv": future_command(out, managed_handle)},
        "packets": [{"case_id": item["packet"]["case_id"], "attempt": item["packet"]["attempt"],
                     "suite": item["suite"], "path": "ai-review/" + item["packet_path"], "sha256": item["packet_sha256"]} for item in packets],
        "prepared_files": rb.source_manifest(out),
        "python_preparation_version": platform.python_version(),
        "omp_version": None, "omp_version_origin": "must be observed at separately authorized execution",
        "supervision_contract": {"mode": "single managed process; no enclosing shell deadline",
            "managed_handle_required": True, "readiness_event": "acceptance_started",
            "readiness_meaning": "runner started only; not reviewer/provider success",
            "raw_stdout": "runner-stdout.txt", "raw_stderr": "runner-stderr.txt",
            "launch_claim": "launch.json, exclusive and permanent even on blocked/interrupted execution",
            "stop_policy": "manual externally supervised stop; no canary or automatic stop-on-first-failure",
            "interruption": "suspend runner before terminating isolated worker groups; retain observed PID/group/signal/exit evidence separately; never synthesize execution.json",
            "retry_policy": "none; no recovery/resume/replacement or best-of aggregation"}}
    rb.save_json(out / "preparation.json", preparation)
    rb.freeze_snapshot(out)
    return preparation


def validate_preparation(out):
    out = rs._root(out, "prepared acceptance")
    preparation = review.load_json(out / "preparation.json")
    required = {"kind": "fresh-split-acceptance-offline-preparation", "model_requested": rb.MODEL,
                "reasoning_requested": "high", "timeout_seconds": 900, "jobs": 3,
                "expected_packets": 411, "expected_capture_slots": 798, "reused_initial_judgments": 0,
                "historical_sessions": 1, "baseline_revision": BASELINE}
    for field, value in required.items():
        if preparation.get(field) != value:
            raise review.ReviewError(f"prepared acceptance control differs: {field}")
    stored_scope = preparation.get("capture_scope")
    if stored_scope is None and preparation.get("candidate_revision") != CANDIDATE:
        raise review.ReviewError("fresh capture scope omitted or changed candidate identity")
    if stored_scope is not None and (not isinstance(stored_scope, dict)
            or not stored_scope.get("capture_preparation") or not stored_scope.get("package_smoke_proof")
            or any(not Path(stored_scope[key]).is_absolute()
                   for key in ("capture_preparation", "package_smoke_proof"))):
        raise review.ReviewError("fresh capture scope paths omitted or not absolute")
    review.verify_files(out, preparation["prepared_files"], "prepared acceptance")
    for name, checksum in preparation["external_files"].items():
        path = Path(name)
        if not path.is_absolute() or path.is_symlink() or rb.digest(path) != checksum:
            raise review.ReviewError(f"retained external binding changed: {name}")
    corpus, boundary = review.preflight(Path(preparation["results"]), Path(preparation["boundary_results"]))
    evals = rs._root(Path(preparation["live_evals"]), "live evaluator")
    scope = capture_scope(corpus, boundary, stored_scope["capture_preparation"],
                          stored_scope["package_smoke_proof"]) if stored_scope else None
    if scope != stored_scope or preparation["candidate_revision"] != corpus["manifest"]["candidate_revision"]:
        raise review.ReviewError("prepared fresh capture scope/identity differs")
    current_bindings(corpus, boundary, Path(preparation["candidate_root"]), evals, scope)
    for field in ("source_manifests", "evaluation_files", "fixtures"):
        if preparation.get(field) != corpus["manifest"][field]:
            raise review.ReviewError(f"prepared capture source bindings differ: {field}")
    manifest_hashes = {run["manifest"]["suite"]: rb.digest(run["root"] / "manifest.json")
                       for run in (corpus, boundary)}
    if preparation.get("capture_manifest_hashes") != manifest_hashes:
        raise review.ReviewError("prepared capture manifest hashes differ")
    dependencies, imports = dependency_closure(evals)
    provenance = out / "ai-review/provenance"
    expected_provenance = {**dependencies, "reviewer-system.txt": rb.digest(evals / "reviewer-system.txt"),
                           "omp-config.json": corpus["manifest"]["evaluation_files"]["omp-config.json"]}
    actual_provenance = {path.relative_to(provenance).as_posix(): rb.digest(path) for path in rs._walk_source(provenance)}
    if (actual_provenance != expected_provenance or actual_provenance != preparation["provenance_files"]
            or imports != preparation["dependency_imports"]):
        raise review.ReviewError("frozen/live evaluator dependency closure drift")
    packets, mappings = review.build_packets(corpus, boundary)
    if review.load_json(out / "ai-review/label-map.json") != mappings:
        raise review.ReviewError("prepared side map differs from retained captures")
    rows = preparation["packets"]
    if len(rows) != len(packets):
        raise review.ReviewError("prepared packet coverage differs")
    for item, row in zip(packets, rows):
        packet = item["packet"]
        expected_path = f"ai-review/packets/{packet['case_id']}/attempt-{packet['attempt']}/packet.json"
        if (row.get("case_id"), row.get("attempt"), row.get("suite"), row.get("path")) != (
                packet["case_id"], packet["attempt"], item["suite"], expected_path):
            raise review.ReviewError("prepared packet coverage/identity differs")
        if review.load_json(out / expected_path) != packet or rb.digest(out / expected_path) != row["sha256"]:
            raise review.ReviewError(f"prepared packet differs: {expected_path}")
        item.update(packet_path=expected_path.removeprefix("ai-review/"), packet_sha256=row["sha256"])
    supplemental = history.prepare_source_history(Path(preparation["source_review"]))
    if (review.load_json(out / "historical-packet.json") != supplemental["packet"]
            or review.load_json(out / "historical-first.json") != supplemental["first"]
            or supplemental["label_alignment"] != preparation["historical_label_alignment"]
            or (scope is not None and "historical_bindings" not in preparation)
            or supplemental["bindings"] != preparation.get("historical_bindings", supplemental["bindings"])
            or any(preparation["external_files"].get(path) != checksum
                   for path, checksum in supplemental["bindings"].items())
            or _historical_provenance(Path(preparation["source_review"]), provenance)
                   != preparation["historical_provenance_difference"]):
        raise review.ReviewError("prepared historical adjudication differs")
    ancillary = fresh_ancillary_evidence(corpus, boundary, scope) if scope else ancillary_evidence(corpus)
    if any(preparation["external_files"].get(path) != checksum for path, checksum in ancillary["bindings"].items()):
        raise review.ReviewError("applicable context/packaging external bindings omitted")
    if ancillary != preparation["ancillary_evidence"]:
        raise review.ReviewError("applicable context/packaging bindings differ")
    expected_gates = {"capture_bindings_valid": True, "current_runtime_inputs_match": True,
                      "packet_coverage_complete": True, "historical_packet_complete": True, **ancillary["gates"]}
    if preparation.get("gates") != expected_gates:
        raise review.ReviewError("preparation gate bindings differ")
    from review_acceptance import future_command
    handle = "scenario-" + out.name
    if preparation.get("future_execution") != {"managed_handle": handle, "argv": future_command(out, handle)}:
        raise review.ReviewError("prepared execution argv/managed handle differs")
    return {"preparation": preparation, "packets": packets, "mappings": mappings,
            "historical_packet": supplemental["packet"], "historical_first": supplemental["first"],
            "provenance": provenance}
