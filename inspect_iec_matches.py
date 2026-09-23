import json
import pickle
from pathlib import Path

import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path("data")

HADOLINT_CACHE = (
    BASE_DIR / "output/embeddings/cache_hadolint_structured.pkl"
)

IEC_CACHE = (
    BASE_DIR / "output/embeddings/cache_iec_structured.pkl"
)

HADOLINT_DATASET = (
    BASE_DIR / "output/datasets/hadolint_rules_structured.json"
)

IEC_DATASET = (
    BASE_DIR / "output/datasets/iec62443_clean.json"
)

OUTPUT_DIR = (
    BASE_DIR / "output/mappings/iec/inspection"
)

OUTPUT_JSON = OUTPUT_DIR / "iec_matches_068_top10.json"
OUTPUT_CSV = OUTPUT_DIR / "iec_matches_068_top10.csv"


# Experimental configuration
THRESHOLD = 0.68
TOP_K = 10
POWER = 5.5


# ============================================================
# UTILITIES
# ============================================================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_pickle(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def get_requirements(dataset):
    """
    IEC can be stored as:

        {
            "metadata": {...},
            "requirements": [...]
        }

    or directly as a list.
    """

    if isinstance(dataset, dict):
        return dataset["requirements"]

    return dataset


def normalize_parent_sr(requirement):
    """
    For an SR:

        id = SR 1.1
        parent_sr = SR 1.1

    Therefore, we do not consider the SR itself as its own parent.

    For an RE:

        id = SR 1.1 RE 1
        parent_sr = SR 1.1
    """

    requirement_id = requirement["id"]
    parent_sr = requirement.get("parent_sr")

    if requirement_id == parent_sr:
        return None

    return parent_sr


def build_embedding_matrix(cache, ids):
    """
    Reconstructs the embedding matrix respecting the order
    of the IDs provided by the dataset.
    """

    embeddings = cache["embeddings"]

    if not isinstance(embeddings, dict):
        matrix = np.asarray(
            embeddings,
            dtype=np.float32
        )

        return matrix

    matrix = []

    for item_id in ids:

        if item_id not in embeddings:
            raise KeyError(
                f"Embedding not found for ID: {item_id}"
            )

        vector = embeddings[item_id]

        if isinstance(vector, dict):

            if "embedding" in vector:
                vector = vector["embedding"]

            elif "vector" in vector:
                vector = vector["vector"]

            else:
                raise ValueError(
                    f"Unknown embedding format "
                    f"for {item_id}: {vector.keys()}"
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
print("QUALITATIVE IEC MATCH INSPECTION")
print("=" * 70)

print("\nConfiguration")
print("-" * 70)
print(f"Threshold : {THRESHOLD}")
print(f"Top-K     : {TOP_K}")
print(f"Power     : {POWER}")


print("\nLoading datasets...")

hadolint_dataset = load_json(HADOLINT_DATASET)
iec_dataset = load_json(IEC_DATASET)

# Hadolint structured is a dictionary:
#
# {
#     "DL1001": {...},
#     "DL3000": {...},
#     ...
# }

if isinstance(hadolint_dataset, dict) and "rules" in hadolint_dataset:
    source_rules = hadolint_dataset["rules"]

elif isinstance(hadolint_dataset, dict):
    source_rules = list(hadolint_dataset.values())

else:
    source_rules = hadolint_dataset


iec_requirements = get_requirements(iec_dataset)


print(f"Source rules     : {len(source_rules)}")
print(f"IEC requirements : {len(iec_requirements)}")


# ============================================================
# DATASET INDICES
# ============================================================

source_by_id = {
    rule["id"]: rule
    for rule in source_rules
}

iec_by_id = {
    req["id"]: req
    for req in iec_requirements
}


source_ids = list(source_by_id.keys())
iec_ids = list(iec_by_id.keys())


# ============================================================
# EMBEDDING LOADING
# ============================================================

print("\nLoading embeddings...")

hadolint_cache = load_pickle(HADOLINT_CACHE)
iec_cache = load_pickle(IEC_CACHE)


hadolint_embeddings = build_embedding_matrix(
    hadolint_cache,
    source_ids
)

iec_embeddings = build_embedding_matrix(
    iec_cache,
    iec_ids
)


print(
    f"Hadolint embeddings : "
    f"{hadolint_embeddings.shape}"
)

print(
    f"IEC embeddings      : "
    f"{iec_embeddings.shape}"
)


# ============================================================
# VALIDATION
# ============================================================

if hadolint_embeddings.shape[0] != len(source_ids):
    raise ValueError(
        "Number of Hadolint embeddings "
        "does not match the dataset."
    )

if iec_embeddings.shape[0] != len(iec_ids):
    raise ValueError(
        "Number of IEC embeddings "
        "does not match the dataset."
    )


# ============================================================
# DL / SC SPLIT
# ============================================================

source_indices = {
    "hadolint": [],
    "shellcheck": [],
}

for index, rule_id in enumerate(source_ids):

    source = source_by_id[rule_id]["source"]

    if source not in source_indices:
        raise ValueError(
            f"Unknown source: {source}"
        )

    source_indices[source].append(index)


print("\nSource split")
print("-" * 70)

print(
    f"Hadolint (DL) : "
    f"{len(source_indices['hadolint'])}"
)

print(
    f"ShellCheck (SC): "
    f"{len(source_indices['shellcheck'])}"
)


# ============================================================
# SIMILARITY MATRIX
# ============================================================

print("\nCalculating similarity...")

# The embeddings are already normalized.
#
# Therefore:
#
# cosine(a,b) = a · b

similarity_matrix = (
    hadolint_embeddings
    @ iec_embeddings.T
)


# ============================================================
# SCORE TRANSFORMATION
# ============================================================

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

relative_matrix = np.divide(
    transformed,
    row_max,
    out=np.zeros_like(transformed),
    where=row_max > 0,
)


# ============================================================
# MATCH CONSTRUCTION
# ============================================================

def get_matches(source_index):

    relative_scores = relative_matrix[
        source_index
    ]

    raw_scores = similarity_matrix[
        source_index
    ]

    # --------------------------------------------------------
    # Threshold
    # --------------------------------------------------------

    candidates = np.where(
        relative_scores >= THRESHOLD
    )[0]

    # --------------------------------------------------------
    # Sort by score
    # --------------------------------------------------------

    candidates = candidates[
        np.argsort(
            relative_scores[candidates]
        )[::-1]
    ]

    # --------------------------------------------------------
    # Top-K
    # --------------------------------------------------------

    candidates = candidates[:TOP_K]

    matches = []

    for rank, iec_index in enumerate(
        candidates,
        start=1
    ):

        requirement = iec_requirements[
            iec_index
        ]

        requirement_id = requirement["id"]

        requirement_type = requirement.get(
            "type"
        )

        parent_sr = normalize_parent_sr(
            requirement
        )

        match = {
            "rank": rank,

            "target_id": requirement_id,

            "target_type": requirement_type,

            "parent_sr": parent_sr,

            "foundational_requirement":
                requirement.get(
                    "foundational_requirement"
                ),

            "raw_cosine":
                round(
                    float(
                        raw_scores[iec_index]
                    ),
                    6
                ),

            "relative_score":
                round(
                    float(
                        relative_scores[iec_index]
                    ),
                    6
                ),

            "target_title":
                requirement.get(
                    "title"
                ),

            "target_text":
                requirement.get(
                    "text"
                ),
        }

        matches.append(match)

    return matches


# ============================================================
# STRUCTURED RESULT
# ============================================================

results = {
    "metadata": {
        "threshold": THRESHOLD,
        "top_k": TOP_K,
        "power": POWER,
        "source_dataset":
            str(HADOLINT_DATASET),
        "target_dataset":
            str(IEC_DATASET),
        "method": (
            "cosine similarity -> "
            "clamp negative -> "
            "power transform -> "
            "L-infinity normalization -> "
            "threshold -> top-K"
        ),
    },

    "sources": {
        "hadolint": {},
        "shellcheck": {},
    }
}


# ============================================================
# GENERATION
# ============================================================

print("\n")
print("=" * 70)
print("GENERATING INSPECTION DATA")
print("=" * 70)


for source, indices in source_indices.items():

    print(
        f"\n{source.upper()}"
    )

    source_output = {}

    for source_index in indices:

        rule_id = source_ids[
            source_index
        ]

        rule = source_by_id[
            rule_id
        ]

        matches = get_matches(
            source_index
        )

        source_output[rule_id] = {
            "source": source,

            "source_rule": {
                "id": rule["id"],

                "title":
                    rule.get("title"),

                "problematic_code":
                    rule.get(
                        "problematic_code"
                    ),

                "correct_code":
                    rule.get(
                        "correct_code"
                    ),

                "rationale":
                    rule.get(
                        "rationale"
                    ),

                "exceptions":
                    rule.get(
                        "exceptions"
                    ),
            },

            "candidate_count":
                len(matches),

            "matches":
                matches,
        }

    results["sources"][source] = (
        source_output
    )

    print(
        f"Rules processed : "
        f"{len(indices)}"
    )


# ============================================================
# CSV
# ============================================================

import csv


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


with open(
    OUTPUT_CSV,
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
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
    )

    writer.writeheader()

    for source, rules in (
        results["sources"].items()
    ):

        for source_id, rule_data in (
            rules.items()
        ):

            source_title = rule_data[
                "source_rule"
            ]["title"]

            for match in rule_data[
                "matches"
            ]:

                writer.writerow({
                    "source":
                        source,

                    "source_id":
                        source_id,

                    "source_title":
                        source_title,

                    "rank":
                        match["rank"],

                    "target_id":
                        match["target_id"],

                    "target_type":
                        match["target_type"],

                    "parent_sr":
                        match["parent_sr"],

                    "foundational_requirement":
                        match[
                            "foundational_requirement"
                        ],

                    "raw_cosine":
                        match["raw_cosine"],

                    "relative_score":
                        match["relative_score"],

                    "target_title":
                        match["target_title"],

                    "target_text":
                        match["target_text"],
                })


# ============================================================
# JSON
# ============================================================

with open(
    OUTPUT_JSON,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("SUMMARY")
print("=" * 70)

for source in [
    "hadolint",
    "shellcheck"
]:

    rules = results[
        "sources"
    ][source]

    candidate_counts = [
        rule["candidate_count"]
        for rule in rules.values()
    ]

    with_candidates = sum(
        count > 0
        for count in candidate_counts
    )

    print(
        f"\n{source.upper()}"
    )

    print(
        f"Rules              : "
        f"{len(rules)}"
    )

    print(
        f"Rules with matches : "
        f"{with_candidates}"
    )

    print(
        f"Rules without      : "
        f"{len(rules) - with_candidates}"
    )

    print(
        f"Average candidates : "
        f"{np.mean(candidate_counts):.2f}"
    )

    print(
        f"Median candidates  : "
        f"{np.median(candidate_counts):.1f}"
    )


print("\n")
print("=" * 70)
print("FILES GENERATED")
print("=" * 70)

print(
    f"JSON : {OUTPUT_JSON}"
)

print(
    f"CSV  : {OUTPUT_CSV}"
)

print("=" * 70)