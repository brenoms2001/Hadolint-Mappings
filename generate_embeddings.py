#!/usr/bin/env python3
"""Audit canonical embedding texts and, when authorized, generate embeddings."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
import pickle
import platform
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Callable, Iterable

import numpy as np


ROOT = Path(__file__).resolve().parent
SOURCE_DATASET = ROOT / "data/output/datasets/hadolint_rules_structured.json"
IEC_DATASET = ROOT / "data/output/datasets/iec62443_clean.json"
IEC_ENRICHED_DATASET = ROOT / "data/output/datasets/iec62443_with_rationale.json"
SOURCE_CACHE = ROOT / "data/output/embeddings/cache_hadolint_structured.pkl"
IEC_CACHE = ROOT / "data/output/embeddings/cache_iec_structured.pkl"
TEXT_AUDIT = ROOT / "data/output/embeddings/embedding_text_audit.json"

SOURCE_DATASET_SHA256 = "708cb58293a9d081f492c1010830f6cf96b040db9d767545cc211f6c6eee37ea"
IEC_DATASET_SHA256 = "fa44e0af3598b58bae7e6dd8057479234bd8c97cd0d9f3effee34f244c007a4c"
IEC_ENRICHED_DATASET_SHA256 = (
    "33e222b4b57bb321933e113634510c19dabf2a1b5e32cc892d6455e48e2c0bdf"
)

MODEL_NAME = "BAAI/bge-large-en-v1.5"
MODEL_REVISION = "d4aa6901d3a41ba39fb536a557fa166f842b0e09"
TOKENIZER_REVISION = MODEL_REVISION
EMBEDDING_DIMENSION = 1024
NORMALIZE_EMBEDDINGS = True
OUTPUT_DTYPE = np.dtype("float32")
NORM_TOLERANCE = 1e-5
DEFAULT_BATCH_SIZE = 64
TEXT_BUILDER_VERSION = "historical-structured-v1"
PICKLE_PROTOCOL = 4

SOURCE_FIELDS = ("id", "title", "problematic_code", "correct_code")
IEC_FIELDS = ("id", "title", "text")
SOURCE_TEXT_SPEC = {
    "version": TEXT_BUILDER_VERSION,
    "representation": "id+title+problematic_code+correct_code",
    "field_order": list(SOURCE_FIELDS),
    "ordering": "preserve_validated_dataset_serialization_order",
    "component_separator": "\n\n",
    "problematic_code_prefix": "Problematic code:\n",
    "correct_code_prefix": "Correct code:\n",
    "falsy_field_behavior": "omit_component",
    "final_operation": "strip",
    "excluded_fields": ["source", "rationale", "exceptions", "raw_markdown"],
}
IEC_TEXT_SPEC = {
    "version": TEXT_BUILDER_VERSION,
    "representation": "id+title+normative_text",
    "field_order": list(IEC_FIELDS),
    "ordering": "preserve_validated_dataset_serialization_order",
    "component_separator": "\n\n",
    "falsy_field_behavior": "omit_component",
    "final_operation": "strip",
    "excluded_fields": [
        "type",
        "parent_sr",
        "foundational_requirement",
        "rationale",
        "rationale_source_pages",
    ],
}


class EmbeddingValidationError(RuntimeError):
    pass


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=4, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def compact_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def hash_file(path: Path) -> str:
    try:
        return sha256_bytes(path.read_bytes())
    except OSError as exc:
        raise EmbeddingValidationError(f"Cannot read {path}") from exc


def verify_file_hash(path: Path, expected_sha256: str) -> str:
    actual = hash_file(path)
    if actual != expected_sha256:
        raise EmbeddingValidationError(
            f"Dataset hash mismatch for {path}: expected {expected_sha256}, found {actual}"
        )
    return actual


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EmbeddingValidationError(f"Invalid JSON dataset: {path}") from exc


def ensure_unique_ids(ids: Iterable[str], dataset_name: str) -> None:
    counts = Counter(ids)
    duplicates = sorted(rule_id for rule_id, count in counts.items() if count > 1)
    if duplicates:
        raise EmbeddingValidationError(
            f"Duplicate IDs in {dataset_name}: {duplicates}"
        )


def load_source_records(path: Path, expected_sha256: str) -> tuple[list[dict], str]:
    dataset_sha = verify_file_hash(path, expected_sha256)
    data = load_json(path)
    if not isinstance(data, dict) or "requirements" in data:
        raise EmbeddingValidationError("Source dataset must be an ID-indexed object")

    records = []
    ids = []
    for key, rule in data.items():
        if not isinstance(key, str) or not isinstance(rule, dict):
            raise EmbeddingValidationError("Source dataset contains an invalid rule")
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or not rule_id:
            raise EmbeddingValidationError(f"Source rule {key!r} has no valid ID")
        if key != rule_id:
            raise EmbeddingValidationError(f"Source key/ID mismatch: {key!r} != {rule_id!r}")
        records.append(rule)
        ids.append(rule_id)
    ensure_unique_ids(ids, "source dataset")
    return records, dataset_sha


def load_iec_records(path: Path, expected_sha256: str) -> tuple[list[dict], str]:
    dataset_sha = verify_file_hash(path, expected_sha256)
    data = load_json(path)
    if not isinstance(data, dict) or not isinstance(data.get("requirements"), list):
        raise EmbeddingValidationError("IEC dataset must contain a requirements list")

    records = []
    ids = []
    for index, requirement in enumerate(data["requirements"]):
        if not isinstance(requirement, dict):
            raise EmbeddingValidationError(f"IEC record {index} is not an object")
        requirement_id = requirement.get("id")
        if not isinstance(requirement_id, str) or not requirement_id:
            raise EmbeddingValidationError(f"IEC record {index} has no valid ID")
        records.append(requirement)
        ids.append(requirement_id)
    ensure_unique_ids(ids, "IEC dataset")
    return records, dataset_sha


def build_source_embedding_text(rule: dict) -> str:
    parts = []
    if rule.get("id"):
        parts.append(str(rule["id"]))
    if rule.get("title"):
        parts.append(str(rule["title"]))
    if rule.get("problematic_code"):
        parts.append("Problematic code:\n" + str(rule["problematic_code"]))
    if rule.get("correct_code"):
        parts.append("Correct code:\n" + str(rule["correct_code"]))
    return "\n\n".join(parts).strip()


def build_iec_embedding_text(requirement: dict) -> str:
    parts = []
    if requirement.get("id"):
        parts.append(str(requirement["id"]))
    if requirement.get("title"):
        parts.append(str(requirement["title"]))
    if requirement.get("text"):
        parts.append(str(requirement["text"]))
    return "\n\n".join(parts).strip()


def build_texts(
    records: list[dict],
    builder: Callable[[dict], str],
    dataset_name: str,
) -> tuple[list[str], list[str]]:
    ids = []
    texts = []
    for index, record in enumerate(records):
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id:
            raise EmbeddingValidationError(f"{dataset_name} record {index} has no valid ID")
        text = builder(record)
        if not text:
            raise EmbeddingValidationError(f"{dataset_name} record {record_id} has empty text")
        ids.append(record_id)
        texts.append(text)
    ensure_unique_ids(ids, dataset_name)
    return ids, texts


def ordered_id_list_sha256(ids: list[str]) -> str:
    return sha256_text("\n".join(ids) + "\n")


def text_builder_spec_sha256(specification: dict) -> str:
    return sha256_bytes(compact_json_bytes(specification))


def duplicate_text_count(texts: list[str]) -> int:
    return len(texts) - len(set(texts))


def verify_iec_projection(clean: list[dict], enriched: list[dict]) -> dict:
    clean_projection = [
        {field: record.get(field) for field in IEC_FIELDS} for record in clean
    ]
    enriched_projection = [
        {field: record.get(field) for field in IEC_FIELDS} for record in enriched
    ]
    if clean_projection != enriched_projection:
        raise EmbeddingValidationError(
            "Clean and enriched IEC datasets differ in id/title/normative text"
        )
    projection_sha = sha256_bytes(compact_json_bytes(clean_projection))
    return {
        "equal": True,
        "record_count": len(clean_projection),
        "fields": list(IEC_FIELDS),
        "projection_sha256": projection_sha,
    }


def dataset_text_audit(
    records: list[dict],
    builder: Callable[[dict], str],
    dataset_path: Path,
    dataset_sha256: str,
    specification: dict,
    null_fields: tuple[str, ...],
) -> dict:
    ids, texts = build_texts(records, builder, str(dataset_path))
    return {
        "dataset_path": str(dataset_path.relative_to(ROOT)),
        "dataset_sha256": dataset_sha256,
        "record_count": len(records),
        "ordered_id_list_sha256": ordered_id_list_sha256(ids),
        "text_builder_version": TEXT_BUILDER_VERSION,
        "text_builder_specification": specification,
        "text_builder_specification_sha256": text_builder_spec_sha256(specification),
        "duplicate_text_count": duplicate_text_count(texts),
        "null_or_falsy_field_counts": {
            field: sum(not record.get(field) for record in records)
            for field in null_fields
        },
        "records": [
            {"id": record_id, "text_sha256": sha256_text(text)}
            for record_id, text in zip(ids, texts)
        ],
    }


def create_text_audit(
    source_path: Path = SOURCE_DATASET,
    source_sha256: str = SOURCE_DATASET_SHA256,
    iec_path: Path = IEC_DATASET,
    iec_sha256: str = IEC_DATASET_SHA256,
    enriched_iec_path: Path = IEC_ENRICHED_DATASET,
    enriched_iec_sha256: str = IEC_ENRICHED_DATASET_SHA256,
) -> dict:
    source_records, verified_source_sha = load_source_records(source_path, source_sha256)
    iec_records, verified_iec_sha = load_iec_records(iec_path, iec_sha256)
    enriched_records, verified_enriched_sha = load_iec_records(
        enriched_iec_path,
        enriched_iec_sha256,
    )
    parity = verify_iec_projection(iec_records, enriched_records)
    parity["clean_dataset_path"] = str(iec_path.relative_to(ROOT))
    parity["clean_dataset_sha256"] = verified_iec_sha
    parity["enriched_dataset_path"] = str(enriched_iec_path.relative_to(ROOT))
    parity["enriched_dataset_sha256"] = verified_enriched_sha

    return {
        "audit_version": 1,
        "generator": {
            "script_path": str(Path(__file__).resolve().relative_to(ROOT)),
            "script_sha256": hash_file(Path(__file__).resolve()),
        },
        "model": {
            "name": MODEL_NAME,
            "revision": MODEL_REVISION,
            "tokenizer_revision": TOKENIZER_REVISION,
            "dimension": EMBEDDING_DIMENSION,
            "normalize_embeddings": NORMALIZE_EMBEDDINGS,
        },
        "source": dataset_text_audit(
            source_records,
            build_source_embedding_text,
            source_path,
            verified_source_sha,
            SOURCE_TEXT_SPEC,
            ("problematic_code", "correct_code"),
        ),
        "iec": dataset_text_audit(
            iec_records,
            build_iec_embedding_text,
            iec_path,
            verified_iec_sha,
            IEC_TEXT_SPEC,
            ("title", "text"),
        ),
        "iec_clean_enriched_embedding_field_parity": parity,
    }


def validate_embedding_matrix(
    vectors: object,
    expected_count: int,
    dimension: int = EMBEDDING_DIMENSION,
    norm_tolerance: float = NORM_TOLERANCE,
) -> np.ndarray:
    matrix = np.asarray(vectors)
    if matrix.shape != (expected_count, dimension):
        raise EmbeddingValidationError(
            f"Embedding shape mismatch: expected {(expected_count, dimension)}, "
            f"found {matrix.shape}"
        )
    if matrix.dtype != OUTPUT_DTYPE:
        raise EmbeddingValidationError(
            f"Embedding dtype mismatch: expected {OUTPUT_DTYPE}, found {matrix.dtype}"
        )
    if not np.isfinite(matrix).all():
        raise EmbeddingValidationError("Embedding matrix contains non-finite values")
    norms = np.linalg.norm(matrix, axis=1)
    if not np.all(np.abs(norms - 1.0) <= norm_tolerance):
        maximum_error = float(np.max(np.abs(norms - 1.0)))
        raise EmbeddingValidationError(
            f"Embedding norms exceed tolerance {norm_tolerance}: {maximum_error}"
        )
    return matrix


def package_version(distribution: str) -> str:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def repository_state() -> dict:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
    except (OSError, subprocess.CalledProcessError):
        commit = None
        dirty = None
    return {"commit": commit, "dirty": dirty}


def metadata_base(
    dataset_name: str,
    dataset_path: Path,
    dataset_sha256: str,
    ids: list[str],
    specification: dict,
    batch_size: int,
    device: str,
) -> dict:
    script_path = Path(__file__).resolve()
    return {
        "metadata_version": 1,
        "dataset": dataset_name,
        "dataset_path": str(dataset_path.relative_to(ROOT)),
        "dataset_sha256": dataset_sha256,
        "ordered_id_list_sha256": ordered_id_list_sha256(ids),
        "text_builder_version": TEXT_BUILDER_VERSION,
        "field_order": specification["field_order"],
        "representation": specification["representation"],
        "text_builder_specification_sha256": text_builder_spec_sha256(specification),
        "model_name": MODEL_NAME,
        "model_revision": MODEL_REVISION,
        "tokenizer_revision": TOKENIZER_REVISION,
        "dimension": EMBEDDING_DIMENSION,
        "normalized": NORMALIZE_EMBEDDINGS,
        "norm_tolerance": NORM_TOLERANCE,
        "dtype": OUTPUT_DTYPE.name,
        "vector_count": len(ids),
        "batch_size": batch_size,
        "device": device,
        "python_version": platform.python_version(),
        "pytorch_version": package_version("torch"),
        "transformers_version": package_version("transformers"),
        "sentence_transformers_version": package_version("sentence-transformers"),
        "numpy_version": np.__version__,
        "generator_script_path": str(script_path.relative_to(ROOT)),
        "generator_script_sha256": hash_file(script_path),
        "repository": repository_state(),
    }


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def cache_sidecar_path(cache_path: Path) -> Path:
    return cache_path.with_suffix(".metadata.json")


def ensure_cache_output_available(cache_path: Path, overwrite: bool) -> None:
    sidecar_path = cache_sidecar_path(cache_path)
    if not overwrite and (cache_path.exists() or sidecar_path.exists()):
        raise EmbeddingValidationError(
            f"Refusing to overwrite existing cache or sidecar: {cache_path}"
        )


def write_embedding_cache(
    cache_path: Path,
    ids: list[str],
    vectors: np.ndarray,
    metadata: dict,
    overwrite: bool,
) -> dict:
    sidecar_path = cache_sidecar_path(cache_path)
    ensure_cache_output_available(cache_path, overwrite)
    matrix = validate_embedding_matrix(vectors, len(ids))
    cache = {
        "metadata": {
            **metadata,
            "entry_count": len(ids),
        },
        "embeddings": {
            record_id: matrix[index].copy()
            for index, record_id in enumerate(ids)
        },
    }
    cache_content = pickle.dumps(cache, protocol=PICKLE_PROTOCOL)
    cache_sha = sha256_bytes(cache_content)
    sidecar = {
        **metadata,
        "output_cache_path": str(cache_path.relative_to(ROOT)),
        "output_cache_sha256": cache_sha,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    atomic_write(cache_path, cache_content)
    atomic_write(sidecar_path, canonical_json_bytes(sidecar))
    return sidecar


def encode_texts(
    texts: list[str],
    batch_size: int,
    device: str,
) -> np.ndarray:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise EmbeddingValidationError("sentence-transformers is not installed") from exc
    model = SentenceTransformer(
        MODEL_NAME,
        revision=MODEL_REVISION,
        device=device,
    )
    dimension = model.get_sentence_embedding_dimension()
    if dimension != EMBEDDING_DIMENSION:
        raise EmbeddingValidationError(
            f"Model dimension mismatch: expected {EMBEDDING_DIMENSION}, found {dimension}"
        )
    vectors = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=batch_size,
        device=device,
        normalize_embeddings=NORMALIZE_EMBEDDINGS,
        convert_to_numpy=True,
    )
    return np.asarray(vectors, dtype=OUTPUT_DTYPE)


def generate_caches(args: argparse.Namespace) -> None:
    ensure_cache_output_available(args.source_cache, args.overwrite)
    ensure_cache_output_available(args.iec_cache, args.overwrite)
    source_records, source_sha = load_source_records(
        args.source_dataset,
        args.source_sha256,
    )
    iec_records, iec_sha = load_iec_records(args.iec_dataset, args.iec_sha256)
    enriched_records, _ = load_iec_records(
        args.enriched_iec_dataset,
        args.enriched_iec_sha256,
    )
    verify_iec_projection(iec_records, enriched_records)

    source_ids, source_texts = build_texts(
        source_records,
        build_source_embedding_text,
        "source dataset",
    )
    iec_ids, iec_texts = build_texts(
        iec_records,
        build_iec_embedding_text,
        "IEC dataset",
    )
    source_vectors = encode_texts(source_texts, args.batch_size, args.device)
    iec_vectors = encode_texts(iec_texts, args.batch_size, args.device)
    validate_embedding_matrix(source_vectors, len(source_ids))
    validate_embedding_matrix(iec_vectors, len(iec_ids))

    source_metadata = metadata_base(
        "Hadolint/ShellCheck source rules",
        args.source_dataset,
        source_sha,
        source_ids,
        SOURCE_TEXT_SPEC,
        args.batch_size,
        args.device,
    )
    iec_metadata = metadata_base(
        "IEC 62443-3-3",
        args.iec_dataset,
        iec_sha,
        iec_ids,
        IEC_TEXT_SPEC,
        args.batch_size,
        args.device,
    )
    write_embedding_cache(
        args.source_cache,
        source_ids,
        source_vectors,
        source_metadata,
        args.overwrite,
    )
    write_embedding_cache(
        args.iec_cache,
        iec_ids,
        iec_vectors,
        iec_metadata,
        args.overwrite,
    )


def add_input_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--source-dataset", type=Path, default=SOURCE_DATASET)
    parser.add_argument("--source-sha256", default=SOURCE_DATASET_SHA256)
    parser.add_argument("--iec-dataset", type=Path, default=IEC_DATASET)
    parser.add_argument("--iec-sha256", default=IEC_DATASET_SHA256)
    parser.add_argument(
        "--enriched-iec-dataset",
        type=Path,
        default=IEC_ENRICHED_DATASET,
    )
    parser.add_argument("--enriched-iec-sha256", default=IEC_ENRICHED_DATASET_SHA256)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_parser = subparsers.add_parser(
        "audit",
        help="Construct and hash texts without loading the embedding model.",
    )
    add_input_arguments(audit_parser)
    audit_parser.add_argument("--output", type=Path, default=TEXT_AUDIT)

    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate canonical caches. This downloads and runs the model.",
    )
    add_input_arguments(generate_parser)
    generate_parser.add_argument("--source-cache", type=Path, default=SOURCE_CACHE)
    generate_parser.add_argument("--iec-cache", type=Path, default=IEC_CACHE)
    generate_parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    generate_parser.add_argument("--device", default="cuda")
    generate_parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    if args.command == "audit":
        audit = create_text_audit(
            args.source_dataset,
            args.source_sha256,
            args.iec_dataset,
            args.iec_sha256,
            args.enriched_iec_dataset,
            args.enriched_iec_sha256,
        )
        atomic_write(args.output, canonical_json_bytes(audit))
        print(f"Source texts: {audit['source']['record_count']}")
        print(f"IEC texts: {audit['iec']['record_count']}")
        print(f"Audit SHA-256: {hash_file(args.output)}")
        return
    if args.batch_size < 1:
        raise EmbeddingValidationError("Batch size must be positive")
    generate_caches(args)


if __name__ == "__main__":
    try:
        main()
    except EmbeddingValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
