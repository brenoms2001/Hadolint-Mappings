import json
import statistics
from pathlib import Path

import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path("data")

MATCHES_FILE = (
    BASE_DIR
    / "output/mappings/iec/inspection/iec_matches_068_top10.json"
)

HADOLINT_DATASET = (
    BASE_DIR
    / "output/datasets/hadolint_rules_structured.json"
)

IEC_DATASET = (
    BASE_DIR
    / "output/datasets/iec62443_clean.json"
)

OUTPUT_DIR = (
    BASE_DIR
    / "output/mappings/iec/inspection/quality"
)

OUTPUT_JSON = OUTPUT_DIR / "iec_match_quality_analysis.json"
OUTPUT_MD = OUTPUT_DIR / "iec_match_quality_report.md"


# Methodological configuration
THRESHOLD = 0.68
TOP_K = 10
POWER = 5.5


# ============================================================
# UTILITIES
# ============================================================

def load_json(path):
    print(f"Loading: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_requirements(dataset):
    """
    IEC may be stored as:

        {
            "metadata": {...},
            "requirements": [...]
        }

    or directly as a list.
    """

    if isinstance(dataset, dict):
        requirements = dataset.get("requirements")

        if requirements is None:
            raise ValueError(
                "The IEC dataset does not have the 'requirements' key."
            )

        return requirements

    if isinstance(dataset, list):
        return dataset

    raise ValueError(
        "Unexpected format for IEC dataset."
    )


def get_source_rules(dataset):
    """
    Hadolint/ShellCheck structured dataset.

    The dataset holds the rules directly as keys:

        {
            "DL1001": {...},
            "DL3000": {...},
            ...
            "SC1000": {...}
        }

    It also accepts, for compatibility, the format:

        {
            "rules": [...]
        }
    """

    if isinstance(dataset, list):
        return dataset

    if not isinstance(dataset, dict):
        raise ValueError(
            "Unexpected format for Hadolint dataset."
        )

    if "rules" in dataset:
        rules = dataset["rules"]

        if not isinstance(rules, list):
            raise ValueError(
                "The 'rules' key must contain a list."
            )

        return rules

    rules = []

    for rule_id, rule in dataset.items():

        if rule_id == "metadata":
            continue

        if not isinstance(rule, dict):
            continue

        if "id" not in rule:
            continue

        rules.append(rule)

    return rules


# ============================================================
# MATCHING
# ============================================================

def normalize_matches_structure(matches):
    """
    Normalizes the actual structure of the IEC inspection file.

    Expected structure:

        {
            "metadata": {...},
            "sources": {
                "hadolint": {
                    "DL1001": {
                        "source": "hadolint",
                        "source_rule": "DL1001",
                        "candidate_count": 7,
                        "matches": [
                            {
                                "target_id": "SR 1.1",
                                "relative_score": 0.91,
                                "raw_cosine": 0.57,
                                ...
                            }
                        ]
                    },
                    ...
                },
                "shellcheck": {
                    "SC....": {
                        ...
                    }
                }
            }
        }

    Returns:

        {
            "DL1001": [candidate, ...],
            "SC....": [candidate, ...]
        }

    The important point is that ``sources/<source>/<rule>`` is a
    rule metadata object, and the candidates are inside
    the ``matches`` key.
    """

    if not isinstance(matches, dict):
        raise ValueError(
            "The matching file must contain a JSON object."
        )

    # --------------------------------------------------------
    # Main structure: "sources" envelope
    # --------------------------------------------------------

    if "sources" in matches:
        sources = matches["sources"]

        if not isinstance(sources, dict):
            raise ValueError(
                "The 'sources' key must contain an object."
            )

        normalized = {}

        for source_name, source_matches in sources.items():

            if not isinstance(source_matches, dict):
                continue

            for source_id, rule_data in source_matches.items():

                # Nunca interpretar metadata como regra.
                if source_id in {
                    "metadata",
                    "config",
                    "configuration",
                    "summary",
                }:
                    continue

                if not isinstance(rule_data, dict):
                    continue

                candidates = rule_data.get("matches", [])

                if candidates is None:
                    candidates = []

                if not isinstance(candidates, list):
                    raise ValueError(
                        f"Invalid format for matches of rule "
                        f"{source_id}: expected list, got "
                        f"{type(candidates).__name__}."
                    )

                normalized[source_id] = candidates

        return normalized

    # --------------------------------------------------------
    # Flat alternative structure
    # --------------------------------------------------------

    normalized = {}

    for source_id, rule_data in matches.items():

        if source_id in {
            "metadata",
            "sources",
            "config",
            "configuration",
            "summary",
        }:
            continue

        # Formato de regra encapsulada:
        # {"matches": [...]}
        if isinstance(rule_data, dict):

            candidates = rule_data.get("matches")

            if candidates is not None:
                if not isinstance(candidates, list):
                    raise ValueError(
                        f"Invalid format for matches of rule "
                        f"{source_id}."
                    )

                normalized[source_id] = candidates
                continue

        # Formato legado:
        # {"DL1001": [...]}
        if isinstance(rule_data, list):
            normalized[source_id] = rule_data

    return normalized


# ============================================================
# STATISTICS
# ============================================================

def descriptive_stats(values):

    if not values:
        return {
            "count": 0,
            "min": 0.0,
            "mean": 0.0,
            "median": 0.0,
            "p90": 0.0,
            "p95": 0.0,
            "max": 0.0,
        }

    arr = np.asarray(values, dtype=float)

    return {
        "count": int(len(arr)),
        "min": float(np.min(arr)),
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "p90": float(np.percentile(arr, 90)),
        "p95": float(np.percentile(arr, 95)),
        "max": float(np.max(arr)),
    }


def safe_float(value):

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# ============================================================
# CANDIDATE EXTRACTION
# ============================================================

def extract_candidate_id(candidate):
    """
    Accepts different names used by the matching.
    """

    if not isinstance(candidate, dict):
        return None

    for key in (
        "target_id",
        "iec_id",
        "requirement_id",
        "id",
    ):
        if key in candidate:
            return candidate[key]

    return None


def extract_relative_score(candidate):
    """
    Extrai relative_score.
    """

    if not isinstance(candidate, dict):
        return None

    for key in (
        "relative_score",
        "score",
        "similarity",
    ):
        if key in candidate:

            value = safe_float(candidate[key])

            if value is not None:
                return value

    return None


def extract_raw_similarity(candidate):
    """
    Extracts the original similarity when available.
    """

    if not isinstance(candidate, dict):
        return None

    for key in (
        "raw_cosine",
        "raw_similarity",
        "cosine_similarity",
        "cosine",
        "raw_score",
    ):
        if key in candidate:

            value = safe_float(candidate[key])

            if value is not None:
                return value

    return None


# ============================================================
# IEC METADATA
# ============================================================

def build_iec_index(requirements):

    index = {}

    for requirement in requirements:

        requirement_id = requirement["id"]

        index[requirement_id] = requirement

    return index


def get_parent_sr(requirement):
    """
    For SR:

        id == parent_sr

    means the requirement is the SR itself.

    In that case we return None.

    For RE:

        parent_sr = parent SR
    """

    requirement_id = requirement.get("id")
    parent_sr = requirement.get("parent_sr")

    if requirement_id == parent_sr:
        return None

    return parent_sr


# ============================================================
# MATCH RECORD
# ============================================================

def extract_match_records(
    normalized_matches,
    source_rules,
    iec_index,
):
    """
    Converts the matching into individual records.

    Each record represents:

        source_rule -> IEC candidate
    """

    source_index = {
        rule["id"]: rule
        for rule in source_rules
    }

    records = []

    missing_sources = []

    for source_id, candidates in normalized_matches.items():

        # ----------------------------------------------------
        # Safety against structural keys
        # ----------------------------------------------------

        if source_id not in source_index:

            missing_sources.append(source_id)
            continue

        source_rule = source_index[source_id]

        if not isinstance(candidates, list):
            continue

        for rank, candidate in enumerate(candidates, start=1):

            target_id = extract_candidate_id(candidate)

            if target_id is None:
                continue

            if target_id not in iec_index:
                continue

            requirement = iec_index[target_id]

            relative_score = extract_relative_score(candidate)
            raw_similarity = extract_raw_similarity(candidate)

            parent_sr = get_parent_sr(requirement)

            records.append(
                {
                    "source_id": source_id,
                    "source": source_rule.get("source"),
                    "source_title": source_rule.get("title"),

                    "target_id": target_id,
                    "target_type": requirement.get("type"),
                    "target_title": requirement.get("title"),

                    "parent_sr": parent_sr,

                    "rank": rank,

                    "relative_score": relative_score,
                    "raw_similarity": raw_similarity,

                    "candidate": candidate,
                }
            )

    if missing_sources:

        raise KeyError(
            "The following source rules exist in the matching "
            "but not in the dataset: "
            f"{missing_sources[:20]}"
            + (
                f" ... ({len(missing_sources)} total)"
                if len(missing_sources) > 20
                else ""
            )
        )

    return records


# ============================================================
# Grouping
# ============================================================

def group_records_by_source(records):

    grouped = {}

    for record in records:

        source_id = record["source_id"]

        grouped.setdefault(
            source_id,
            []
        ).append(record)

    return grouped


# ============================================================
# Rule Quality
# ============================================================

def analyze_rule_quality(records):

    grouped = group_records_by_source(records)

    rule_results = []

    for source_id, matches in grouped.items():

        matches = sorted(
            matches,
            key=lambda x: x["rank"]
        )

        scores = [
            m["relative_score"]
            for m in matches
            if m["relative_score"] is not None
        ]

        raw_scores = [
            m["raw_similarity"]
            for m in matches
            if m["raw_similarity"] is not None
        ]

        # ----------------------------------------------------
        # Top-1 / Top-2
        # ----------------------------------------------------

        top1 = scores[0] if len(scores) >= 1 else None
        top2 = scores[1] if len(scores) >= 2 else None

        gap = (
            top1 - top2
            if top1 is not None and top2 is not None
            else None
        )

        # ----------------------------------------------------
        # IEC SRs distintos
        # ----------------------------------------------------

        distinct_srs = set()

        for match in matches:

            parent_sr = match["parent_sr"]

            if parent_sr is None:
                parent_sr = match["target_id"]

            distinct_srs.add(parent_sr)

        # ----------------------------------------------------
        # Top target
        # ----------------------------------------------------

        top_match = matches[0] if matches else None

        rule_result = {
            "source_id": source_id,

            "source": (
                matches[0]["source"]
                if matches
                else None
            ),

            "candidate_count": len(matches),

            "top1_relative_score": top1,

            "top2_relative_score": top2,

            "top1_top2_gap": gap,

            "top1_target_id": (
                top_match["target_id"]
                if top_match
                else None
            ),

            "top1_target_type": (
                top_match["target_type"]
                if top_match
                else None
            ),

            "distinct_parent_sr_count": len(
                distinct_srs
            ),

            "distinct_parent_srs": sorted(
                distinct_srs
            ),

            "relative_scores": scores,

            "raw_similarities": raw_scores,
        }

        rule_results.append(rule_result)

    return rule_results


# ============================================================
# ANALYSIS BY SOURCE
# ============================================================

def analyze_source(
    source,
    source_rules,
    normalized_matches,
    iec_index,
):

    source_ids = {
        rule["id"]
        for rule in source_rules
        if rule.get("source") == source
    }

    matched_ids = (
        source_ids
        & set(normalized_matches.keys())
    )

    records = [
        record
        for record in extract_match_records(
            normalized_matches,
            source_rules,
            iec_index,
        )
        if record["source"] == source
    ]

    rule_results = analyze_rule_quality(records)

    candidate_counts = [
        r["candidate_count"]
        for r in rule_results
    ]

    relative_scores = [
        r["top1_relative_score"]
        for r in rule_results
        if r["top1_relative_score"] is not None
    ]

    gaps = [
        r["top1_top2_gap"]
        for r in rule_results
        if r["top1_top2_gap"] is not None
    ]

    parent_counts = [
        r["distinct_parent_sr_count"]
        for r in rule_results
    ]

    return {
        "source": source,

        "rules": len(source_ids),

        "rules_with_matches": len(matched_ids),

        "rules_without_matches": (
            len(source_ids - matched_ids)
        ),

        "coverage": (
            len(matched_ids) / len(source_ids)
            if source_ids
            else 0.0
        ),

        "candidate_count": descriptive_stats(
            candidate_counts
        ),

        "top1_relative_score": descriptive_stats(
            relative_scores
        ),

        "top1_top2_gap": descriptive_stats(
            gaps
        ),

        "distinct_parent_sr_count": descriptive_stats(
            parent_counts
        ),

        "rule_results": rule_results,
    }


# ============================================================
# IEC TYPE DISTRIBUTION
# ============================================================

def analyze_target_types(records):

    counts = {}

    for record in records:

        target_type = record["target_type"]

        counts[target_type] = (
            counts.get(target_type, 0) + 1
        )

    return counts


# ============================================================
# TARGET DISTRIBUTION
# ============================================================

def analyze_target_distribution(records):

    counts = {}

    for record in records:

        target_id = record["target_id"]

        counts[target_id] = (
            counts.get(target_id, 0) + 1
        )

    return sorted(
        counts.items(),
        key=lambda x: x[1],
        reverse=True,
    )


# ============================================================
# GENERATION DO MARKDOWN
# ============================================================

def generate_markdown(
    results,
    source_results,
    target_type_distribution,
    target_distribution,
):

    lines = []

    lines.append(
        "# IEC 62443-3-3 Match Quality Analysis"
    )

    lines.append("")

    lines.append("## Configuration")
    lines.append("")

    lines.append(
        f"- Threshold: `{THRESHOLD}`"
    )
    lines.append(
        f"- Top-K: `{TOP_K}`"
    )
    lines.append(
        f"- Power: `{POWER}`"
    )

    lines.append("")

    lines.append("## Dataset")
    lines.append("")

    lines.append(
        f"- Source rules: `{results['metadata']['source_rule_count']}`"
    )

    lines.append(
        f"- IEC requirements: `{results['metadata']['iec_requirement_count']}`"
    )

    lines.append(
        f"- Candidate records: `{results['metadata']['candidate_records']}`"
    )

    lines.append("")

    # --------------------------------------------------------
    # Source
    # --------------------------------------------------------

    for source in ["hadolint", "shellcheck"]:

        data = source_results[source]

        lines.append(
            f"## {source.upper()}"
        )

        lines.append("")

        lines.append(
            f"- Rules: `{data['rules']}`"
        )

        lines.append(
            f"- Rules with matches: "
            f"`{data['rules_with_matches']}`"
        )

        lines.append(
            f"- Coverage: "
            f"`{data['coverage'] * 100:.2f}%`"
        )

        lines.append(
            f"- Average candidates: "
            f"`{data['candidate_count']['mean']:.2f}`"
        )

        lines.append(
            f"- Median candidates: "
            f"`{data['candidate_count']['median']:.2f}`"
        )

        lines.append(
            f"- Mean Top-1 relative score: "
            f"`{data['top1_relative_score']['mean']:.4f}`"
        )

        lines.append(
            f"- Median Top-1 relative score: "
            f"`{data['top1_relative_score']['median']:.4f}`"
        )

        lines.append(
            f"- Mean Top-1/Top-2 gap: "
            f"`{data['top1_top2_gap']['mean']:.4f}`"
        )

        lines.append(
            f"- Mean distinct SRs: "
            f"`{data['distinct_parent_sr_count']['mean']:.2f}`"
        )

        lines.append("")

    # --------------------------------------------------------
    # Target types
    # --------------------------------------------------------

    lines.append(
        "## IEC Target Type Distribution"
    )

    lines.append("")

    for target_type, count in sorted(
        target_type_distribution.items(),
        key=lambda x: x[1],
        reverse=True,
    ):

        lines.append(
            f"- `{target_type}`: `{count}`"
        )

    lines.append("")

    # --------------------------------------------------------
    # Most frequently selected targets
    # --------------------------------------------------------

    lines.append(
        "## Most Frequently Selected IEC Requirements"
    )

    lines.append("")

    for target_id, count in target_distribution[:20]:

        lines.append(
            f"- `{target_id}`: `{count}`"
        )

    lines.append("")

    # --------------------------------------------------------
    # Top-1 examples
    # --------------------------------------------------------

    lines.append(
        "## Top-1 Matches"
    )

    lines.append("")

    for source in ["hadolint", "shellcheck"]:

        lines.append(
            f"### {source.upper()}"
        )

        lines.append("")

        rules = source_results[source]["rule_results"]

        for rule in rules[:20]:

            lines.append(
                f"- `{rule['source_id']}` → "
                f"`{rule['top1_target_id']}` "
                f"({rule['top1_target_type']}) "
                f"score="
                f"`{rule['top1_relative_score']:.4f}`"
            )

        lines.append("")

    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================

print("=" * 70)
print("IEC MATCH QUALITY ANALYSIS")
print("=" * 70)


# ------------------------------------------------------------
# Loading
# ------------------------------------------------------------

print("\nLoading data...")

matches_raw = load_json(MATCHES_FILE)

hadolint_dataset = load_json(
    HADOLINT_DATASET
)

iec_dataset = load_json(
    IEC_DATASET
)


# ------------------------------------------------------------
# Normalization
# ------------------------------------------------------------

source_rules = get_source_rules(
    hadolint_dataset
)

iec_requirements = get_requirements(
    iec_dataset
)

normalized_matches = normalize_matches_structure(
    matches_raw
)

print(
    f"Source rules     : {len(source_rules)}"
)

print(
    f"IEC requirements : {len(iec_requirements)}"
)

print(
    f"Rules in matches : {len(normalized_matches)}"
)


# ------------------------------------------------------------
# Split
# ------------------------------------------------------------

hadolint_rules = [
    rule
    for rule in source_rules
    if rule.get("source") == "hadolint"
]

shellcheck_rules = [
    rule
    for rule in source_rules
    if rule.get("source") == "shellcheck"
]

matched_dl = (
    set(rule["id"] for rule in hadolint_rules)
    & set(normalized_matches.keys())
)

matched_sc = (
    set(rule["id"] for rule in shellcheck_rules)
    & set(normalized_matches.keys())
)

print(
    f"  Hadolint rules  : {len(hadolint_rules)}"
)

print(
    f"  ShellCheck rules: {len(shellcheck_rules)}"
)

print(
    f"  Matched DL      : {len(matched_dl)}"
)

print(
    f"  Matched SC      : {len(matched_sc)}"
)


# ------------------------------------------------------------
# IEC index
# ------------------------------------------------------------

iec_index = build_iec_index(
    iec_requirements
)


# ------------------------------------------------------------
# Registros
# ------------------------------------------------------------

records = extract_match_records(
    normalized_matches,
    source_rules,
    iec_index,
)

print(
    f"Candidate records : {len(records)}"
)


# ------------------------------------------------------------
# Analyses
# ------------------------------------------------------------

print("\nComputing analyses...")

dl_result = analyze_source(
    "hadolint",
    source_rules,
    normalized_matches,
    iec_index,
)

sc_result = analyze_source(
    "shellcheck",
    source_rules,
    normalized_matches,
    iec_index,
)

source_results = {
    "hadolint": dl_result,
    "shellcheck": sc_result,
}

target_type_distribution = (
    analyze_target_types(records)
)

target_distribution = (
    analyze_target_distribution(records)
)


# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("SUMMARY")
print("=" * 70)


for source in ["hadolint", "shellcheck"]:

    data = source_results[source]

    print(f"\n{source.upper()}")

    print(
        f"  Rules              : "
        f"{data['rules']}"
    )

    print(
        f"  Rules with matches : "
        f"{data['rules_with_matches']}"
    )

    print(
        f"  Coverage           : "
        f"{data['coverage'] * 100:.2f}%"
    )

    print(
        f"  Avg candidates     : "
        f"{data['candidate_count']['mean']:.2f}"
    )

    print(
        f"  Median candidates  : "
        f"{data['candidate_count']['median']:.1f}"
    )

    print(
        f"  Mean Top1 score    : "
        f"{data['top1_relative_score']['mean']:.4f}"
    )

    print(
        f"  Median Top1 score  : "
        f"{data['top1_relative_score']['median']:.4f}"
    )

    print(
        f"  Mean Top1-Top2 gap : "
        f"{data['top1_top2_gap']['mean']:.4f}"
    )

    print(
        f"  Mean distinct SRs  : "
        f"{data['distinct_parent_sr_count']['mean']:.2f}"
    )


# ============================================================
# TOP TARGETS
# ============================================================

print("\n")
print("=" * 70)
print("MOST FREQUENT IEC TARGETS")
print("=" * 70)

for target_id, count in target_distribution[:15]:

    print(
        f"  {target_id:15s} : {count}"
    )


# ============================================================
# TARGET TYPES
# ============================================================

print("\n")
print("=" * 70)
print("TARGET TYPE DISTRIBUTION")
print("=" * 70)

for target_type, count in sorted(
    target_type_distribution.items(),
    key=lambda x: x[1],
    reverse=True,
):

    print(
        f"  {target_type:15s} : {count}"
    )


# ============================================================
# Save
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


output = {
    "metadata": {
        "matches_file": str(MATCHES_FILE),
        "hadolint_dataset": str(HADOLINT_DATASET),
        "iec_dataset": str(IEC_DATASET),

        "threshold": THRESHOLD,
        "top_k": TOP_K,
        "power": POWER,

        "method": (
            "cosine similarity -> clamp negative -> "
            "power transform -> L-infinity normalization -> "
            "threshold -> top-K"
        ),

        "source_rule_count": len(source_rules),
        "iec_requirement_count": len(
            iec_requirements
        ),
        "candidate_records": len(records),
    },

    "summary": {
        "hadolint": {
            key: value
            for key, value in dl_result.items()
            if key != "rule_results"
        },

        "shellcheck": {
            key: value
            for key, value in sc_result.items()
            if key != "rule_results"
        },
    },

    "target_type_distribution":
        target_type_distribution,

    "target_distribution": [
        {
            "target_id": target_id,
            "count": count,
        }
        for target_id, count in target_distribution
    ],

    "rules": {
        "hadolint":
            dl_result["rule_results"],

        "shellcheck":
            sc_result["rule_results"],
    },
}


with open(
    OUTPUT_JSON,
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        output,
        f,
        indent=2,
        ensure_ascii=False,
    )


markdown = generate_markdown(
    output,
    source_results,
    target_type_distribution,
    target_distribution,
)


with open(
    OUTPUT_MD,
    "w",
    encoding="utf-8",
) as f:

    f.write(markdown)


# ============================================================
# FINAL
# ============================================================

print("\n")
print("=" * 70)
print("FILES GENERATED")
print("=" * 70)

print(
    f"JSON : {OUTPUT_JSON}"
)

print(
    f"MD   : {OUTPUT_MD}"
)

print("=" * 70)