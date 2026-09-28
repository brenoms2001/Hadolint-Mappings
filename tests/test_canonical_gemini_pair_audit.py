import copy
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

import audit_gold_standard_gemini as auditor


def valid_response(record, verdict="NO", confidence=5):
    return {
        "pair_id": record["prompt_pair_id"],
        "verdict": verdict,
        "relation_type": "unrestricted raw value",
        "directness": "none",
        "confidence": confidence,
        "security_objective": "Objective",
        "justification": "Justification",
        "caveat": "None",
    }


def merged_result(record, config):
    return auditor.merge_result(record, valid_response(record), config)


class CanonicalAuditFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = auditor.load_config()
        cls.state = auditor.preflight(cls.config)
        cls.fingerprint = auditor.build_run_fingerprint(cls.state)


class PromptAndSchemaTests(CanonicalAuditFixture):
    def test_prompt_template_hash_is_frozen(self):
        prompt_path = auditor.resolve_path(self.config["prompt_path"])
        self.assertEqual(
            auditor.sha256_file(prompt_path), auditor.EXPECTED_PROMPT_SHA256
        )
        self.assertEqual(
            auditor.EXPECTED_PROMPT_SHA256,
            "e328d92c192e420694e57820e03ebef575bfebb48bd5f23df62499d2586390e5",
        )

    def test_rendered_prompt_matches_historical_substitution_semantics(self):
        record = self.state["records"][0]
        rendered = auditor.render_prompt([record], self.config)
        template = auditor.resolve_path(self.config["prompt_path"]).read_text(
            encoding="utf-8"
        )
        payload = [
            {
                "pair_id": record["prompt_pair_id"],
                "source": record["source"],
                "source_id": record["source_id"],
                "source_title": record["source_title"],
                "problematic_code": record["problematic_code"],
                "correct_code": record["correct_code"],
                "rationale": record["rationale"],
                "exceptions": record["exceptions"],
                "rank": record["rank"],
                "target_id": record["target_id"],
                "target_type": record["target_type"],
                "parent_sr": record["parent_sr"],
                "foundational_requirement": record["foundational_requirement"],
                "target_title": record["target_title"],
                "target_text": record["target_text"],
                "target_rationale": record["target_rationale"],
                "rationale_source_pages": record["rationale_source_pages"],
                "raw_cosine": record["raw_cosine"],
                "relative_score": record["relative_score"],
                "top1_relative_score": record["top1_relative_score"],
                "top2_relative_score": record["top2_relative_score"],
                "top1_top2_gap": record["top1_top2_gap"],
                "gap_bin": record["gap_bin"],
            }
        ]
        historical = template.replace(
            self.config["prompt_marker"],
            json.dumps(payload, ensure_ascii=False, indent=2),
        )
        self.assertEqual(rendered.encode("utf-8"), historical.encode("utf-8"))
        self.assertTrue(rendered.startswith("\nYou are performing a PRELIMINARY"))
        self.assertTrue(rendered.endswith("\n"))

    def test_response_schema_hash_is_frozen(self):
        self.assertEqual(
            auditor.response_schema_sha256(), auditor.EXPECTED_SCHEMA_SHA256
        )
        properties = auditor.GEMINI_RESPONSE_SCHEMA["items"]["properties"]
        self.assertNotIn("enum", properties["relation_type"])
        self.assertNotIn("enum", properties["directness"])

    def test_boolean_confidence_is_rejected(self):
        record = self.state["records"][0]
        with self.assertRaisesRegex(auditor.ResponseValidationError, "not bool"):
            auditor.validate_gemini_results([record], [valid_response(record, confidence=True)])

    def test_config_is_executable_authority(self):
        changed = copy.deepcopy(self.config)
        changed["batch_size"] = 6
        with tempfile.TemporaryDirectory(dir=auditor.ROOT) as directory:
            path = Path(directory) / "config.yaml"
            path.write_text(yaml.safe_dump(changed), encoding="utf-8")
            with self.assertRaisesRegex(
                auditor.AuditConfigurationError, "batch_size"
            ):
                auditor.load_config(path)


class CanonicalPreflightTests(CanonicalAuditFixture):
    def test_canonical_hashes_counts_and_context_validate(self):
        summary = auditor.preflight_summary(self.state)
        self.assertEqual(summary["gemini_requests_made"], 0)
        self.assertEqual(summary["source_count"], 595)
        self.assertEqual(summary["pair_count"], 4149)
        self.assertEqual(summary["candidate_sha256"], auditor.EXPECTED_CANDIDATE_SHA256)
        self.assertEqual(summary["source_sha256"], auditor.EXPECTED_SOURCE_SHA256)
        self.assertEqual(summary["clean_iec_sha256"], auditor.EXPECTED_CLEAN_IEC_SHA256)
        self.assertEqual(
            summary["enriched_iec_sha256"], auditor.EXPECTED_ENRICHED_IEC_SHA256
        )

    def test_preflight_never_creates_gemini_client(self):
        with mock.patch.object(auditor, "create_client") as create_client:
            state = auditor.preflight()
        create_client.assert_not_called()
        self.assertEqual(len(state["records"]), 4149)

    def test_hash_binding_rejects_each_input_category(self):
        with tempfile.TemporaryDirectory(dir=auditor.ROOT) as directory:
            path = Path(directory) / "artifact"
            path.write_bytes(b"wrong")
            for label in ("candidate", "source", "clean IEC", "enriched IEC"):
                with self.subTest(label=label):
                    with self.assertRaisesRegex(auditor.PreflightError, "SHA-256"):
                        auditor.require_file_hash(path, "0" * 64, label)

    def test_sr_parent_representation_remains_null(self):
        sr = next(
            record
            for record in self.state["records"]
            if record["target_type"] == "SR"
        )
        self.assertIsNone(sr["parent_sr"])

    def test_full_precision_derived_values(self):
        records = self.state["records"]
        first_rule = [r for r in records if r["source_id"] == records[0]["source_id"]]
        expected_gap = first_rule[0]["relative_score"] - first_rule[1]["relative_score"]
        self.assertEqual(first_rule[0]["top1_top2_gap"], expected_gap)
        self.assertEqual(first_rule[1]["top1_top2_gap"], expected_gap)
        singleton = next(record for record in records if record["top2_relative_score"] is None)
        self.assertIsNone(singleton["top1_top2_gap"])
        self.assertIsNone(singleton["gap_bin"])

    def test_gap_bin_boundaries(self):
        cases = {
            None: None,
            0.0: "very_low_gap",
            0.049999999: "very_low_gap",
            0.05: "low_gap",
            0.10: "medium_gap",
            0.20: "high_gap",
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(auditor.classify_gap(value), expected)


class IdentityAndManifestTests(CanonicalAuditFixture):
    def test_preparation_artifacts_are_hash_frozen(self):
        freeze = auditor.load_json(auditor.ROOT / "manifests/canonical_artifacts.json")
        preparation = freeze["artifacts"]["canonical_pair_audit_preparation"]
        artifacts = {
            "auditor": preparation["auditor_path"],
            "config": preparation["config_path"],
            "prompt": preparation["prompt_path"],
            "pair_manifest": preparation["pair_manifest_path"],
            "batch_manifest": preparation["batch_manifest_path"],
        }
        for name, relative_path in artifacts.items():
            with self.subTest(name=name):
                self.assertEqual(
                    auditor.sha256_file(auditor.ROOT / relative_path),
                    preparation[f"{name}_sha256"],
                )
        self.assertEqual(preparation["response_schema_sha256"], auditor.EXPECTED_SCHEMA_SHA256)
        self.assertEqual(preparation["gemini_requests_made"], 0)

    def test_canonical_identity_is_stable_and_rank_independent(self):
        first = self.state["records"][0]
        expected_payload = {
            "source": first["source"],
            "source_id": first["source_id"],
            "target_id": first["target_id"],
        }
        expected = "pair-v1:" + hashlib.sha256(
            json.dumps(
                expected_payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        self.assertEqual(first["canonical_pair_id"], expected)
        self.assertNotIn("rank_", first["canonical_pair_id"])

    def test_prompt_pair_id_preserves_historical_format(self):
        first = self.state["records"][0]
        self.assertEqual(
            first["prompt_pair_id"],
            f"{first['source']}:{first['source_id']}:rank_{first['rank']}:{first['target_id']}",
        )
        self.assertEqual(first["pair_id"], first["prompt_pair_id"])

    def test_pair_manifest_is_complete_unique_and_frozen(self):
        manifest = self.state["pair_manifest"]
        ids = [item["canonical_pair_id"] for item in manifest["pairs"]]
        self.assertEqual(manifest["pair_count"], 4149)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            self.state["pair_manifest_sha256"],
            self.config["canonical"]["pair_manifest_sha256"],
        )

    def test_batch_manifest_has_exact_deterministic_membership(self):
        manifest = self.state["batch_manifest"]
        sizes = [item["size"] for item in manifest["batches"]]
        self.assertEqual(len(sizes), 830)
        self.assertEqual(sizes[:-1], [5] * 829)
        self.assertEqual(sizes[-1], 4)
        rebuilt = auditor.build_batch_manifest(
            self.state["records"],
            self.state["pair_manifest_sha256"],
            self.config["batch_size"],
        )
        self.assertEqual(rebuilt, manifest)
        self.assertEqual(
            self.state["batch_manifest_sha256"],
            self.config["canonical"]["batch_manifest_sha256"],
        )


class CheckpointAndResumeTests(CanonicalAuditFixture):
    def checkpoint_with_first_batch(self):
        checkpoint = auditor.new_checkpoint(self.fingerprint)
        first_spec = self.state["batch_manifest"]["batches"][0]
        records = auditor._records_for_batch(self.state, first_spec)
        checkpoint["completed_batches"][first_spec["batch_id"]] = {
            "status": "completed",
            "membership_sha256": first_spec["membership_sha256"],
            "request_tree": {"attempts": [], "children": []},
            "results": [merged_result(record, self.config) for record in records],
        }
        return checkpoint

    def test_resume_skips_only_whole_completed_batches(self):
        checkpoint = self.checkpoint_with_first_batch()
        pending = auditor.pending_batch_specs(self.state, checkpoint)
        self.assertEqual(len(pending), 829)
        self.assertEqual(
            pending[0]["batch_id"], self.state["batch_manifest"]["batches"][1]["batch_id"]
        )

    def test_incomplete_batch_is_rerun_with_original_membership(self):
        checkpoint = auditor.new_checkpoint(self.fingerprint)
        first_spec = self.state["batch_manifest"]["batches"][0]
        checkpoint["failed_batch"] = {
            "batch_id": first_spec["batch_id"],
            "partial_results": ["must-not-be-used"],
        }
        pending = auditor.pending_batch_specs(self.state, checkpoint)
        self.assertEqual(pending[0], first_spec)
        records = auditor._records_for_batch(self.state, pending[0])
        self.assertEqual(
            [record["canonical_pair_id"] for record in records],
            first_spec["canonical_pair_ids"],
        )

    def test_historical_checkpoint_is_rejected_before_results(self):
        historical = (
            auditor.ROOT
            / "data/output/mappings/iec/inspection/gold_standard/gemini_audit/full/"
            "iec_gold_standard_gemini_audit_checkpoint.json"
        )
        with self.assertRaisesRegex(RuntimeError, "fingerprint mismatch"):
            auditor.load_checkpoint(historical, self.fingerprint, self.state)

    def test_every_run_fingerprint_category_is_exact(self):
        for key in self.fingerprint:
            with self.subTest(key=key), tempfile.TemporaryDirectory(
                dir=auditor.ROOT
            ) as directory:
                changed = copy.deepcopy(self.fingerprint)
                changed[key] = {"mismatch": True}
                path = Path(directory) / "checkpoint.json"
                path.write_text(
                    json.dumps(
                        {
                            "run_fingerprint": changed,
                            "completed_batches": {
                                "malicious": {"results": ["must-not-load"]}
                            },
                        }
                    ),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(RuntimeError, "fingerprint mismatch"):
                    auditor.load_checkpoint(path, self.fingerprint, self.state)

    def test_checkpoint_round_trip_and_atomic_failure(self):
        checkpoint = self.checkpoint_with_first_batch()
        with tempfile.TemporaryDirectory(dir=auditor.ROOT) as directory:
            path = Path(directory) / "checkpoint.json"
            auditor.save_checkpoint(path, checkpoint)
            loaded = auditor.load_checkpoint(path, self.fingerprint, self.state)
            self.assertEqual(
                set(loaded["completed_batches"]), set(checkpoint["completed_batches"])
            )
            original = path.read_bytes()
            with mock.patch.object(auditor.os, "replace", side_effect=OSError("stop")):
                with self.assertRaises(OSError):
                    auditor.atomic_write(path, b"replacement")
            self.assertEqual(path.read_bytes(), original)


class AdaptiveSplitTests(CanonicalAuditFixture):
    def setUp(self):
        self.batch = self.state["records"][:5]

    def test_only_validation_failure_splits_in_original_order(self):
        calls = []

        def call(records, node):
            calls.append([record["canonical_pair_id"] for record in records])
            if len(records) == 5:
                raise auditor.GeminiBatchError("invalid", "validation")
            return [valid_response(record) for record in records]

        results, tree = auditor.process_batch_adaptive(self.batch, call)
        self.assertEqual([len(item) for item in calls], [5, 2, 3])
        self.assertEqual(
            [item["pair_id"] for item in results],
            [record["prompt_pair_id"] for record in self.batch],
        )
        self.assertEqual(tree["status"], "completed_after_split")
        self.assertEqual(len(tree["children"]), 2)

    def test_terminal_failures_never_split(self):
        for kind in ("quota", "authentication", "configuration", "transient", "api"):
            calls = []

            def call(records, node, failure_kind=kind):
                calls.append(len(records))
                raise auditor.GeminiBatchError("terminal", failure_kind)

            with self.subTest(kind=kind):
                with self.assertRaises(auditor.GeminiBatchError) as caught:
                    auditor.process_batch_adaptive(self.batch, call)
                self.assertEqual(calls, [5])
                self.assertEqual(caught.exception.request_tree["children"], [])


class ResultIntegrityTests(CanonicalAuditFixture):
    def setUp(self):
        self.batch = self.state["records"][:2]

    def test_missing_extra_and_duplicate_responses_are_rejected(self):
        valid = [valid_response(record) for record in self.batch]
        cases = {
            "missing": valid[:1],
            "extra": valid
            + [dict(valid[0], pair_id="unexpected:pair")],
            "duplicate": [valid[0], valid[0]],
        }
        for label, responses in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(auditor.ResponseValidationError):
                    auditor.validate_gemini_results(self.batch, responses)

    def test_final_validation_requires_exact_canonical_set(self):
        results = [merged_result(record, self.config) for record in self.state["records"]]
        auditor.validate_final_results(self.state, results)
        with self.assertRaises(auditor.ResponseValidationError):
            auditor.validate_final_results(self.state, results[:-1])
        duplicate = results[:-1] + [results[0]]
        with self.assertRaises(auditor.ResponseValidationError):
            auditor.validate_final_results(self.state, duplicate)

    def test_raw_relation_and_directness_are_preserved(self):
        response = valid_response(self.batch[0])
        response["relation_type"] = "Mixed Case / arbitrary_value"
        response["directness"] = "Unrestricted Raw"
        merged = auditor.merge_result(self.batch[0], response, self.config)
        self.assertEqual(merged["llm_relation_type"], response["relation_type"])
        self.assertEqual(merged["llm_directness"], response["directness"])


class OutputIsolationTests(CanonicalAuditFixture):
    def test_namespace_is_canonical_and_not_historical(self):
        paths = auditor.output_paths(self.config)
        self.assertIn("/gemini_audit/canonical/", str(paths["directory"]))
        self.assertNotIn("/gemini_audit/full/", str(paths["directory"]))

    def test_historical_namespace_is_refused(self):
        paths = {
            "directory": auditor.HISTORICAL_OUTPUT_NAMESPACE,
            "json": auditor.HISTORICAL_OUTPUT_NAMESPACE / "result.json",
            "provenance": auditor.HISTORICAL_OUTPUT_NAMESPACE / "provenance.json",
        }
        with self.assertRaisesRegex(
            auditor.AuditConfigurationError, "historical"
        ):
            auditor.ensure_output_namespace(paths)

    def test_completed_output_overwrite_is_refused(self):
        with tempfile.TemporaryDirectory(dir=auditor.ROOT) as directory:
            base = Path(directory)
            result = base / "result.json"
            result.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "overwrite"):
                auditor.ensure_output_namespace(
                    {
                        "directory": base,
                        "json": result,
                        "provenance": base / "provenance.json",
                    }
                )


if __name__ == "__main__":
    unittest.main()
