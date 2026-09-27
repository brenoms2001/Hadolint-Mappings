import copy
import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import extract_hadolint_wiki as parser


class ParserUnitTests(unittest.TestCase):
    def parse(self, markdown, rule_id="DL9999", source="hadolint"):
        return parser.extract_rule_with_diagnostics(rule_id, source, markdown)

    def test_atx_title_and_missing_fields(self):
        rule, diagnostics = self.parse("# Semantic `title`\n\nText only.\n")
        self.assertEqual(rule["title"], "Semantic title")
        self.assertIsNone(rule["problematic_code"])
        self.assertIsNone(rule["correct_code"])
        self.assertEqual(len(diagnostics.warnings), 3)

    def test_setext_title(self):
        rule, _ = self.parse(
            "Semantic title\n==============\n\n### Rationale\nBecause.\n"
        )
        self.assertEqual(rule["title"], "Semantic title")
        self.assertEqual(rule["rationale"], "Because.")

    def test_heading_inside_fence_is_not_structural(self):
        rule, diagnostics = self.parse(
            "## Title\n\n### Problematic code\n```sh\n## Correct code\nfalse\n```\n"
            "\n### Correct code\n```sh\ntrue\n```\n"
        )
        self.assertEqual(rule["problematic_code"], "## Correct code\nfalse")
        self.assertEqual(rule["correct_code"], "true")
        self.assertEqual(diagnostics.section_occurrences["correct_code"], 1)

    def test_repeated_and_qualified_sections_preserve_order(self):
        rule, diagnostics = self.parse(
            "## Title\n\n### Problematic code #1\none\n\n"
            "### Problematic code #2\ntwo\n\n"
            "### Correct code (first)\nalpha\n\n"
            "### Correct code: (second)\nbeta\n"
        )
        self.assertEqual(
            rule["problematic_code"],
            "Problematic code #1\none\n\nProblematic code #2\ntwo",
        )
        self.assertEqual(
            rule["correct_code"],
            "Correct code (first)\nalpha\n\nCorrect code: (second)\nbeta",
        )
        self.assertEqual(diagnostics.section_occurrences["problematic_code"], 2)
        self.assertEqual(diagnostics.qualified_occurrences["correct_code"], 2)

    def test_peer_heading_ends_semantic_section(self):
        rule, _ = self.parse(
            "## Title\n\n### Rationale\nBecause.\n\n### Related resources\nLink.\n"
        )
        self.assertEqual(rule["rationale"], "Because.")

    def test_multiple_backtick_and_tilde_fences_remove_all_delimiters(self):
        rule, diagnostics = self.parse(
            "## Title\n\n### Correct code\nBefore.\n\n````bash\n  echo one  \n```\n````\n"
            "\n~~~sh\nprintf two\n~~~\n\nAfter.\n"
        )
        self.assertEqual(
            rule["correct_code"],
            "Before.\n\n  echo one  \n```\n\nprintf two\n\nAfter.",
        )
        # A shorter run inside a four-backtick block is code payload, not a
        # delimiter, and must be preserved exactly.
        self.assertNotIn("````", rule["correct_code"])
        self.assertNotIn("~~~", rule["correct_code"])
        self.assertEqual(diagnostics.fence_count, 2)
        self.assertEqual(diagnostics.fence_languages, {"bash": 1, "sh": 1})

    def test_unmatched_fence_is_fatal(self):
        with self.assertRaisesRegex(parser.ParserError, "unmatched fenced block"):
            self.parse("## Title\n\n### Correct code\n```sh\necho nope\n")

    def test_crlf_is_normalized_only_in_raw_markdown(self):
        markdown = "## Title\r\n\r\n### Rationale\r\nLine.  \r\n"
        rule, _ = self.parse(markdown)
        self.assertEqual(
            rule["raw_markdown"],
            "## Title\n\n### Rationale\nLine.  \n",
        )
        self.assertEqual(rule["rationale"], "Line.  ")

    def test_ambiguous_titles_are_fatal(self):
        with self.assertRaisesRegex(parser.ParserError, "ambiguous H1"):
            self.parse("# First\n\n# Second\n\n### Rationale\nText.\n")

    def test_generic_heading_is_not_a_title(self):
        with self.assertRaisesRegex(parser.ParserError, "no semantic title"):
            self.parse("## Example code\n\n### Rationale\nText.\n")

    def test_duplicate_normalized_ids_are_fatal(self):
        rules = {}
        parser.add_unique_rule(rules, {"id": "DL9999"})
        with self.assertRaisesRegex(parser.ParserError, "Duplicate normalized"):
            parser.add_unique_rule(rules, {"id": "DL9999"})

    def test_curation_cannot_replace_non_null_without_authorization(self):
        rule, diagnostics = self.parse("## Existing title\n")
        override = {
            ("hadolint", "DL9999", "title"): {
                "source": "hadolint",
                "source_id": "DL9999",
                "field": "title",
                "value": "Curated title",
                "reason": "Test",
                "authority": {"name": "Test", "url": "https://example.test"},
                "frozen_source_commit": "commit",
                "allow_replace_non_null": False,
                "source_evidence": {"location": "Test", "source_url": "https://example.test"},
                "curation_type": "official_rule_metadata",
                "value_sha256": parser.sha256_text("Curated title"),
            }
        }
        with self.assertRaisesRegex(parser.ParserError, "replace a non-null"):
            parser.apply_curations(rule, diagnostics, override, "commit")

    def test_duplicate_curation_entries_are_fatal(self):
        document = json.loads(parser.CURATION_FILE.read_text(encoding="utf-8"))
        document["overrides"].append(copy.deepcopy(document["overrides"][0]))
        with TemporaryDirectory(dir=parser.ROOT) as directory:
            path = Path(directory) / "curations.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(parser.ParserError, "Duplicate"):
                parser.load_curations(path)

    def test_curation_source_commit_mismatch_is_fatal(self):
        document = json.loads(parser.CURATION_FILE.read_text(encoding="utf-8"))
        document["overrides"][0]["frozen_source_commit"] = "0" * 40
        with TemporaryDirectory(dir=parser.ROOT) as directory:
            path = Path(directory) / "curations.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(parser.ParserError, "frozen hadolint commit"):
                parser.load_curations(path)


class FrozenCorpusRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs = {spec.source: spec for spec in parser.SOURCE_SPECS}
        cls.result = parser.extract_all()

    def source_rule(self, source, rule_id):
        spec = self.specs[source]
        markdown, _ = parser.load_source_blob(spec, f"{rule_id}.md")
        return parser.extract_rule_with_diagnostics(rule_id, source, markdown)

    def test_dl3003_numbered_sections(self):
        rule, diagnostics = self.source_rule("hadolint", "DL3003")
        self.assertEqual(diagnostics.section_occurrences["problematic_code"], 2)
        self.assertEqual(diagnostics.section_occurrences["correct_code"], 2)
        self.assertIn("Problematic code #1", rule["problematic_code"])
        self.assertIn("Problematic code #2", rule["problematic_code"])
        self.assertNotIn("Correct code", rule["problematic_code"])

    def test_dl3018_qualified_correct_sections(self):
        rule, diagnostics = self.source_rule("hadolint", "DL3018")
        self.assertEqual(diagnostics.section_occurrences["correct_code"], 2)
        partial = rule["correct_code"].index("Partial pin glob")
        exact = rule["correct_code"].index("Exact pin")
        self.assertLess(partial, exact)
        self.assertNotIn("Correct code", rule["problematic_code"])

    def test_dl3029_h1_title(self):
        rule, _ = self.source_rule("hadolint", "DL3029")
        self.assertEqual(rule["title"], "Do not use --platform= with FROM.")

    def test_dl3049_example_sections(self):
        rule, diagnostics = self.source_rule("hadolint", "DL3049")
        self.assertEqual(diagnostics.qualified_occurrences["problematic_code"], 1)
        self.assertIn("FROM busybox", rule["problematic_code"])
        self.assertIn('LABEL version="1.0.1"', rule["correct_code"])

    def test_dl3062_title_is_resolved_only_by_curation(self):
        spec = self.specs["hadolint"]
        markdown, _ = parser.load_source_blob(spec, "DL3062.md")
        with self.assertRaisesRegex(parser.ParserError, "no semantic title"):
            parser.extract_rule("DL3062", "hadolint", markdown)

        overrides, _ = parser.load_curations()
        rule, diagnostics = parser.extract_rule_with_diagnostics(
            "DL3062",
            "hadolint",
            markdown,
            allow_missing_title=True,
        )
        applied = parser.apply_curations(
            rule,
            diagnostics,
            overrides,
            spec.commit,
        )
        self.assertEqual(
            rule["title"],
            "Pin versions in go install. Instead of `go install <package>` use "
            "`go install <package>@<version>`",
        )
        self.assertEqual(applied, {("hadolint", "DL3062", "title")})
        self.assertEqual(len(diagnostics.applied_curations), 1)

    def test_sc2000_h1_title(self):
        rule, _ = self.source_rule("shellcheck", "SC2000")
        self.assertEqual(rule["title"], "See if you can use ${#variable} instead")

    def test_sc2034_h1_title(self):
        rule, _ = self.source_rule("shellcheck", "SC2034")
        self.assertEqual(rule["title"], "foo appears unused. Verify it or export it.")

    def test_sc2145_second_examples_stay_in_their_categories(self):
        rule, diagnostics = self.source_rule("shellcheck", "SC2145")
        self.assertEqual(diagnostics.section_occurrences["problematic_code"], 2)
        self.assertEqual(diagnostics.section_occurrences["correct_code"], 2)
        self.assertIn("${ARRAY_VAR[@]}", rule["problematic_code"])
        self.assertNotIn('"Bad parameters: "', rule["problematic_code"])
        self.assertIn('"Bad parameters: "', rule["correct_code"])

    def test_sc2155_preserves_all_repeated_sections(self):
        rule, diagnostics = self.source_rule("shellcheck", "SC2155")
        self.assertEqual(diagnostics.section_occurrences["problematic_code"], 3)
        self.assertEqual(diagnostics.section_occurrences["correct_code"], 3)
        self.assertEqual(diagnostics.section_occurrences["rationale"], 2)
        self.assertEqual(diagnostics.section_occurrences["exceptions"], 1)
        self.assertIn("case of `export`", rule["problematic_code"])
        self.assertIn("case of `local`", rule["problematic_code"])
        self.assertIn("case of `readonly`", rule["problematic_code"])

    def test_sc2248_h1_title(self):
        rule, _ = self.source_rule("shellcheck", "SC2248")
        self.assertEqual(
            rule["title"],
            "Prefer double quoting even when variables don't contain special characters.",
        )

    def test_sc2312_corrected_example_is_a_second_correct_section(self):
        rule, diagnostics = self.source_rule("shellcheck", "SC2312")
        self.assertEqual(diagnostics.section_occurrences["correct_code"], 2)
        self.assertIn("Correct code: (with correction)", rule["correct_code"])
        self.assertLess(
            rule["correct_code"].index('dir="$(get_chroot_dir)"'),
            rule["correct_code"].index('[[ -d "${dir}" ]]'),
        )

    def test_frozen_manifest_and_complete_corpus_are_valid(self):
        result = self.result
        self.assertEqual(result.source_manifest["observed_counts"]["hadolint"], 75)
        self.assertEqual(result.source_manifest["observed_counts"]["shellcheck"], 520)
        self.assertEqual(result.source_manifest["observed_counts"]["total"], 595)
        self.assertTrue(parser.validate_dataset(result)["passed"])

    def test_missing_embedding_field_reviews_have_exact_coverage(self):
        audit = parser.audit_missing_embedding_fields(self.result)
        self.assertEqual(audit["reviewed_missing_fields"], 63)
        self.assertEqual(audit["counts_by_classification"], {"A": 46, "B": 17})
        self.assertEqual(audit["category_b_count"], 17)
        self.assertEqual(
            audit["category_b_ids_by_field"],
            {
                "problematic_code": [
                    "SC1034",
                    "SC1105",
                    "SC2000",
                    "SC2039",
                    "SC2079",
                    "SC3010",
                    "SC3035",
                ],
                "correct_code": [
                    "DL3010",
                    "SC1018",
                    "SC1047",
                    "SC1062",
                    "SC2000",
                    "SC2019",
                    "SC2039",
                    "SC2040",
                    "SC2119",
                    "SC3010",
                ],
            },
        )
        self.assertEqual(
            audit["counts_by_resolution"],
            {
                "explicit_source_curation": 15,
                "genuinely_absent_retained_null": 46,
                "methodological_null_exception": 2,
            },
        )
        self.assertEqual(audit["unresolved_category_b_count"], 0)
        self.assertTrue(audit["publication_allowed"])

    def test_incomplete_missing_field_reviews_are_fatal(self):
        document = json.loads(
            parser.MISSING_FIELD_REVIEW_FILE.read_text(encoding="utf-8")
        )
        document["reviews"].pop()
        with TemporaryDirectory(dir=parser.ROOT) as directory:
            path = Path(directory) / "reviews.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(parser.ParserError, "coverage mismatch"):
                parser.audit_missing_embedding_fields(self.result, path)

    def test_stale_missing_field_reviews_are_fatal(self):
        result = copy.deepcopy(self.result)
        result.rules["SC2039"]["problematic_code"] = "unexpected value"
        with self.assertRaisesRegex(parser.ParserError, "coverage mismatch"):
            parser.audit_missing_embedding_fields(result)

    def test_publication_succeeds_only_after_category_b_resolution(self):
        validation = parser.validate_dataset(self.result)
        audit = parser.audit_missing_embedding_fields(self.result)
        parser.apply_missing_field_audit(validation, audit)
        self.assertTrue(validation["passed"])
        self.assertTrue(validation["publication_allowed"])

        unresolved = copy.deepcopy(self.result)
        unresolved.rules["DL3010"]["correct_code"] = None
        dl3010 = next(
            item for item in unresolved.diagnostics if item.source_id == "DL3010"
        )
        dl3010.applied_curations = [
            item
            for item in dl3010.applied_curations
            if item["field"] != "correct_code"
        ]
        unresolved_audit = parser.audit_missing_embedding_fields(unresolved)
        self.assertEqual(unresolved_audit["unresolved_category_b_count"], 1)
        self.assertFalse(unresolved_audit["publication_allowed"])

    def test_exact_source_curations_are_verbatim_and_hashed(self):
        overrides, _ = parser.load_curations()
        exact_curations = [
            entry
            for entry in overrides.values()
            if entry["curation_type"] == "frozen_source_exact_span"
        ]
        self.assertEqual(len(exact_curations), 15)
        for entry in exact_curations:
            evidence = entry["source_evidence"]
            markdown, _ = parser.load_source_blob(
                self.specs[entry["source"]], evidence["path"]
            )
            lines = parser.normalize_newlines(markdown).splitlines()
            selected = "\n".join(
                lines[evidence["start_line"] - 1:evidence["end_line"]]
            )
            self.assertEqual(entry["value"], evidence["exact_text"])
            self.assertIn(entry["value"], selected)
            self.assertEqual(parser.sha256_text(entry["value"]), entry["value_sha256"])

    def test_unused_curation_entries_are_fatal(self):
        document = json.loads(parser.CURATION_FILE.read_text(encoding="utf-8"))
        unused = copy.deepcopy(
            next(
                entry
                for entry in document["overrides"]
                if entry["curation_type"] == "official_rule_metadata"
            )
        )
        unused["source_id"] = "DL9999"
        document["overrides"].append(unused)
        with TemporaryDirectory(dir=parser.ROOT) as directory:
            path = Path(directory) / "curations.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaises(parser.CorpusValidationError) as context:
                parser.extract_all(curation_path=path)
        self.assertIn(
            "unused_source_curation",
            {failure["code"] for failure in context.exception.report["failures"]},
        )

    def test_sc2039_methodological_exception_retains_nulls(self):
        self.assertIsNone(self.result.rules["SC2039"]["problematic_code"])
        self.assertIsNone(self.result.rules["SC2039"]["correct_code"])
        audit = parser.audit_missing_embedding_fields(self.result)
        exceptions = {
            (item["source_id"], item["field"])
            for item in audit["methodological_exceptions"]
        }
        self.assertEqual(
            exceptions,
            {("SC2039", "problematic_code"), ("SC2039", "correct_code")},
        )

    def test_historical_dataset_baseline_is_still_recoverable(self):
        historical = parser.run_git(
            parser.ROOT,
            "show",
            "HEAD:data/output/datasets/hadolint_rules_structured.json",
            binary=True,
        )
        self.assertEqual(
            hashlib.sha256(historical).hexdigest(),
            "1d38e3fd2501da6248a03b34ad6dd90020025d8eb246236462ca6b27957b4088",
        )

    def test_final_dataset_generation_is_deterministic(self):
        first = parser.json_bytes(self.result.rules)
        second = parser.json_bytes(parser.extract_all().rules)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
