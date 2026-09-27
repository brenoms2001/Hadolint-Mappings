import hashlib
import json
import pickle
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

import generate_embeddings as generator


class TextConstructionTests(unittest.TestCase):
    def test_source_text_matches_historical_notebook(self):
        rule = {
            "id": "DL9999",
            "title": "Example title",
            "problematic_code": "bad\ncode",
            "correct_code": "good code",
            "rationale": "must be excluded",
            "exceptions": "must be excluded",
            "raw_markdown": "must be excluded",
        }
        self.assertEqual(
            generator.build_source_embedding_text(rule),
            "DL9999\n\nExample title\n\nProblematic code:\nbad\ncode"
            "\n\nCorrect code:\ngood code",
        )

    def test_source_null_fields_omit_entire_labeled_component(self):
        rule = {
            "id": "SC2039",
            "title": "In POSIX sh, something is undefined.",
            "problematic_code": None,
            "correct_code": None,
        }
        text = generator.build_source_embedding_text(rule)
        self.assertEqual(text, "SC2039\n\nIn POSIX sh, something is undefined.")
        self.assertNotIn("Problematic code:", text)
        self.assertNotIn("Correct code:", text)

    def test_iec_text_excludes_rationale(self):
        requirement = {
            "id": "SR 1.1",
            "title": "Title",
            "text": "Normative text",
            "rationale": "Excluded rationale",
        }
        self.assertEqual(
            generator.build_iec_embedding_text(requirement),
            "SR 1.1\n\nTitle\n\nNormative text",
        )

    def test_input_order_is_preserved_deterministically(self):
        document = {
            "SC0002": {"id": "SC0002", "title": "Second"},
            "DL0001": {"id": "DL0001", "title": "First"},
        }
        content = (json.dumps(document) + "\n").encode()
        with TemporaryDirectory(dir=generator.ROOT) as directory:
            path = Path(directory) / "source.json"
            path.write_bytes(content)
            records, _ = generator.load_source_records(
                path,
                hashlib.sha256(content).hexdigest(),
            )
        ids, _ = generator.build_texts(
            records,
            generator.build_source_embedding_text,
            "test source",
        )
        self.assertEqual(ids, ["SC0002", "DL0001"])

    def test_dataset_hash_mismatch_is_fatal(self):
        with TemporaryDirectory(dir=generator.ROOT) as directory:
            path = Path(directory) / "source.json"
            path.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(
                generator.EmbeddingValidationError,
                "Dataset hash mismatch",
            ):
                generator.load_source_records(path, "0" * 64)

    def test_duplicate_ids_are_rejected(self):
        with self.assertRaisesRegex(
            generator.EmbeddingValidationError,
            "Duplicate IDs",
        ):
            generator.ensure_unique_ids(["SR 1.1", "SR 1.1"], "test")

    def test_clean_and_enriched_iec_projection_is_identical(self):
        clean, _ = generator.load_iec_records(
            generator.IEC_DATASET,
            generator.IEC_DATASET_SHA256,
        )
        enriched, _ = generator.load_iec_records(
            generator.IEC_ENRICHED_DATASET,
            generator.IEC_ENRICHED_DATASET_SHA256,
        )
        parity = generator.verify_iec_projection(clean, enriched)
        self.assertTrue(parity["equal"])
        self.assertEqual(parity["record_count"], 100)


class CacheValidationTests(unittest.TestCase):
    def unit_vectors(self, count=2):
        vectors = np.zeros((count, generator.EMBEDDING_DIMENSION), dtype=np.float32)
        for index in range(count):
            vectors[index, index] = 1.0
        return vectors

    def test_valid_synthetic_vectors(self):
        vectors = self.unit_vectors()
        validated = generator.validate_embedding_matrix(vectors, 2)
        self.assertIs(validated, vectors)

    def test_dimension_and_count_mismatch_is_fatal(self):
        with self.assertRaisesRegex(generator.EmbeddingValidationError, "shape mismatch"):
            generator.validate_embedding_matrix(np.ones((2, 3), dtype=np.float32), 2)

    def test_non_finite_vector_is_fatal(self):
        vectors = self.unit_vectors()
        vectors[0, 0] = np.nan
        with self.assertRaisesRegex(generator.EmbeddingValidationError, "non-finite"):
            generator.validate_embedding_matrix(vectors, 2)

    def test_non_unit_vector_is_fatal(self):
        vectors = self.unit_vectors()
        vectors[0, 0] = 2.0
        with self.assertRaisesRegex(generator.EmbeddingValidationError, "norms"):
            generator.validate_embedding_matrix(vectors, 2)

    def test_non_float32_vector_is_fatal(self):
        with self.assertRaisesRegex(generator.EmbeddingValidationError, "dtype mismatch"):
            generator.validate_embedding_matrix(self.unit_vectors().astype(np.float64), 2)

    def test_metadata_and_cache_sidecar(self):
        ids = ["A", "B"]
        with TemporaryDirectory(dir=generator.ROOT) as directory:
            directory_path = Path(directory)
            dataset_path = directory_path / "dataset.json"
            dataset_path.write_text("{}\n", encoding="utf-8")
            metadata = generator.metadata_base(
                "synthetic",
                dataset_path,
                generator.hash_file(dataset_path),
                ids,
                generator.SOURCE_TEXT_SPEC,
                2,
                "cpu",
            )
            cache_path = directory_path / "cache.pkl"
            sidecar = generator.write_embedding_cache(
                cache_path,
                ids,
                self.unit_vectors(),
                metadata,
                overwrite=False,
            )
            cache_content = cache_path.read_bytes()
            cache = pickle.loads(cache_content)
            recorded_sidecar = json.loads(
                generator.cache_sidecar_path(cache_path).read_text(encoding="utf-8")
            )

            self.assertEqual(list(cache["embeddings"]), ids)
            self.assertEqual(sidecar, recorded_sidecar)
            self.assertEqual(
                recorded_sidecar["output_cache_sha256"],
                hashlib.sha256(cache_content).hexdigest(),
            )
            for key in (
                "dataset_path",
                "dataset_sha256",
                "ordered_id_list_sha256",
                "text_builder_version",
                "field_order",
                "text_builder_specification_sha256",
                "model_name",
                "model_revision",
                "tokenizer_revision",
                "dimension",
                "normalized",
                "dtype",
                "vector_count",
                "batch_size",
                "device",
                "python_version",
                "pytorch_version",
                "transformers_version",
                "sentence_transformers_version",
                "generator_script_path",
                "generator_script_sha256",
                "repository",
                "output_cache_sha256",
                "generated_at_utc",
            ):
                self.assertIn(key, recorded_sidecar)

            with self.assertRaisesRegex(
                generator.EmbeddingValidationError,
                "Refusing to overwrite",
            ):
                generator.write_embedding_cache(
                    cache_path,
                    ids,
                    self.unit_vectors(),
                    metadata,
                    overwrite=False,
                )


if __name__ == "__main__":
    unittest.main()
