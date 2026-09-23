import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path("data")

INPUT_FILE = (
    BASE_DIR
    / "output/mappings/iec/inspection/gold_standard/"
    / "iec_gold_standard_candidates.json"
)

OUTPUT_DIR = (
    BASE_DIR
    / "output/mappings/iec/inspection/gold_standard"
)

OUTPUT_JSON = OUTPUT_DIR / "iec_gold_standard_sample.json"
OUTPUT_CSV = OUTPUT_DIR / "iec_gold_standard_sample.csv"
OUTPUT_MD = OUTPUT_DIR / "iec_gold_standard_sample_report.md"


# ------------------------------------------------------------
# Sample size
# ------------------------------------------------------------

# Number of rules from each source to be sampled.
#
# The sampling is done by RULE, not by candidate.
# All candidates of the selected rule will be preserved.
#
# If None, use all the rules.
SAMPLE_RULES = {
    "hadolint": 25,
    "shellcheck": 50,
}


# ------------------------------------------------------------
# Sampling strategy
# ------------------------------------------------------------

RANDOM_SEED = 42


# ------------------------------------------------------------
# Confidence bands based on the Top1-Top2 gap
# ------------------------------------------------------------

GAP_BINS = [
    ("very_low_gap", 0.00, 0.05),
    ("low_gap", 0.05, 0.10),
    ("medium_gap", 0.10, 0.20),
    ("high_gap", 0.20, 1.01),
]


# ============================================================
# UTILITIES
# ============================================================

def load_json(path):
    print(f"Loading: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False,
        )


def gap_bin(gap):
    """
    Classifies a rule according to the gap between
    Top-1 and Top-2.

    The smaller the gap, the higher the ambiguity.
    """

    if gap is None:
        return "no_gap"

    for label, lower, upper in GAP_BINS:
        if lower <= gap < upper:
            return label

    return "unknown"


def normalize_source_name(source):
    """
    Normalizes the names of the sources.
    """

    source = source.lower().strip()

    aliases = {
        "dl": "hadolint",
        "hadolint": "hadolint",
        "sc": "shellcheck",
        "shellcheck": "shellcheck",
    }

    if source not in aliases:
        raise ValueError(
            f"Fonte desconhecida: {source}"
        )

    return aliases[source]


# ============================================================
# CONFIGURATION METADATA
# ============================================================

def extract_matching_metadata(data):
    """
    Extracts and normalizes the configuration metadata of the
    original matching.

    The source of truth is the metadata of
    iec_gold_standard_candidates.json.

    Compatibility:

    Direct format:
        metadata.threshold
        metadata.top_k
        metadata.power
        metadata.method

    Grouped format:
        metadata.matching_configuration.threshold
        metadata.matching_configuration.top_k
        metadata.matching_configuration.power
        metadata.matching_configuration.method

    It also accepts aliases used in previous versions.
    """

    if not isinstance(data, dict):
        raise ValueError(
            "The gold standard file needs to be "
            "a JSON object."
        )

    metadata = data.get("metadata", {})

    if not isinstance(metadata, dict):
        raise ValueError(
            "Campo 'metadata' do gold standard "
            "has an invalid format."
        )

    matching_configuration = metadata.get(
        "matching_configuration",
        {},
    )

    if not isinstance(matching_configuration, dict):
        matching_configuration = {}

    # --------------------------------------------------------
    # Standard
    # --------------------------------------------------------

    standard = metadata.get(
        "standard",
        matching_configuration.get(
            "standard",
            "IEC 62443-3-3",
        ),
    )

    # --------------------------------------------------------
    # Threshold
    # --------------------------------------------------------

    threshold = metadata.get(
        "threshold"
    )

    if threshold is None:
        threshold = matching_configuration.get(
            "threshold"
        )

    if threshold is None:
        threshold = metadata.get(
            "similarity_threshold"
        )

    # --------------------------------------------------------
    # Top-K
    # --------------------------------------------------------

    top_k = metadata.get(
        "top_k"
    )

    if top_k is None:
        top_k = matching_configuration.get(
            "top_k"
        )

    if top_k is None:
        top_k = metadata.get(
            "top_k_candidates"
        )

    # --------------------------------------------------------
    # Power
    # --------------------------------------------------------

    power = metadata.get(
        "power"
    )

    if power is None:
        power = matching_configuration.get(
            "power"
        )

    if power is None:
        power = metadata.get(
            "power_exponent"
        )

    # --------------------------------------------------------
    # Method
    # --------------------------------------------------------

    method = metadata.get(
        "method"
    )

    if method is None:
        method = matching_configuration.get(
            "method"
        )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    missing = []

    if threshold is None:
        missing.append("threshold")

    if top_k is None:
        missing.append("top_k")

    if power is None:
        missing.append("power")

    if method is None:
        missing.append("method")

    if missing:
        print(
            "\n⚠ Metadados de matching ausentes:"
        )

        for field in missing:
            print(
                f"  - {field}"
            )

        print(
"\nThe sample will still be built, "
"but these fields cannot be preserved."
        )

    return {
        "standard": standard,
        "threshold": threshold,
        "top_k": top_k,
        "power": power,
        "method": method,
    }


# ============================================================
# GOLD STANDARD EXTRACTION
# ============================================================

def extract_rules(data):
    """
    Extracts the rules from the structure:

        sources
          ├── hadolint
          │     ├── DL1001
          │     │     ├── source_rule
          │     │     ├── candidate_count
          │     │     └── matches
          │     └── ...
          └── shellcheck
                └── ...

    Retorna:

        {
            "hadolint": [...],
            "shellcheck": [...]
        }
    """

    if not isinstance(data, dict):
        raise ValueError(
            "The gold standard file needs to be a JSON object."
        )

    sources = data.get("sources")

    if not isinstance(sources, dict):
        raise ValueError(
            "Invalid structure: 'sources' field not found."
        )

    normalized = {
        "hadolint": [],
        "shellcheck": [],
    }

    for raw_source, rules in sources.items():

        source = normalize_source_name(raw_source)

        if not isinstance(rules, dict):
            raise ValueError(
                f"Source '{source}' has an invalid format."
            )

        for source_id, entry in rules.items():

            if not isinstance(entry, dict):
                raise ValueError(
                    f"Invalid entry for {source_id}."
                )

            source_rule = entry.get("source_rule")

            matches = entry.get("matches")

            if not isinstance(source_rule, dict):
                raise ValueError(
                    f"{source_id}: field 'source_rule' missing "
                    f"or invalid."
                )

            if not isinstance(matches, list):
                raise ValueError(
                    f"{source_id}: field 'matches' missing "
                    f"or invalid."
                )

            if source_rule.get("id") != source_id:
                raise ValueError(
                    f"Inconsistency in {source_id}: "
                    f"source_rule.id = "
                    f"{source_rule.get('id')}"
                )

            # ------------------------------------------------
            # Rule statistics
            # ------------------------------------------------

            candidate_count = len(matches)

            top1_score = None
            top2_score = None

            if matches:
                top1_score = matches[0].get(
                    "relative_score"
                )

            if len(matches) >= 2:
                top2_score = matches[1].get(
                    "relative_score"
                )

            gap = None

            if (
                top1_score is not None
                and top2_score is not None
            ):
                gap = top1_score - top2_score

            record = {
                "source_id": source_id,
                "source": source,
                "source_rule": source_rule,
                "candidate_count": candidate_count,
                "top1_relative_score": top1_score,
                "top2_relative_score": top2_score,
                "top1_top2_gap": gap,
                "gap_bin": gap_bin(gap),
                "matches": matches,
            }

            normalized[source].append(record)

    return normalized


# ============================================================
# VALIDATION
# ============================================================

def validate_rules(rules_by_source):

    for source, rules in rules_by_source.items():

        ids = [
            rule["source_id"]
            for rule in rules
        ]

        if len(ids) != len(set(ids)):
            raise ValueError(
                f"IDs duplicados em {source}."
            )

        for rule in rules:

            matches = rule["matches"]

            # ------------------------------------------------
            # The ranks must be sequential.
            # ------------------------------------------------

            ranks = [
                match.get("rank")
                for match in matches
            ]

            expected = list(
                range(1, len(ranks) + 1)
            )

            if ranks != expected:
                raise ValueError(
                    f"{source}/{rule['source_id']}: "
                    f"invalid ranks: {ranks}"
                )

            # ------------------------------------------------
            # Candidate count
            # ------------------------------------------------

            if rule["candidate_count"] != len(matches):
                raise ValueError(
                    f"{source}/{rule['source_id']}: "
                    f"candidate_count inconsistente."
                )


# ============================================================
# STRATIFIED SAMPLING
# ============================================================

def sample_rules(rules, sample_size, rng):
    """
    Stratified sampling by the Top1-Top2 gap.

    This is important because we want to evaluate not only
    easy cases, but also cases where the embedding has
    semantically close candidates.

    The sample is done per rule.
    All candidates of the selected rule remain.
    """

    if sample_size is None:
        return list(rules)

    if sample_size <= 0:
        return []

    if sample_size >= len(rules):
        return list(rules)

    strata = defaultdict(list)

    for rule in rules:
        strata[rule["gap_bin"]].append(rule)

    # Embaralha cada estrato
    for items in strata.values():
        rng.shuffle(items)

    # --------------------------------------------------------
    # Initial proportional distribution
    # --------------------------------------------------------

    total = len(rules)

    allocation = {}

    for label, items in strata.items():

        proportion = len(items) / total

        allocation[label] = int(
            round(sample_size * proportion)
        )

    # --------------------------------------------------------
    # Correct rounding
    # --------------------------------------------------------

    allocated = sum(allocation.values())

    while allocated < sample_size:

        candidates = [
            label
            for label in strata
            if allocation[label] < len(strata[label])
        ]

        if not candidates:
            break

        # Adds to the largest available stratum
        label = max(
            candidates,
            key=lambda x: len(strata[x]) - allocation[x]
        )

        allocation[label] += 1
        allocated += 1

    while allocated > sample_size:

        candidates = [
            label
            for label in strata
            if allocation[label] > 0
        ]

        if not candidates:
            break

        label = max(
            candidates,
            key=lambda x: allocation[x]
        )

        allocation[label] -= 1
        allocated -= 1

    # --------------------------------------------------------
    # Selection
    # --------------------------------------------------------

    selected = []

    for label, count in allocation.items():

        selected.extend(
            strata[label][:count]
        )

    rng.shuffle(selected)

    return selected


# ============================================================
# SAMPLE CONSTRUCTION
# ============================================================

def build_sample(rules_by_source):

    rng = random.Random(RANDOM_SEED)

    sampled = {
        "hadolint": [],
        "shellcheck": [],
    }

    for source in ["hadolint", "shellcheck"]:

        requested = SAMPLE_RULES.get(source)

        selected = sample_rules(
            rules_by_source[source],
            requested,
            rng,
        )

        sampled[source] = selected

    return sampled


# ============================================================
# CANDIDATE EXPANSION
# ============================================================

def build_candidate_records(sampled):

    records = []

    for source, rules in sampled.items():

        for rule in rules:

            for match in rule["matches"]:

                record = {
                    "source": source,
                    "source_id": rule["source_id"],
                    "source_title": (
                        rule["source_rule"].get("title")
                    ),
                    "candidate_count": (
                        rule["candidate_count"]
                    ),
                    "top1_relative_score": (
                        rule["top1_relative_score"]
                    ),
                    "top2_relative_score": (
                        rule["top2_relative_score"]
                    ),
                    "top1_top2_gap": (
                        rule["top1_top2_gap"]
                    ),
                    "gap_bin": rule["gap_bin"],

                    "rank": match.get("rank"),

                    "target_id": match.get(
                        "target_id"
                    ),

                    "target_type": match.get(
                        "target_type"
                    ),

                    "parent_sr": match.get(
                        "parent_sr"
                    ),

                    "foundational_requirement": (
                        match.get(
                            "foundational_requirement"
                        )
                    ),

                    "target_title": match.get(
                        "target_title"
                    ),

                    "target_text": match.get(
                        "target_text"
                    ),

                    "raw_cosine": match.get(
                        "raw_cosine"
                    ),

                    "relative_score": match.get(
                        "relative_score"
                    ),

                    # ------------------------------------------------
                    # Fields for human annotation
                    # ------------------------------------------------

                    "human_label": match.get(
                        "human_label"
                    ),

                    "human_confidence": match.get(
                        "human_confidence"
                    ),

                    "human_notes": match.get(
                        "human_notes"
                    ),
                }

                records.append(record)

    return records


# ============================================================
# CSV
# ============================================================

def save_csv(path, records):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "source",
        "source_id",
        "source_title",

        "candidate_count",
        "top1_relative_score",
        "top2_relative_score",
        "top1_top2_gap",
        "gap_bin",

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
    ]

    with open(
        path,
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for record in records:
            writer.writerow(record)


# ============================================================
# MARKDOWN
# ============================================================

def generate_markdown(
    sampled,
    records,
    matching_metadata,
):

    lines = []

    lines.append(
        "# IEC 62443-3-3 Gold Standard Sample"
    )

    lines.append("")

    lines.append(
"Dataset generated for human evaluation "
"of the semantic mapping candidates."
    )

    lines.append("")

    # ========================================================
    # MATCHING CONFIGURATION
    # ========================================================

    lines.append("## Matching configuration")

    lines.append("")

    lines.append(
        f"- Standard: "
        f"`{matching_metadata['standard']}`"
    )

    threshold = matching_metadata["threshold"]
    top_k = matching_metadata["top_k"]
    power = matching_metadata["power"]

    lines.append(
        f"- Threshold: "
        f"`{threshold}`"
    )

    lines.append(
        f"- Top-K: "
        f"`{top_k}`"
    )

    lines.append(
        f"- Power: "
        f"`{power}`"
    )

    lines.append("")

    # ========================================================
    # SAMPLING
    # ========================================================

    lines.append("## Sampling configuration")

    lines.append("")

    lines.append(
        f"- Random seed: `{RANDOM_SEED}`"
    )

    lines.append(
        f"- Hadolint rules: "
        f"`{len(sampled['hadolint'])}`"
    )

    lines.append(
        f"- ShellCheck rules: "
        f"`{len(sampled['shellcheck'])}`"
    )

    lines.append(
        f"- Candidate records: `{len(records)}`"
    )

    lines.append("")

    # ========================================================
    # Summary by Source
    # ========================================================

    lines.append("## Summary")

    lines.append("")

    lines.append(
        "| Source | Rules | Candidates | "
        "Avg candidates/rule |"
    )

    lines.append("|---|---:|---:|---:|")

    for source in ["hadolint", "shellcheck"]:

        rules = sampled[source]

        candidate_count = sum(
            r["candidate_count"]
            for r in rules
        )

        average = (
            candidate_count / len(rules)
            if rules
            else 0
        )

        lines.append(
            f"| {source} | "
            f"{len(rules)} | "
            f"{candidate_count} | "
            f"{average:.2f} |"
        )

    lines.append("")

    # ========================================================
    # STRATIFICATION
    # ========================================================

    lines.append(
        "## Gap stratification"
    )

    lines.append("")

    counter = Counter(
        record["gap_bin"]
        for record in records
        if record["rank"] == 1
    )

    lines.append(
        "| Gap bin | Rules |"
    )

    lines.append("|---|---:|")

    for label, _, _ in GAP_BINS:

        lines.append(
            f"| {label} | "
            f"{counter.get(label, 0)} |"
        )

    lines.append("")

    # ========================================================
    # TARGET TYPE DISTRIBUTION
    # ========================================================

    lines.append(
        "## Target type distribution"
    )

    lines.append("")

    target_types = Counter(
        record["target_type"]
        for record in records
    )

    lines.append(
        "| Target type | Candidates |"
    )

    lines.append("|---|---:|")

    for target_type in ["SR", "RE"]:

        lines.append(
            f"| {target_type} | "
            f"{target_types.get(target_type, 0)} |"
        )

    lines.append("")

    # ========================================================
    # SELECTED RULES
    # ========================================================

    lines.append(
        "## Sampled rules"
    )

    lines.append("")

    for source in ["hadolint", "shellcheck"]:

        lines.append(
            f"### {source.upper()}"
        )

        lines.append("")

        lines.append(
            "| Rule | Candidates | "
            "Top1 | Top1-Top2 gap | Gap bin |"
        )

        lines.append(
            "|---|---:|---:|---:|---|"
        )

        for rule in sorted(
            sampled[source],
            key=lambda x: x["source_id"]
        ):

            gap = rule["top1_top2_gap"]

            gap_text = (
                f"{gap:.4f}"
                if gap is not None
                else "N/A"
            )

            top1 = rule["top1_relative_score"]

            top1_text = (
                f"{top1:.4f}"
                if top1 is not None
                else "N/A"
            )

            lines.append(
                f"| {rule['source_id']} | "
                f"{rule['candidate_count']} | "
                f"{top1_text} | "
                f"{gap_text} | "
                f"{rule['gap_bin']} |"
            )

        lines.append("")

    # ========================================================
    # ANNOTATION INSTRUCTIONS
    # ========================================================

    lines.append(
        "## Human annotation"
    )

    lines.append("")

    lines.append(
        "Each candidate must receive one of the following "
        "classifications:"
    )

    lines.append("")

    lines.append(
"- `relevant` — direct and semantically "
"defensible relation."
    )

    lines.append(
"- `partially_relevant` — a plausible relation, "
"but incomplete, indirect or dependent on an "
"interpretation."
    )

    lines.append(
        "- `irrelevant` — absence of a relevant relation."
    )

    lines.append("")

    lines.append(
"The evaluation must consider the meaning of the "
"source rule and the IEC requirement, and not only "
        "a similaridade lexical."
    )

    lines.append("")

    lines.append(
        "Reproducible sampling via the "
        f"`RANDOM_SEED = {RANDOM_SEED}`."
    )

    lines.append("")

    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================

print("=" * 70)
print("IEC 62443 GOLD STANDARD SAMPLER")
print("=" * 70)

print("\nLoading candidates...")

data = load_json(INPUT_FILE)

# ============================================================
# MATCHING METADATA
# ============================================================

matching_metadata = extract_matching_metadata(data)

print("\nConfiguration of the original matching:")

print(
    f"  Standard  : "
    f"{matching_metadata['standard']}"
)

print(
    f"  Threshold : "
    f"{matching_metadata['threshold']}"
)

print(
    f"  Top-K     : "
    f"{matching_metadata['top_k']}"
)

print(
    f"  Power     : "
    f"{matching_metadata['power']}"
)

print(
    f"  Method    : "
    f"{matching_metadata['method']}"
)

print("\nNormalizing structure...")

rules_by_source = extract_rules(data)

validate_rules(rules_by_source)

print(
    f"  HADOLINT    : "
    f"{len(rules_by_source['hadolint'])} rules"
)

print(
    f"  SHELLCHECK  : "
    f"{len(rules_by_source['shellcheck'])} rules"
)

print("\nBuilding sample...")

sampled = build_sample(
    rules_by_source
)

for source in ["hadolint", "shellcheck"]:

    print(
        f"  {source.upper():12s}: "
        f"{len(sampled[source])} rules"
    )

print("\nExpanding candidates...")

records = build_candidate_records(
    sampled
)

print(
    f"  Candidate records: "
    f"{len(records)}"
)


# ============================================================
# STATISTICS
# ============================================================

print("\nComputing statistics...")

for source in ["hadolint", "shellcheck"]:

    source_records = [
        r
        for r in records
        if r["source"] == source
    ]

    print(
        f"\n{source.upper()}"
    )

    print(
        f"  Rules      : "
        f"{len(sampled[source])}"
    )

    print(
        f"  Candidates : "
        f"{len(source_records)}"
    )

    gap_counter = Counter(
        r["gap_bin"]
        for r in source_records
        if r["rank"] == 1
    )

    print("  Gap bins:")

    for label, _, _ in GAP_BINS:

        print(
            f"    {label:15s}: "
            f"{gap_counter.get(label, 0)}"
        )


# ============================================================
# SAVE
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

output = {
    "metadata": {
        "standard": matching_metadata["standard"],

        "purpose": (
            "Human evaluation sample of semantic "
            "mapping candidates."
        ),

        "input_file": str(
            INPUT_FILE
        ),

        # ----------------------------------------------------
        # Original matching configuration
        # ----------------------------------------------------

        "threshold": matching_metadata["threshold"],
        "top_k": matching_metadata["top_k"],
        "power": matching_metadata["power"],
        "method": matching_metadata["method"],

# We also keep the explicit grouping for
# documentation and future compatibility.
        "matching_configuration": {
            "threshold": matching_metadata["threshold"],
            "top_k": matching_metadata["top_k"],
            "power": matching_metadata["power"],
            "method": matching_metadata["method"],
        },

        # ----------------------------------------------------
        #  Sampling configuration
        # ----------------------------------------------------

        "random_seed": RANDOM_SEED,

        "sample_rules": SAMPLE_RULES,

        "gap_bins": [
            {
                "label": label,
                "lower": lower,
                "upper": upper,
            }
            for label, lower, upper
            in GAP_BINS
        ],

        "label_status": "unreviewed",

        "allowed_labels": [
            "relevant",
            "partially_relevant",
            "irrelevant",
        ],

        "rule_counts": {
            source: len(sampled[source])
            for source in sampled
        },

        "candidate_count": len(records),
    },

    "rules": {
        source: sampled[source]
        for source in ["hadolint", "shellcheck"]
    },

    "records": records,
}


save_json(
    OUTPUT_JSON,
    output,
)

save_csv(
    OUTPUT_CSV,
    records,
)

markdown = generate_markdown(
    sampled,
    records,
    matching_metadata,
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
    f"CSV  : {OUTPUT_CSV}"
)

print(
    f"MD   : {OUTPUT_MD}"
)

print("=" * 70)