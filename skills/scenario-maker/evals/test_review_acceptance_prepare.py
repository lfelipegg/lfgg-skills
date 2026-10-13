"""Offline rejection of changed capture inputs and unbound evaluator imports."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import review_acceptance_prepare as prepare
import review_split as review


class CurrentBindingsTest(unittest.TestCase):
    def setUp(self):
        self.live = {"candidate_files": {"scenario-maker": {"SKILL.md": "source-hash"}},
                     "evaluation_files": {"cases.jsonl": "input-hash"},
                     "fixture_files": {"source.png": "fixture-hash"}}
        self.corpus = {"baseline": Path("baseline"), "manifest": {
            "suite": "corpus", "baseline_revision": prepare.BASELINE, "candidate_revision": prepare.CANDIDATE,
            "source_manifests": {"candidate": copy.deepcopy(self.live["candidate_files"])},
            "evaluation_files": copy.deepcopy(self.live["evaluation_files"]),
            "fixtures": copy.deepcopy(self.live["fixture_files"])},
            "captures": {index: {"available": True, "issues": []} for index in range(744)}}
        self.boundary = {"manifest": {"suite": "boundary"},
                         "captures": {index: {"available": True, "issues": []} for index in range(54)}}

    def test_each_current_source_input_or_fixture_drift_blocks_capture_reuse(self):
        for field, name in (("candidate_files", "scenario-maker"), ("evaluation_files", "cases.jsonl"),
                            ("fixture_files", "source.png")):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.live)
                if field == "candidate_files":
                    changed[field][name]["SKILL.md"] = "changed-prompt-hash"
                else:
                    changed[field][name] = "changed-content-hash"
                with mock.patch.object(prepare.rs, "preflight", return_value=changed):
                    with self.assertRaisesRegex(review.ReviewError, "drift"):
                        prepare.current_bindings(self.corpus, self.boundary, Path("skills"), Path("evals"))

    def test_unavailable_or_missing_boundary_capture_blocks_preparation(self):
        for mutation in ("unavailable", "missing"):
            with self.subTest(mutation=mutation):
                boundary = copy.deepcopy(self.boundary)
                if mutation == "unavailable":
                    boundary["captures"][0] = {"available": False, "issues": ["final output missing"]}
                else:
                    del boundary["captures"][0]
                with mock.patch.object(prepare.rs, "preflight", return_value=self.live):
                    with self.assertRaisesRegex(review.ReviewError, "798"):
                        prepare.current_bindings(self.corpus, boundary, Path("skills"), Path("evals"))


class PreparationSafetyTest(unittest.TestCase):
    def test_output_inside_or_above_retained_evidence_is_rejected_without_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            retained = root / "retained"
            retained.mkdir()
            out = retained / "new-review"
            with self.assertRaisesRegex(review.ReviewError, "overlaps"):
                prepare._outside(out, (retained,))
            self.assertFalse(out.exists())
            missing_parent = root / "future"
            with self.assertRaisesRegex(review.ReviewError, "overlaps"):
                prepare._outside(missing_parent, (missing_parent / "retained",))
            self.assertFalse(missing_parent.exists())

    def test_symlink_output_parent_cannot_redirect_into_old_campaign(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            retained = root / "retained"
            retained.mkdir()
            alias = root / "alias"
            alias.symlink_to(retained, target_is_directory=True)
            with self.assertRaisesRegex(review.ReviewError, "non-symlink"):
                prepare._outside(alias / "new-review", ())
            self.assertFalse((retained / "new-review").exists())

    def test_nonstdlib_import_cannot_escape_frozen_evaluator_closure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "review_acceptance.py").write_text("import unbound_paid_client\n", encoding="utf-8")
            with self.assertRaisesRegex(review.ReviewError, "unbound evaluator dependency"):
                prepare.dependency_closure(root)


class FrozenBindingsTest(unittest.TestCase):
    def test_packet_or_historical_source_tamper_refuses_before_capture_preflight(self):
        for target in ("packet.json", "historical-review.json"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                out = root / "prepared"
                out.mkdir()
                packet = out / "packet.json"
                original = root / "historical-review.json"
                packet.write_text('{"request": "Preserve source"}\n', encoding="utf-8")
                original.write_text('{"valid": true}\n', encoding="utf-8")
                metadata = {"kind": "fresh-split-acceptance-offline-preparation",
                    "model_requested": prepare.rb.MODEL, "reasoning_requested": "high",
                    "timeout_seconds": 900, "jobs": 3, "expected_packets": 411,
                    "expected_capture_slots": 798, "reused_initial_judgments": 0,
                    "historical_sessions": 1, "baseline_revision": prepare.BASELINE,
                    "candidate_revision": prepare.CANDIDATE,
                    "prepared_files": {"packet.json": prepare.rb.digest(packet)},
                    "external_files": {str(original): prepare.rb.digest(original)}}
                prepare.rb.save_json(out / "preparation.json", metadata)
                (packet if target == "packet.json" else original).write_text("changed\n", encoding="utf-8")
                with mock.patch.object(prepare.review, "preflight", side_effect=AssertionError("too late")):
                    with self.assertRaisesRegex(review.ReviewError, "hash mismatch|external binding changed"):
                        prepare.validate_preparation(out)


@unittest.skipUnless((prepare.EVALS / "comparisons/repaired-captures-20261011T214359Z").is_dir(),
                     "retained capture archive is not present locally")
class FreshScopeBindingsTest(unittest.TestCase):
    """Consume retained offline evidence, never execute a capture or reviewer."""
    @classmethod
    def setUpClass(cls):
        cls.root = prepare.EVALS / "comparisons/repaired-captures-20261011T214359Z"
        cls.smoke = prepare.EVALS / "comparisons/offline-repair-20261011T211940Z/offline-proof.json"
        cls.runs = [{"root": cls.root / suite,
                     "manifest": review.load_json(cls.root / suite / "manifest.json")}
                    for suite in ("corpus", "boundary")]
        cls.scope = prepare.capture_scope(*cls.runs, cls.root / "preparation.json", cls.smoke)
        cls.documents = {str(path): review.load_json(path) for path in (
            cls.root / "preparation.json", cls.smoke, cls.root / "context-proof.json",
            cls.root / "packaging-proof-binding.json", cls.root / "authorization.json",
            cls.root / "capture-outcome.json", cls.root / "managed-terminal.json")}

    def test_explicit_scope_binds_full_identity_and_absolute_external_inputs(self):
        self.assertNotEqual(self.scope["candidate_revision"], prepare.CANDIDATE)
        self.assertNotEqual(self.scope["candidate_revision"], self.documents[str(self.smoke)]["candidate_identity"])
        for path, checksum in self.scope["bindings"].items():
            self.assertTrue(Path(path).is_absolute())
            self.assertEqual(checksum, prepare.rb.digest(Path(path)))
        ancillary = prepare.fresh_ancillary_evidence(*self.runs, self.scope)
        self.assertTrue(all(ancillary["gates"].values()))
        self.assertEqual(ancillary["bindings"][str(self.smoke)], prepare.rb.digest(self.smoke))

    def test_one_scope_input_cannot_select_fresh_or_legacy_scope(self):
        for capture, smoke in ((self.root / "preparation.json", None), (None, self.smoke)):
            with self.subTest(capture=capture), self.assertRaisesRegex(review.ReviewError, "together"):
                prepare.capture_scope(*self.runs, capture, smoke)

    def test_fresh_current_sources_require_scope_and_reject_live_drift(self):
        runs = copy.deepcopy(self.runs)
        runs[0]["baseline"] = self.root / "before"
        for run, count in zip(runs, (744, 54)):
            run["captures"] = {index: {"available": True, "issues": []} for index in range(count)}
        manifest = runs[0]["manifest"]
        live = {"candidate_files": manifest["source_manifests"]["candidate"],
                "evaluation_files": manifest["evaluation_files"], "fixture_files": manifest["fixtures"]}
        with mock.patch.object(prepare.rs, "preflight", return_value=live):
            self.assertEqual(prepare.current_bindings(*runs, self.root / "skills", prepare.EVALS, self.scope), live)
            with self.assertRaisesRegex(review.ReviewError, "unchanged-capture scope"):
                prepare.current_bindings(*runs, self.root / "skills", prepare.EVALS)
        for field in live:
            changed = {**live, field: {}}
            with self.subTest(field=field), mock.patch.object(prepare.rs, "preflight", return_value=changed):
                with self.assertRaisesRegex(review.ReviewError, "drift"):
                    prepare.current_bindings(*runs, self.root / "skills", prepare.EVALS, self.scope)

    def test_boundary_source_or_root_drift_rejected(self):
        for field in ("candidate_revision", "source_manifests", "evaluation_files", "fixtures", "root"):
            runs = copy.deepcopy(self.runs)
            if field == "root":
                runs[1]["root"] = self.root / "another-boundary"
            else:
                runs[1]["manifest"][field] = "changed"
            with self.subTest(field=field), self.assertRaisesRegex(review.ReviewError, "bindings differ"):
                prepare.capture_scope(*runs, self.root / "preparation.json", self.smoke)

    def test_passing_labels_cannot_hide_ancillary_binding_or_control_drift(self):
        mutations = (
            ("context-proof.json", lambda d: d["trace_gate"]["suites"][1].update(root="old-campaign")),
            ("context-proof.json", lambda d: d["trace_gate"]["suites"][0].update(manifest_sha256="changed")),
            ("context-proof.json", lambda d: d["trace_gate"].update(captures_complete=False)),
            ("context-proof.json", lambda d: d["trace_gate"].update(consistency_errors=["missing trace"])),
            ("context-proof.json", lambda d: d["byte_gate"].update(failing_paths=["oversized"])),
            ("authorization.json", lambda d: d.update(reuse=True)),
            ("capture-outcome.json", lambda d: d["execution_summaries"]["boundary"].update(completed=53)),
            ("managed-terminal.json", lambda d: d.update(exit_code=1)),
            ("packaging-proof-binding.json", lambda d: d.update(offline_package_proof="different/offline-proof.json")),
            ("offline-proof.json", lambda d: d["packages"]["scenario-maker"].update(terminal_exit=1)),
            ("offline-proof.json", lambda d: d["packages"]["scenario-maker"]["manifest"].update(
                **{"SKILL.md": "different-source"})),
            ("offline-proof.json", lambda d: d["guide_hashes"].clear()),
        )
        for name, mutate in mutations:
            path = self.smoke if name == "offline-proof.json" else self.root / name
            changed = copy.deepcopy(self.documents[str(path)])
            mutate(changed)
            def load(path, changed_path=str(path), document=changed):
                return document if str(path) == changed_path else self.documents[str(path)]
            with self.subTest(name=name), mock.patch.object(review, "load_json", side_effect=load):
                with self.assertRaises(review.ReviewError):
                    prepare.fresh_ancillary_evidence(*self.runs, self.scope)

    def test_changed_identity_without_scope_refuses_before_capture_reads(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary)
            metadata = {"kind": "fresh-split-acceptance-offline-preparation", "model_requested": prepare.rb.MODEL,
                        "reasoning_requested": "high", "timeout_seconds": 900, "jobs": 3,
                        "expected_packets": 411, "expected_capture_slots": 798, "reused_initial_judgments": 0,
                        "historical_sessions": 1, "baseline_revision": prepare.BASELINE,
                        "candidate_revision": self.scope["candidate_revision"]}
            prepare.rb.save_json(out / "preparation.json", metadata)
            with mock.patch.object(review, "preflight", side_effect=AssertionError("capture read forbidden")):
                with self.assertRaisesRegex(review.ReviewError, "scope omitted"):
                    prepare.validate_preparation(out)


if __name__ == "__main__":
    unittest.main()
