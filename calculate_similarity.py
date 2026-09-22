"""
Calculate semantic similarity between Hadolint/ShellCheck rules
and IEC 62443-3-3 requirements.

Methodology
-----------
1. Load precomputed, normalized embeddings.
2. Calculate cosine similarity using dot product.
3. Clamp negative similarities to zero.
4. Apply power transformation (p=5.5).
5. Normalize by the maximum transformed score for each source rule.
6. Generate the complete ranking against all IEC requirements.
7. Keep candidates with relative_score >= 0.60.
8. Preserve IEC SR/RE hierarchy.
9. Produce separate outputs for:
   - Hadolint (DL) -> IEC
   - ShellCheck (SC) -> IEC

Important
---------
The 0.60 threshold is RELATIVE to the best IEC candidate for each
source rule. It is NOT an absolute cosine similarity threshold.

The candidate generation stage evaluates all 100 IEC requirements.
Top-k is used only for optional diagnostic output and does not
precede the 0.60 filtering step.
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

EMBEDDINGS_DIR = DATA_DIR / "output" / "embeddings"

DATASET_DIR = DATA_DIR / "output" / "datasets"

OUTPUT_DIR = DATA_DIR / "output" / "mappings" / "iec"

HADOLINT_CACHE = (
    EMBEDDINGS_DIR / "cache_hadolint_structured.pkl"
)

IEC_CACHE = (
    EMBEDDINGS_DIR / "cache_iec_structured.pkl"
)

HADOLINT_DATASET = (
    DATASET_DIR / "hadolint_rules_structured.json"
)

IEC_DATASET = (
    DATASET_DIR / "iec62443_with_rationale.json"
)


# Relative-score threshold required by the methodology.
RELATIVE_THRESHOLD = 0.60

# Power transformation.
POWER = 5.5

# Number of candidates retained in the diagnostic full ranking.
# This does NOT affect candidate generation or the 0.60 filtering.
TOP_K = 10


# ============================================================
# IO HELPERS
# ============================================================

def load_pickle(path: Path) -> dict:
    """Load a pickle file."""
    print(f"Loading: {path}")

    if not path.exists():
        raise FileNotFoundError(
            f"Embedding cache not found: {path}"
        )

    with path.open("rb") as f:
        data = pickle.load(f)

    if not isinstance(data, dict):
        raise TypeError(
            f"Expected dict in {path}, got {type(data).__name__}"
        )

    return data


def load_json(path: Path) -> dict:
    """Load a JSON file."""
    print(f"Loading: {path}")

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def save_json(data, path: Path) -> None:
    """Save JSON with UTF-8 and readable formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Saved: {path}")


# ============================================================
# EMBEDDING HELPERS
# ============================================================

def extract_embeddings(cache: dict, name: str) -> dict[str, np.ndarray]:
    """
    Extract the actual embedding dictionary from the structured cache.

    Expected cache structure:

    {
        "metadata": {...},
        "embeddings": {
            "DL1001": [...],
            ...
        }
    }
    """

    if "embeddings" not in cache:
        raise KeyError(
            f"{name} cache does not contain an 'embeddings' key."
        )

    embeddings = cache["embeddings"]

    if not isinstance(embeddings, dict):
        raise TypeError(
            f"{name}['embeddings'] must be a dict, "
            f"got {type(embeddings).__name__}"
        )

    return {
        rule_id: np.asarray(vector, dtype=np.float32)
        for rule_id, vector in embeddings.items()
    }


def validate_embeddings(
    embeddings: dict[str, np.ndarray],
    name: str,
) -> int:
    """Validate embedding dimensions and report normalization."""

    if not embeddings:
        raise ValueError(f"{name} embeddings are empty.")

    dimensions = {
        vector.shape
        for vector in embeddings.values()
    }

    if len(dimensions) != 1:
        raise ValueError(
            f"{name} embeddings have inconsistent shapes: "
            f"{dimensions}"
        )

    shape = next(iter(dimensions))

    if len(shape) != 1:
        raise ValueError(
            f"{name} embeddings must be 1-dimensional vectors. "
            f"Got shape: {shape}"
        )

    dimension = shape[0]

    norms = np.array(
        [
            np.linalg.norm(vector)
            for vector in embeddings.values()
        ],
        dtype=np.float32,
    )

    min_norm = float(norms.min())
    max_norm = float(norms.max())

    print(f"{name}:")
    print(f"  Entries : {len(embeddings)}")
    print(f"  Dim     : {dimension}")
    print(f"  Norm    : {min_norm:.6f} - {max_norm:.6f}")

    return dimension


# ============================================================
# DATASET HELPERS
# ============================================================

def load_hadolint_rules(path: Path) -> dict[str, dict]:
    """
    Load structured Hadolint/ShellCheck dataset.

    Expected structure:

    {
        "DL1001": {
            "id": "DL1001",
            "source": "hadolint",
            ...
        },
        ...
    }
    """

    data = load_json(path)

    if not isinstance(data, dict):
        raise TypeError(
            "Hadolint dataset must be a dictionary."
        )

    rules = {}

    for rule_id, rule in data.items():

        if not isinstance(rule, dict):
            continue

        actual_id = rule.get("id", rule_id)
        source = rule.get("source")

        if source not in {"hadolint", "shellcheck"}:
            continue

        rules[actual_id] = rule

    return rules


def load_iec_requirements(path: Path) -> dict[str, dict]:
    """
    Load IEC 62443-3-3 requirements.

    Expected structure:

    {
        "requirements": [
            {
                "id": "SR 1.1",
                "type": "SR",
                "title": "...",
                "text": "...",
                "parent_sr": "SR 1.1",
                ...
            }
        ]
    }
    """

    data = load_json(path)

    if not isinstance(data, dict):
        raise TypeError(
            "IEC dataset must be a dictionary."
        )

    requirements = data.get("requirements")

    if not isinstance(requirements, list):
        raise ValueError(
            "IEC dataset does not contain a valid "
            "'requirements' list."
        )

    result = {}

    for requirement in requirements:

        if not isinstance(requirement, dict):
            continue

        requirement_id = requirement.get("id")

        if not requirement_id:
            continue

        result[requirement_id] = requirement

    return result


# ============================================================
# IEC HIERARCHY
# ============================================================

def normalize_parent_sr(requirement: dict) -> str | None:
    """
    Normalize parent_sr.

    Important rule:
    If target_id == parent_sr, return None.

    Example:

        SR 1.3
            parent_sr = SR 1.3

    becomes:

        parent_sr = null

    Whereas:

        SR 1.3 RE 1
            parent_sr = SR 1.3

    remains:

        parent_sr = "SR 1.3"
    """

    target_id = requirement.get("id")
    parent_sr = requirement.get("parent_sr")

    if not parent_sr:
        return None

    if target_id == parent_sr:
        return None

    return parent_sr


# ============================================================
# SIMILARITY
# ============================================================

def build_iec_matrix(
    iec_embeddings: dict[str, np.ndarray],
    iec_requirements: dict[str, dict],
):
    """
    Build a matrix of IEC embeddings and matching IDs.

    The order of IDs is preserved explicitly so that matrix
    columns can be mapped back to IEC requirements.
    """

    ids = [
        requirement_id
        for requirement_id in iec_requirements
        if requirement_id in iec_embeddings
    ]

    if not ids:
        raise ValueError(
            "No IEC requirements have matching embeddings."
        )

    matrix = np.vstack(
        [iec_embeddings[requirement_id] for requirement_id in ids]
    )

    return ids, matrix


def calculate_scores(
    source_vector: np.ndarray,
    target_matrix: np.ndarray,
):
    """
    Calculate raw and transformed similarity scores.

    Because BGE embeddings were generated with
    normalize_embeddings=True, cosine similarity can be calculated
    through a dot product.

    Steps:

        cosine
          ↓
        max(cosine, 0)
          ↓
        score ** POWER
          ↓
        divide by maximum
    """

    # Cosine similarity because vectors are normalized.
    raw_similarity = target_matrix @ source_vector

    # Remove negative similarity values.
    clipped_similarity = np.maximum(
        raw_similarity,
        0.0,
    )

    # Power transformation.
    transformed = np.power(
        clipped_similarity,
        POWER,
    )

    maximum = float(transformed.max())

    if maximum <= 0:
        relative_scores = np.zeros_like(
            transformed,
            dtype=np.float32,
        )
    else:
        relative_scores = transformed / maximum

    return (
        raw_similarity,
        clipped_similarity,
        transformed,
        relative_scores,
    )


# ============================================================
# MAPPING GENERATION
# ============================================================

def generate_mapping(
    source_rules: dict[str, dict],
    source_embeddings: dict[str, np.ndarray],
    iec_requirements: dict[str, dict],
    iec_embeddings: dict[str, np.ndarray],
    source_name: str,
):
    """
    Generate complete rankings and thresholded candidates.

    Returns:

    {
        "metadata": {...},
        "rules": {
            "DL1000": {
                "source_rule": {...},
                "best_match": {...},
                "candidates": [...]
            }
        }
    }
    """

    iec_ids, iec_matrix = build_iec_matrix(
        iec_embeddings,
        iec_requirements,
    )

    results = {}

    processed = 0
    candidate_count = 0

    for source_id, source_rule in source_rules.items():

        if source_id not in source_embeddings:
            print(
                f"WARNING: no embedding for {source_id}; skipping."
            )
            continue

        source_vector = source_embeddings[source_id]

        (
            raw_similarity,
            clipped_similarity,
            transformed,
            relative_scores,
        ) = calculate_scores(
            source_vector,
            iec_matrix,
        )

        # Ranking is based on the relative score.
        ranking = np.argsort(
            relative_scores
        )[::-1]

        ranked_candidates = []

        for index in ranking:

            target_id = iec_ids[index]
            target_requirement = iec_requirements[target_id]

            parent_sr = normalize_parent_sr(
                target_requirement
            )

            candidate = {
                "target_id": target_id,
                "target_type": target_requirement.get("type"),
                "parent_sr": parent_sr,
                "title": target_requirement.get("title"),
                "raw_similarity": round(
                    float(raw_similarity[index]),
                    6,
                ),
                "relative_score": round(
                    float(relative_scores[index]),
                    6,
                ),
            }

            ranked_candidates.append(candidate)

        # ----------------------------------------------------
        # Best candidate
        # ----------------------------------------------------

        best_match = ranked_candidates[0]

        # ----------------------------------------------------
        # Threshold AFTER ranking across all IEC requirements.
        #
        # This is important:
        # we do NOT first take top-k and then apply 0.60.
        # Every IEC requirement gets a chance to pass.
        # ----------------------------------------------------

        threshold_candidates = [
            candidate
            for candidate in ranked_candidates
            if candidate["relative_score"] >= RELATIVE_THRESHOLD
        ]

        candidate_count += len(threshold_candidates)

        # ----------------------------------------------------
        # Diagnostic top-k.
        #
        # This is only retained to inspect the ranking.
        # It does not influence threshold_candidates.
        # ----------------------------------------------------

        top_k = ranked_candidates[:TOP_K]

        results[source_id] = {
            "source_id": source_id,
            "source": source_rule.get("source"),
            "title": source_rule.get("title"),

            "best_match": best_match,

            "candidates": threshold_candidates,

            "top_k": top_k,

            "candidate_count": len(
                threshold_candidates
            ),
        }

        processed += 1

    print()
    print(f"{source_name}")
    print("-" * 60)
    print(f"Rules processed       : {processed}")
    print(f"Rules with candidates : {sum(
        1 for result in results.values()
        if result['candidate_count'] > 0
    )}")
    print(f"Total candidates      : {candidate_count}")

    return results


# ============================================================
# OUTPUT SUMMARIZATION
# ============================================================

def build_output(
    results: dict[str, dict],
    source_name: str,
    metadata: dict,
):
    """
    Convert internal results into the final JSON representation.

    The output intentionally separates:
      - metadata
      - source rule
      - best match
      - thresholded candidates
      - diagnostic top-k
    """

    return {
        "metadata": {
            "method": "relative semantic similarity",
            "source": source_name,
            "target": "IEC 62443-3-3",

            "embedding_model": metadata.get(
                "embedding_model"
            ),

            "embedding_dimension": metadata.get(
                "embedding_dimension"
            ),

            "similarity": "cosine",
            "negative_similarity": "clamped_to_zero",
            "power": POWER,

            "relative_normalization": (
                "per source rule, divided by maximum "
                "transformed similarity"
            ),

            "relative_threshold": RELATIVE_THRESHOLD,

            "threshold_type": "relative",

            "candidate_generation": (
                "all IEC requirements evaluated before "
                "threshold filtering"
            ),

            "top_k": TOP_K,

            "note": (
                "top_k is diagnostic only and does not "
                "limit candidate generation"
            ),
        },

        "rules": results,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("HADOLINT / SHELLCHECK → IEC 62443-3-3")
    print("Semantic Similarity Mapping")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # Load caches
    # --------------------------------------------------------

    hadolint_cache = load_pickle(
        HADOLINT_CACHE
    )

    iec_cache = load_pickle(
        IEC_CACHE
    )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    hadolint_metadata = hadolint_cache.get(
        "metadata",
        {},
    )

    iec_metadata = iec_cache.get(
        "metadata",
        {},
    )

    print()
    print("Embedding metadata")
    print("-" * 60)

    print(
        f"Hadolint model     : "
        f"{hadolint_metadata.get('model')}"
    )

    print(
        f"Hadolint dimension : "
        f"{hadolint_metadata.get('dimension')}"
    )

    print(
        f"IEC model          : "
        f"{iec_metadata.get('model')}"
    )

    print(
        f"IEC dimension      : "
        f"{iec_metadata.get('dimension')}"
    )

    # --------------------------------------------------------
    # Extract embeddings
    # --------------------------------------------------------

    hadolint_embeddings = extract_embeddings(
        hadolint_cache,
        "Hadolint",
    )

    iec_embeddings = extract_embeddings(
        iec_cache,
        "IEC",
    )

    print()

    hadolint_dimension = validate_embeddings(
        hadolint_embeddings,
        "Hadolint",
    )

    iec_dimension = validate_embeddings(
        iec_embeddings,
        "IEC",
    )

    if hadolint_dimension != iec_dimension:
        raise ValueError(
            "Embedding dimensions do not match: "
            f"Hadolint={hadolint_dimension}, "
            f"IEC={iec_dimension}"
        )

    # --------------------------------------------------------
    # Load structured datasets
    # --------------------------------------------------------

    source_rules = load_hadolint_rules(
        HADOLINT_DATASET
    )

    iec_requirements = load_iec_requirements(
        IEC_DATASET
    )

    print()
    print("Dataset")
    print("-" * 60)

    print(
        f"Source rules loaded : {len(source_rules)}"
    )

    print(
        f"IEC requirements    : {len(iec_requirements)}"
    )

    # --------------------------------------------------------
    # Split DL / SC
    # --------------------------------------------------------

    hadolint_rules = {
        rule_id: rule
        for rule_id, rule in source_rules.items()
        if rule.get("source") == "hadolint"
    }

    shellcheck_rules = {
        rule_id: rule
        for rule_id, rule in source_rules.items()
        if rule.get("source") == "shellcheck"
    }

    hadolint_embeddings_filtered = {
        rule_id: hadolint_embeddings[rule_id]
        for rule_id in hadolint_rules
        if rule_id in hadolint_embeddings
    }

    shellcheck_embeddings_filtered = {
        rule_id: hadolint_embeddings[rule_id]
        for rule_id in shellcheck_rules
        if rule_id in hadolint_embeddings
    }

    print()
    print("Source split")
    print("-" * 60)

    print(
        f"Hadolint (DL) : {len(hadolint_rules)}"
    )

    print(
        f"ShellCheck (SC): {len(shellcheck_rules)}"
    )

    # --------------------------------------------------------
    # Generate DL → IEC mapping
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("GENERATING HADOLINT (DL) → IEC")
    print("=" * 70)

    dl_results = generate_mapping(
        source_rules=hadolint_rules,
        source_embeddings=hadolint_embeddings_filtered,
        iec_requirements=iec_requirements,
        iec_embeddings=iec_embeddings,
        source_name="Hadolint",
    )

    dl_output = build_output(
        results=dl_results,
        source_name="Hadolint (DL)",
        metadata={
            "embedding_model": hadolint_metadata.get(
                "model"
            ),
            "embedding_dimension": hadolint_metadata.get(
                "dimension"
            ),
        },
    )

    # --------------------------------------------------------
    # Generate SC → IEC mapping
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("GENERATING SHELLCHECK (SC) → IEC")
    print("=" * 70)

    sc_results = generate_mapping(
        source_rules=shellcheck_rules,
        source_embeddings=shellcheck_embeddings_filtered,
        iec_requirements=iec_requirements,
        iec_embeddings=iec_embeddings,
        source_name="ShellCheck",
    )

    sc_output = build_output(
        results=sc_results,
        source_name="ShellCheck (SC)",
        metadata={
            "embedding_model": hadolint_metadata.get(
                "model"
            ),
            "embedding_dimension": hadolint_metadata.get(
                "dimension"
            ),
        },
    )

    # --------------------------------------------------------
    # Save outputs
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    dl_path = (
        OUTPUT_DIR
        / "hadolint_iec_candidates_60.json"
    )

    sc_path = (
        OUTPUT_DIR
        / "shellcheck_iec_candidates_60.json"
    )

    save_json(
        dl_output,
        dl_path,
    )

    save_json(
        sc_output,
        sc_path,
    )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("COMPLETE")
    print("=" * 70)

    print(
        f"Hadolint rules : {len(dl_results)}"
    )

    print(
        f"ShellCheck rules: {len(sc_results)}"
    )

    print()
    print(
        f"DL output : {dl_path}"
    )

    print(
        f"SC output : {sc_path}"
    )


if __name__ == "__main__":
    main()