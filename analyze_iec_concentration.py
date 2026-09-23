import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path("data")

MATCHES_FILE = (
    BASE_DIR
    / "output/mappings/iec/inspection/iec_matches_068_top10.json"
)

OUTPUT_DIR = (
    BASE_DIR
    / "output/mappings/iec/inspection/concentration"
)

OUTPUT_JSON = (
    OUTPUT_DIR
    / "iec_concentration_ranking_analysis.json"
)

OUTPUT_MD = (
    OUTPUT_DIR
    / "iec_concentration_ranking_report.md"
)

OUTPUT_CSV = (
    OUTPUT_DIR
    / "iec_target_ranking.csv"
)

OUTPUT_DL_JSON = (
    OUTPUT_DIR
    / "hadolint_iec_separated.json"
)

OUTPUT_SC_JSON = (
    OUTPUT_DIR
    / "shellcheck_iec_separated.json"
)


# Number of positions shown in the rankings
TOP_N = 20


# ============================================================
# UTILITIES
# ============================================================

def load_json(path):
    print(f"Loading: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False,
        )


def save_csv(rows, path, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)

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
        writer.writerows(rows)


def safe_percentage(value, total):
    if total == 0:
        return 0.0

    return 100.0 * value / total


def entropy(counter):
    """
    Shannon entropy in bits.

    Measures how distributed the matches are.

    Low entropy:
        strong concentration.

    High entropy:
        more uniform distribution.
    """

    total = sum(counter.values())

    if total == 0:
        return 0.0

    result = 0.0

    for count in counter.values():

        if count <= 0:
            continue

        p = count / total
        result -= p * math.log2(p)

    return result


def normalized_entropy(counter):
    """
    Normalized entropy between 0 and 1.

    0 = maximum concentration
    1 = perfectly uniform distribution
    """

    if len(counter) <= 1:
        return 0.0

    h = entropy(counter)
    max_h = math.log2(len(counter))

    if max_h == 0:
        return 0.0

    return h / max_h


def herfindahl(counter):
    """
    Herfindahl-Hirschman concentration index (HHI).

    HHI = sum(p_i²)

    The higher, the greater the concentration.
    """

    total = sum(counter.values())

    if total == 0:
        return 0.0

    return sum(
        (count / total) ** 2
        for count in counter.values()
    )


def top_share(counter, n):
    """
    Share of all matches covered
    by the N most frequent targets.
    """

    total = sum(counter.values())

    if total == 0:
        return 0.0

    top_values = sorted(
        counter.values(),
        reverse=True,
    )[:n]

    return 100.0 * sum(top_values) / total


def gini_from_counter(counter):
    """
    Gini coefficient of the frequency distribution.

    0 = perfectly uniform
    1 = maximum concentration.
    """

    values = sorted(counter.values())

    if not values:
        return 0.0

    n = len(values)
    total = sum(values)

    if total == 0:
        return 0.0

    weighted_sum = sum(
        (i + 1) * value
        for i, value in enumerate(values)
    )

    return (
        (2 * weighted_sum)
        / (n * total)
        - (n + 1) / n
    )


# ============================================================
# MATCHING NORMALIZATION
# ============================================================

def normalize_matching(data):
    """
    Normalizes the structure of the file:

        {
            "metadata": {...},
            "sources": {
                "hadolint": {
                    "DL1001": {
                        ...
                        "matches": [...]
                    }
                },
                "shellcheck": {
                    ...
                }
            }
        }

    Returns a list of records:

        {
            source_type,
            source_id,
            source_title,
            rank,
            target_id,
            target_type,
            parent_sr,
            foundational_requirement,
            raw_cosine,
            relative_score,
            target_title
        }
    """

    if not isinstance(data, dict):
        raise ValueError(
            "The matching file must be a JSON object."
        )

    sources = data.get("sources")

    if not isinstance(sources, dict):
        raise ValueError(
            "The matching file does not have a "
            "'sources' structure."
        )

    records = []

    for source_type, source_rules in sources.items():

        if source_type not in {
            "hadolint",
            "shellcheck",
        }:
            print(
                f"⚠️ Unexpected source ignored: "
                f"{source_type}"
            )
            continue

        if not isinstance(source_rules, dict):
            continue

        for source_id, rule_data in source_rules.items():

            if not isinstance(rule_data, dict):
                continue

            matches = rule_data.get("matches", [])

            if not isinstance(matches, list):
                continue

            source_rule = rule_data.get(
                "source_rule",
                {},
            )

            if not isinstance(source_rule, dict):
                source_rule = {}

            source_title = source_rule.get(
                "title",
                source_id,
            )

            for match in matches:

                if not isinstance(match, dict):
                    continue

                target_id = match.get("target_id")

                if not target_id:
                    continue

                records.append(
                    {
                        "source_type": source_type,
                        "source_id": source_id,
                        "source_title": source_title,

                        "rank": match.get(
                            "rank"
                        ),

                        "target_id": target_id,

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

                        "raw_cosine": match.get(
                            "raw_cosine"
                        ),

                        "relative_score": match.get(
                            "relative_score"
                        ),

                        "target_title": match.get(
                            "target_title"
                        ),
                    }
                )

    return records


# ============================================================
# SPLIT BY SOURCE
# ============================================================

def separate_by_source(records):

    separated = {
        "hadolint": defaultdict(list),
        "shellcheck": defaultdict(list),
    }

    for record in records:

        source = record["source_type"]
        source_id = record["source_id"]

        separated[source][source_id].append(
            record
        )

    return separated


# ============================================================
# CONTADORES
# ============================================================

def build_counters(records):

    target_counter = Counter()
    parent_counter = Counter()
    type_counter = Counter()
    foundational_counter = Counter()

    source_target_counter = Counter()
    source_parent_counter = Counter()

    for record in records:

        target_id = record["target_id"]
        parent_sr = record["parent_sr"]
        target_type = record["target_type"]
        foundational = record[
            "foundational_requirement"
        ]

        source = record["source_type"]

        target_counter[target_id] += 1

        # ----------------------------------------------------
        # SR pai
        #
        # If the target itself is an SR,
        # parent_sr is null. In that case we use the target_id.
        #
        # This prevents the loss of directly selected SRs..
        # ----------------------------------------------------

        effective_parent = (
            parent_sr
            if parent_sr is not None
            else target_id
        )

        parent_counter[effective_parent] += 1

        type_counter[target_type] += 1

        if foundational is not None:
            foundational_counter[
                foundational
            ] += 1

        source_target_counter[
            (source, target_id)
        ] += 1

        source_parent_counter[
            (source, effective_parent)
        ] += 1

    return {
        "target": target_counter,
        "parent_sr": parent_counter,
        "target_type": type_counter,
        "foundational_requirement": foundational_counter,
        "source_target": source_target_counter,
        "source_parent_sr": source_parent_counter,
    }


# ============================================================
# RANKING
# ============================================================

def ranking_from_counter(counter, top_n=None):

    items = []

    total = sum(counter.values())

    ordered = counter.most_common(top_n)

    for rank, (key, count) in enumerate(
        ordered,
        start=1,
    ):

        items.append(
            {
                "rank": rank,
                "id": key,
                "count": count,
                "percentage": (
                    safe_percentage(
                        count,
                        total,
                    )
                ),
            }
        )

    return items


def ranking_target_details(records, source=None):

    filtered = records

    if source is not None:
        filtered = [
            r
            for r in records
            if r["source_type"] == source
        ]

    groups = defaultdict(list)

    for record in filtered:
        groups[
            record["target_id"]
        ].append(record)

    rows = []

    total = len(filtered)

    ordered = sorted(
        groups.items(),
        key=lambda item: (
            -len(item[1]),
            item[0],
        ),
    )

    for rank, (target_id, matches) in enumerate(
        ordered[:TOP_N],
        start=1,
    ):

        first = matches[0]

        rows.append(
            {
                "rank": rank,
                "source": source or "ALL",
                "target_id": target_id,
                "target_type": first[
                    "target_type"
                ],
                "parent_sr": (
                    first["parent_sr"]
                    if first["parent_sr"] is not None
                    else target_id
                ),
                "target_title": first[
                    "target_title"
                ],
                "count": len(matches),
                "percentage": safe_percentage(
                    len(matches),
                    total,
                ),
                "mean_relative_score": (
                    sum(
                        r["relative_score"]
                        for r in matches
                        if r["relative_score"]
                        is not None
                    )
                    /
                    max(
                        1,
                        len(
                            [
                                r
                                for r in matches
                                if r[
                                    "relative_score"
                                ]
                                is not None
                            ]
                        ),
                    )
                ),
                "mean_raw_cosine": (
                    sum(
                        r["raw_cosine"]
                        for r in matches
                        if r["raw_cosine"] is not None
                    )
                    /
                    max(
                        1,
                        len(
                            [
                                r
                                for r in matches
                                if r[
                                    "raw_cosine"
                                ]
                                is not None
                            ]
                        ),
                    )
                ),
            }
        )

    return rows


# ============================================================
# CONCENTRATION
# ============================================================

def concentration_summary(records):

    total = len(records)

    target_counter = Counter(
        r["target_id"]
        for r in records
    )

    parent_counter = Counter(
        (
            r["parent_sr"]
            if r["parent_sr"] is not None
            else r["target_id"]
        )
        for r in records
    )

    return {
        "total_candidate_records": total,

        "distinct_target_ids": len(
            target_counter
        ),

        "distinct_parent_srs": len(
            parent_counter
        ),

        "target_id_concentration": {
            "hhi": herfindahl(
                target_counter
            ),

            "gini": gini_from_counter(
                target_counter
            ),

            "entropy_bits": entropy(
                target_counter
            ),

            "normalized_entropy": (
                normalized_entropy(
                    target_counter
                )
            ),

            "top_1_share_percent": top_share(
                target_counter,
                1,
            ),

            "top_5_share_percent": top_share(
                target_counter,
                5,
            ),

            "top_10_share_percent": top_share(
                target_counter,
                10,
            ),
        },

        "parent_sr_concentration": {
            "hhi": herfindahl(
                parent_counter
            ),

            "gini": gini_from_counter(
                parent_counter
            ),

            "entropy_bits": entropy(
                parent_counter
            ),

            "normalized_entropy": (
                normalized_entropy(
                    parent_counter
                )
            ),

            "top_1_share_percent": top_share(
                parent_counter,
                1,
            ),

            "top_5_share_percent": top_share(
                parent_counter,
                5,
            ),

            "top_10_share_percent": top_share(
                parent_counter,
                10,
            ),
        },
    }


# ============================================================
# CONCENTRATION BY SOURCE
# ============================================================

def analyze_sources(records):

    result = {}

    for source in [
        "hadolint",
        "shellcheck",
    ]:

        source_records = [
            r
            for r in records
            if r["source_type"] == source
        ]

        result[source] = {
            "rules": len(
                set(
                    r["source_id"]
                    for r in source_records
                )
            ),

            "candidate_records": len(
                source_records
            ),

            "concentration": (
                concentration_summary(
                    source_records
                )
            ),

            "target_ranking": (
                ranking_target_details(
                    source_records
                )
            ),

            "parent_sr_ranking": (
                ranking_parent_details(
                    source_records
                )
            ),

            "target_type_ranking": (
                ranking_from_counter(
                    Counter(
                        r["target_type"]
                        for r in source_records
                    )
                )
            ),

            "foundational_requirement_ranking": (
                ranking_from_counter(
                    Counter(
                        r[
                            "foundational_requirement"
                        ]
                        for r in source_records
                        if r[
                            "foundational_requirement"
                        ] is not None
                    )
                )
            ),
        }

    return result


def ranking_parent_details(records):

    groups = defaultdict(list)

    for record in records:

        parent = (
            record["parent_sr"]
            if record["parent_sr"] is not None
            else record["target_id"]
        )

        groups[parent].append(record)

    total = len(records)

    rows = []

    ordered = sorted(
        groups.items(),
        key=lambda item: (
            -len(item[1]),
            item[0],
        ),
    )

    for rank, (parent_sr, matches) in enumerate(
        ordered[:TOP_N],
        start=1,
    ):

        rows.append(
            {
                "rank": rank,
                "parent_sr": parent_sr,
                "count": len(matches),
                "percentage": safe_percentage(
                    len(matches),
                    total,
                ),
                "distinct_target_ids": len(
                    set(
                        r["target_id"]
                        for r in matches
                    )
                ),
                "mean_relative_score": (
                    sum(
                        r["relative_score"]
                        for r in matches
                        if r["relative_score"]
                        is not None
                    )
                    /
                    max(
                        1,
                        len(
                            [
                                r
                                for r in matches
                                if r[
                                    "relative_score"
                                ]
                                is not None
                            ]
                        ),
                    )
                ),
            }
        )

    return rows


# ============================================================
# MATRIZ SOURCE × TARGET
# ============================================================

def build_source_target_matrix(records):

    sources = [
        "hadolint",
        "shellcheck",
    ]

    target_ids = sorted(
        set(
            r["target_id"]
            for r in records
        )
    )

    matrix = {}

    for source in sources:

        source_records = [
            r
            for r in records
            if r["source_type"] == source
        ]

        counter = Counter(
            r["target_id"]
            for r in source_records
        )

        matrix[source] = {
            target_id: counter.get(
                target_id,
                0,
            )
            for target_id in target_ids
        }

    return {
        "target_ids": target_ids,
        "sources": matrix,
    }


# ============================================================
# JSON SEPARATION
# ============================================================

def build_separated_mapping(records):

    separated = {
        "hadolint": {},
        "shellcheck": {},
    }

    grouped = defaultdict(
        lambda: defaultdict(list)
    )

    for record in records:

        source = record["source_type"]
        source_id = record["source_id"]

        grouped[source][source_id].append(
            {
                "rank": record["rank"],
                "target_id": record["target_id"],
                "target_type": record["target_type"],
                "parent_sr": record["parent_sr"],
                "foundational_requirement": (
                    record[
                        "foundational_requirement"
                    ]
                ),
                "raw_cosine": record["raw_cosine"],
                "relative_score": (
                    record["relative_score"]
                ),
                "target_title": (
                    record["target_title"]
                ),
            }
        )

    for source in separated:

        for source_id in grouped[source]:

            separated[source][
                source_id
            ] = {
                "candidate_count": len(
                    grouped[source][source_id]
                ),
                "matches": grouped[source][
                    source_id
                ],
            }

    return separated


# ============================================================
# CSV
# ============================================================

def build_csv_rows(records):

    rows = []

    for record in records:

        effective_parent = (
            record["parent_sr"]
            if record["parent_sr"] is not None
            else record["target_id"]
        )

        rows.append(
            {
                "source_type": record[
                    "source_type"
                ],
                "source_id": record[
                    "source_id"
                ],
                "rank": record["rank"],
                "target_id": record[
                    "target_id"
                ],
                "target_type": record[
                    "target_type"
                ],
                "parent_sr": effective_parent,
                "foundational_requirement": (
                    record[
                        "foundational_requirement"
                    ]
                ),
                "raw_cosine": record[
                    "raw_cosine"
                ],
                "relative_score": record[
                    "relative_score"
                ],
                "target_title": record[
                    "target_title"
                ],
            }
        )

    return rows


# ============================================================
# MARKDOWN
# ============================================================

def generate_markdown(
    data,
    rankings,
):

    metadata = data["metadata"]

    lines = []

    lines.append(
        "# IEC 62443 Match Concentration, Ranking and Separation"
    )

    lines.append("")

    lines.append("## Configuration")

    lines.append("")

    lines.append(
        f"- Threshold: `{metadata['threshold']}`"
    )

    lines.append(
        f"- Top-K: `{metadata['top_k']}`"
    )

    lines.append(
        f"- Power: `{metadata['power']}`"
    )

    lines.append(
        f"- Candidate records: `{metadata['candidate_records']}`"
    )

    lines.append("")

    lines.append("## Global Summary")

    lines.append("")

    lines.append(
        "| Source | Rules | Candidates | Distinct targets | Distinct SRs |"
    )

    lines.append(
        "|---|---:|---:|---:|---:|"
    )

    for source in [
        "hadolint",
        "shellcheck",
    ]:

        item = data[
            "sources"
        ][source]

        concentration = item[
            "concentration"
        ]

        lines.append(
            "| "
            f"{source.upper()} | "
            f"{item['rules']} | "
            f"{item['candidate_records']} | "
            f"{concentration['distinct_target_ids']} | "
            f"{concentration['distinct_parent_srs']} |"
        )

    lines.append("")

    # --------------------------------------------------------
    # Rankings
    # --------------------------------------------------------

    for source in [
        "hadolint",
        "shellcheck",
    ]:

        item = data[
            "sources"
        ][source]

        lines.append(
            f"## {source.upper()} — Target Ranking"
        )

        lines.append("")

        lines.append(
            "| Rank | Target | Type | Parent SR | Count | % | Mean score |"
        )

        lines.append(
            "|---:|---|---|---|---:|---:|---:|"
        )

        for row in item[
            "target_ranking"
        ]:

            lines.append(
                "| "
                f"{row['rank']} | "
                f"{row['target_id']} | "
                f"{row['target_type']} | "
                f"{row['parent_sr']} | "
                f"{row['count']} | "
                f"{row['percentage']:.2f}% | "
                f"{row['mean_relative_score']:.4f} |"
            )

        lines.append("")

        # ----------------------------------------------------
        # Parent SR ranking
        # ----------------------------------------------------

        lines.append(
            f"## {source.upper()} — Parent SR Ranking"
        )

        lines.append("")

        lines.append(
            "| Rank | Parent SR | Matches | % | Distinct targets |"
        )

        lines.append(
            "|---:|---|---:|---:|---:|"
        )

        for row in item[
            "parent_sr_ranking"
        ]:

            lines.append(
                "| "
                f"{row['rank']} | "
                f"{row['parent_sr']} | "
                f"{row['count']} | "
                f"{row['percentage']:.2f}% | "
                f"{row['distinct_target_ids']} |"
            )

        lines.append("")

        # ----------------------------------------------------
        # Concentration
        # ----------------------------------------------------

        concentration = item[
            "concentration"
        ]

        lines.append(
            f"## {source.upper()} — Concentration"
        )

        lines.append("")

        for label, key in [
            (
                "Target ID",
                "target_id_concentration",
            ),
            (
                "Parent SR",
                "parent_sr_concentration",
            ),
        ]:

            c = concentration[key]

            lines.append(
                f"### {label}"
            )

            lines.append("")

            lines.append(
                f"- HHI: `{c['hhi']:.6f}`"
            )

            lines.append(
                f"- Gini: `{c['gini']:.6f}`"
            )

            lines.append(
                f"- Entropy: `{c['entropy_bits']:.4f}` bits"
            )

            lines.append(
                f"- Normalized entropy: `{c['normalized_entropy']:.4f}`"
            )

            lines.append(
                f"- Top-1 share: `{c['top_1_share_percent']:.2f}%`"
            )

            lines.append(
                f"- Top-5 share: `{c['top_5_share_percent']:.2f}%`"
            )

            lines.append(
                f"- Top-10 share: `{c['top_10_share_percent']:.2f}%`"
            )

            lines.append("")

    # --------------------------------------------------------
    # DL × SC comparison
    # --------------------------------------------------------

    lines.append(
        "## DL × SC Comparison"
    )

    lines.append("")

    lines.append(
        "| Metric | DL | SC |"
    )

    lines.append(
        "|---|---:|---:|"
    )

    for label, path in [
        (
            "Distinct target IDs",
            ("distinct_target_ids", None),
        ),
        (
            "Distinct parent SRs",
            ("distinct_parent_srs", None),
        ),
        (
            "Target Top-5 share",
            (
                "target_id_concentration",
                "top_5_share_percent",
            ),
        ),
        (
            "Target Top-10 share",
            (
                "target_id_concentration",
                "top_10_share_percent",
            ),
        ),
        (
            "Parent SR Top-5 share",
            (
                "parent_sr_concentration",
                "top_5_share_percent",
            ),
        ),
        (
            "Parent SR Top-10 share",
            (
                "parent_sr_concentration",
                "top_10_share_percent",
            ),
        ),
        (
            "Target HHI",
            (
                "target_id_concentration",
                "hhi",
            ),
        ),
        (
            "Parent SR HHI",
            (
                "parent_sr_concentration",
                "hhi",
            ),
        ),
    ]:

        direct_key, nested_key = path

        values = []

        for source in [
            "hadolint",
            "shellcheck",
        ]:

            concentration = data[
                "sources"
            ][source]["concentration"]

            if nested_key is None:
                value = concentration[
                    direct_key
                ]

            else:
                value = concentration[
                    direct_key
                ][nested_key]

            values.append(value)

        if isinstance(values[0], float):

            lines.append(
                f"| {label} | "
                f"{values[0]:.4f} | "
                f"{values[1]:.4f} |"
            )

        else:

            lines.append(
                f"| {label} | "
                f"{values[0]} | "
                f"{values[1]} |"
            )

    lines.append("")

    # --------------------------------------------------------
    # Methodological interpretation
    # --------------------------------------------------------

    lines.append(
        "## Interpretation Notes"
    )

    lines.append("")

    lines.append(
        "- `target_id` measures concentration at the individual IEC requirement level."
    )

    lines.append(
        "- `parent_sr` aggregates each RE under its parent SR, allowing concentration to be measured per security requirement."
    )

    lines.append(
        "- For a target that is already an SR, its own `target_id` is used as the effective `parent_sr`."
    )

    lines.append(
        "- Higher HHI and Gini indicate greater concentration."
    )

    lines.append(
        "- Higher normalized entropy indicates a more diversified distribution."
    )

    lines.append(
        "- Top-N share shows what fraction of all candidates is concentrated in the N most frequent targets."
    )

    lines.append("")

    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================

print("=" * 70)
print(
    "IEC MATCH CONCENTRATION × RANKING × SEPARATION"
)
print("=" * 70)

print("\nLoading matching...")

matches_data = load_json(
    MATCHES_FILE
)

metadata = matches_data.get(
    "metadata",
    {},
)

print(
    f"Threshold : "
    f"{metadata.get('threshold', 'unknown')}"
)

print(
    f"Top-K     : "
    f"{metadata.get('top_k', 'unknown')}"
)

print(
    f"Power     : "
    f"{metadata.get('power', 'unknown')}"
)


# ============================================================
# NORMALIZATION
# ============================================================

print("\nNormalizing records...")

records = normalize_matching(
    matches_data
)

print(
    f"Candidate records : {len(records)}"
)


if not records:
    raise RuntimeError(
        "No matching records were found."
    )


# ============================================================
# FONTE
# ============================================================

source_rule_counts = {}

for source in [
    "hadolint",
    "shellcheck",
]:

    source_records = [
        r
        for r in records
        if r["source_type"] == source
    ]

    source_rule_counts[source] = len(
        set(
            r["source_id"]
            for r in source_records
        )
    )

    print(
        f"  {source.upper():12s}: "
        f"{source_rule_counts[source]} rules / "
        f"{len(source_records)} candidates"
    )


# ============================================================
# ANALYSIS
# ============================================================

print(
    "\nComputing concentration and rankings..."
)

source_analysis = analyze_sources(
    records
)

global_concentration = concentration_summary(
    records
)

global_target_ranking = (
    ranking_target_details(
        records
    )
)

global_parent_ranking = (
    ranking_parent_details(
        records
    )
)

global_target_type_ranking = (
    ranking_from_counter(
        Counter(
            r["target_type"]
            for r in records
        )
    )
)

global_foundational_ranking = (
    ranking_from_counter(
        Counter(
            r[
                "foundational_requirement"
            ]
            for r in records
            if r[
                "foundational_requirement"
            ] is not None
        )
    )
)


# ============================================================
# SEPARATION
# ============================================================

print(
    "\nGenerating separated mappings..."
)

separated = build_separated_mapping(
    records
)

save_json(
    separated["hadolint"],
    OUTPUT_DL_JSON,
)

save_json(
    separated["shellcheck"],
    OUTPUT_SC_JSON,
)

print(
    f"  DL : {OUTPUT_DL_JSON}"
)

print(
    f"  SC : {OUTPUT_SC_JSON}"
)


# ============================================================
# CSV
# ============================================================

print("\nGenerating CSV...")

csv_rows = build_csv_rows(
    records
)

save_csv(
    csv_rows,
    OUTPUT_CSV,
    [
        "source_type",
        "source_id",
        "rank",
        "target_id",
        "target_type",
        "parent_sr",
        "foundational_requirement",
        "raw_cosine",
        "relative_score",
        "target_title",
    ],
)

print(
    f"  CSV : {OUTPUT_CSV}"
)


# ============================================================
# JSON PRINCIPAL
# ============================================================

output = {
    "metadata": {
        "matches_file": str(
            MATCHES_FILE
        ),
        "threshold": metadata.get(
            "threshold"
        ),
        "top_k": metadata.get(
            "top_k"
        ),
        "power": metadata.get(
            "power"
        ),
        "candidate_records": len(
            records
        ),
        "source_rule_counts": (
            source_rule_counts
        ),
        "method": (
            "Frequency ranking and concentration "
            "analysis over embedding-generated "
            "IEC candidates."
        ),
    },

    "global": {
        "concentration": (
            global_concentration
        ),

        "target_ranking": (
            global_target_ranking
        ),

        "parent_sr_ranking": (
            global_parent_ranking
        ),

        "target_type_ranking": (
            global_target_type_ranking
        ),

        "foundational_requirement_ranking": (
            global_foundational_ranking
        ),
    },

    "sources": source_analysis,

    "source_target_matrix": (
        build_source_target_matrix(
            records
        )
    ),
}


# ============================================================
# SALVAR JSON
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

save_json(
    output,
    OUTPUT_JSON,
)

print(
    f"\nJSON : {OUTPUT_JSON}"
)


# ============================================================
# MARKDOWN
# ============================================================

markdown = generate_markdown(
    {
        "metadata": {
            "threshold": metadata.get(
                "threshold"
            ),
            "top_k": metadata.get(
                "top_k"
            ),
            "power": metadata.get(
                "power"
            ),
            "candidate_records": len(
                records
            ),
        },
        "sources": source_analysis,
    },
    {
        "global_target_ranking": (
            global_target_ranking
        ),
    },
)

with open(
    OUTPUT_MD,
    "w",
    encoding="utf-8",
) as f:

    f.write(markdown)


print(
    f"MD   : {OUTPUT_MD}"
)


# ============================================================
# TERMINAL SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("SUMMARY")
print("=" * 70)

for source in [
    "hadolint",
    "shellcheck",
]:

    concentration = source_analysis[
        source
    ]["concentration"]

    target_c = concentration[
        "target_id_concentration"
    ]

    parent_c = concentration[
        "parent_sr_concentration"
    ]

    print(
        f"\n{source.upper()}"
    )

    print(
        f"  Rules              : "
        f"{source_analysis[source]['rules']}"
    )

    print(
        f"  Candidates         : "
        f"{source_analysis[source]['candidate_records']}"
    )

    print(
        f"  Distinct targets   : "
        f"{concentration['distinct_target_ids']}"
    )

    print(
        f"  Distinct parent SRs: "
        f"{concentration['distinct_parent_srs']}"
    )

    print(
        f"  Target Top-5       : "
        f"{target_c['top_5_share_percent']:.2f}%"
    )

    print(
        f"  Target Top-10      : "
        f"{target_c['top_10_share_percent']:.2f}%"
    )

    print(
        f"  Parent SR Top-5    : "
        f"{parent_c['top_5_share_percent']:.2f}%"
    )

    print(
        f"  Parent SR Top-10   : "
        f"{parent_c['top_10_share_percent']:.2f}%"
    )

    print(
        f"  Target HHI         : "
        f"{target_c['hhi']:.6f}"
    )

    print(
        f"  Parent SR HHI      : "
        f"{parent_c['hhi']:.6f}"
    )

    print(
        "\n  Top 5 targets:"
    )

    for row in source_analysis[
        source
    ]["target_ranking"][:5]:

        print(
            f"    {row['rank']:2d}. "
            f"{row['target_id']:14s} "
            f"{row['count']:4d} "
            f"({row['percentage']:.2f}%)"
        )


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

print(
    f"CSV  : {OUTPUT_CSV}"
)

print(
    f"DL   : {OUTPUT_DL_JSON}"
)

print(
    f"SC   : {OUTPUT_SC_JSON}"
)

print("=" * 70)