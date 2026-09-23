import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path("data")

SECURITY_AUDIT_PATH = (
    BASE_DIR
    / "output/mappings/iec/inspection/gold_standard/"
    / "gemini_audit/security_relevance/"
    / "security_relevance_gemini_audit.json"
)

GEMINI_AUDIT_PATH = (
    BASE_DIR
    / "output/mappings/iec/inspection/gold_standard/"
    / "gemini_audit/full/"
    / "iec_gold_standard_gemini_audit.json"
)

OUTPUT_DIR = (
    BASE_DIR
    / "output/mappings/iec/inspection/gold_standard/"
    / "gemini_audit/security_relevance/"
)

OUTPUT_JSON = (
    OUTPUT_DIR
    / "security_relevance_rule_level_analysis.json"
)

OUTPUT_CSV = (
    OUTPUT_DIR
    / "security_relevance_rule_level_analysis.csv"
)

OUTPUT_MD = (
    OUTPUT_DIR
    / "security_relevance_rule_level_analysis.md"
)


ALLOWED_SECURITY_CLASSES = {
    "security_related",
    "non_security",
    "uncertain",
}

ALLOWED_VERDICTS = {
    "YES",
    "MAYBE",
    "NO",
}


# ============================================================
# UTILITIES
# ============================================================

def load_json(path):
    print(f"Loading: {path}")

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def save_json(path, data):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


def save_csv(path, rows):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not rows:
        return

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0].keys()),
        )

        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# SECURITY AUDIT
# ============================================================

def load_security_classifications(data):

    if not isinstance(data, dict):
        raise ValueError(
            "The security relevance audit "
            "should be a JSON object."
        )

    results = data.get("results")

    if not isinstance(results, list):
        raise ValueError(
            "The security relevance audit "
            "does not have 'results' as a list."
        )

    classifications = {}

    for result in results:

        source_id = result.get("source_id")

        if not source_id:
            raise ValueError(
                "Result without source_id."
            )

        if source_id in classifications:
            raise ValueError(
                f"Duplicated security classification "
                f"for {source_id}."
            )

        security_relevance = result.get(
            "security_relevance"
        )

        if security_relevance not in (
            ALLOWED_SECURITY_CLASSES
        ):
            raise ValueError(
                f"Invalid security_relevance for "
                f"{source_id}: "
                f"{security_relevance!r}"
            )

        classifications[source_id] = {
            "source": result.get("source"),
            "source_id": source_id,
            "security_relevance": (
                security_relevance
            ),
            "security_category": (
                result.get(
                    "security_category"
                )
            ),
            "confidence": result.get(
                "confidence"
            ),
        }

    return classifications


# ============================================================
# GEMINI PAIR AUDIT
# ============================================================

def load_pair_audit(data):

    if not isinstance(data, dict):
        raise ValueError(
            "The Gemini audit should "
            "be a JSON object."
        )

    results = data.get("results")

    if not isinstance(results, list):
        raise ValueError(
            "The Gemini audit does not have "
            "'results' as a list."
        )

    return results


# ============================================================
# RULE-LEVEL ANALYSIS CONSTRUCTION
# ============================================================

def build_rule_analysis(
    classifications,
    pair_results,
):

    grouped = defaultdict(list)

    pair_ids = set()

    for result in pair_results:

        pair_id = result.get("pair_id")

        if not pair_id:
            raise ValueError(
                "Association without pair_id."
            )

        if pair_id in pair_ids:
            raise ValueError(
                f"Duplicated pair_id: {pair_id}"
            )

        pair_ids.add(pair_id)

        source_id = result.get(
            "source_id"
        )

        verdict = result.get(
            "llm_verdict"
        )

        if not source_id:
            raise ValueError(
                f"Pair {pair_id} without source_id."
            )

        if verdict not in ALLOWED_VERDICTS:
            raise ValueError(
                f"Invalid verdict for "
                f"{pair_id}: {verdict!r}"
            )

        grouped[source_id].append(
            result
        )

    # --------------------------------------------------------
    # Check that every rule has a classification
    # --------------------------------------------------------

    pair_rule_ids = set(grouped.keys())
    security_rule_ids = set(
        classifications.keys()
    )

    missing_security = (
        pair_rule_ids
        - security_rule_ids
    )

    if missing_security:

        raise ValueError(
"There are rules present in the "
                "pair audit without a "
                "security relevance classification: "
            f"{sorted(missing_security)}"
        )

    # --------------------------------------------------------
    # Build record by rule
    # --------------------------------------------------------

    rows = []

    for source_id in sorted(
        security_rule_ids
    ):

        classification = (
            classifications[source_id]
        )

        pairs = grouped.get(
            source_id,
            [],
        )

        counts = Counter(
            pair.get("llm_verdict")
            for pair in pairs
        )

        candidate_count = len(pairs)

        yes_count = counts.get(
            "YES",
            0,
        )

        maybe_count = counts.get(
            "MAYBE",
            0,
        )

        no_count = counts.get(
            "NO",
            0,
        )

        positive_count = (
            yes_count
            + maybe_count
        )

        positive_rate = (
            positive_count
            / candidate_count
            if candidate_count
            else 0.0
        )

        rows.append(
            {
                "source": (
                    classification["source"]
                ),
                "source_id": source_id,
                "security_relevance": (
                    classification[
                        "security_relevance"
                    ]
                ),
                "security_category": (
                    classification[
                        "security_category"
                    ]
                ),
                "security_confidence": (
                    classification[
                        "confidence"
                    ]
                ),
                "candidate_count": (
                    candidate_count
                ),
                "yes_count": yes_count,
                "maybe_count": maybe_count,
                "no_count": no_count,
                "positive_count": (
                    positive_count
                ),
                "has_positive": (
                    positive_count > 0
                ),
                "positive_rate": (
                    round(
                        positive_rate,
                        6,
                    )
                ),
            }
        )

    return rows


# ============================================================
# STATISTICS BY CLASSIFICATION
# ============================================================

def build_group_statistics(rows):

    grouped = defaultdict(list)

    for row in rows:

        grouped[
            row["security_relevance"]
        ].append(row)

    statistics_by_group = {}

    for security_class in (
        "security_related",
        "non_security",
        "uncertain",
    ):

        group = grouped.get(
            security_class,
            [],
        )

        rule_count = len(group)

        rules_with_positive = sum(
            row["has_positive"]
            for row in group
        )

        rules_without_positive = (
            rule_count
            - rules_with_positive
        )

        coverage_rate = (
            rules_with_positive
            / rule_count
            if rule_count
            else 0.0
        )

        positive_rates = [
            row["positive_rate"]
            for row in group
            if row["candidate_count"] > 0
        ]

        statistics_by_group[
            security_class
        ] = {
            "rule_count": rule_count,
            "rules_with_positive": (
                rules_with_positive
            ),
            "rules_without_positive": (
                rules_without_positive
            ),
            "rule_positive_coverage": round(
                coverage_rate,
                6,
            ),
            "mean_positive_rate": round(
                statistics.mean(
                    positive_rates
                )
                if positive_rates
                else 0.0,
                6,
            ),
            "median_positive_rate": round(
                statistics.median(
                    positive_rates
                )
                if positive_rates
                else 0.0,
                6,
            ),
            "total_candidates": sum(
                row["candidate_count"]
                for row in group
            ),
            "total_yes": sum(
                row["yes_count"]
                for row in group
            ),
            "total_maybe": sum(
                row["maybe_count"]
                for row in group
            ),
            "total_no": sum(
                row["no_count"]
                for row in group
            ),
            "total_positive": sum(
                row["positive_count"]
                for row in group
            ),
        }

    return statistics_by_group


# ============================================================
# COMPARISONS
# ============================================================

def build_comparisons(
    statistics_by_group
):

    security = statistics_by_group[
        "security_related"
    ]

    non_security = statistics_by_group[
        "non_security"
    ]

    comparisons = {}

    # --------------------------------------------------------
    # Coverage por regra
    # --------------------------------------------------------

    if (
        security["rule_positive_coverage"]
        and non_security[
            "rule_positive_coverage"
        ]
    ):

        comparisons[
            "coverage_rate_ratio"
        ] = round(
            security[
                "rule_positive_coverage"
            ]
            / non_security[
                "rule_positive_coverage"
            ],
            6,
        )

    else:

        comparisons[
            "coverage_rate_ratio"
        ] = None

    # --------------------------------------------------------
    # Mean positive rate
    # --------------------------------------------------------

    if (
        security["mean_positive_rate"]
        and non_security[
            "mean_positive_rate"
        ]
    ):

        comparisons[
            "mean_positive_rate_ratio"
        ] = round(
            security[
                "mean_positive_rate"
            ]
            / non_security[
                "mean_positive_rate"
            ],
            6,
        )

    else:

        comparisons[
            "mean_positive_rate_ratio"
        ] = None

    # --------------------------------------------------------
    # YES rate across associations
    # --------------------------------------------------------

    security_candidates = (
        security["total_candidates"]
    )

    non_security_candidates = (
        non_security["total_candidates"]
    )

    security_yes_rate = (
        security["total_yes"]
        / security_candidates
        if security_candidates
        else 0.0
    )

    non_security_yes_rate = (
        non_security["total_yes"]
        / non_security_candidates
        if non_security_candidates
        else 0.0
    )

    comparisons[
        "candidate_yes_rate_security"
    ] = round(
        security_yes_rate,
        6,
    )

    comparisons[
        "candidate_yes_rate_non_security"
    ] = round(
        non_security_yes_rate,
        6,
    )

    if non_security_yes_rate:

        comparisons[
            "candidate_yes_rate_ratio"
        ] = round(
            security_yes_rate
            / non_security_yes_rate,
            6,
        )

    else:

        comparisons[
            "candidate_yes_rate_ratio"
        ] = None

    return comparisons


# ============================================================
# MARKDOWN REPORT
# ============================================================

def write_markdown(
    rows,
    statistics_by_group,
    comparisons,
):

    lines = []

    lines.append(
        "# Security Relevance — Rule-Level Analysis"
    )

    lines.append("")

    lines.append(
        "This analysis aggregates Gemini candidate "
        "verdicts at the source-rule level."
    )

    lines.append("")

    lines.append(
        "A rule is considered to have positive "
        "candidate coverage when at least one "
        "of its IEC 62443 candidate associations "
        "was classified as YES or MAYBE by Gemini."
    )

    lines.append("")

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    lines.append("## Rule-level coverage")

    lines.append("")

    lines.append(
        "| Security classification | Rules | "
        "With YES/MAYBE | Without YES/MAYBE | "
        "Coverage |"
    )

    lines.append(
        "|---|---:|---:|---:|---:|"
    )

    for security_class in (
        "security_related",
        "non_security",
        "uncertain",
    ):

        stats = statistics_by_group[
            security_class
        ]

        lines.append(
            "| "
            f"{security_class} | "
            f"{stats['rule_count']} | "
            f"{stats['rules_with_positive']} | "
            f"{stats['rules_without_positive']} | "
            f"{stats['rule_positive_coverage']:.2%} |"
        )

    lines.append("")

    # --------------------------------------------------------
    # Rates
    # --------------------------------------------------------

    lines.append(
        "## Positive association rate per rule"
    )

    lines.append("")

    lines.append(
        "| Security classification | "
        "Mean positive rate | "
        "Median positive rate |"
    )

    lines.append(
        "|---|---:|---:|"
    )

    for security_class in (
        "security_related",
        "non_security",
        "uncertain",
    ):

        stats = statistics_by_group[
            security_class
        ]

        lines.append(
            "| "
            f"{security_class} | "
            f"{stats['mean_positive_rate']:.2%} | "
            f"{stats['median_positive_rate']:.2%} |"
        )

    lines.append("")

    # --------------------------------------------------------
    # Comparisons
    # --------------------------------------------------------

    lines.append(
        "## Security-related vs non-security"
    )

    lines.append("")

    lines.append(
        f"- Rule positive-coverage ratio: "
        f"`{comparisons['coverage_rate_ratio']}`"
    )

    lines.append(
        f"- Mean positive-rate ratio: "
        f"`{comparisons['mean_positive_rate_ratio']}`"
    )

    lines.append(
        f"- Candidate-level YES-rate ratio: "
        f"`{comparisons['candidate_yes_rate_ratio']}`"
    )

    lines.append("")

    lines.append(
        "These ratios are descriptive comparisons "
        "and are not statistical effect estimates."
    )

    lines.append("")

    # --------------------------------------------------------
    # Highest positive coverage
    # --------------------------------------------------------

    positive_rows = [
        row
        for row in rows
        if row["positive_count"] > 0
    ]

    positive_rows.sort(
        key=lambda row: (
            row["positive_count"],
            row["positive_rate"],
        ),
        reverse=True,
    )

    lines.append(
        "## Rules with the most positive associations"
    )

    lines.append("")

    lines.append(
        "| Rule | Classification | Candidates | "
        "YES | MAYBE | Positive | Positive rate |"
    )

    lines.append(
        "|---|---|---:|---:|---:|---:|---:|"
    )

    for row in positive_rows[:30]:

        lines.append(
            "| "
            f"{row['source_id']} | "
            f"{row['security_relevance']} | "
            f"{row['candidate_count']} | "
            f"{row['yes_count']} | "
            f"{row['maybe_count']} | "
            f"{row['positive_count']} | "
            f"{row['positive_rate']:.2%} |"
        )

    lines.append("")

    OUTPUT_MD.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "SECURITY RELEVANCE — RULE-LEVEL ANALYSIS"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Load classification
    # --------------------------------------------------------

    print("")
    print(
        "Loading security relevance audit..."
    )

    security_data = load_json(
        SECURITY_AUDIT_PATH
    )

    classifications = (
        load_security_classifications(
            security_data
        )
    )

    print(
        f"  Classified rules: "
        f"{len(classifications)}"
    )

    # --------------------------------------------------------
    # Load pair audit
    # --------------------------------------------------------

    print("")
    print(
        "Loading full Gemini pair audit..."
    )

    pair_data = load_json(
        GEMINI_AUDIT_PATH
    )

    pair_results = load_pair_audit(
        pair_data
    )

    print(
        f"  Pair associations: "
        f"{len(pair_results)}"
    )

    # --------------------------------------------------------
    # Build analysis
    # --------------------------------------------------------

    print("")
    print(
        "Building rule-level analysis..."
    )

    rows = build_rule_analysis(
        classifications,
        pair_results,
    )

    print(
        f"  Rules analyzed: "
        f"{len(rows)}"
    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    statistics_by_group = (
        build_group_statistics(rows)
    )

    comparisons = (
        build_comparisons(
            statistics_by_group
        )
    )

    # --------------------------------------------------------
    # Global validation
    # --------------------------------------------------------

    total_candidates = sum(
        row["candidate_count"]
        for row in rows
    )

    total_yes = sum(
        row["yes_count"]
        for row in rows
    )

    total_maybe = sum(
        row["maybe_count"]
        for row in rows
    )

    total_no = sum(
        row["no_count"]
        for row in rows
    )

    if total_candidates != len(
        pair_results
    ):
        raise ValueError(
            "Candidate count mismatch: "
            f"{total_candidates} != "
            f"{len(pair_results)}"
        )

    if (
        total_yes
        + total_maybe
        + total_no
        != total_candidates
    ):
        raise ValueError(
            "Verdict counts do not sum "
            "to total candidates."
        )

    # --------------------------------------------------------
    # Output JSON
    # --------------------------------------------------------

    output_data = {
        "metadata": {
            "purpose": (
                "Rule-level aggregation of the "
                "independent security relevance "
                "classification and the existing "
                "Gemini candidate audit."
            ),
            "security_audit_path": (
                str(
                    SECURITY_AUDIT_PATH
                )
            ),
            "gemini_audit_path": (
                str(
                    GEMINI_AUDIT_PATH
                )
            ),
            "rule_count": len(rows),
            "candidate_count": (
                total_candidates
            ),
            "yes_count": total_yes,
            "maybe_count": total_maybe,
            "no_count": total_no,
            "positive_definition": (
                "YES or MAYBE"
            ),
        },
        "statistics_by_security_class": (
            statistics_by_group
        ),
        "comparisons": comparisons,
        "rules": rows,
    }

    save_json(
        OUTPUT_JSON,
        output_data,
    )

    save_csv(
        OUTPUT_CSV,
        rows,
    )

    write_markdown(
        rows,
        statistics_by_group,
        comparisons,
    )

    # --------------------------------------------------------
    # Console summary
    # --------------------------------------------------------

    print("")
    print("=" * 70)
    print(
        "RULE-LEVEL SECURITY RELEVANCE SUMMARY"
    )
    print("=" * 70)

    for security_class in (
        "security_related",
        "non_security",
        "uncertain",
    ):

        stats = statistics_by_group[
            security_class
        ]

        print("")
        print(
            security_class
        )

        print(
            f"  Rules: "
            f"{stats['rule_count']}"
        )

        print(
            f"  With YES/MAYBE: "
            f"{stats['rules_with_positive']}"
        )

        print(
            f"  Without YES/MAYBE: "
            f"{stats['rules_without_positive']}"
        )

        print(
            f"  Rule coverage: "
            f"{stats['rule_positive_coverage']:.2%}"
        )

        print(
            f"  Mean positive rate: "
            f"{stats['mean_positive_rate']:.2%}"
        )

        print(
            f"  Median positive rate: "
            f"{stats['median_positive_rate']:.2%}"
        )

    print("")
    print(
        "Security-related / non-security "
        "coverage ratio: "
        f"{comparisons['coverage_rate_ratio']}"
    )

    print(
        "Security-related / non-security "
        "mean positive-rate ratio: "
        f"{comparisons['mean_positive_rate_ratio']}"
    )

    print("")
    print("Outputs:")
    print(f"  JSON: {OUTPUT_JSON}")
    print(f"  CSV:  {OUTPUT_CSV}")
    print(f"  MD:   {OUTPUT_MD}")
    print("")


if __name__ == "__main__":
    main()