#!/usr/bin/env python3
"""Validate canonical embeddings and generate deterministic IEC matches."""

from __future__ import annotations

import argparse
import contextlib
import csv
import datetime as dt
import hashlib
import io
import json
import os
import pickle
import platform
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import yaml


ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "config/matching.yaml"
DEFAULT_OUTPUT_JSON = (
    ROOT / "data/output/mappings/iec/inspection/iec_matches_068_top10.json"
)
DEFAULT_OUTPUT_CSV = DEFAULT_OUTPUT_JSON.with_suffix(".csv")


class MatchingValidationError(RuntimeError):
    """Raised when canonical matching inputs or outputs violate their contract."""


@dataclass(frozen=True)
class ValidatedInputs:
    config: dict[str, Any]
    config_path: Path
    config_sha256: str
    source_records: list[dict[str, Any]]
    target_records: list[dict[str, Any]]
    source_ids: list[str]
    target_ids: list[str]
    source_matrix: np.ndarray
    target_matrix: np.ndarray
    hashes: dict[str, str]


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def hash_file(path: Path) -> str:
    try:
        return sha256_bytes(path.read_bytes())
    except OSError as exc:
        raise MatchingValidationError(f"Cannot read required file: {path}") from exc


def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def require_outputs_available(paths: list[Path], overwrite: bool) -> None:
    existing = [str(path) for path in paths if path.exists()]
    if existing and not overwrite:
        raise MatchingValidationError(
            "Refusing to overwrite existing output(s): " + ", ".join(existing)
        )


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MatchingValidationError(f"Invalid JSON file: {path}") from exc


def require_file_hash(path: Path, expected: str, label: str) -> str:
    actual = hash_file(path)
    if actual != expected:
        raise MatchingValidationError(
            f"{label} SHA-256 mismatch: expected {expected}, found {actual}"
        )
    return actual


def ordered_id_hash(ids: list[str]) -> str:
    return sha256_bytes(("\n".join(ids) + "\n").encode("utf-8"))


def source_embedding_text(record: dict[str, Any]) -> str:
    parts = []
    if record.get("id"):
        parts.append(str(record["id"]))
    if record.get("title"):
        parts.append(str(record["title"]))
    if record.get("problematic_code"):
        parts.append("Problematic code:\n" + str(record["problematic_code"]))
    if record.get("correct_code"):
        parts.append("Correct code:\n" + str(record["correct_code"]))
    return "\n\n".join(parts).strip()


def target_embedding_text(record: dict[str, Any]) -> str:
    return "\n\n".join(
        str(record[field]) for field in ("id", "title", "text") if record.get(field)
    ).strip()


def load_matching_config(path: Path = DEFAULT_CONFIG) -> tuple[dict[str, Any], str]:
    try:
        config = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise MatchingValidationError(f"Invalid matching configuration: {path}") from exc
    if not isinstance(config, dict):
        raise MatchingValidationError("Matching configuration must be a YAML object")

    try:
        embedding = config["embedding"]
        matching = config["matching"]
        artifacts = config["artifacts"]
        checks = {
            "version": config["version"] == 2,
            "dtype": embedding["dtype"] == "float32"
            and matching["execution_dtype"] == "float32",
            "normalized": embedding["normalized"] is True,
            "similarity": matching["similarity"] == "cosine",
            "cosine_implementation": matching["cosine_implementation"]
            == "matrix_product_of_validated_unit_vectors",
            "negative_clamp": matching["negative_clamp"]
            == {"enabled": True, "value": 0.0},
            "power": matching["power_transform"]["enabled"] is True,
            "normalization": matching["normalization"]
            == {"method": "l_infinity", "scope": "per_source_rule"},
            "threshold": matching["threshold"]["type"] == "relative"
            and matching["threshold"]["operator"] == ">=",
            "zero_row": matching["zero_row_policy"]
            == "all_relative_scores_zero_and_no_candidates",
            "primary_order": matching["ordering"]["primary"]
            == "relative_score_descending",
            "secondary_order": matching["ordering"]["secondary"]
            == "frozen_iec_dataset_order_ascending",
            "json_rounding": matching["serialization"][
                "canonical_json_score_rounding"
            ]
            is None,
            "artifact_sections": all(
                name in artifacts
                for name in (
                    "source_dataset",
                    "target_dataset",
                    "source_cache",
                    "target_cache",
                    "text_audit",
                    "generator",
                )
            ),
        }
    except (KeyError, TypeError) as exc:
        raise MatchingValidationError(
            f"Missing canonical matching configuration field: {exc}"
        ) from exc
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise MatchingValidationError(
            "Unsupported canonical matching configuration: " + ", ".join(failed)
        )
    if matching["power_transform"]["exponent"] <= 0:
        raise MatchingValidationError("Power exponent must be positive")
    if not 0 <= matching["threshold"]["value"] <= 1:
        raise MatchingValidationError("Relative threshold must be between zero and one")
    if matching["top_k"] < 1:
        raise MatchingValidationError("top_k must be positive")
    return config, hash_file(path)


def _load_source_dataset(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    data = load_json(path)
    if not isinstance(data, dict) or "requirements" in data:
        raise MatchingValidationError("Source dataset must be an ID-indexed object")
    records = []
    ids = []
    for key, record in data.items():
        if not isinstance(key, str) or not isinstance(record, dict):
            raise MatchingValidationError("Source dataset contains an invalid record")
        if record.get("id") != key:
            raise MatchingValidationError(f"Source key/ID mismatch for {key!r}")
        records.append(record)
        ids.append(key)
    if len(ids) != len(set(ids)):
        raise MatchingValidationError("Source dataset contains duplicate IDs")
    return records, ids


def _load_target_dataset(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    data = load_json(path)
    if not isinstance(data, dict) or not isinstance(data.get("requirements"), list):
        raise MatchingValidationError("Target dataset must contain a requirements list")
    records = data["requirements"]
    if any(not isinstance(record, dict) for record in records):
        raise MatchingValidationError("Target dataset contains a non-object record")
    ids = [record.get("id") for record in records]
    if any(not isinstance(item, str) or not item for item in ids):
        raise MatchingValidationError("Target dataset contains a missing or invalid ID")
    if len(ids) != len(set(ids)):
        raise MatchingValidationError("Target dataset contains duplicate IDs")
    return records, ids


def validate_vector_map(
    embeddings: object,
    expected_ids: list[str],
    dimension: int,
    norm_tolerance: float,
    label: str,
) -> np.ndarray:
    if not isinstance(embeddings, dict):
        raise MatchingValidationError(f"{label} embeddings must be ID-indexed")
    actual_ids = list(embeddings)
    missing = sorted(set(expected_ids) - set(actual_ids))
    extra = sorted(set(actual_ids) - set(expected_ids))
    if missing or extra:
        raise MatchingValidationError(
            f"{label} embedding ID coverage mismatch: missing={missing}, extra={extra}"
        )
    if actual_ids != expected_ids:
        raise MatchingValidationError(f"{label} embedding ID order mismatch")

    vectors = []
    for item_id in expected_ids:
        vector = embeddings[item_id]
        if not isinstance(vector, np.ndarray):
            raise MatchingValidationError(f"{label} vector {item_id} is not a NumPy array")
        if vector.dtype != np.dtype("float32"):
            raise MatchingValidationError(
                f"{label} vector {item_id} has dtype {vector.dtype}, expected float32"
            )
        if vector.shape != (dimension,):
            raise MatchingValidationError(
                f"{label} vector {item_id} has shape {vector.shape}, expected {(dimension,)}"
            )
        if not np.isfinite(vector).all():
            raise MatchingValidationError(f"{label} vector {item_id} is non-finite")
        vectors.append(vector)
    matrix = np.stack(vectors)
    norms = np.linalg.norm(matrix, axis=1)
    errors = np.abs(norms - np.float32(1.0))
    if not np.all(errors <= np.float32(norm_tolerance)):
        raise MatchingValidationError(
            f"{label} vector norm exceeds tolerance {norm_tolerance}: "
            f"maximum error {float(errors.max())}"
        )
    return matrix


def _load_cache(path: Path, label: str) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            cache = pickle.load(handle)
    except (OSError, pickle.PickleError, EOFError) as exc:
        raise MatchingValidationError(f"Cannot load {label} cache: {path}") from exc
    if not isinstance(cache, dict) or not isinstance(cache.get("metadata"), dict):
        raise MatchingValidationError(f"Invalid {label} cache structure")
    return cache


def _validate_cache_and_sidecar(
    *,
    label: str,
    cache_spec: dict[str, Any],
    dataset_spec: dict[str, Any],
    audit_section: dict[str, Any],
    expected_ids: list[str],
    config: dict[str, Any],
) -> tuple[np.ndarray, dict[str, str]]:
    cache_path = ROOT / cache_spec["path"]
    sidecar_path = ROOT / cache_spec["sidecar_path"]
    cache_hash = require_file_hash(cache_path, cache_spec["sha256"], f"{label} cache")
    sidecar_hash = require_file_hash(
        sidecar_path, cache_spec["sidecar_sha256"], f"{label} sidecar"
    )
    sidecar = load_json(sidecar_path)
    if not isinstance(sidecar, dict):
        raise MatchingValidationError(f"{label} sidecar must be an object")
    cache = _load_cache(cache_path, label)
    internal = cache["metadata"]

    embedding = config["embedding"]
    expected_metadata = {
        "dataset_path": dataset_spec["path"],
        "dataset_sha256": dataset_spec["sha256"],
        "ordered_id_list_sha256": ordered_id_hash(expected_ids),
        "text_builder_version": embedding["text_builder_version"],
        "model_name": embedding["model"],
        "model_revision": embedding["revision"],
        "tokenizer_revision": embedding["tokenizer_revision"],
        "dimension": embedding["dimensions"],
        "normalized": embedding["normalized"],
        "norm_tolerance": embedding["norm_tolerance"],
        "dtype": embedding["dtype"],
        "vector_count": dataset_spec["count"],
    }
    if sidecar.get("output_cache_sha256") != cache_hash:
        raise MatchingValidationError(f"{label} sidecar cache hash mismatch")
    for key, expected in expected_metadata.items():
        if sidecar.get(key) != expected:
            raise MatchingValidationError(
                f"{label} sidecar field {key!r} mismatch: "
                f"expected {expected!r}, found {sidecar.get(key)!r}"
            )
        if key in internal and internal[key] != expected:
            raise MatchingValidationError(f"{label} internal metadata {key!r} mismatch")
    if internal.get("entry_count") != dataset_spec["count"]:
        raise MatchingValidationError(f"{label} internal entry count mismatch")
    if audit_section.get("dataset_sha256") != dataset_spec["sha256"]:
        raise MatchingValidationError(f"{label} text-audit dataset hash mismatch")
    if audit_section.get("ordered_id_list_sha256") != ordered_id_hash(expected_ids):
        raise MatchingValidationError(f"{label} text-audit ordered ID hash mismatch")
    if audit_section.get("record_count") != dataset_spec["count"]:
        raise MatchingValidationError(f"{label} text-audit record count mismatch")
    if sidecar.get("text_builder_specification_sha256") != audit_section.get(
        "text_builder_specification_sha256"
    ):
        raise MatchingValidationError(f"{label} text-builder specification mismatch")

    matrix = validate_vector_map(
        cache.get("embeddings"),
        expected_ids,
        embedding["dimensions"],
        embedding["norm_tolerance"],
        label,
    )
    return matrix, {
        f"{label}_cache_sha256": cache_hash,
        f"{label}_sidecar_sha256": sidecar_hash,
    }


def validate_canonical_inputs(
    config_path: Path = DEFAULT_CONFIG,
) -> ValidatedInputs:
    config_path = config_path.resolve()
    config, config_sha = load_matching_config(config_path)
    artifacts = config["artifacts"]

    source_dataset_path = ROOT / artifacts["source_dataset"]["path"]
    target_dataset_path = ROOT / artifacts["target_dataset"]["path"]
    source_dataset_hash = require_file_hash(
        source_dataset_path,
        artifacts["source_dataset"]["sha256"],
        "source dataset",
    )
    target_dataset_hash = require_file_hash(
        target_dataset_path,
        artifacts["target_dataset"]["sha256"],
        "target dataset",
    )
    audit_path = ROOT / artifacts["text_audit"]["path"]
    audit_hash = require_file_hash(
        audit_path, artifacts["text_audit"]["sha256"], "embedding text audit"
    )
    generator_path = ROOT / artifacts["generator"]["path"]
    generator_hash = require_file_hash(
        generator_path, artifacts["generator"]["sha256"], "embedding generator"
    )

    source_records, source_ids = _load_source_dataset(source_dataset_path)
    target_records, target_ids = _load_target_dataset(target_dataset_path)
    if len(source_ids) != artifacts["source_dataset"]["count"]:
        raise MatchingValidationError("Source dataset count mismatch")
    if len(target_ids) != artifacts["target_dataset"]["count"]:
        raise MatchingValidationError("Target dataset count mismatch")

    audit = load_json(audit_path)
    if not isinstance(audit, dict):
        raise MatchingValidationError("Embedding text audit must be an object")
    model = audit.get("model", {})
    embedding = config["embedding"]
    expected_audit_model = {
        "name": embedding["model"],
        "revision": embedding["revision"],
        "tokenizer_revision": embedding["tokenizer_revision"],
        "dimension": embedding["dimensions"],
        "normalize_embeddings": embedding["normalized"],
    }
    if any(model.get(key) != value for key, value in expected_audit_model.items()):
        raise MatchingValidationError("Embedding text-audit model metadata mismatch")
    if audit.get("generator", {}).get("script_sha256") != generator_hash:
        raise MatchingValidationError("Embedding text-audit generator hash mismatch")

    for label, records, ids, builder in (
        ("source", source_records, source_ids, source_embedding_text),
        ("target", target_records, target_ids, target_embedding_text),
    ):
        section = audit["source" if label == "source" else "iec"]
        audited_records = section.get("records")
        if not isinstance(audited_records, list):
            raise MatchingValidationError(f"{label} text-audit records are invalid")
        expected = [
            {"id": item_id, "text_sha256": sha256_bytes(builder(record).encode("utf-8"))}
            for item_id, record in zip(ids, records)
        ]
        if audited_records != expected:
            raise MatchingValidationError(f"{label} embedding-text audit mismatch")

    source_matrix, source_hashes = _validate_cache_and_sidecar(
        label="source",
        cache_spec=artifacts["source_cache"],
        dataset_spec=artifacts["source_dataset"],
        audit_section=audit["source"],
        expected_ids=source_ids,
        config=config,
    )
    target_matrix, target_hashes = _validate_cache_and_sidecar(
        label="target",
        cache_spec=artifacts["target_cache"],
        dataset_spec=artifacts["target_dataset"],
        audit_section=audit["iec"],
        expected_ids=target_ids,
        config=config,
    )
    hashes = {
        "source_dataset_sha256": source_dataset_hash,
        "target_dataset_sha256": target_dataset_hash,
        "text_audit_sha256": audit_hash,
        "generator_sha256": generator_hash,
        **source_hashes,
        **target_hashes,
    }
    return ValidatedInputs(
        config=config,
        config_path=config_path,
        config_sha256=config_sha,
        source_records=source_records,
        target_records=target_records,
        source_ids=source_ids,
        target_ids=target_ids,
        source_matrix=source_matrix,
        target_matrix=target_matrix,
        hashes=hashes,
    )


def compute_score_matrices(
    source_matrix: np.ndarray,
    target_matrix: np.ndarray,
    config: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray]:
    if source_matrix.dtype != np.float32 or target_matrix.dtype != np.float32:
        raise MatchingValidationError("Canonical matching matrices must be float32")
    if source_matrix.ndim != 2 or target_matrix.ndim != 2:
        raise MatchingValidationError("Canonical matching matrices must be two-dimensional")
    if source_matrix.shape[1] != target_matrix.shape[1]:
        raise MatchingValidationError("Source and target embedding dimensions differ")
    matching = config["matching"]
    raw = source_matrix @ target_matrix.T
    if raw.dtype != np.float32:
        raise MatchingValidationError("Cosine matrix is not float32")
    clamped = np.maximum(raw, np.float32(matching["negative_clamp"]["value"]))
    transformed = np.power(
        clamped,
        np.float32(matching["power_transform"]["exponent"]),
    )
    row_max = transformed.max(axis=1, keepdims=True)
    relative = np.divide(
        transformed,
        row_max,
        out=np.zeros_like(transformed),
        where=row_max > np.float32(0.0),
    )
    return raw, relative


def select_target_indices(relative_scores: np.ndarray, config: dict[str, Any]) -> np.ndarray:
    matching = config["matching"]
    threshold = np.float32(matching["threshold"]["value"])
    candidates = np.flatnonzero(relative_scores >= threshold)
    if not len(candidates):
        return candidates
    order = np.lexsort((candidates, -relative_scores[candidates]))
    return candidates[order][: matching["top_k"]]


def normalize_parent_sr(requirement: dict[str, Any]) -> Any:
    parent = requirement.get("parent_sr")
    return None if parent == requirement["id"] else parent


def _observed_counts(
    sources: dict[str, dict[str, Any]], target_by_id: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    distribution: Counter[int] = Counter()
    source_counts = {"hadolint": 0, "shellcheck": 0}
    type_counts = {"SR": 0, "RE": 0}
    zero = 0
    total = 0
    for source, rules in sources.items():
        for entry in rules.values():
            count = len(entry["matches"])
            distribution[count] += 1
            zero += count == 0
            source_counts[source] += count
            total += count
            for match in entry["matches"]:
                target_type = target_by_id[match["target_id"]].get("type")
                type_counts[target_type] = type_counts.get(target_type, 0) + 1
    return {
        "source_count": sum(len(rules) for rules in sources.values()),
        "target_count": len(target_by_id),
        "match_count": total,
        "hadolint_match_count": source_counts["hadolint"],
        "shellcheck_match_count": source_counts["shellcheck"],
        "sr_match_count": type_counts.get("SR", 0),
        "re_match_count": type_counts.get("RE", 0),
        "zero_candidate_source_count": zero,
        "candidate_count_distribution": {
            str(count): distribution[count] for count in sorted(distribution)
        },
    }


def build_matching_payload(inputs: ValidatedInputs) -> dict[str, Any]:
    raw, relative = compute_score_matrices(
        inputs.source_matrix, inputs.target_matrix, inputs.config
    )
    target_by_id = {record["id"]: record for record in inputs.target_records}
    sources: dict[str, dict[str, Any]] = {"hadolint": {}, "shellcheck": {}}
    for source_index, rule in enumerate(inputs.source_records):
        source = rule.get("source")
        if source not in sources:
            raise MatchingValidationError(f"Unknown source category: {source!r}")
        selected = select_target_indices(relative[source_index], inputs.config)
        matches = []
        for rank, target_index in enumerate(selected, start=1):
            target = inputs.target_records[int(target_index)]
            matches.append(
                {
                    "rank": rank,
                    "target_id": target["id"],
                    "target_type": target.get("type"),
                    "parent_sr": normalize_parent_sr(target),
                    "foundational_requirement": target.get("foundational_requirement"),
                    "raw_cosine": float(raw[source_index, target_index]),
                    "relative_score": float(relative[source_index, target_index]),
                    "target_title": target.get("title"),
                    "target_text": target.get("text"),
                }
            )
        sources[source][rule["id"]] = {
            "source": source,
            "source_rule": {
                "id": rule["id"],
                "title": rule.get("title"),
                "problematic_code": rule.get("problematic_code"),
                "correct_code": rule.get("correct_code"),
                "rationale": rule.get("rationale"),
                "exceptions": rule.get("exceptions"),
            },
            "candidate_count": len(matches),
            "matches": matches,
        }

    observed = _observed_counts(sources, target_by_id)
    artifacts = inputs.config["artifacts"]
    matching = inputs.config["matching"]
    metadata = {
        "artifact_version": 2,
        "status": "definitive_canonical",
        "standard": "IEC 62443-3-3",
        "threshold": matching["threshold"]["value"],
        "threshold_operator": matching["threshold"]["operator"],
        "top_k": matching["top_k"],
        "power": matching["power_transform"]["exponent"],
        "method": inputs.config["canonical_method"],
        "source_dataset": artifacts["source_dataset"]["path"],
        "target_dataset": artifacts["target_dataset"]["path"],
        "numerical_semantics": {
            "dtype": matching["execution_dtype"],
            "cosine_implementation": matching["cosine_implementation"],
            "negative_clamp": matching["negative_clamp"],
            "normalization": matching["normalization"],
            "zero_row_policy": matching["zero_row_policy"],
            "ordering": matching["ordering"],
            "canonical_json_score_rounding": matching["serialization"][
                "canonical_json_score_rounding"
            ],
        },
        "provenance": {
            "source_dataset_sha256": inputs.hashes["source_dataset_sha256"],
            "target_dataset_sha256": inputs.hashes["target_dataset_sha256"],
            "source_cache_sha256": inputs.hashes["source_cache_sha256"],
            "source_cache_sidecar_sha256": inputs.hashes["source_sidecar_sha256"],
            "target_cache_sha256": inputs.hashes["target_cache_sha256"],
            "target_cache_sidecar_sha256": inputs.hashes["target_sidecar_sha256"],
            "embedding_text_audit_sha256": inputs.hashes["text_audit_sha256"],
            "embedding_generator_sha256": inputs.hashes["generator_sha256"],
            "matching_config_path": str(inputs.config_path.relative_to(ROOT)),
            "matching_config_sha256": inputs.config_sha256,
            "matching_script_path": str(Path(__file__).resolve().relative_to(ROOT)),
            "matching_script_sha256": hash_file(Path(__file__).resolve()),
        },
        "observed": observed,
    }
    payload = {"metadata": metadata, "sources": sources}
    validate_matching_payload(payload, inputs)
    return payload


def validate_matching_payload(payload: dict[str, Any], inputs: ValidatedInputs) -> dict[str, Any]:
    if not isinstance(payload, dict) or not isinstance(payload.get("sources"), dict):
        raise MatchingValidationError("Matching payload has no sources object")
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict) or metadata.get("status") != "definitive_canonical":
        raise MatchingValidationError("Matching payload is not marked definitive canonical")
    if metadata.get("provenance", {}).get("matching_config_sha256") != inputs.config_sha256:
        raise MatchingValidationError("Matching payload configuration hash mismatch")

    source_ids = []
    target_positions = {item_id: index for index, item_id in enumerate(inputs.target_ids)}
    target_set = set(inputs.target_ids)
    threshold = np.float32(inputs.config["matching"]["threshold"]["value"])
    top_k = inputs.config["matching"]["top_k"]
    for source in ("hadolint", "shellcheck"):
        rules = payload["sources"].get(source)
        if not isinstance(rules, dict):
            raise MatchingValidationError(f"Missing source group: {source}")
        expected_order = [
            record["id"] for record in inputs.source_records if record.get("source") == source
        ]
        if list(rules) != expected_order:
            raise MatchingValidationError(f"{source} source order or coverage mismatch")
        for source_id, entry in rules.items():
            source_ids.append(source_id)
            matches = entry.get("matches")
            if not isinstance(matches, list) or len(matches) > top_k:
                raise MatchingValidationError(f"Invalid match list for {source_id}")
            if entry.get("candidate_count") != len(matches):
                raise MatchingValidationError(f"Candidate count mismatch for {source_id}")
            if [match.get("rank") for match in matches] != list(
                range(1, len(matches) + 1)
            ):
                raise MatchingValidationError(f"Non-contiguous ranks for {source_id}")
            target_ids = [match.get("target_id") for match in matches]
            if len(target_ids) != len(set(target_ids)):
                raise MatchingValidationError(f"Duplicate target for {source_id}")
            if any(target_id not in target_set for target_id in target_ids):
                raise MatchingValidationError(f"Unknown target for {source_id}")
            scores = [np.float32(match.get("relative_score")) for match in matches]
            if any(score < threshold for score in scores):
                raise MatchingValidationError(f"Below-threshold score for {source_id}")
            ordering = [(-score, target_positions[target_id]) for score, target_id in zip(scores, target_ids)]
            if ordering != sorted(ordering):
                raise MatchingValidationError(f"Noncanonical candidate order for {source_id}")
    if source_ids != [record["id"] for record in inputs.source_records]:
        raise MatchingValidationError("Matching source coverage is incomplete")

    target_by_id = {record["id"]: record for record in inputs.target_records}
    observed = _observed_counts(payload["sources"], target_by_id)
    if metadata.get("observed") != observed:
        raise MatchingValidationError("Matching observed counts are inconsistent")
    return observed


def matching_csv_bytes(payload: dict[str, Any], decimal_places: int) -> bytes:
    stream = io.StringIO(newline="")
    fieldnames = [
        "source",
        "source_id",
        "source_title",
        "rank",
        "target_id",
        "target_type",
        "parent_sr",
        "foundational_requirement",
        "raw_cosine",
        "relative_score",
        "target_title",
        "target_text",
    ]
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for source, rules in payload["sources"].items():
        for source_id, entry in rules.items():
            for match in entry["matches"]:
                writer.writerow(
                    {
                        "source": source,
                        "source_id": source_id,
                        "source_title": entry["source_rule"].get("title"),
                        "rank": match["rank"],
                        "target_id": match["target_id"],
                        "target_type": match["target_type"],
                        "parent_sr": match["parent_sr"],
                        "foundational_requirement": match["foundational_requirement"],
                        "raw_cosine": f"{match['raw_cosine']:.{decimal_places}f}",
                        "relative_score": f"{match['relative_score']:.{decimal_places}f}",
                        "target_title": match["target_title"],
                        "target_text": match["target_text"],
                    }
                )
    return stream.getvalue().encode("utf-8")


def repository_state() -> dict[str, Any]:
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
        commit, dirty = None, None
    return {"commit": commit, "dirty": dirty}


def portable_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def matching_sidecar(
    payload: dict[str, Any], output_json: Path, command: list[str]
) -> dict[str, Any]:
    numpy_config = io.StringIO()
    with contextlib.redirect_stdout(numpy_config):
        np.show_config()
    metadata = payload["metadata"]
    return {
        "metadata_version": 1,
        "output_json_path": portable_path(output_json),
        "output_json_sha256": hash_file(output_json),
        **metadata["provenance"],
        "observed": metadata["observed"],
        "repository": repository_state(),
        "runtime": {
            "python_version": platform.python_version(),
            "numpy_version": np.__version__,
            "platform": platform.platform(),
            "numpy_backend": numpy_config.getvalue(),
        },
        "command": ["python", *command[1:]],
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--metadata-output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--validate-inputs-only",
        action="store_true",
        help="Validate all canonical inputs without computing similarities.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    inputs = validate_canonical_inputs(args.config)
    print(
        f"Validated canonical embeddings: {len(inputs.source_ids)} source, "
        f"{len(inputs.target_ids)} target, dimension {inputs.source_matrix.shape[1]}"
    )
    if args.validate_inputs_only:
        return

    output_json = args.output_json.resolve()
    output_csv = args.output_csv.resolve()
    metadata_output = (
        args.metadata_output.resolve()
        if args.metadata_output
        else output_json.with_suffix(".metadata.json")
    )
    require_outputs_available(
        [output_json, output_csv, metadata_output], overwrite=args.overwrite
    )
    payload = build_matching_payload(inputs)
    json_content = canonical_json_bytes(payload)
    csv_content = matching_csv_bytes(
        payload,
        inputs.config["matching"]["serialization"]["derived_csv_decimal_places"],
    )
    atomic_write(output_json, json_content)
    atomic_write(output_csv, csv_content)
    sidecar = matching_sidecar(payload, output_json, [sys.executable, *sys.argv])
    atomic_write(metadata_output, canonical_json_bytes(sidecar))
    observed = payload["metadata"]["observed"]
    print(f"Matching JSON SHA-256: {hash_file(output_json)}")
    print(f"Observed matches: {observed['match_count']}")
    print(f"Output: {output_json}")


if __name__ == "__main__":
    try:
        main()
    except MatchingValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
