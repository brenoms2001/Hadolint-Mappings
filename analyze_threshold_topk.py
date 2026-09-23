import json
import pickle
from pathlib import Path

import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path("data")

HADOLINT_CACHE = BASE_DIR / "output/embeddings/cache_hadolint_structured.pkl"
IEC_CACHE = BASE_DIR / "output/embeddings/cache_iec_structured.pkl"

HADOLINT_DATASET = BASE_DIR / "output/datasets/hadolint_rules_structured.json"
IEC_DATASET = BASE_DIR / "output/datasets/iec62443_clean.json"

OUTPUT_FILE = BASE_DIR / "output/mappings/iec/threshold_topk_analysis.json"

# Valuees que queremos comparar
THRESHOLDS = [
    0.60,
    0.65,
    0.68,
    0.70,
    0.75,
    0.80,
]

TOP_K_VALUES = [
    5,
    10,
    15,
]

POWER = 5.5


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_pickle(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_source_rules(dataset):
    """
    Extracts the rules from the Hadolint/ShellCheck dataset.

    The structured JSON holds the IDs directly as keys:

        {
            "DL1001": {...},
            "DL3000": {...},
            "SC2016": {...}
        }

    Returns a list of rules, preserving the order of the JSON.
    """
    if not isinstance(dataset, dict):
        raise TypeError(
            "The Hadolint/ShellCheck dataset must be a JSON object."
        )

    return list(dataset.values())


def get_requirements(dataset):
    """
    Extracts the requirements of the IEC 62443.

    Expected format:

        {
            "metadata": {...},
            "requirements": [...]
        }
    """
    if isinstance(dataset, dict):
        requirements = dataset.get("requirements")

        if not isinstance(requirements, list):
            raise ValueError(
                "Invalid IEC dataset: "
                "'requirements' must be a list."
            )

        return requirements

    if isinstance(dataset, list):
        return dataset

    raise TypeError(
        "Unexpected format for IEC dataset."
    )

def normalize_parent_sr(req):
    """
    For an SR:
        parent_sr = null

    For an RE:
        parent_sr = parent SR
    """
    if req["id"] == req.get("parent_sr"):
        return None

    return req.get("parent_sr")


def descriptive_stats(values):
    """
    Basic statistics for a numeric list.
    """
    if not values:
        return {
            "min": 0,
            "mean": 0,
            "median": 0,
            "p90": 0,
            "p95": 0,
            "max": 0,
        }

    arr = np.asarray(values, dtype=float)

    return {
        "min": float(np.min(arr)),
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "p90": float(np.percentile(arr, 90)),
        "p95": float(np.percentile(arr, 95)),
        "max": float(np.max(arr)),
    }


def build_embedding_matrix(cache, ids):
    """
    Rebuilds the embedding matrix in the order of the IDs
    provided by the dataset.

    Supports:
        1. embeddings as a matrix/list;
        2. embeddings as {id: vector};
        3. embeddings as {id: {"embedding": vector}};
        4. embeddings as {id: {"vector": vector}}.
    """

    embeddings = cache["embeddings"]

    # --------------------------------------------------------
    # Matrix format
    # --------------------------------------------------------

    if not isinstance(embeddings, dict):
        return np.asarray(
            embeddings,
            dtype=np.float32
        )

    # --------------------------------------------------------
    # ID-indexed format
    # --------------------------------------------------------

    matrix = []

    for item_id in ids:

        if item_id not in embeddings:
            raise KeyError(
                f"Embedding not found for ID: {item_id}"
            )

        vector = embeddings[item_id]

        # If the embedding is encapsulated in a dictionary
        if isinstance(vector, dict):

            if "embedding" in vector:
                vector = vector["embedding"]

            elif "vector" in vector:
                vector = vector["vector"]

            else:
                raise ValueError(
                    f"Unknown embedding format for "
                    f"ID {item_id}: "
                    f"{vector.keys()}"
                )

        matrix.append(vector)

    return np.asarray(
        matrix,
        dtype=np.float32
    )


# ============================================================
# LOADING
# ============================================================

print("=" * 70)
print("THRESHOLD × TOP-K ANALYSIS")
print("=" * 70)

print("\nLoading caches...")

hadolint_cache = load_pickle(HADOLINT_CACHE)
iec_cache = load_pickle(IEC_CACHE)

print(
    f"Hadolint cache embeddings type: "
    f"{type(hadolint_cache['embeddings']).__name__}"
)

print(
    f"IEC cache embeddings type      : "
    f"{type(iec_cache['embeddings']).__name__}"
)

print("\nLoading datasets...")

hadolint_dataset = load_json(HADOLINT_DATASET)
iec_dataset = load_json(IEC_DATASET)

source_rules = get_source_rules(hadolint_dataset)
iec_requirements = get_requirements(iec_dataset)

print(f"Source rules         : {len(source_rules)}")
print(f"IEC requirements     : {len(iec_requirements)}")


# ============================================================
# IDs
# ============================================================

source_ids = [
    rule["id"]
    for rule in source_rules
]

iec_ids = [
    req["id"]
    for req in iec_requirements
]


# ============================================================
# MATRIX CONSTRUCTION
# ============================================================

hadolint_embeddings = build_embedding_matrix(
    hadolint_cache,
    source_ids
)

iec_embeddings = build_embedding_matrix(
    iec_cache,
    iec_ids
)

print(
    f"\nHadolint embeddings : "
    f"{hadolint_embeddings.shape}"
)

print(
    f"IEC embeddings      : "
    f"{iec_embeddings.shape}"
)


# ============================================================
# EMBEDDINGS VALIDATION
# ============================================================

if len(source_rules) != len(hadolint_embeddings):
    raise ValueError(
        "The number of Hadolint/ShellCheck rules "
        "does not match the number of embeddings."
    )

if len(iec_requirements) != len(iec_embeddings):
    raise ValueError(
        "The number of IEC requirements "
        "does not match the number of embeddings."
    )

if len(set(source_ids)) != len(source_ids):
    raise ValueError(
        "Duplicate IDs in source rules."
    )

if len(set(iec_ids)) != len(iec_ids):
    raise ValueError(
        "Duplicate IDs in IEC requirements."
    )


# ============================================================
# COSINE SIMILARITY
# ============================================================

print("\nComputing similarity matrix...")

# Since the embeddings are already normalized:
# cosine(a, b) = dot(a, b)

similarity_matrix = (
    hadolint_embeddings @ iec_embeddings.T
)

print(
    f"Similarity matrix    : "
    f"{similarity_matrix.shape}"
)

print(
    f"Raw similarity range : "
    f"{similarity_matrix.min():.4f} - "
    f"{similarity_matrix.max():.4f}"
)


# ============================================================
# RELATIVE-SCORE PRECALCULATION
# ============================================================

"""
For each source rule:

1. negative cosine -> 0
2. cosine ** POWER
3. normalization by that rule's maximum

Thus:

    relative_score = transformed / max(transformed)

The best candidate of each rule will have score = 1.0.
"""

clamped = np.maximum(
    similarity_matrix,
    0.0
)

transformed = np.power(
    clamped,
    POWER
)

row_max = transformed.max(
    axis=1,
    keepdims=True
)

# Avoids division by zero.
relative_matrix = np.divide(
    transformed,
    row_max,
    out=np.zeros_like(transformed),
    where=row_max > 0,
)

print(
    f"Relative score range: "
    f"{relative_matrix.min():.4f} - "
    f"{relative_matrix.max():.4f}"
)


# ============================================================
# SRs' metadata
# ============================================================

iec_parent_sr = []

for req in iec_requirements:
    iec_parent_sr.append(
        normalize_parent_sr(req)
    )


# ============================================================
# DL / SC SPLIT
# ============================================================

source_indices = {
    "hadolint": [],
    "shellcheck": [],
}

for idx, rule in enumerate(source_rules):

    source = rule["source"]

    if source not in source_indices:
        raise ValueError(
            f"Unexpected source: {source}"
        )

    source_indices[source].append(idx)


print("\nRules by source:")

for source, indices in source_indices.items():

    print(
        f"  {source:12s}: {len(indices)}"
    )


# ============================================================
# ANALYSIS
# ============================================================

all_results = []

for threshold in THRESHOLDS:

    for top_k in TOP_K_VALUES:

        result = {
            "threshold": threshold,
            "top_k": top_k,
            "power": POWER,
            "sources": {},
        }

        for source, indices in source_indices.items():

            candidate_counts = []
            parent_counts = []

            selected_relative_scores = []
            selected_raw_similarities = []

            rules_with_candidates = 0
            rules_without_candidates = 0

            for source_idx in indices:

                scores = relative_matrix[source_idx]
                raw_scores = similarity_matrix[source_idx]

                # ------------------------------------------------
                # FIRST: THRESHOLD
                # ------------------------------------------------

                threshold_indices = np.where(
                    scores >= threshold
                )[0]

                # ------------------------------------------------
                # THEN: SORTING
                # ------------------------------------------------

                threshold_indices = threshold_indices[
                    np.argsort(
                        scores[threshold_indices]
                    )[::-1]
                ]

                # ------------------------------------------------
                # FINALLY: TOP-K
                # ------------------------------------------------

                selected = threshold_indices[:top_k]

                candidate_count = len(selected)

                candidate_counts.append(
                    candidate_count
                )

                if candidate_count > 0:
                    rules_with_candidates += 1
                else:
                    rules_without_candidates += 1

                # ------------------------------------------------
                # DISTINCT SRs
                # ------------------------------------------------

                parents = set()

                for iec_idx in selected:

                    req = iec_requirements[iec_idx]

                    parent = normalize_parent_sr(req)

                    # If the requirement itself is an SR,
                    # we use its own ID as the group.
                    if parent is None:
                        parent = req["id"]

                    parents.add(parent)

                    selected_relative_scores.append(
                        float(scores[iec_idx])
                    )

                    selected_raw_similarities.append(
                        float(raw_scores[iec_idx])
                    )

                parent_counts.append(
                    len(parents)
                )

            total_rules = len(indices)

            source_result = {
                "rules": total_rules,

                "rules_with_candidates": (
                    rules_with_candidates
                ),

                "rules_without_candidates": (
                    rules_without_candidates
                ),

                "coverage": (
                    rules_with_candidates / total_rules
                    if total_rules
                    else 0
                ),

                "candidate_count": descriptive_stats(
                    candidate_counts
                ),

                "distinct_parent_sr_count": descriptive_stats(
                    parent_counts
                ),

                "selected_relative_score": descriptive_stats(
                    selected_relative_scores
                ),

                "selected_raw_similarity": descriptive_stats(
                    selected_raw_similarities
                ),
            }

            result["sources"][source] = source_result

        all_results.append(result)


# ============================================================
# PRINTING
# ============================================================

print("\n")
print("=" * 70)
print("RESULTS")
print("=" * 70)


for source in ["hadolint", "shellcheck"]:

    print("\n" + "-" * 70)
    print(source.upper())
    print("-" * 70)

    print(
        f"{'Threshold':>10} "
        f"{'Top-K':>6} "
        f"{'Avg':>8} "
        f"{'Median':>8} "
        f"{'P90':>8} "
        f"{'SRs':>8} "
        f"{'Coverage':>10}"
    )

    for result in all_results:

        data = result["sources"][source]

        counts = data["candidate_count"]
        parents = data["distinct_parent_sr_count"]

        print(
            f"{result['threshold']:>10.2f} "
            f"{result['top_k']:>6} "
            f"{counts['mean']:>8.2f} "
            f"{counts['median']:>8.1f} "
            f"{counts['p90']:>8.1f} "
            f"{parents['mean']:>8.2f} "
            f"{data['coverage'] * 100:>9.2f}%"
        )


# ============================================================
# DIRECT COMPARISON WITH THE PAPER
# ============================================================

print("\n")
print("=" * 70)
print("PAPER CONFIGURATION")
print("=" * 70)

matching = next(
    r for r in all_results
    if r["threshold"] == 0.68
    and r["top_k"] == 10
)

for source in ["hadolint", "shellcheck"]:

    data = matching["sources"][source]

    print(f"\n{source.upper()}")

    print(
        f"  Average candidates : "
        f"{data['candidate_count']['mean']:.2f}"
    )

    print(
        f"  Mediana           : "
        f"{data['candidate_count']['median']:.1f}"
    )

    print(
        f"  P90               : "
        f"{data['candidate_count']['p90']:.1f}"
    )

    print(
        f"  SRs distintos     : "
        f"{data['distinct_parent_sr_count']['mean']:.2f}"
    )

    print(
        f"  Cobertura         : "
        f"{data['coverage'] * 100:.2f}%"
    )

    print(
        f"  No candidates     : "
        f"{data['rules_without_candidates']}"
    )


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

output = {
    "metadata": {
        "power": POWER,
        "thresholds": THRESHOLDS,
        "top_k_values": TOP_K_VALUES,
        "source_rule_count": len(source_rules),
        "iec_requirement_count": len(iec_requirements),
        "method": (
            "cosine similarity -> clamp negative -> "
            "power transform -> L-infinity normalization -> "
            "threshold -> top-K"
        ),
    },
    "results": all_results,
}

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        output,
        f,
        indent=2,
        ensure_ascii=False
    )


print("\n")
print("=" * 70)
print("Result saved at:")
print(OUTPUT_FILE)
print("=" * 70)