"""Canonical preliminary Gemini audit for IEC 62443 candidate pairs.

The ``preflight`` and ``prepare-manifests`` commands never create a Gemini
client. Only the explicit ``run`` command can issue external requests.
"""

import argparse
import csv
import hashlib
import importlib.metadata
import io
import json
import math
import os
import platform
import tempfile
import time
from collections import Counter
from pathlib import Path

import yaml
from google import genai
from google.genai import types
from openpyxl import Workbook


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config/gemini_pair_audit.yaml"
SCRIPT_PATH = Path(__file__).resolve()

EXPECTED_PROMPT_SHA256 = (
    "e328d92c192e420694e57820e03ebef575bfebb48bd5f23df62499d2586390e5"
)
EXPECTED_SCHEMA_SHA256 = (
    "fab3fde89ff122e86e788cb4f5044f422e5316b8111023dfd8c03af9b76bd763"
)
EXPECTED_FREEZE_COMMIT = "c86caf8b47cd89cd219a27cc01a69fa4679ccf1a"
EXPECTED_CANDIDATE_SHA256 = (
    "064093f08764f3cbeeb1599a5626c4402349b2d35290d630e81bb00ac1b925a7"
)
EXPECTED_SOURCE_SHA256 = (
    "708cb58293a9d081f492c1010830f6cf96b040db9d767545cc211f6c6eee37ea"
)
EXPECTED_CLEAN_IEC_SHA256 = (
    "fa44e0af3598b58bae7e6dd8057479234bd8c97cd0d9f3effee34f244c007a4c"
)
EXPECTED_ENRICHED_IEC_SHA256 = (
    "33e222b4b57bb321933e113634510c19dabf2a1b5e32cc892d6455e48e2c0bdf"
)
EXPECTED_OUTPUT_NAMESPACE = (
    "data/output/mappings/iec/inspection/gold_standard/gemini_audit/"
    "canonical/v3-c86caf8-064093f08764"
)
HISTORICAL_OUTPUT_NAMESPACE = (
    ROOT
    / "data/output/mappings/iec/inspection/gold_standard/gemini_audit/full"
)

GEMINI_RESPONSE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "pair_id": {"type": "string"},
            "verdict": {
                "type": "string",
                "enum": ["YES", "MAYBE", "NO"],
            },
            "relation_type": {"type": "string"},
            "directness": {"type": "string"},
            "confidence": {"type": "integer"},
            "security_objective": {"type": "string"},
            "justification": {"type": "string"},
            "caveat": {"type": "string"},
        },
        "required": [
            "pair_id",
            "verdict",
            "relation_type",
            "directness",
            "confidence",
            "security_objective",
            "justification",
            "caveat",
        ],
    },
}

RESPONSE_STRING_FIELDS = (
    "pair_id",
    "verdict",
    "relation_type",
    "directness",
    "security_objective",
    "justification",
    "caveat",
)
HUMAN_FIELDS = ("human_label", "human_confidence", "human_notes")
CONTEXT_FIELDS = (
    "id",
    "type",
    "title",
    "text",
    "parent_sr",
    "foundational_requirement",
)


class AuditConfigurationError(RuntimeError):
    pass


class PreflightError(RuntimeError):
    pass


class ResponseValidationError(ValueError):
    pass


class GeminiBatchError(RuntimeError):
    def __init__(self, message, kind, original_error=None):
        super().__init__(message)
        self.kind = kind
        self.original_error = original_error


def sha256_bytes(content):
    return hashlib.sha256(content).hexdigest()


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def formatted_json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def atomic_write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def load_json(path):
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_path(value):
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def package_version(distribution):
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def response_schema_sha256():
    return sha256_bytes(canonical_json_bytes(GEMINI_RESPONSE_SCHEMA))


def load_config(path=CONFIG_PATH):
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise AuditConfigurationError("Pair-audit config must be a YAML object.")

    approved = {
        "version": 3,
        "audit_format_version": 1,
        "role": "preliminary_pair_auditor",
        "model": "gemini-3.1-flash-lite",
        "temperature": 0.0,
        "batch_size": 5,
        "response_mime": "application/json",
        "prompt_version": "iec-gemini-preliminary-audit-v3-enriched-context",
        "prompt_marker": "__CANDIDATE_PAYLOAD_JSON__",
        "prompt_template_sha256": EXPECTED_PROMPT_SHA256,
        "response_schema_sha256": EXPECTED_SCHEMA_SHA256,
    }
    for key, expected in approved.items():
        if config.get(key) != expected:
            raise AuditConfigurationError(
                f"Unsupported canonical config value for {key!r}: "
                f"expected {expected!r}, found {config.get(key)!r}."
            )

    retry_expected = {
        "transient_attempts": 5,
        "validation_attempts": 2,
        "request_delay_seconds": 5.0,
        "backoff_base_seconds": 10.0,
    }
    if config.get("retries") != retry_expected:
        raise AuditConfigurationError("Canonical retry settings differ from approval.")

    canonical = config.get("canonical", {})
    canonical_expected = {
        "freeze_commit": EXPECTED_FREEZE_COMMIT,
        "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
        "candidate_pair_count": 4149,
        "source_count": 595,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "clean_iec_sha256": EXPECTED_CLEAN_IEC_SHA256,
        "enriched_iec_sha256": EXPECTED_ENRICHED_IEC_SHA256,
        "output_namespace": EXPECTED_OUTPUT_NAMESPACE,
    }
    for key, expected in canonical_expected.items():
        if canonical.get(key) != expected:
            raise AuditConfigurationError(
                f"Unsupported canonical config value for canonical.{key}: "
                f"expected {expected!r}, found {canonical.get(key)!r}."
            )

    authority = config.get("authority")
    if authority != {"gold_standard": False, "human_review_required": True}:
        raise AuditConfigurationError("Gemini authority settings are invalid.")

    generation = config.get("generation_settings", {})
    explicitly_set = generation.get("explicitly_set")
    if explicitly_set != ["temperature", "response_mime_type", "response_schema"]:
        raise AuditConfigurationError("Explicit generation settings changed.")
    required_defaults = {
        "candidate_count",
        "max_output_tokens",
        "safety_settings",
        "seed",
        "stop_sequences",
        "top_k",
        "top_p",
    }
    defaults = generation.get("provider_defaults")
    if not isinstance(defaults, dict) or set(defaults) != required_defaults:
        raise AuditConfigurationError("Provider-default generation settings changed.")
    if any(value is not None for value in defaults.values()):
        raise AuditConfigurationError("Provider-default settings must remain unset.")

    prompt_path = resolve_path(config.get("prompt_path", ""))
    if not prompt_path.is_file():
        raise AuditConfigurationError(f"Prompt artifact not found: {prompt_path}")
    prompt = prompt_path.read_bytes()
    if sha256_bytes(prompt) != EXPECTED_PROMPT_SHA256:
        raise AuditConfigurationError("Historical v3 prompt-template hash mismatch.")
    marker = config["prompt_marker"].encode("utf-8")
    if prompt.count(marker) != 1:
        raise AuditConfigurationError("Prompt template must contain exactly one marker.")
    if response_schema_sha256() != EXPECTED_SCHEMA_SHA256:
        raise AuditConfigurationError("Historical v3 response-schema hash mismatch.")

    output_path = resolve_path(canonical["output_namespace"]).resolve()
    historical = HISTORICAL_OUTPUT_NAMESPACE.resolve()
    if output_path == historical or historical in output_path.parents:
        raise AuditConfigurationError("Canonical output may not reuse historical full/.")
    return config


def require_file_hash(path, expected, label):
    path = Path(path)
    if not path.is_file():
        raise PreflightError(f"Missing {label}: {path}")
    actual = sha256_file(path)
    if actual != expected:
        raise PreflightError(
            f"{label} SHA-256 mismatch: expected {expected}, found {actual}."
        )
    return actual


def classify_gap(gap):
    if gap is None:
        return None
    if gap >= 0.20:
        return "high_gap"
    if gap >= 0.10:
        return "medium_gap"
    if gap >= 0.05:
        return "low_gap"
    return "very_low_gap"


def make_prompt_pair_id(source, source_id, rank, target_id):
    return f"{source}:{source_id}:rank_{rank}:{target_id}"


def make_canonical_pair_id(source, source_id, target_id):
    identity = {
        "source": source,
        "source_id": source_id,
        "target_id": target_id,
    }
    return "pair-v1:" + sha256_bytes(canonical_json_bytes(identity))


def _forbidden_llm_keys(value, location="candidate"):
    if isinstance(value, dict):
        for key, nested in value.items():
            lowered = str(key).lower()
            if (
                lowered.startswith("llm")
                or "gemini" in lowered
                or lowered in {"verdict", "reasoning"}
            ):
                raise PreflightError(
                    f"Historical LLM field {key!r} found at {location}."
                )
            _forbidden_llm_keys(nested, f"{location}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _forbidden_llm_keys(nested, f"{location}[{index}]")


def _requirements(dataset, label):
    records = dataset.get("requirements") if isinstance(dataset, dict) else None
    if not isinstance(records, list):
        raise PreflightError(f"{label} must contain a requirements list.")
    ids = [record.get("id") for record in records if isinstance(record, dict)]
    if len(ids) != len(records) or any(not item for item in ids):
        raise PreflightError(f"{label} contains an invalid requirement record.")
    if len(ids) != len(set(ids)):
        raise PreflightError(f"{label} contains duplicate requirement IDs.")
    return records


def _validate_iec_parity(clean_records, enriched_records):
    if len(clean_records) != 100 or len(enriched_records) != 100:
        raise PreflightError("Clean/enriched IEC datasets must each contain 100 IDs.")
    if [item["id"] for item in clean_records] != [item["id"] for item in enriched_records]:
        raise PreflightError("Clean/enriched IEC ordered ID parity failed.")
    for clean, enriched in zip(clean_records, enriched_records):
        for field in CONTEXT_FIELDS:
            if clean.get(field) != enriched.get(field):
                raise PreflightError(
                    f"Clean/enriched IEC context mismatch for {clean['id']} field {field}."
                )


def _validate_number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PreflightError(f"{label} must be numeric.")
    if not math.isfinite(value):
        raise PreflightError(f"{label} must be finite.")


def build_canonical_records(candidate, source_data, clean_records, enriched_records):
    if not isinstance(source_data, dict) or len(source_data) != 595:
        raise PreflightError("Source dataset must be a 595-rule object.")
    expected_sources = {}
    for source_id, rule in source_data.items():
        if not isinstance(rule, dict) or rule.get("id") != source_id:
            raise PreflightError(f"Invalid source record identity for {source_id!r}.")
        source = rule.get("source")
        if source not in {"hadolint", "shellcheck"}:
            raise PreflightError(f"Invalid source for {source_id}: {source!r}.")
        expected_sources.setdefault(source, []).append(source_id)

    sources = candidate.get("sources") if isinstance(candidate, dict) else None
    if not isinstance(sources, dict):
        raise PreflightError("Candidate artifact must contain a sources object.")
    if list(sources) != list(expected_sources):
        raise PreflightError("Candidate source-group ordering is invalid.")

    clean_by_id = {item["id"]: item for item in clean_records}
    enriched_by_id = {item["id"]: item for item in enriched_records}
    target_order = {item["id"]: index for index, item in enumerate(clean_records)}
    records = []
    canonical_ids = set()
    prompt_ids = set()

    _forbidden_llm_keys(candidate)
    for source, expected_ids in expected_sources.items():
        rules = sources.get(source)
        if not isinstance(rules, dict) or list(rules) != expected_ids:
            raise PreflightError(f"Candidate source ordering/coverage failed for {source}.")
        for source_id in expected_ids:
            entry = rules[source_id]
            if not isinstance(entry, dict):
                raise PreflightError(f"Candidate entry {source_id} must be an object.")
            if entry.get("source_rule") != source_data[source_id]:
                raise PreflightError(f"Source context mismatch for {source_id}.")
            matches = entry.get("matches")
            if not isinstance(matches, list):
                raise PreflightError(f"Matches for {source_id} must be a list.")
            if entry.get("candidate_count") != len(matches):
                raise PreflightError(f"Candidate count mismatch for {source_id}.")
            if [item.get("rank") for item in matches] != list(
                range(1, len(matches) + 1)
            ):
                raise PreflightError(f"Invalid rank sequence for {source_id}.")
            target_ids = [item.get("target_id") for item in matches]
            if len(target_ids) != len(set(target_ids)):
                raise PreflightError(f"Duplicate target for {source_id}.")
            if any(target_id not in clean_by_id for target_id in target_ids):
                raise PreflightError(f"Unknown target ID for {source_id}.")
            expected_order = sorted(
                matches,
                key=lambda item: (
                    -item.get("relative_score", float("-inf")),
                    target_order[item.get("target_id")],
                ),
            )
            if [item["target_id"] for item in matches] != [
                item["target_id"] for item in expected_order
            ]:
                raise PreflightError(f"Candidate ordering invalid for {source_id}.")

            scores = []
            for match in matches:
                for field in HUMAN_FIELDS:
                    if field not in match or match[field] is not None:
                        raise PreflightError(
                            f"Canonical human field {field} is not null for {source_id}."
                        )
                _validate_number(match.get("raw_cosine"), f"{source_id}.raw_cosine")
                _validate_number(
                    match.get("relative_score"), f"{source_id}.relative_score"
                )
                target = clean_by_id[match["target_id"]]
                expected_parent = target.get("parent_sr")
                if expected_parent == target["id"]:
                    expected_parent = None
                expected_context = {
                    "target_type": target.get("type"),
                    "parent_sr": expected_parent,
                    "foundational_requirement": target.get(
                        "foundational_requirement"
                    ),
                    "target_title": target.get("title"),
                    "target_text": target.get("text"),
                }
                for field, expected in expected_context.items():
                    if match.get(field) != expected:
                        raise PreflightError(
                            f"Candidate target context mismatch for {source_id}/"
                            f"{target['id']} field {field}."
                        )
                scores.append(match["relative_score"])

            top1 = scores[0] if scores else None
            top2 = scores[1] if len(scores) >= 2 else None
            gap = top1 - top2 if top1 is not None and top2 is not None else None
            gap_bin = classify_gap(gap)
            source_rule = source_data[source_id]
            for match in matches:
                target = enriched_by_id[match["target_id"]]
                prompt_pair_id = make_prompt_pair_id(
                    source, source_id, match["rank"], match["target_id"]
                )
                canonical_pair_id = make_canonical_pair_id(
                    source, source_id, match["target_id"]
                )
                if prompt_pair_id in prompt_ids or canonical_pair_id in canonical_ids:
                    raise PreflightError(f"Duplicate pair identity for {source_id}.")
                prompt_ids.add(prompt_pair_id)
                canonical_ids.add(canonical_pair_id)
                records.append(
                    {
                        "canonical_pair_id": canonical_pair_id,
                        "prompt_pair_id": prompt_pair_id,
                        "pair_id": prompt_pair_id,
                        "source": source,
                        "source_id": source_id,
                        "source_title": source_rule.get("title"),
                        "problematic_code": source_rule.get("problematic_code"),
                        "correct_code": source_rule.get("correct_code"),
                        "rationale": source_rule.get("rationale"),
                        "exceptions": source_rule.get("exceptions"),
                        "raw_markdown": source_rule.get("raw_markdown"),
                        "rank": match["rank"],
                        "target_id": match["target_id"],
                        "target_type": match["target_type"],
                        "parent_sr": match["parent_sr"],
                        "foundational_requirement": match[
                            "foundational_requirement"
                        ],
                        "target_title": match["target_title"],
                        "target_text": match["target_text"],
                        "target_rationale": target.get("rationale"),
                        "rationale_source_pages": target.get(
                            "rationale_source_pages"
                        ),
                        "raw_cosine": match["raw_cosine"],
                        "relative_score": match["relative_score"],
                        "top1_relative_score": top1,
                        "top2_relative_score": top2,
                        "top1_top2_gap": gap,
                        "gap_bin": gap_bin,
                        "target_rationale_available": bool(target.get("rationale")),
                        "human_label": None,
                        "human_confidence": None,
                        "human_notes": None,
                    }
                )
    if len(records) != 4149:
        raise PreflightError(f"Expected 4149 canonical pairs, found {len(records)}.")
    return records


def build_pair_manifest(records, candidate_sha256):
    return {
        "manifest_version": 1,
        "candidate_sha256": candidate_sha256,
        "pair_count": len(records),
        "pairs": [
            {
                "index": index,
                "canonical_pair_id": record["canonical_pair_id"],
                "prompt_pair_id": record["prompt_pair_id"],
                "source": record["source"],
                "source_id": record["source_id"],
                "rank": record["rank"],
                "target_id": record["target_id"],
            }
            for index, record in enumerate(records)
        ],
    }


def build_batch_manifest(records, pair_manifest_sha256, batch_size):
    batches = []
    for batch_index, start in enumerate(range(0, len(records), batch_size)):
        batch_records = records[start : start + batch_size]
        membership = [record["canonical_pair_id"] for record in batch_records]
        membership_sha256 = sha256_bytes(canonical_json_bytes(membership))
        batches.append(
            {
                "batch_index": batch_index,
                "batch_id": f"batch-{batch_index + 1:04d}:{membership_sha256}",
                "start_index": start,
                "size": len(batch_records),
                "membership_sha256": membership_sha256,
                "canonical_pair_ids": membership,
                "prompt_pair_ids": [
                    record["prompt_pair_id"] for record in batch_records
                ],
            }
        )
    return {
        "manifest_version": 1,
        "pair_manifest_sha256": pair_manifest_sha256,
        "pair_count": len(records),
        "batch_size": batch_size,
        "batch_count": len(batches),
        "batches": batches,
    }


def preflight(config=None, verify_manifest_files=True):
    config = config or load_config()
    canonical = config["canonical"]
    paths = {
        "candidate": resolve_path(canonical["candidate_path"]),
        "source": resolve_path(canonical["source_path"]),
        "clean_iec": resolve_path(canonical["clean_iec_path"]),
        "enriched_iec": resolve_path(canonical["enriched_iec_path"]),
    }
    hashes = {
        "candidate_sha256": require_file_hash(
            paths["candidate"], canonical["candidate_sha256"], "candidate artifact"
        ),
        "source_sha256": require_file_hash(
            paths["source"], canonical["source_sha256"], "source dataset"
        ),
        "clean_iec_sha256": require_file_hash(
            paths["clean_iec"], canonical["clean_iec_sha256"], "clean IEC dataset"
        ),
        "enriched_iec_sha256": require_file_hash(
            paths["enriched_iec"],
            canonical["enriched_iec_sha256"],
            "enriched IEC dataset",
        ),
    }
    candidate = load_json(paths["candidate"])
    source_data = load_json(paths["source"])
    clean_records = _requirements(load_json(paths["clean_iec"]), "Clean IEC")
    enriched_records = _requirements(
        load_json(paths["enriched_iec"]), "Enriched IEC"
    )
    _validate_iec_parity(clean_records, enriched_records)
    records = build_canonical_records(
        candidate, source_data, clean_records, enriched_records
    )
    pair_manifest = build_pair_manifest(records, hashes["candidate_sha256"])
    pair_manifest_sha256 = sha256_bytes(canonical_json_bytes(pair_manifest))
    batch_manifest = build_batch_manifest(
        records, pair_manifest_sha256, config["batch_size"]
    )
    batch_manifest_sha256 = sha256_bytes(canonical_json_bytes(batch_manifest))

    batch_sizes = [batch["size"] for batch in batch_manifest["batches"]]
    if len(batch_sizes) != 830 or batch_sizes.count(5) != 829 or batch_sizes[-1] != 4:
        raise PreflightError("Canonical batch shape must be 829x5 plus one batch of 4.")

    if verify_manifest_files:
        expected = (
            (
                resolve_path(canonical["pair_manifest_path"]),
                canonical["pair_manifest_sha256"],
                pair_manifest,
                pair_manifest_sha256,
                "pair manifest",
            ),
            (
                resolve_path(canonical["batch_manifest_path"]),
                canonical["batch_manifest_sha256"],
                batch_manifest,
                batch_manifest_sha256,
                "batch manifest",
            ),
        )
        for path, configured_hash, value, computed_hash, label in expected:
            if configured_hash != computed_hash:
                raise PreflightError(
                    f"Configured {label} hash mismatch: expected computed "
                    f"{computed_hash}, found {configured_hash}."
                )
            require_file_hash(path, computed_hash, label)
            if load_json(path) != value:
                raise PreflightError(f"{label.title()} content is not canonical.")

    return {
        "config": config,
        "paths": paths,
        "hashes": hashes,
        "records": records,
        "pair_manifest": pair_manifest,
        "pair_manifest_sha256": pair_manifest_sha256,
        "batch_manifest": batch_manifest,
        "batch_manifest_sha256": batch_manifest_sha256,
    }


def write_manifests(state):
    canonical = state["config"]["canonical"]
    pair_path = resolve_path(canonical["pair_manifest_path"])
    batch_path = resolve_path(canonical["batch_manifest_path"])
    atomic_write(pair_path, canonical_json_bytes(state["pair_manifest"]))
    atomic_write(batch_path, canonical_json_bytes(state["batch_manifest"]))
    return pair_path, batch_path


def render_prompt(batch, config=None):
    config = config or load_config()
    payload = []
    for record in batch:
        payload.append(
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
        )
    payload_json = json.dumps(payload, ensure_ascii=False, indent=2)
    template = resolve_path(config["prompt_path"]).read_text(encoding="utf-8")
    marker = config["prompt_marker"]
    if template.count(marker) != 1:
        raise AuditConfigurationError("Prompt marker count changed.")
    return template.replace(marker, payload_json)


def validate_gemini_results(batch, results):
    if not isinstance(results, list):
        raise ResponseValidationError("Gemini response is not a list.")
    expected_ids = [record["prompt_pair_id"] for record in batch]
    returned_ids = []
    for result in results:
        if not isinstance(result, dict):
            raise ResponseValidationError("Gemini result must be an object.")
        missing_fields = [
            field
            for field in (*RESPONSE_STRING_FIELDS, "confidence")
            if field not in result
        ]
        if missing_fields:
            raise ResponseValidationError(
                "Gemini result omitted required fields: " + ", ".join(missing_fields)
            )
        for field in RESPONSE_STRING_FIELDS:
            if not isinstance(result[field], str):
                raise ResponseValidationError(f"Gemini field {field} must be a string.")
        if result["verdict"] not in {"YES", "MAYBE", "NO"}:
            raise ResponseValidationError("Invalid Gemini verdict.")
        confidence = result["confidence"]
        if type(confidence) is not int or not 1 <= confidence <= 5:
            raise ResponseValidationError(
                "Gemini confidence must be an integer from 1 to 5, not bool."
            )
        returned_ids.append(result["pair_id"])
    if len(returned_ids) != len(set(returned_ids)):
        raise ResponseValidationError("Gemini returned duplicate pair_ids.")
    missing = set(expected_ids) - set(returned_ids)
    extra = set(returned_ids) - set(expected_ids)
    if missing:
        raise ResponseValidationError(
            "Gemini omitted pair_ids: " + ", ".join(sorted(missing))
        )
    if extra:
        raise ResponseValidationError(
            "Gemini returned unexpected pair_ids: " + ", ".join(sorted(extra))
        )
    if len(results) != len(batch):
        raise ResponseValidationError("Gemini result count differs from batch size.")


def is_transient_error(error):
    text = str(error).lower()
    return any(
        pattern in text
        for pattern in (
            "503",
            "service unavailable",
            "temporarily unavailable",
            "deadline exceeded",
            "timeout",
            "connection reset",
            "internal server error",
            "unavailable",
        )
    )


def classify_api_error(error):
    text = str(error).lower()
    if any(item in text for item in ("429", "quota", "rate limit", "resource exhausted")):
        return "quota"
    if any(
        item in text
        for item in ("401", "403", "unauthorized", "authentication", "api key", "permission denied")
    ):
        return "authentication"
    if is_transient_error(error):
        return "transient"
    if any(
        item in text
        for item in ("400", "invalid argument", "model not found", "configuration")
    ):
        return "configuration"
    return "api"


def _usage_metadata(response):
    usage = getattr(response, "usage_metadata", None)
    if usage is None:
        return None
    fields = (
        "prompt_token_count",
        "candidates_token_count",
        "total_token_count",
        "cached_content_token_count",
    )
    return {field: getattr(usage, field, None) for field in fields}


def call_gemini(batch, node, client, config, sleep=time.sleep):
    prompt = render_prompt(batch, config)
    prompt_hash = sha256_bytes(prompt.encode("utf-8"))
    transient_failures = 0
    validation_failures = 0
    attempt_number = 0
    while True:
        attempt_number += 1
        attempt = {
            "attempt": attempt_number,
            "started_at_unix": time.time(),
            "prompt_sha256": prompt_hash,
            "prompt_pair_ids": [record["prompt_pair_id"] for record in batch],
        }
        node["attempts"].append(attempt)
        try:
            response = client.models.generate_content(
                model=config["model"],
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=config["temperature"],
                    response_mime_type=config["response_mime"],
                    response_schema=GEMINI_RESPONSE_SCHEMA,
                ),
            )
        except Exception as error:
            kind = classify_api_error(error)
            attempt.update(
                {
                    "completed_at_unix": time.time(),
                    "status": "api_error",
                    "error_kind": kind,
                    "error": str(error),
                }
            )
            if kind != "transient":
                raise GeminiBatchError(str(error), kind, error) from error
            transient_failures += 1
            if transient_failures >= config["retries"]["transient_attempts"]:
                raise GeminiBatchError(
                    "Transient/API failure exhausted approved attempts.",
                    "transient",
                    error,
                ) from error
            delay = config["retries"]["backoff_base_seconds"] * (
                2 ** (transient_failures - 1)
            )
            attempt["retry_delay_seconds"] = delay
            sleep(delay)
            continue

        text = getattr(response, "text", None)
        attempt["completed_at_unix"] = time.time()
        attempt["response_sha256"] = (
            sha256_bytes(text.encode("utf-8")) if isinstance(text, str) else None
        )
        attempt["usage"] = _usage_metadata(response)
        attempt["provider_model_version"] = getattr(response, "model_version", None)
        try:
            if not text:
                raise ResponseValidationError("Gemini returned an empty response.")
            results = json.loads(text)
            validate_gemini_results(batch, results)
        except (json.JSONDecodeError, ResponseValidationError) as error:
            validation_failures += 1
            attempt.update(
                {
                    "status": "validation_error",
                    "error_kind": "validation",
                    "error": str(error),
                }
            )
            if validation_failures >= config["retries"]["validation_attempts"]:
                raise GeminiBatchError(
                    "Gemini response failed validation attempts.",
                    "validation",
                    error,
                ) from error
            delay = config["retries"]["backoff_base_seconds"] * (
                2 ** (validation_failures - 1)
            )
            attempt["retry_delay_seconds"] = delay
            sleep(delay)
            continue
        attempt["status"] = "completed"
        return results


def process_batch_adaptive(batch, call, node_id="root"):
    node = {
        "node_id": node_id,
        "canonical_pair_ids": [record["canonical_pair_id"] for record in batch],
        "prompt_pair_ids": [record["prompt_pair_id"] for record in batch],
        "attempts": [],
        "children": [],
        "status": "running",
    }
    try:
        results = call(batch, node)
        validate_gemini_results(batch, results)
        node["status"] = "completed"
        return results, node
    except GeminiBatchError as error:
        node["failure_kind"] = error.kind
        node["failure"] = str(error)
        if error.kind != "validation" or len(batch) == 1:
            node["status"] = "failed"
            error.request_tree = node
            raise
        node["status"] = "split"
        midpoint = len(batch) // 2
        try:
            left_results, left_node = process_batch_adaptive(
                batch[:midpoint], call, f"{node_id}.L"
            )
            node["children"].append(left_node)
            right_results, right_node = process_batch_adaptive(
                batch[midpoint:], call, f"{node_id}.R"
            )
            node["children"].append(right_node)
        except GeminiBatchError as child_error:
            child_tree = getattr(child_error, "request_tree", None)
            if child_tree is not None and child_tree not in node["children"]:
                node["children"].append(child_tree)
            node["status"] = "failed"
            child_error.request_tree = node
            raise
        results = left_results + right_results
        validate_gemini_results(batch, results)
        node["status"] = "completed_after_split"
        return results, node


def merge_result(record, gemini_result, config):
    merged = dict(record)
    merged.update(
        {
            "llm_model": config["model"],
            "llm_prompt_version": config["prompt_version"],
            "llm_verdict": gemini_result["verdict"],
            "llm_relation_type": gemini_result["relation_type"],
            "llm_directness": gemini_result["directness"],
            "llm_confidence": gemini_result["confidence"],
            "llm_security_objective": gemini_result["security_objective"],
            "llm_justification": gemini_result["justification"],
            "llm_caveat": gemini_result["caveat"],
        }
    )
    return merged


def build_run_fingerprint(state):
    config = state["config"]
    canonical = config["canonical"]
    return {
        "fingerprint_version": 1,
        "canonical_freeze_commit": canonical["freeze_commit"],
        **state["hashes"],
        "input_paths": {
            name: str(path.relative_to(ROOT))
            for name, path in state["paths"].items()
        },
        "auditor_script_sha256": sha256_file(SCRIPT_PATH),
        "config_sha256": sha256_file(CONFIG_PATH),
        "prompt_template_sha256": config["prompt_template_sha256"],
        "response_schema_sha256": config["response_schema_sha256"],
        "model": config["model"],
        "temperature": config["temperature"],
        "batch_size": config["batch_size"],
        "retry_settings": config["retries"],
        "response_mime": config["response_mime"],
        "explicit_generation_settings": {
            "temperature": config["temperature"],
            "response_mime_type": config["response_mime"],
            "response_schema_sha256": config["response_schema_sha256"],
        },
        "provider_default_generation_settings": config["generation_settings"][
            "provider_defaults"
        ],
        "audit_format_version": config["audit_format_version"],
        "prompt_version": config["prompt_version"],
        "ordered_pair_manifest_sha256": state["pair_manifest_sha256"],
        "ordered_batch_manifest_sha256": state["batch_manifest_sha256"],
        "python_version": platform.python_version(),
        "google_genai_version": package_version("google-genai"),
    }


def output_paths(config):
    directory = resolve_path(config["canonical"]["output_namespace"])
    return {
        "directory": directory,
        "json": directory / "canonical_pair_audit.json",
        "csv": directory / "canonical_pair_audit.csv",
        "xlsx": directory / "canonical_pair_audit.xlsx",
        "markdown": directory / "canonical_pair_audit.md",
        "provenance": directory / "canonical_pair_audit.provenance.json",
        "checkpoint": directory / "canonical_pair_audit_checkpoint.json",
    }


def ensure_output_namespace(paths):
    directory = paths["directory"].resolve()
    historical = HISTORICAL_OUTPUT_NAMESPACE.resolve()
    if directory == historical or historical in directory.parents:
        raise AuditConfigurationError("Refusing historical output reuse.")
    if paths["json"].exists() or paths["provenance"].exists():
        raise RuntimeError("Refusing to overwrite a completed canonical audit.")


def _records_for_batch(state, batch_spec):
    start = batch_spec["start_index"]
    records = state["records"][start : start + batch_spec["size"]]
    if [record["canonical_pair_id"] for record in records] != batch_spec[
        "canonical_pair_ids"
    ]:
        raise PreflightError("Batch manifest membership differs from pair manifest.")
    return records


def pending_batch_specs(state, checkpoint):
    completed = checkpoint.get("completed_batches", {})
    return [
        batch
        for batch in state["batch_manifest"]["batches"]
        if batch["batch_id"] not in completed
    ]


def validate_merged_batch(batch, results):
    if not isinstance(results, list) or len(results) != len(batch):
        raise ResponseValidationError("Checkpoint batch result count mismatch.")
    expected = {record["canonical_pair_id"]: record for record in batch}
    observed = set()
    for result in results:
        if not isinstance(result, dict):
            raise ResponseValidationError("Checkpoint result must be an object.")
        canonical_id = result.get("canonical_pair_id")
        if canonical_id in observed:
            raise ResponseValidationError("Duplicate canonical_pair_id in results.")
        if canonical_id not in expected:
            raise ResponseValidationError("Unexpected canonical_pair_id in results.")
        observed.add(canonical_id)
        record = expected[canonical_id]
        if result.get("prompt_pair_id") != record["prompt_pair_id"]:
            raise ResponseValidationError("prompt_pair_id mapping mismatch.")
        if result.get("pair_id") != record["prompt_pair_id"]:
            raise ResponseValidationError("Historical pair_id mapping mismatch.")
        for field in HUMAN_FIELDS:
            if result.get(field) is not None:
                raise ResponseValidationError("Human annotation field was modified.")
        response_projection = {
            "pair_id": result.get("prompt_pair_id"),
            "verdict": result.get("llm_verdict"),
            "relation_type": result.get("llm_relation_type"),
            "directness": result.get("llm_directness"),
            "confidence": result.get("llm_confidence"),
            "security_objective": result.get("llm_security_objective"),
            "justification": result.get("llm_justification"),
            "caveat": result.get("llm_caveat"),
        }
        validate_gemini_results([record], [response_projection])
    if observed != set(expected):
        raise ResponseValidationError("Checkpoint batch canonical ID set mismatch.")


def new_checkpoint(fingerprint):
    now = time.time()
    return {
        "checkpoint_format_version": 1,
        "run_fingerprint": fingerprint,
        "status": "running",
        "created_at_unix": now,
        "updated_at_unix": now,
        "checkpoint_lineage": [{"event": "created", "timestamp_unix": now}],
        "completed_batches": {},
        "failed_batch": None,
    }


def load_checkpoint(path, fingerprint, state):
    path = Path(path)
    if not path.exists():
        return new_checkpoint(fingerprint)
    checkpoint = load_json(path)
    if not isinstance(checkpoint, dict):
        raise RuntimeError("Checkpoint must be an object.")
    if checkpoint.get("run_fingerprint") != fingerprint:
        raise RuntimeError(
            "Checkpoint run fingerprint mismatch; results were not accepted."
        )
    completed = checkpoint.get("completed_batches")
    if not isinstance(completed, dict):
        raise RuntimeError("Checkpoint completed_batches must be an object.")
    batch_by_id = {
        batch["batch_id"]: batch for batch in state["batch_manifest"]["batches"]
    }
    seen = set()
    for batch_id, block in completed.items():
        if batch_id not in batch_by_id:
            raise RuntimeError(f"Checkpoint contains unknown batch {batch_id}.")
        if not isinstance(block, dict) or block.get("status") != "completed":
            raise RuntimeError("Checkpoint may contain only fully completed batches.")
        records = _records_for_batch(state, batch_by_id[batch_id])
        validate_merged_batch(records, block.get("results"))
        block_ids = {item["canonical_pair_id"] for item in block["results"]}
        if seen & block_ids:
            raise RuntimeError("Checkpoint contains duplicate canonical pair results.")
        seen.update(block_ids)
    now = time.time()
    checkpoint.setdefault("checkpoint_lineage", []).append(
        {"event": "resumed", "timestamp_unix": now}
    )
    checkpoint["status"] = "running"
    checkpoint["updated_at_unix"] = now
    checkpoint["failed_batch"] = None
    return checkpoint


def save_checkpoint(path, checkpoint):
    checkpoint["updated_at_unix"] = time.time()
    atomic_write(path, formatted_json_bytes(checkpoint))


def validate_final_results(state, results):
    if len(results) != 4149:
        raise ResponseValidationError(f"Expected 4149 results, found {len(results)}.")
    expected = {record["canonical_pair_id"] for record in state["records"]}
    observed_list = [result.get("canonical_pair_id") for result in results]
    if len(observed_list) != len(set(observed_list)):
        raise ResponseValidationError("Final results contain duplicate canonical IDs.")
    observed = set(observed_list)
    if observed != expected:
        missing = expected - observed
        extra = observed - expected
        raise ResponseValidationError(
            f"Final canonical ID set mismatch: missing={len(missing)}, extra={len(extra)}."
        )
    by_id = {record["canonical_pair_id"]: record for record in state["records"]}
    for result in results:
        validate_merged_batch([by_id[result["canonical_pair_id"]]], [result])


def _atomic_csv(path, results):
    fieldnames = []
    seen = set()
    for result in results:
        for key in result:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    for result in results:
        writer.writerow(
            {
                key: json.dumps(value, ensure_ascii=False)
                if isinstance(value, (list, dict))
                else value
                for key, value in result.items()
            }
        )
    atomic_write(path, stream.getvalue().encode("utf-8"))


def _atomic_xlsx(path, metadata, results):
    workbook = Workbook()
    review = workbook.active
    review.title = "Review"
    columns = list(results[0]) if results else []
    review.append(columns)
    for result in results:
        review.append(
            [
                json.dumps(result.get(column), ensure_ascii=False)
                if isinstance(result.get(column), (list, dict))
                else result.get(column)
                for column in columns
            ]
        )
    review.freeze_panes = "A2"
    metadata_sheet = workbook.create_sheet("Metadata")
    metadata_sheet.append(["Key", "Value"])
    for key, value in metadata.items():
        metadata_sheet.append(
            [
                key,
                json.dumps(value, ensure_ascii=False)
                if isinstance(value, (list, dict))
                else value,
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".xlsx", dir=path.parent
    )
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    try:
        workbook.save(temporary_path)
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def _markdown(metadata, results):
    counts = Counter(result["llm_verdict"] for result in results)
    return (
        "# Canonical IEC 62443-3-3 Gemini Preliminary Pair Audit\n\n"
        "> Gemini is a preliminary auditor. Human review remains authoritative.\n\n"
        f"- Status: `{metadata['status']}`\n"
        f"- Results: `{len(results)}`\n"
        f"- YES: `{counts['YES']}`\n"
        f"- MAYBE: `{counts['MAYBE']}`\n"
        f"- NO: `{counts['NO']}`\n"
        f"- Prompt version: `{metadata['run_fingerprint']['prompt_version']}`\n"
        f"- Candidate SHA-256: `{metadata['run_fingerprint']['candidate_sha256']}`\n"
    )


def _collect_usage(request_tree, totals):
    for attempt in request_tree.get("attempts", []):
        totals["request_attempts"] += 1
        usage = attempt.get("usage") or {}
        for field, value in usage.items():
            if isinstance(value, int):
                totals[field] += value
    for child in request_tree.get("children", []):
        _collect_usage(child, totals)


def save_final_outputs(paths, state, checkpoint, fingerprint, started_at):
    results = []
    request_history = []
    for batch in state["batch_manifest"]["batches"]:
        block = checkpoint["completed_batches"][batch["batch_id"]]
        results.extend(block["results"])
        request_history.append(
            {"batch_id": batch["batch_id"], "request_tree": block["request_tree"]}
        )
    validate_final_results(state, results)
    completed_at = time.time()
    metadata = {
        "audit_format_version": state["config"]["audit_format_version"],
        "status": "completed",
        "purpose": "Preliminary Gemini audit; human review remains authoritative.",
        "gold_standard_authority": False,
        "human_review_required": True,
        "result_count": len(results),
        "started_at_unix": started_at,
        "completed_at_unix": completed_at,
        "run_fingerprint": fingerprint,
    }
    audit = {"metadata": metadata, "results": results}
    atomic_write(paths["json"], formatted_json_bytes(audit))
    _atomic_csv(paths["csv"], results)
    _atomic_xlsx(paths["xlsx"], metadata, results)
    atomic_write(paths["markdown"], _markdown(metadata, results).encode("utf-8"))

    usage_totals = Counter()
    for item in request_history:
        _collect_usage(item["request_tree"], usage_totals)
    verdict_counts = Counter(result["llm_verdict"] for result in results)
    provenance = {
        "provenance_version": 1,
        "status": "completed",
        "preliminary_audit": True,
        "human_review_required": True,
        "run_fingerprint": fingerprint,
        "candidate_count": len(results),
        "checkpoint_lineage": checkpoint["checkpoint_lineage"],
        "request_history": request_history,
        "started_at_unix": started_at,
        "completed_at_unix": completed_at,
        "provider_usage_totals_when_available": dict(usage_totals),
        "verdict_counts": dict(verdict_counts),
        "artifacts": {
            "result_json": {
                "path": str(paths["json"].relative_to(ROOT)),
                "sha256": sha256_file(paths["json"]),
            },
            "csv": {
                "path": str(paths["csv"].relative_to(ROOT)),
                "sha256": sha256_file(paths["csv"]),
            },
            "xlsx": {
                "path": str(paths["xlsx"].relative_to(ROOT)),
                "sha256": sha256_file(paths["xlsx"]),
            },
            "markdown": {
                "path": str(paths["markdown"].relative_to(ROOT)),
                "sha256": sha256_file(paths["markdown"]),
            },
        },
        "determinism_statement": (
            "Inputs, prompts, batching, settings, and run history are frozen; "
            "Gemini verdicts are not claimed to be byte-identical across reruns."
        ),
    }
    atomic_write(paths["provenance"], formatted_json_bytes(provenance))
    return results


def create_client():
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY before the explicit run command.")
    return genai.Client(api_key=api_key)


def run_canonical_audit(state=None, client=None, sleep=time.sleep):
    state = state or preflight()
    config = state["config"]
    paths = output_paths(config)
    ensure_output_namespace(paths)
    fingerprint = build_run_fingerprint(state)
    checkpoint = load_checkpoint(paths["checkpoint"], fingerprint, state)
    started_at = checkpoint.get("created_at_unix", time.time())
    if client is None:
        try:
            client = create_client()
        except Exception as error:
            checkpoint["status"] = "failed"
            checkpoint["failed_batch"] = {
                "batch_id": None,
                "failed_at_unix": time.time(),
                "error_kind": "configuration",
                "error": str(error),
                "request_tree": None,
            }
            save_checkpoint(paths["checkpoint"], checkpoint)
            raise
    batches = state["batch_manifest"]["batches"]

    for position, batch_spec in enumerate(batches):
        batch_id = batch_spec["batch_id"]
        if batch_id in checkpoint["completed_batches"]:
            continue
        records = _records_for_batch(state, batch_spec)
        call = lambda current, node: call_gemini(
            current, node, client, config, sleep=sleep
        )
        try:
            gemini_results, request_tree = process_batch_adaptive(records, call)
            by_prompt_id = {item["pair_id"]: item for item in gemini_results}
            merged = [
                merge_result(record, by_prompt_id[record["prompt_pair_id"]], config)
                for record in records
            ]
            validate_merged_batch(records, merged)
            checkpoint["completed_batches"][batch_id] = {
                "status": "completed",
                "completed_at_unix": time.time(),
                "membership_sha256": batch_spec["membership_sha256"],
                "request_tree": request_tree,
                "results": merged,
            }
            checkpoint["failed_batch"] = None
            save_checkpoint(paths["checkpoint"], checkpoint)
        except Exception as error:
            checkpoint["status"] = "failed"
            checkpoint["failed_batch"] = {
                "batch_id": batch_id,
                "failed_at_unix": time.time(),
                "error_kind": getattr(error, "kind", "internal"),
                "error": str(error),
                "request_tree": getattr(error, "request_tree", None),
            }
            save_checkpoint(paths["checkpoint"], checkpoint)
            raise
        if any(
            later["batch_id"] not in checkpoint["completed_batches"]
            for later in batches[position + 1 :]
        ):
            sleep(config["retries"]["request_delay_seconds"])

    checkpoint["status"] = "completed"
    results = save_final_outputs(paths, state, checkpoint, fingerprint, started_at)
    save_checkpoint(paths["checkpoint"], checkpoint)
    return results


def preflight_summary(state):
    return {
        "status": "canonical_preflight_passed",
        "gemini_requests_made": 0,
        "source_count": state["config"]["canonical"]["source_count"],
        "pair_count": len(state["records"]),
        "batch_count": len(state["batch_manifest"]["batches"]),
        "full_batches": sum(
            batch["size"] == 5 for batch in state["batch_manifest"]["batches"]
        ),
        "final_batch_size": state["batch_manifest"]["batches"][-1]["size"],
        "pair_manifest_sha256": state["pair_manifest_sha256"],
        "batch_manifest_sha256": state["batch_manifest_sha256"],
        **state["hashes"],
        "prompt_template_sha256": state["config"]["prompt_template_sha256"],
        "response_schema_sha256": state["config"]["response_schema_sha256"],
        "output_namespace": state["config"]["canonical"]["output_namespace"],
    }


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("prepare-manifests", "preflight", "run")
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    if args.command == "prepare-manifests":
        state = preflight(verify_manifest_files=False)
        pair_path, batch_path = write_manifests(state)
        print(json.dumps(preflight_summary(state), indent=2))
        print(f"Pair manifest: {pair_path}")
        print(f"Batch manifest: {batch_path}")
        return
    state = preflight()
    if args.command == "preflight":
        print(json.dumps(preflight_summary(state), indent=2))
        return
    run_canonical_audit(state)


if __name__ == "__main__":
    main()
