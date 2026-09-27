import copy
import unittest

import build_gold_standard as builder
import inspect_iec_matches as matcher


class CandidateBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (
            cls.matching,
            _,
            cls.inputs,
            cls.matching_hashes,
        ) = builder.load_canonical_matching()
        cls.candidates = builder.build_candidate_payload(
            cls.matching, cls.inputs, cls.matching_hashes
        )

    def validate(self, payload):
        return builder.validate_candidate_payload(
            payload, self.matching, self.inputs, self.matching_hashes
        )

    def first_entry(self, payload=None):
        data = payload or self.candidates
        source = next(iter(data["sources"]))
        source_id = next(iter(data["sources"][source]))
        return source, source_id, data["sources"][source][source_id]

    def test_complete_canonical_candidate_payload(self):
        observed = self.validate(self.candidates)
        self.assertEqual(observed["source_count"], 595)
        self.assertEqual(observed["match_count"], self.matching["metadata"]["observed"]["match_count"])
        self.assertTrue(
            all(
                0 <= entry["candidate_count"] <= 10
                for rules in self.candidates["sources"].values()
                for entry in rules.values()
            )
        )

    def test_zero_candidate_source_is_supported(self):
        matching = copy.deepcopy(self.matching)
        source, source_id, entry = self.first_entry(matching)
        entry["matches"] = []
        entry["candidate_count"] = 0
        target_by_id = {record["id"]: record for record in self.inputs.target_records}
        matching["metadata"]["observed"] = matcher._observed_counts(
            matching["sources"], target_by_id
        )
        payload = builder.build_candidate_payload(
            matching, self.inputs, self.matching_hashes
        )
        self.assertEqual(payload["sources"][source][source_id]["candidate_count"], 0)

    def test_incomplete_source_coverage_is_fatal(self):
        matching = copy.deepcopy(self.matching)
        source, source_id, _ = self.first_entry(matching)
        del matching["sources"][source][source_id]
        with self.assertRaisesRegex(builder.CandidateValidationError, "missing source"):
            builder.build_candidate_payload(
                matching, self.inputs, self.matching_hashes
            )

    def test_invalid_target_id_is_fatal(self):
        matching = copy.deepcopy(self.matching)
        _, _, entry = self.first_entry(matching)
        entry["matches"][0]["target_id"] = "NOT AN IEC ID"
        with self.assertRaisesRegex(builder.CandidateValidationError, "Unknown target"):
            builder.build_candidate_payload(
                matching, self.inputs, self.matching_hashes
            )

    def test_rank_continuity_is_fatal(self):
        payload = copy.deepcopy(self.candidates)
        _, _, entry = self.first_entry(payload)
        entry["matches"][0]["rank"] = 2
        with self.assertRaisesRegex(builder.CandidateValidationError, "ranks"):
            self.validate(payload)

    def test_duplicate_target_is_fatal(self):
        payload = copy.deepcopy(self.candidates)
        _, _, entry = self.first_entry(payload)
        entry["matches"][1]["target_id"] = entry["matches"][0]["target_id"]
        with self.assertRaisesRegex(builder.CandidateValidationError, "Duplicate target"):
            self.validate(payload)

    def test_candidate_count_mismatch_is_fatal(self):
        payload = copy.deepcopy(self.candidates)
        _, _, entry = self.first_entry(payload)
        entry["candidate_count"] += 1
        with self.assertRaisesRegex(builder.CandidateValidationError, "count mismatch"):
            self.validate(payload)

    def test_source_order_mismatch_is_fatal(self):
        payload = copy.deepcopy(self.candidates)
        rules = payload["sources"]["hadolint"]
        first, second = list(rules)[:2]
        reordered = {second: rules[second], first: rules[first]}
        reordered.update({key: value for key, value in rules.items() if key not in {first, second}})
        payload["sources"]["hadolint"] = reordered
        with self.assertRaisesRegex(builder.CandidateValidationError, "order or coverage"):
            self.validate(payload)

    def test_candidate_order_and_full_precision_equal_matching(self):
        for source, rules in self.candidates["sources"].items():
            for source_id, entry in rules.items():
                matching_records = self.matching["sources"][source][source_id]["matches"]
                self.assertEqual(
                    [item["target_id"] for item in entry["matches"]],
                    [item["target_id"] for item in matching_records],
                )
                self.assertEqual(
                    [item["raw_cosine"] for item in entry["matches"]],
                    [item["raw_cosine"] for item in matching_records],
                )
                self.assertEqual(
                    [item["relative_score"] for item in entry["matches"]],
                    [item["relative_score"] for item in matching_records],
                )

    def test_human_fields_are_null_and_llm_fields_absent(self):
        forbidden_fragments = ("gemini", "llm", "verdict", "reasoning")
        for rules in self.candidates["sources"].values():
            for entry in rules.values():
                for candidate in entry["matches"]:
                    self.assertEqual(set(candidate), builder.CANDIDATE_KEYS)
                    self.assertIsNone(candidate["human_label"])
                    self.assertIsNone(candidate["human_confidence"])
                    self.assertIsNone(candidate["human_notes"])
                    self.assertFalse(
                        any(
                            fragment in key.lower()
                            for key in candidate
                            for fragment in forbidden_fragments
                        )
                    )

    def test_provenance_hashes_are_propagated(self):
        provenance = self.candidates["metadata"]["provenance"]
        for key, expected in self.matching_hashes.items():
            self.assertEqual(provenance[key], expected)
        self.assertEqual(
            provenance["source_cache_sha256"],
            self.matching["metadata"]["provenance"]["source_cache_sha256"],
        )

    def test_repeated_candidate_payload_is_byte_identical(self):
        second = builder.build_candidate_payload(
            self.matching, self.inputs, self.matching_hashes
        )
        self.assertEqual(
            matcher.canonical_json_bytes(self.candidates),
            matcher.canonical_json_bytes(second),
        )


if __name__ == "__main__":
    unittest.main()
