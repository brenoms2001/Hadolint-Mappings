#!/usr/bin/env python3
"""Build the deterministic, unreviewed candidate set from canonical matches."""

from __future__ import annotations

import argparse
import contextlib
import csv
import datetime as dt
import io
import json
import platform
import sys
from pathlib import Path
from typing import Any

import numpy as np

import inspect_iec_matches as matcher


ROOT = Path(__file__).resolve().parent
DEFAULT_MATCHING_JSON = (
    ROOT / "data/output/mappings/iec/inspection/iec_matches_068_top10.json"
)
DEFAULT_MATCHING_SIDECAR = DEFAULT_MATCHING_JSON.with_suffix(".metadata.json")
DEFAULT_OUTPUT_JSON = (
    ROOT
    / "data/output/mappings/iec/inspection/gold_standard"
    / "iec_gold_standard_candidates.json"
)
DEFAULT_OUTPUT_CSV = DEFAULT_OUTPUT_JSON.with_suffix(".csv")


class CandidateValidationError(RuntimeError):
    """Raised when canonical candidate inputs or outputs violate their contract."""


CANDIDATE_KEYS = {
    "rank",
    "target_id",
    "target_type",
    "parent_sr",
    "foundational_requirement",
    "target_title",
    "target_text",
    "raw_cosine",
    "relative_score",
    "human_label",
    "human_confidence",
    "human_notes",
}


def load_canonical_matching(
    matching_path: Path = DEFAULT_MATCHING_JSON,
    sidecar_path: Path = DEFAULT_MATCHING_SIDECAR,
    config_path: Path = matcher.DEFAULT_CONFIG,
) -> tuple[dict[str, Any], dict[str, Any], matcher.ValidatedInputs, dict[str, str]]:
    inputs = matcher.validate_canonical_inputs(config_path)
    matching_hash = matcher.hash_file(matching_path)
    sidecar_hash = matcher.hash_file(sidecar_path)
    payload = matcher.load_json(matching_path)
    sidecar = matcher.load_json(sidecar_path)
    if not isinstance(payload, dict) or not isinstance(sidecar, dict):
        raise CandidateValidationError("Canonical matching or sidecar is not an object")
    if sidecar.get("output_json_sha256") != matching_hash:
        raise CandidateValidationError("Canonical matching sidecar hash mismatch")
    try:
        matcher.validate_matching_payload(payload, inputs)
    except matcher.MatchingValidationError as exc:
        raise CandidateValidationError(str(exc)) from exc
    provenance = payload["metadata"].get("provenance", {})
    if provenance.get("matching_config_sha256") != inputs.config_sha256:
        raise CandidateValidationError("Canonical matching configuration hash mismatch")
    return payload, sidecar, inputs, {
        "matching_json_sha256": matching_hash,
        "matching_sidecar_sha256": sidecar_hash,
    }


def build_candidate_payload(
    matching_payload: dict[str, Any],
    inputs: matcher.ValidatedInputs,
    matching_hashes: dict[str, str],
) -> dict[str, Any]:
    target_by_id = {record["id"]: record for record in inputs.target_records}
    sources: dict[str, dict[str, Any]] = {"hadolint": {}, "shellcheck": {}}
    for rule in inputs.source_records:
        source = rule.get("source")
        if source not in sources:
            raise CandidateValidationError(f"Unknown source category: {source!r}")
        source_id = rule["id"]
        try:
            matching_entry = matching_payload["sources"][source][source_id]
        except KeyError as exc:
            raise CandidateValidationError(
                f"Canonical matching is missing source {source_id}"
            ) from exc
        matches = []
        for matching_record in matching_entry["matches"]:
            target_id = matching_record["target_id"]
            if target_id not in target_by_id:
                raise CandidateValidationError(f"Unknown target ID: {target_id}")
            target = target_by_id[target_id]
            matches.append(
                {
                    "rank": matching_record["rank"],
                    "target_id": target_id,
                    "target_type": target.get("type"),
                    "parent_sr": matcher.normalize_parent_sr(target),
                    "foundational_requirement": target.get("foundational_requirement"),
                    "target_title": target.get("title"),
                    "target_text": target.get("text"),
                    "raw_cosine": matching_record["raw_cosine"],
                    "relative_score": matching_record["relative_score"],
                    "human_label": None,
                    "human_confidence": None,
                    "human_notes": None,
                }
            )
        sources[source][source_id] = {
            "source_rule": rule,
            "candidate_count": len(matches),
            "matches": matches,
        }

    matching_metadata = matching_payload["metadata"]
    output = {
        "metadata": {
            "artifact_version": 2,
            "status": "definitive_canonical_unreviewed",
            "standard": "IEC 62443-3-3",
            "threshold": matching_metadata["threshold"],
            "threshold_operator": matching_metadata["threshold_operator"],
            "top_k": matching_metadata["top_k"],
            "power": matching_metadata["power"],
            "method": matching_metadata["method"],
            "source_dataset": matching_metadata["source_dataset"],
            "target_dataset": matching_metadata["target_dataset"],
            "purpose": "Unreviewed human-evaluation candidates.",
            "label_status": "unreviewed",
            "labels": ["relevant", "partially_relevant", "irrelevant"],
            "provenance": {
                **matching_metadata["provenance"],
                **matching_hashes,
                "candidate_script_path": str(
                    Path(__file__).resolve().relative_to(ROOT)
                ),
                "candidate_script_sha256": matcher.hash_file(Path(__file__).resolve()),
            },
            "observed": matching_metadata["observed"],
        },
        "sources": sources,
    }
    validate_candidate_payload(output, matching_payload, inputs, matching_hashes)
    return output


def validate_candidate_payload(
    candidate_payload: dict[str, Any],
    matching_payload: dict[str, Any],
    inputs: matcher.ValidatedInputs,
    matching_hashes: dict[str, str],
) -> dict[str, Any]:
    metadata = candidate_payload.get("metadata")
    sources = candidate_payload.get("sources")
    if not isinstance(metadata, dict) or not isinstance(sources, dict):
        raise CandidateValidationError("Candidate payload has invalid top-level structure")
    if metadata.get("status") != "definitive_canonical_unreviewed":
        raise CandidateValidationError("Candidate payload is not definitive and unreviewed")
    provenance = metadata.get("provenance", {})
    for key, expected in matching_hashes.items():
        if provenance.get(key) != expected:
            raise CandidateValidationError(f"Candidate provenance mismatch: {key}")

    expected_all_ids = [record["id"] for record in inputs.source_records]
    actual_all_ids = []
    target_by_id = {record["id"]: record for record in inputs.target_records}
    target_set = set(target_by_id)
    top_k = inputs.config["matching"]["top_k"]
    total_pairs = 0
    hadolint_pairs = 0
    shellcheck_pairs = 0
    sr_pairs = 0
    re_pairs = 0
    zero_candidates = 0

    for source in ("hadolint", "shellcheck"):
        rules = sources.get(source)
        matching_rules = matching_payload["sources"].get(source)
        if not isinstance(rules, dict) or not isinstance(matching_rules, dict):
            raise CandidateValidationError(f"Missing source group: {source}")
        expected_order = [
            record["id"] for record in inputs.source_records if record.get("source") == source
        ]
        if list(rules) != expected_order:
            raise CandidateValidationError(f"{source} source order or coverage mismatch")
        for source_id, entry in rules.items():
            actual_all_ids.append(source_id)
            matches = entry.get("matches")
            matching_matches = matching_rules[source_id]["matches"]
            if not isinstance(matches, list) or not 0 <= len(matches) <= top_k:
                raise CandidateValidationError(f"Invalid candidates for {source_id}")
            if entry.get("candidate_count") != len(matches):
                raise CandidateValidationError(f"Candidate count mismatch for {source_id}")
            if len(matches) != len(matching_matches):
                raise CandidateValidationError(f"Matching order/length mismatch for {source_id}")
            if [item.get("rank") for item in matches] != list(
                range(1, len(matches) + 1)
            ):
                raise CandidateValidationError(f"Non-contiguous ranks for {source_id}")
            target_ids = [item.get("target_id") for item in matches]
            if len(target_ids) != len(set(target_ids)):
                raise CandidateValidationError(f"Duplicate target ID for {source_id}")
            if any(target_id not in target_set for target_id in target_ids):
                raise CandidateValidationError(f"Unknown target ID for {source_id}")
            zero_candidates += len(matches) == 0
            total_pairs += len(matches)
            if source == "hadolint":
                hadolint_pairs += len(matches)
            else:
                shellcheck_pairs += len(matches)

            for candidate, matching_record in zip(matches, matching_matches):
                if set(candidate) != CANDIDATE_KEYS:
                    raise CandidateValidationError(
                        f"Unexpected candidate fields for {source_id}: "
                        f"{sorted(set(candidate) - CANDIDATE_KEYS)}"
                    )
                if candidate["target_id"] != matching_record["target_id"]:
                    raise CandidateValidationError(f"Candidate order mismatch for {source_id}")
                if candidate["rank"] != matching_record["rank"]:
                    raise CandidateValidationError(f"Candidate rank mismatch for {source_id}")
                if candidate["raw_cosine"] != matching_record["raw_cosine"]:
                    raise CandidateValidationError(f"Raw cosine changed for {source_id}")
                if candidate["relative_score"] != matching_record["relative_score"]:
                    raise CandidateValidationError(f"Relative score changed for {source_id}")
                if any(
                    candidate[field] is not None
                    for field in ("human_label", "human_confidence", "human_notes")
                ):
                    raise CandidateValidationError(f"Non-null human field for {source_id}")
                target = target_by_id[candidate["target_id"]]
                expected_context = {
                    "target_type": target.get("type"),
                    "parent_sr": matcher.normalize_parent_sr(target),
                    "foundational_requirement": target.get("foundational_requirement"),
                    "target_title": target.get("title"),
                    "target_text": target.get("text"),
                }
                if any(candidate[key] != value for key, value in expected_context.items()):
                    raise CandidateValidationError(f"Target context mismatch for {source_id}")
                if candidate["target_type"] == "SR":
                    sr_pairs += 1
                elif candidate["target_type"] == "RE":
                    re_pairs += 1
                else:
                    raise CandidateValidationError(
                        f"Unexpected target type for {source_id}: {candidate['target_type']!r}"
                    )

    if actual_all_ids != expected_all_ids:
        raise CandidateValidationError("Candidate source coverage is incomplete")
    observed = {
        **matching_payload["metadata"]["observed"],
        "source_count": len(actual_all_ids),
        "match_count": total_pairs,
        "hadolint_match_count": hadolint_pairs,
        "shellcheck_match_count": shellcheck_pairs,
        "sr_match_count": sr_pairs,
        "re_match_count": re_pairs,
        "zero_candidate_source_count": zero_candidates,
    }
    if metadata.get("observed") != observed:
        raise CandidateValidationError("Candidate observed counts are inconsistent")
    return observed


def candidate_csv_bytes(payload: dict[str, Any], decimal_places: int) -> bytes:
    stream = io.StringIO(newline="")
    fieldnames = [
        "source",
        "source_id",
        "source_rule_title",
        "target_id",
        "target_type",
        "parent_sr",
        "foundational_requirement",
        "target_title",
        "rank",
        "raw_cosine",
        "relative_score",
        "human_label",
        "human_confidence",
        "human_notes",
    ]
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for source, rules in payload["sources"].items():
        for source_id, entry in rules.items():
            for candidate in entry["matches"]:
                writer.writerow(
                    {
                        "source": source,
                        "source_id": source_id,
                        "source_rule_title": entry["source_rule"].get("title"),
                        "target_id": candidate["target_id"],
                        "target_type": candidate["target_type"],
                        "parent_sr": candidate["parent_sr"],
                        "foundational_requirement": candidate[
                            "foundational_requirement"
                        ],
                        "target_title": candidate["target_title"],
                        "rank": candidate["rank"],
                        "raw_cosine": f"{candidate['raw_cosine']:.{decimal_places}f}",
                        "relative_score": f"{candidate['relative_score']:.{decimal_places}f}",
                        "human_label": "",
                        "human_confidence": "",
                        "human_notes": "",
                    }
                )
    return stream.getvalue().encode("utf-8")


def candidate_sidecar(
    payload: dict[str, Any], output_json: Path, command: list[str]
) -> dict[str, Any]:
    numpy_config = io.StringIO()
    with contextlib.redirect_stdout(numpy_config):
        np.show_config()
    return {
        "metadata_version": 1,
        "output_json_path": matcher.portable_path(output_json),
        "output_json_sha256": matcher.hash_file(output_json),
        **payload["metadata"]["provenance"],
        "observed": payload["metadata"]["observed"],
        "repository": matcher.repository_state(),
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
    parser.add_argument("--config", type=Path, default=matcher.DEFAULT_CONFIG)
    parser.add_argument("--matching-json", type=Path, default=DEFAULT_MATCHING_JSON)
    parser.add_argument(
        "--matching-metadata", type=Path, default=DEFAULT_MATCHING_SIDECAR
    )
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--metadata-output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    matching_payload, _, inputs, matching_hashes = load_canonical_matching(
        args.matching_json.resolve(),
        args.matching_metadata.resolve(),
        args.config.resolve(),
    )
    output_json = args.output_json.resolve()
    output_csv = args.output_csv.resolve()
    metadata_output = (
        args.metadata_output.resolve()
        if args.metadata_output
        else output_json.with_suffix(".metadata.json")
    )
    try:
        matcher.require_outputs_available(
            [output_json, output_csv, metadata_output], overwrite=args.overwrite
        )
    except matcher.MatchingValidationError as exc:
        raise CandidateValidationError(str(exc)) from exc
    payload = build_candidate_payload(matching_payload, inputs, matching_hashes)
    matcher.atomic_write(output_json, matcher.canonical_json_bytes(payload))
    matcher.atomic_write(
        output_csv,
        candidate_csv_bytes(
            payload,
            inputs.config["matching"]["serialization"]["derived_csv_decimal_places"],
        ),
    )
    sidecar = candidate_sidecar(payload, output_json, [sys.executable, *sys.argv])
    matcher.atomic_write(metadata_output, matcher.canonical_json_bytes(sidecar))
    observed = payload["metadata"]["observed"]
    print(f"Candidate JSON SHA-256: {matcher.hash_file(output_json)}")
    print(f"Observed sources: {observed['source_count']}")
    print(f"Observed pairs: {observed['match_count']}")
    print(f"Output: {output_json}")


if __name__ == "__main__":
    try:
        main()
    except (CandidateValidationError, matcher.MatchingValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
