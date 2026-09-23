import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path("data")

MATCHING_FILE = (
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
    / "output/mappings/iec/inspection/gold_standard"
)

OUTPUT_JSON = OUTPUT_DIR / "iec_gold_standard_candidates.json"
OUTPUT_CSV = OUTPUT_DIR / "iec_gold_standard_candidates.csv"
OUTPUT_MD = OUTPUT_DIR / "iec_gold_standard_report.md"


# ============================================================
# UTILITIES
# ============================================================

def load_json(path):
    print(f"Loading: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False,
        )


# ============================================================
# MATCHING'S METADATA
# ============================================================

def extract_matching_metadata(matching):
    """
    Preserves the configuration/provenance of the original matching.

    The matching file is the source of truth for:

        threshold
        top_k
        power
        method
        source_dataset
        target_dataset

    We should not duplicate these values in this script.
    """

    if not isinstance(matching, dict):
        raise ValueError(
            "The matching should be a JSON object."
        )

    metadata = matching.get("metadata")

    if not isinstance(metadata, dict):
        raise ValueError(
            "The matching does not have a 'metadata' object."
        )

    return {
        "standard": "IEC 62443-3-3",

        "threshold": metadata.get(
            "threshold"
        ),

        "top_k": metadata.get(
            "top_k"
        ),

        "power": metadata.get(
            "power"
        ),

        "method": metadata.get(
            "method"
        ),

        "source_dataset": metadata.get(
            "source_dataset"
        ),

        "target_dataset": metadata.get(
            "target_dataset"
        ),
    }


# ============================================================
# IEC
# ============================================================

def normalize_parent_sr(requirement):
    """
    IEC:

        SR 1.1
            parent_sr = SR 1.1

        SR 1.1 RE 1
            parent_sr = SR 1.1

    For an SR, we do not want to consider the requirement itself
    as its parent_sr.

    Therefore:

        SR -> None
        RE -> parent SR
    """

    req_id = requirement.get("id")
    parent_sr = requirement.get("parent_sr")

    if req_id == parent_sr:
        return None

    return parent_sr


# ============================================================
# SOURCE DATASETS
# ============================================================

def normalize_source_dataset(dataset):
    """
    hadolint_rules_structured.json is directly indexed:

        {
            "DL1001": {...},
            "DL3000": {...},
            ...
            "SC3067": {...}
        }

    A "rules" key does not necessarily exist.

    The function also accepts, for compatibility, a structure:

        {
            "rules": [...]
        }
    """

    if not isinstance(dataset, dict):
        raise ValueError(
            "The source dataset should be a JSON object "
            "indexed by ID."
        )

    metadata_keys = {
        "metadata",
        "rules",
        "requirements",
    }

    # --------------------------------------------------------
    # Alternative structure:
    #
    # {
    #     "rules": [...]
    # }
    # --------------------------------------------------------

    if "rules" in dataset:

        rules = dataset["rules"]

        if not isinstance(rules, list):
            raise ValueError(
                "The 'rules' key exists but does not contain "
                "a list."
            )

        normalized = {}

        for rule in rules:

            if not isinstance(rule, dict):
                continue

            rule_id = rule.get("id")

            if not rule_id:
                continue

            normalized[rule_id] = rule

        return normalized

    # --------------------------------------------------------
    # Current structure:
    #
    # {
    #     "DL1001": {...},
    #     ...
    # }
    # --------------------------------------------------------

    rules = {}

    for rule_id, rule in dataset.items():

        if rule_id in metadata_keys:
            continue

        if not isinstance(rule, dict):
            continue

        rules[rule_id] = rule

    return rules


def normalize_iec_dataset(dataset):
    """
    IEC usa:

        {
            "metadata": {...},
            "requirements": [...]
        }
    """

    if not isinstance(dataset, dict):
        raise ValueError(
            "The IEC dataset should be a JSON object."
        )

    requirements = dataset.get("requirements")

    if not isinstance(requirements, list):
        raise ValueError(
            "The IEC dataset does not have a list named 'requirements'."
        )

    normalized = {}

    for requirement in requirements:

        if not isinstance(requirement, dict):
            continue

        req_id = requirement.get("id")

        if not req_id:
            continue

        normalized[req_id] = requirement

    return normalized


# ============================================================
# MATCHING NORMALIZATION
# ============================================================

def normalize_matching(matching):
    """
    Expected structure:

    {
        "metadata": {...},

        "sources": {

            "hadolint": {

                "DL1001": {

                    "source_rule": {...},

                    "candidate_count": 10,

                    "matches": [

                        {
                            "target_id": "...",
                            "target_type": "SR",
                            "parent_sr": null,
                            "foundational_requirement": 1,
                            "raw_cosine": 0.4,
                            "relative_score": 1.0,
                            "target_title": "...",
                            "target_text": "...",
                            "rank": 1
                        }

                    ]
                }

            },

            "shellcheck": {...}

        }
    }
    """

    if not isinstance(matching, dict):
        raise ValueError(
            "The matching should be a JSON object."
        )

    sources = matching.get("sources")

    if not isinstance(sources, dict):
        raise ValueError(
            "The matching does not have the expected structure "
            "'sources'."
        )

    records = []

    for source_name, source_rules in sources.items():

        if source_name not in {
            "hadolint",
            "shellcheck",
        }:
            print(
                f"  ⚠ Ignoring unknown source: "
                f"{source_name}"
            )
            continue

        if not isinstance(source_rules, dict):
            continue

        for source_id, rule_data in source_rules.items():

            if not isinstance(rule_data, dict):
                continue

            matches = rule_data.get(
                "matches",
                [],
            )

            if not isinstance(matches, list):
                continue

            for match in matches:

                if not isinstance(match, dict):
                    continue

                record = {
                    "source": source_name,

                    "source_id": source_id,

                    "candidate_count": rule_data.get(
                        "candidate_count",
                        len(matches),
                    ),

                    "target_id": match.get(
                        "target_id"
                    ),

                    "target_type": match.get(
                        "target_type"
                    ),

                    "parent_sr": match.get(
                        "parent_sr"
                    ),

                    "foundational_requirement":
                        match.get(
                            "foundational_requirement"
                        ),

                    "raw_cosine":
                        match.get(
                            "raw_cosine"
                        ),

                    "relative_score":
                        match.get(
                            "relative_score"
                        ),

                    "target_title":
                        match.get(
                            "target_title"
                        ),

                    "target_text":
                        match.get(
                            "target_text"
                        ),

                    "rank":
                        match.get(
                            "rank"
                        ),
                }

                records.append(record)

    return records


# ============================================================
# MATCH VALIDATION
# ============================================================

def validate_records(
    records,
    source_rules,
    iec_requirements,
):
    """
    Checks that the IDs present in the matching really exist
    in the datasets used as source.

    It also replaces the IEC metadata present in the matching
    with the canonical values of the IEC dataset.
    """

    valid_records = []

    invalid_source_ids = set()
    invalid_target_ids = set()

    for record in records:

        source_id = record["source_id"]
        target_id = record["target_id"]

        if source_id not in source_rules:

            invalid_source_ids.add(
                source_id
            )

            continue

        if target_id not in iec_requirements:

            invalid_target_ids.add(
                target_id
            )

            continue

        requirement = iec_requirements[target_id]

        # ----------------------------------------------------
        # Canonical data of the IEC dataset
        # ----------------------------------------------------

        record["target_type"] = (
            requirement.get("type")
        )

        record["target_title"] = (
            requirement.get("title")
        )

        record["target_text"] = (
            requirement.get("text")
        )

        record["foundational_requirement"] = (
            requirement.get(
                "foundational_requirement"
            )
        )

        record["parent_sr"] = (
            normalize_parent_sr(
                requirement
            )
        )

        # ----------------------------------------------------
        # Source metadata
        # ----------------------------------------------------

        source_rule = source_rules[
            source_id
        ]

        record["source_rule_title"] = (
            source_rule.get("title")
        )

        record["source_rule_text"] = (
            source_rule.get("text")
        )

        valid_records.append(record)

    if invalid_source_ids:

        print(
            "\n⚠ Invalid Source IDs:"
        )

        for item in sorted(
            invalid_source_ids
        ):
            print(
                f"  {item}"
            )

    if invalid_target_ids:

        print(
            "\n⚠ Invalid IEC Target IDs:"
        )

        for item in sorted(
            invalid_target_ids
        ):
            print(
                f"  {item}"
            )

    return valid_records


# ============================================================
# GROUPING
# ============================================================

def group_by_source(records):

    grouped = defaultdict(list)

    for record in records:

        grouped[
            record["source"]
        ].append(record)

    return grouped


def group_by_source_rule(records):

    grouped = defaultdict(list)

    for record in records:

        key = (
            record["source"],
            record["source_id"],
        )

        grouped[key].append(record)

    return grouped


# ============================================================
# STATISTICS
# ============================================================

def calculate_statistics(
    records,
    source_rules,
):
    grouped = group_by_source_rule(
        records
    )

    statistics = {}

    for source in [
        "hadolint",
        "shellcheck",
    ]:

        source_ids = [
            rule_id
            for rule_id, rule in source_rules.items()
            if rule.get("source") == source
        ]

        source_records = [
            r
            for r in records
            if r["source"] == source
        ]

        counts = []

        targets = Counter()

        parent_srs = Counter()

        for source_id in source_ids:

            candidates = grouped.get(
                (
                    source,
                    source_id,
                ),
                [],
            )

            counts.append(
                len(candidates)
            )

            for record in candidates:

                target_id = (
                    record["target_id"]
                )

                if target_id:
                    targets[
                        target_id
                    ] += 1

                parent_sr = (
                    record.get(
                        "parent_sr"
                    )
                )

                if parent_sr:

                    parent_srs[
                        parent_sr
                    ] += 1

                elif (
                    record.get(
                        "target_type"
                    ) == "SR"
                    and target_id
                ):

                    parent_srs[
                        target_id
                    ] += 1

        statistics[source] = {
            "rules": len(source_ids),

            "candidates": len(
                source_records
            ),

            "average_candidates": (
                sum(counts) / len(counts)
                if counts
                else 0
            ),

            "distinct_targets": len(
                targets
            ),

            "distinct_parent_srs": len(
                parent_srs
            ),

            "target_frequency": targets,

            "parent_sr_frequency": parent_srs,
        }

    return statistics


# ============================================================
# GOLD STANDARD
# ============================================================

def build_gold_standard(
    records,
    source_rules,
    iec_requirements,
    matching_metadata,
):
    """
    The gold standard does not invent new matches.

    It turns the automatic candidates into a structure
    suitable for human evaluation.

    The automatic results are preserved.

    Human fields are initially null.

    The method configuration is inherited directly from the
    original matching.
    """

    grouped = group_by_source_rule(
        records
    )

    output = {
        "metadata": {
            # ------------------------------------------------
            # Provenance
            # ------------------------------------------------

            "standard": matching_metadata.get(
                "standard"
            ),

            "threshold": matching_metadata.get(
                "threshold"
            ),

            "top_k": matching_metadata.get(
                "top_k"
            ),

            "power": matching_metadata.get(
                "power"
            ),

            "method": matching_metadata.get(
                "method"
            ),

            "source_dataset": matching_metadata.get(
                "source_dataset"
            ),

            "target_dataset": matching_metadata.get(
                "target_dataset"
            ),

            # ------------------------------------------------
            # Goal
            # ------------------------------------------------

            "purpose": (
                "Human evaluation dataset for "
                "semantic mapping candidates."
            ),

            "label_status": (
                "unreviewed"
            ),

            "labels": [
                "relevant",
                "partially_relevant",
                "irrelevant",
            ],
        },

        "sources": {},
    }

    for source in [
        "hadolint",
        "shellcheck",
    ]:

        source_output = {}

        source_ids = [
            rule_id
            for rule_id, rule in source_rules.items()
            if rule.get("source") == source
        ]

        # Stable sorting
        source_ids = sorted(
            source_ids
        )

        for source_id in source_ids:

            candidates = grouped.get(
                (
                    source,
                    source_id,
                ),
                [],
            )

            # Sorts by matching rank
            candidates = sorted(
                candidates,
                key=lambda x: (
                    x["rank"]
                    if x["rank"] is not None
                    else 999999
                ),
            )

            source_rule = source_rules[
                source_id
            ]

            candidate_output = []

            for record in candidates:

                target_id = (
                    record["target_id"]
                )

                requirement = (
                    iec_requirements[
                        target_id
                    ]
                )

                candidate_output.append(
                    {
                        "rank": record[
                            "rank"
                        ],

                        "target_id": target_id,

                        "target_type":
                            requirement.get(
                                "type"
                            ),

                        "parent_sr":
                            normalize_parent_sr(
                                requirement
                            ),

                        "foundational_requirement":
                            requirement.get(
                                "foundational_requirement"
                            ),

                        "target_title":
                            requirement.get(
                                "title"
                            ),

                        "target_text":
                            requirement.get(
                                "text"
                            ),

                        # ------------------------------------
                        # Automatic metrics
                        # ------------------------------------

                        "raw_cosine":
                            record[
                                "raw_cosine"
                            ],

                        "relative_score":
                            record[
                                "relative_score"
                            ],

                        # ------------------------------------
                        # HUMAN REVIEW
                        # ------------------------------------

                        "human_label":
                            None,

                        "human_confidence":
                            None,

                        "human_notes":
                            None,
                    }
                )

            source_output[
                source_id
            ] = {
                "source_rule": source_rule,

                "candidate_count":
                    len(candidate_output),

                "matches":
                    candidate_output,
            }

        output[
            "sources"
        ][source] = source_output

    return output


# ============================================================
# CSV
# ============================================================

def save_csv(
    records,
    path,
):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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

            row = {
                field: record.get(
                    field
                )
                for field in fieldnames
            }

            writer.writerow(row)


# ============================================================
# MARKDOWN
# ============================================================

def save_markdown(
    statistics,
    records,
    matching_metadata,
    path,
):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lines = []

    lines.append(
        "# IEC 62443 Gold Standard Dataset"
    )

    lines.append("")

    lines.append(
        "## Configuration"
    )

    lines.append("")

    lines.append(
        f"- Standard: "
        f"`{matching_metadata.get('standard')}`"
    )

    lines.append(
        f"- Threshold: "
        f"`{matching_metadata.get('threshold')}`"
    )

    lines.append(
        f"- Top-K: "
        f"`{matching_metadata.get('top_k')}`"
    )

    lines.append(
        f"- Power: "
        f"`{matching_metadata.get('power')}`"
    )

    lines.append(
        f"- Method: "
        f"`{matching_metadata.get('method')}`"
    )

    lines.append(
        f"- Source dataset: "
        f"`{matching_metadata.get('source_dataset')}`"
    )

    lines.append(
        f"- Target dataset: "
        f"`{matching_metadata.get('target_dataset')}`"
    )

    lines.append("")

    lines.append(
        "## Dataset summary"
    )

    lines.append("")

    lines.append(
        f"- Candidate records: "
        f"`{len(records)}`"
    )

    lines.append("")

    for source in [
        "hadolint",
        "shellcheck",
    ]:

        stats = statistics[source]

        label = (
            "Hadolint"
            if source == "hadolint"
            else "ShellCheck"
        )

        lines.append(
            f"### {label}"
        )

        lines.append("")

        lines.append(
            f"- Rules: "
            f"`{stats['rules']}`"
        )

        lines.append(
            f"- Candidates: "
            f"`{stats['candidates']}`"
        )

        lines.append(
            f"- Average candidates: "
            f"`{stats['average_candidates']:.2f}`"
        )

        lines.append(
            f"- Distinct targets: "
            f"`{stats['distinct_targets']}`"
        )

        lines.append(
            f"- Distinct parent SRs: "
            f"`{stats['distinct_parent_srs']}`"
        )

        lines.append("")

        lines.append(
            "#### Top 10 IEC targets"
        )

        lines.append("")

        for target, count in (
            stats[
                "target_frequency"
            ].most_common(10)
        ):

            lines.append(
                f"- `{target}` — {count}"
            )

        lines.append("")

    lines.append(
        "## Human-review schema"
    )

    lines.append("")

    lines.append(
        "Each candidate contains three empty "
        "fields for manual annotation:"
    )

    lines.append("")

    lines.append(
        "- `human_label`"
    )

    lines.append(
        "- `human_confidence`"
    )

    lines.append(
        "- `human_notes`"
    )

    lines.append("")

    lines.append(
        "The automatic similarity result and "
        "matching configuration are preserved "
        "unchanged."
    )

    lines.append("")

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:

        f.write(
            "\n".join(lines)
        )


# ============================================================
# MAIN
# ============================================================

print("=" * 70)
print(
    "IEC 62443 GOLD STANDARD DATASET BUILDER"
)
print("=" * 70)

print(
    "\nLoading files..."
)

matching = load_json(
    MATCHING_FILE
)

hadolint_dataset = load_json(
    HADOLINT_DATASET
)

iec_dataset = load_json(
    IEC_DATASET
)


# ============================================================
# MATCHING METADATA
# ============================================================

matching_metadata = (
    extract_matching_metadata(
        matching
    )
)

print(
    "\nConfiguration of the original matching:"
)

print(
    f"  Standard  : "
    f"{matching_metadata.get('standard')}"
)

print(
    f"  Threshold : "
    f"{matching_metadata.get('threshold')}"
)

print(
    f"  Top-K     : "
    f"{matching_metadata.get('top_k')}"
)

print(
    f"  Power     : "
    f"{matching_metadata.get('power')}"
)

print(
    f"  Method    : "
    f"{matching_metadata.get('method')}"
)


# ============================================================
# NORMALIZATION
# ============================================================

print(
    "\nNormalizing datasets..."
)

source_rules = (
    normalize_source_dataset(
        hadolint_dataset
    )
)

iec_requirements = (
    normalize_iec_dataset(
        iec_dataset
    )
)

print(
    f"Source rules     : "
    f"{len(source_rules)}"
)

print(
    f"IEC requirements : "
    f"{len(iec_requirements)}"
)


# ============================================================
# MATCHING
# ============================================================

print(
    "\nNormalizing matching..."
)

records = normalize_matching(
    matching
)

print(
    f"Candidate records : "
    f"{len(records)}"
)


# ============================================================
# VALIDATION
# ============================================================

print(
    "\nValidating candidates..."
)

valid_records = validate_records(
    records,
    source_rules,
    iec_requirements,
)

print(
    f"Valid candidate records : "
    f"{len(valid_records)}"
)


if not valid_records:

    raise RuntimeError(
"No valid candidate was found. "
        "The matching is probably not being "
        "interpreted correctly."
    )


# ============================================================
# STATISTICS
# ============================================================

print(
    "\nComputing statistics..."
)

statistics = calculate_statistics(
    valid_records,
    source_rules,
)


# ============================================================
# GOLD STANDARD
# ============================================================

print(
    "\nBuilding gold standard..."
)

gold_standard = build_gold_standard(
    valid_records,
    source_rules,
    iec_requirements,
    matching_metadata,
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ------------------------------------------------------------
# JSON
# ------------------------------------------------------------

save_json(
    OUTPUT_JSON,
    gold_standard,
)

print(
    f"JSON : {OUTPUT_JSON}"
)


# ------------------------------------------------------------
# CSV
# ------------------------------------------------------------

save_csv(
    valid_records,
    OUTPUT_CSV,
)

print(
    f"CSV  : {OUTPUT_CSV}"
)


# ------------------------------------------------------------
# MARKDOWN
# ------------------------------------------------------------

save_markdown(
    statistics,
    valid_records,
    matching_metadata,
    OUTPUT_MD,
)

print(
    f"MD   : {OUTPUT_MD}"
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
    "shellcheck",
]:

    stats = statistics[source]

    label = (
        "HADOLINT"
        if source == "hadolint"
        else "SHELLCHECK"
    )

    print(
        f"\n{label}"
    )

    print(
        f"  Rules              : "
        f"{stats['rules']}"
    )

    print(
        f"  Candidates         : "
        f"{stats['candidates']}"
    )

    print(
        f"  Average candidates : "
        f"{stats['average_candidates']:.2f}"
    )

    print(
        f"  Distinct targets   : "
        f"{stats['distinct_targets']}"
    )

    print(
        f"  Distinct parent SRs: "
        f"{stats['distinct_parent_srs']}"
    )

    print(
        "\n  Top 10 targets:"
    )

    for rank, (
        target,
        count,
    ) in enumerate(
        stats[
            "target_frequency"
        ].most_common(10),
        start=1,
    ):

        print(
            f"    {rank:2d}. "
            f"{target:15s} "
            f"{count}"
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

print(
    f"MD   : {OUTPUT_MD}"
)

print("=" * 70)