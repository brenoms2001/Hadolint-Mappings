import copy
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

import inspect_iec_matches as matcher


class CanonicalInputValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = matcher.validate_canonical_inputs()

    def test_canonical_inputs_and_hashes_validate(self):
        self.assertEqual(self.inputs.source_matrix.shape, (595, 1024))
        self.assertEqual(self.inputs.target_matrix.shape, (100, 1024))
        self.assertEqual(self.inputs.source_matrix.dtype, np.float32)
        self.assertEqual(self.inputs.target_matrix.dtype, np.float32)
        self.assertEqual(
            self.inputs.hashes["source_cache_sha256"],
            "0ce1921e4a4b021eafe735edd49fbbe05ea7c40839df9a6e154662c83b4ee761",
        )
        self.assertEqual(
            self.inputs.hashes["target_cache_sha256"],
            "3ba7d6cc0c7056f63f04f0569d25abf795773555536b227356b6586c8bfa7886",
        )

    def test_hash_mismatch_is_fatal(self):
        with tempfile.TemporaryDirectory(dir=matcher.ROOT) as directory:
            path = Path(directory) / "artifact.bin"
            path.write_bytes(b"content")
            with self.assertRaisesRegex(
                matcher.MatchingValidationError, "SHA-256 mismatch"
            ):
                matcher.require_file_hash(path, "0" * 64, "synthetic")

    def test_missing_and_extra_embedding_ids_are_fatal(self):
        vector = np.array([1.0, 0.0], dtype=np.float32)
        with self.assertRaisesRegex(
            matcher.MatchingValidationError, "ID coverage mismatch"
        ):
            matcher.validate_vector_map(
                {"A": vector, "C": vector}, ["A", "B"], 2, 1e-5, "synthetic"
            )

    def test_duplicate_dataset_ids_are_fatal(self):
        data = {
            "requirements": [
                {"id": "SR 1.1", "title": "A", "text": "A"},
                {"id": "SR 1.1", "title": "B", "text": "B"},
            ]
        }
        with tempfile.TemporaryDirectory(dir=matcher.ROOT) as directory:
            path = Path(directory) / "target.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(
                matcher.MatchingValidationError, "duplicate IDs"
            ):
                matcher._load_target_dataset(path)

    def test_invalid_vectors_are_fatal(self):
        valid = np.array([1.0, 0.0], dtype=np.float32)
        cases = {
            "dtype": np.array([1.0, 0.0], dtype=np.float64),
            "shape": np.array([1.0, 0.0, 0.0], dtype=np.float32),
            "non-finite": np.array([np.nan, 0.0], dtype=np.float32),
            "norm": np.array([2.0, 0.0], dtype=np.float32),
        }
        for label, invalid in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(matcher.MatchingValidationError):
                    matcher.validate_vector_map(
                        {"A": valid, "B": invalid},
                        ["A", "B"],
                        2,
                        1e-5,
                        "synthetic",
                    )


class NumericalSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.config, _ = matcher.load_matching_config()

    def test_cosine_shape_clamp_power_and_linf(self):
        source = np.array([[1.0, 0.0]], dtype=np.float32)
        target = np.array(
            [[1.0, 0.0], [0.5, np.sqrt(0.75)], [-1.0, 0.0]],
            dtype=np.float32,
        )
        raw, relative = matcher.compute_score_matrices(source, target, self.config)
        self.assertEqual(raw.shape, (1, 3))
        self.assertEqual(raw.dtype, np.float32)
        self.assertEqual(relative.dtype, np.float32)
        self.assertEqual(float(relative[0, 0]), 1.0)
        self.assertAlmostEqual(float(relative[0, 1]), 0.5**5.5, places=7)
        self.assertEqual(float(relative[0, 2]), 0.0)

    def test_all_zero_row_has_no_candidates(self):
        source = np.array([[1.0, 0.0]], dtype=np.float32)
        target = np.array([[-1.0, 0.0], [-0.5, -0.5]], dtype=np.float32)
        _, relative = matcher.compute_score_matrices(source, target, self.config)
        np.testing.assert_array_equal(relative, np.zeros_like(relative))
        self.assertEqual(len(matcher.select_target_indices(relative[0], self.config)), 0)

    def test_float32_threshold_edges_are_inclusive(self):
        threshold = np.float32(self.config["matching"]["threshold"]["value"])
        scores = np.array(
            [
                np.nextafter(threshold, np.float32(0.0)),
                threshold,
                np.nextafter(threshold, np.float32(1.0)),
            ],
            dtype=np.float32,
        )
        selected = matcher.select_target_indices(scores, self.config)
        self.assertEqual(selected.tolist(), [2, 1])

    def test_threshold_precedes_top_k_and_top_k_is_bounded(self):
        scores = np.linspace(1.0, 0.69, 12, dtype=np.float32)
        selected = matcher.select_target_indices(scores, self.config)
        self.assertEqual(len(selected), 10)
        self.assertTrue(np.all(scores[selected] >= np.float32(0.68)))

    def test_ties_use_frozen_target_order_including_rank_10_boundary(self):
        scores = np.ones(11, dtype=np.float32)
        selected = matcher.select_target_indices(scores, self.config)
        self.assertEqual(selected.tolist(), list(range(10)))

    def test_config_is_threshold_authority(self):
        config = copy.deepcopy(self.config)
        config["matching"]["threshold"]["value"] = 0.75
        scores = np.array([0.74, 0.75, 0.76], dtype=np.float32)
        self.assertEqual(
            matcher.select_target_indices(scores, config).tolist(), [2, 1]
        )

    def test_unsupported_config_semantics_are_fatal(self):
        config = copy.deepcopy(self.config)
        config["matching"]["threshold"]["operator"] = ">"
        with tempfile.TemporaryDirectory(dir=matcher.ROOT) as directory:
            path = Path(directory) / "matching.yaml"
            import yaml

            path.write_text(yaml.safe_dump(config), encoding="utf-8")
            with self.assertRaisesRegex(
                matcher.MatchingValidationError, "Unsupported"
            ):
                matcher.load_matching_config(path)


class MatchingPayloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = matcher.validate_canonical_inputs()
        cls.first = matcher.build_matching_payload(cls.inputs)

    def test_payload_is_valid_and_complete(self):
        observed = matcher.validate_matching_payload(self.first, self.inputs)
        self.assertEqual(observed["source_count"], 595)
        self.assertEqual(observed["target_count"], 100)

    def test_scores_retain_float32_precision_in_json(self):
        match = next(
            match
            for rules in self.first["sources"].values()
            for entry in rules.values()
            for match in entry["matches"]
            if match["raw_cosine"] != round(match["raw_cosine"], 6)
        )
        content = matcher.canonical_json_bytes({"score": match["raw_cosine"]})
        self.assertIn(repr(match["raw_cosine"]).encode("ascii"), content)

    def test_repeat_run_payload_is_byte_identical(self):
        second = matcher.build_matching_payload(self.inputs)
        self.assertEqual(
            matcher.canonical_json_bytes(self.first),
            matcher.canonical_json_bytes(second),
        )


if __name__ == "__main__":
    unittest.main()
