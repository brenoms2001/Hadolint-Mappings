"""
Analyze Hadolint/ShellCheck -> IEC 62443-3-3 candidate mappings.

This script is diagnostic only. It does NOT modify the mappings.

Inputs:
    data/output/mappings/iec/hadolint_iec_candidates_60.json
    data/output/mappings/iec/shellcheck_iec_candidates_60.json

Outputs:
    Terminal summary
    data/output/mappings/iec/candidate_analysis_summary.json
"""

from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MAPPING_DIR = (
    BASE_DIR
    / "data"
    / "output"
    / "mappings"
    / "iec"
)

DL_FILE = (
    MAPPING_DIR
    / "hadolint_iec_candidates_60.json"
)

SC_FILE = (
    MAPPING_DIR
    / "shellcheck_iec_candidates_60.json"
)

OUTPUT_FILE = (
    MAPPING_DIR
    / "candidate_analysis_summary.json"
)


# ============================================================
# IO
# ============================================================

def load_mapping(path: Path) -> dict:
    """Load a mapping JSON."""

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# STATISTICS
# ============================================================

def descriptive_stats(values: list[float]) -> dict:
    """Return descriptive statistics for a numeric list."""

    if not values:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
            "stdev": None,
        }

    result = {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
    }

    if len(values) >= 2:
        result["stdev"] = statistics.stdev(values)
    else:
        result["stdev"] = 0.0

    return result


def percentile(values: list[float], p: float) -> float | None:
    """Calculate a percentile using linear interpolation."""

    if not values:
        return None

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    position = (len(ordered) - 1) * p
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)

    fraction = position - lower

    return (
        ordered[lower]
        + (ordered[upper] - ordered[lower]) * fraction
    )


# ============================================================
# CANDIDATE COUNT DISTRIBUTION
# ============================================================

def count_distribution(
    values: list[int],
) -> dict[str, int]:
    """
    Create useful bins for number of candidates per source rule.
    """

    bins = {
        "0": 0,
        "1-5": 0,
        "6-10": 0,
        "11-15": 0,
        "16-20": 0,
        "21-30": 0,
        "31-50": 0,
        ">50": 0,
    }

    for value in values:

        if value == 0:
            bins["0"] += 1

        elif value <= 5:
            bins["1-5"] += 1

        elif value <= 10:
            bins["6-10"] += 1

        elif value <= 15:
            bins["11-15"] += 1

        elif value <= 20:
            bins["16-20"] += 1

        elif value <= 30:
            bins["21-30"] += 1

        elif value <= 50:
            bins["31-50"] += 1

        else:
            bins[">50"] += 1

    return bins


# ============================================================
# ANALYSIS
# ============================================================

def analyze_mapping(
    mapping: dict,
    source_label: str,
) -> dict:

    rules = mapping.get("rules", {})

    if not isinstance(rules, dict):
        raise ValueError(
            f"{source_label}: invalid 'rules' structure."
        )

    # --------------------------------------------------------
    # Basic counters
    # --------------------------------------------------------

    rule_count = len(rules)

    candidate_counts = []

    all_candidates = []

    rules_without_candidates = []
    rules_with_candidates = []

    for source_id, rule_data in rules.items():

        candidates = rule_data.get(
            "candidates",
            [],
        )

        count = len(candidates)

        candidate_counts.append(count)

        all_candidates.extend(candidates)

        if count == 0:
            rules_without_candidates.append(source_id)
        else:
            rules_with_candidates.append(source_id)

    total_candidates = len(all_candidates)

    # --------------------------------------------------------
    # Candidate count statistics
    # --------------------------------------------------------

    candidate_count_stats = descriptive_stats(
        candidate_counts
    )

    candidate_count_percentiles = {
        "p25": percentile(candidate_counts, 0.25),
        "p50": percentile(candidate_counts, 0.50),
        "p75": percentile(candidate_counts, 0.75),
        "p90": percentile(candidate_counts, 0.90),
        "p95": percentile(candidate_counts, 0.95),
        "p99": percentile(candidate_counts, 0.99),
    }

    # --------------------------------------------------------
    # SR / RE distribution
    # --------------------------------------------------------

    target_type_counter = Counter(
        candidate.get("target_type")
        for candidate in all_candidates
    )

    # --------------------------------------------------------
    # Parent SR distribution
    # --------------------------------------------------------

    parent_sr_counter = Counter(
        candidate.get("parent_sr")
        for candidate in all_candidates
        if candidate.get("parent_sr") is not None
    )

    # --------------------------------------------------------
    # Distinct SRs per source rule
    #
    # An important diagnostic:
    #
    # DLxxxx
    #   SR 3.1
    #   SR 3.1 RE 1
    #   SR 3.1 RE 2
    #
    # represents 3 candidates but only ONE parent SR.
    # --------------------------------------------------------

    distinct_parent_sr_counts = []

    for source_id, rule_data in rules.items():

        candidates = rule_data.get(
            "candidates",
            [],
        )

        parent_srs = {
            candidate.get("parent_sr")
            for candidate in candidates
            if candidate.get("parent_sr") is not None
        }

        # Direct SR targets need to be counted too.
        #
        # For an SR target, parent_sr is intentionally null.
        # Therefore we use target_id itself as the SR identity.
        #
        # For an RE target, parent_sr identifies its parent SR.
        #

        sr_groups = set()

        for candidate in candidates:

            target_type = candidate.get(
                "target_type"
            )

            if target_type == "SR":
                sr_groups.add(
                    candidate.get("target_id")
                )

            elif target_type == "RE":
                parent_sr = candidate.get(
                    "parent_sr"
                )

                if parent_sr is not None:
                    sr_groups.add(parent_sr)

        distinct_parent_sr_counts.append(
            len(sr_groups)
        )

    distinct_sr_stats = descriptive_stats(
        distinct_parent_sr_counts
    )

    # --------------------------------------------------------
    # Relative score statistics
    # --------------------------------------------------------

    relative_scores = [
        candidate["relative_score"]
        for candidate in all_candidates
        if candidate.get("relative_score") is not None
    ]

    raw_similarities = [
        candidate["raw_similarity"]
        for candidate in all_candidates
        if candidate.get("raw_similarity") is not None
    ]

    relative_score_stats = descriptive_stats(
        relative_scores
    )

    relative_score_percentiles = {
        "p25": percentile(relative_scores, 0.25),
        "p50": percentile(relative_scores, 0.50),
        "p75": percentile(relative_scores, 0.75),
        "p90": percentile(relative_scores, 0.90),
        "p95": percentile(relative_scores, 0.95),
        "p99": percentile(relative_scores, 0.99),
    }

    raw_similarity_stats = descriptive_stats(
        raw_similarities
    )

    raw_similarity_percentiles = {
        "p25": percentile(raw_similarities, 0.25),
        "p50": percentile(raw_similarities, 0.50),
        "p75": percentile(raw_similarities, 0.75),
        "p90": percentile(raw_similarities, 0.90),
        "p95": percentile(raw_similarities, 0.95),
        "p99": percentile(raw_similarities, 0.99),
    }

    # --------------------------------------------------------
    # IEC requirement frequency
    # --------------------------------------------------------

    target_frequency = Counter(
        candidate.get("target_id")
        for candidate in all_candidates
    )

    # --------------------------------------------------------
    # Top IEC requirements
    # --------------------------------------------------------

    top_targets = [
        {
            "target_id": target_id,
            "count": count,
        }
        for target_id, count in target_frequency.most_common(20)
    ]

    # --------------------------------------------------------
    # Top rules by candidate count
    # --------------------------------------------------------

    rules_by_candidate_count = sorted(
        (
            {
                "source_id": source_id,
                "title": rule_data.get("title"),
                "candidate_count": len(
                    rule_data.get("candidates", [])
                ),
            }
            for source_id, rule_data in rules.items()
        ),
        key=lambda item: item["candidate_count"],
        reverse=True,
    )

    # --------------------------------------------------------
    # Top rules by distinct parent SR count
    # --------------------------------------------------------

    distinct_sr_by_rule = []

    for source_id, rule_data in rules.items():

        candidates = rule_data.get(
            "candidates",
            [],
        )

        sr_groups = set()

        for candidate in candidates:

            target_type = candidate.get(
                "target_type"
            )

            if target_type == "SR":
                sr_groups.add(
                    candidate.get("target_id")
                )

            elif target_type == "RE":
                parent_sr = candidate.get(
                    "parent_sr"
                )

                if parent_sr is not None:
                    sr_groups.add(parent_sr)

        distinct_sr_by_rule.append(
            {
                "source_id": source_id,
                "title": rule_data.get("title"),
                "candidate_count": len(candidates),
                "distinct_parent_sr_count": len(
                    sr_groups
                ),
            }
        )

    distinct_sr_by_rule.sort(
        key=lambda item: item[
            "distinct_parent_sr_count"
        ],
        reverse=True,
    )

    # --------------------------------------------------------
    # Candidates per parent SR
    # --------------------------------------------------------

    parent_sr_candidate_distribution = {
        parent_sr: count
        for parent_sr, count
        in parent_sr_counter.most_common()
    }

    # --------------------------------------------------------
    # Relative-score bins
    # --------------------------------------------------------

    score_bins = {
        "0.60-0.69": 0,
        "0.70-0.79": 0,
        "0.80-0.89": 0,
        "0.90-0.99": 0,
        "1.00": 0,
    }

    for score in relative_scores:

        if score >= 0.999999:
            score_bins["1.00"] += 1

        elif score >= 0.90:
            score_bins["0.90-0.99"] += 1

        elif score >= 0.80:
            score_bins["0.80-0.89"] += 1

        elif score >= 0.70:
            score_bins["0.70-0.79"] += 1

        else:
            score_bins["0.60-0.69"] += 1

    # --------------------------------------------------------
    # Raw cosine bins
    # --------------------------------------------------------

    raw_bins = {
        "<0.10": 0,
        "0.10-0.19": 0,
        "0.20-0.29": 0,
        "0.30-0.39": 0,
        "0.40-0.49": 0,
        "0.50-0.59": 0,
        "0.60-0.69": 0,
        "0.70-0.79": 0,
        "0.80-0.89": 0,
        "0.90-1.00": 0,
    }

    for score in raw_similarities:

        if score < 0.10:
            raw_bins["<0.10"] += 1

        elif score < 0.20:
            raw_bins["0.10-0.19"] += 1

        elif score < 0.30:
            raw_bins["0.20-0.29"] += 1

        elif score < 0.40:
            raw_bins["0.30-0.39"] += 1

        elif score < 0.50:
            raw_bins["0.40-0.49"] += 1

        elif score < 0.60:
            raw_bins["0.50-0.59"] += 1

        elif score < 0.70:
            raw_bins["0.60-0.69"] += 1

        elif score < 0.80:
            raw_bins["0.70-0.79"] += 1

        elif score < 0.90:
            raw_bins["0.80-0.89"] += 1

        else:
            raw_bins["0.90-1.00"] += 1

    # --------------------------------------------------------
    # Return analysis
    # --------------------------------------------------------

    return {
        "source": source_label,

        "rules": {
            "total": rule_count,
            "with_candidates": len(
                rules_with_candidates
            ),
            "without_candidates": len(
                rules_without_candidates
            ),
        },

        "candidates": {
            "total": total_candidates,

            "per_rule": candidate_count_stats,

            "per_rule_percentiles":
                candidate_count_percentiles,

            "per_rule_distribution":
                count_distribution(candidate_counts),
        },

        "target_type": {
            "SR": target_type_counter.get(
                "SR",
                0,
            ),
            "RE": target_type_counter.get(
                "RE",
                0,
            ),
            "unknown": target_type_counter.get(
                None,
                0,
            ),
        },

        "distinct_parent_sr_per_rule": {
            "statistics": distinct_sr_stats,

            "interpretation": (
                "For SR targets, target_id is used as "
                "the SR group because parent_sr is null. "
                "For RE targets, parent_sr is used."
            ),
        },

        "relative_score": {
            "statistics": relative_score_stats,
            "percentiles": relative_score_percentiles,
            "distribution": score_bins,
        },

        "raw_similarity": {
            "statistics": raw_similarity_stats,
            "percentiles": raw_similarity_percentiles,
            "distribution": raw_bins,
        },

        "most_frequent_iec_targets": top_targets,

        "most_candidates_per_rule":
            rules_by_candidate_count[:20],

        "most_distinct_parent_srs_per_rule":
            distinct_sr_by_rule[:20],

        "parent_sr_frequency":
            parent_sr_candidate_distribution,

        "rules_without_candidates":
            rules_without_candidates,
    }


# ============================================================
# TERMINAL REPORT
# ============================================================

def print_separator():
    print("-" * 70)


def print_stats(
    title: str,
    stats: dict,
):
    print(title)
    print_separator()

    print(f"Count   : {stats['count']}")

    if stats["count"] == 0:
        return

    print(f"Min     : {stats['min']:.4f}")
    print(f"Max     : {stats['max']:.4f}")
    print(f"Mean    : {stats['mean']:.4f}")
    print(f"Median  : {stats['median']:.4f}")
    print(f"Std dev : {stats['stdev']:.4f}")


def print_analysis(
    analysis: dict,
):
    source = analysis["source"]

    print()
    print("=" * 70)
    print(f"{source.upper()}")
    print("=" * 70)

    # --------------------------------------------------------
    # Basic
    # --------------------------------------------------------

    rules = analysis["rules"]
    candidates = analysis["candidates"]

    print()
    print("RULES")
    print_separator()

    print(
        f"Total               : {rules['total']}"
    )

    print(
        f"With candidates     : {rules['with_candidates']}"
    )

    print(
        f"Without candidates  : {rules['without_candidates']}"
    )

    print()
    print("CANDIDATES")
    print_separator()

    print(
        f"Total               : {candidates['total']}"
    )

    stats = candidates["per_rule"]

    print(
        f"Mean/rule           : {stats['mean']:.2f}"
    )

    print(
        f"Median/rule         : {stats['median']:.2f}"
    )

    print(
        f"Min/rule            : {stats['min']}"
    )

    print(
        f"Max/rule            : {stats['max']}"
    )

    print()
    print("Candidate count distribution:")
    for key, value in candidates[
        "per_rule_distribution"
    ].items():
        print(
            f"  {key:>7}: {value}"
        )

    # --------------------------------------------------------
    # SR / RE
    # --------------------------------------------------------

    print()
    print("TARGET TYPE")
    print_separator()

    target_type = analysis["target_type"]

    total = sum(
        target_type.values()
    )

    for key, value in target_type.items():

        if total:
            percentage = (
                value / total * 100
            )
        else:
            percentage = 0

        print(
            f"{key:>7}: "
            f"{value:>6} "
            f"({percentage:6.2f}%)"
        )

    # --------------------------------------------------------
    # Distinct SR
    # --------------------------------------------------------

    print()
    print(
        "DISTINCT PARENT SRs PER SOURCE RULE"
    )
    print_separator()

    sr_stats = analysis[
        "distinct_parent_sr_per_rule"
    ]["statistics"]

    print(
        f"Mean                : "
        f"{sr_stats['mean']:.2f}"
    )

    print(
        f"Median              : "
        f"{sr_stats['median']:.2f}"
    )

    print(
        f"Min                 : "
        f"{sr_stats['min']}"
    )

    print(
        f"Max                 : "
        f"{sr_stats['max']}"
    )

    print()

    # --------------------------------------------------------
    # Relative score
    # --------------------------------------------------------

    print("RELATIVE SCORE")
    print_separator()

    relative = analysis["relative_score"]

    stats = relative["statistics"]

    print(
        f"Mean                : "
        f"{stats['mean']:.4f}"
    )

    print(
        f"Median              : "
        f"{stats['median']:.4f}"
    )

    print(
        f"Min                 : "
        f"{stats['min']:.4f}"
    )

    print(
        f"Max                 : "
        f"{stats['max']:.4f}"
    )

    print()
    print("Distribution:")

    for key, value in relative[
        "distribution"
    ].items():
        print(
            f"  {key:>9}: {value}"
        )

    # --------------------------------------------------------
    # Raw cosine
    # --------------------------------------------------------

    print()
    print("RAW COSINE SIMILARITY")
    print_separator()

    raw = analysis["raw_similarity"]

    stats = raw["statistics"]

    print(
        f"Mean                : "
        f"{stats['mean']:.4f}"
    )

    print(
        f"Median              : "
        f"{stats['median']:.4f}"
    )

    print(
        f"Min                 : "
        f"{stats['min']:.4f}"
    )

    print(
        f"Max                 : "
        f"{stats['max']:.4f}"
    )

    print()
    print("Distribution:")

    for key, value in raw[
        "distribution"
    ].items():
        print(
            f"  {key:>9}: {value}"
        )

    # --------------------------------------------------------
    # Most frequent IEC targets
    # --------------------------------------------------------

    print()
    print("TOP 20 IEC TARGETS")
    print_separator()

    for item in analysis[
        "most_frequent_iec_targets"
    ]:

        print(
            f"{item['target_id']:15} "
            f"{item['count']:>5}"
        )

    # --------------------------------------------------------
    # Rules with most candidates
    # --------------------------------------------------------

    print()
    print("TOP 20 RULES BY CANDIDATE COUNT")
    print_separator()

    for item in analysis[
        "most_candidates_per_rule"
    ]:

        print(
            f"{item['source_id']:8} "
            f"{item['candidate_count']:>4} "
            f"{item['title']}"
        )

    # --------------------------------------------------------
    # Rules with most distinct parent SRs
    # --------------------------------------------------------

    print()
    print(
        "TOP 20 RULES BY DISTINCT PARENT SR COUNT"
    )
    print_separator()

    for item in analysis[
        "most_distinct_parent_srs_per_rule"
    ]:

        print(
            f"{item['source_id']:8} "
            f"SRs={item['distinct_parent_sr_count']:>3} "
            f"candidates={item['candidate_count']:>3} "
            f"{item['title']}"
        )


# ============================================================
# COMPARISON
# ============================================================

def build_comparison(
    dl: dict,
    sc: dict,
) -> dict:

    dl_candidates = dl["candidates"]
    sc_candidates = sc["candidates"]

    dl_rules = dl["rules"]
    sc_rules = sc["rules"]

    return {
        "rules": {
            "hadolint": dl_rules["total"],
            "shellcheck": sc_rules["total"],
        },

        "total_candidates": {
            "hadolint": dl_candidates["total"],
            "shellcheck": sc_candidates["total"],
            "combined": (
                dl_candidates["total"]
                + sc_candidates["total"]
            ),
        },

        "mean_candidates_per_rule": {
            "hadolint":
                dl_candidates["per_rule"]["mean"],
            "shellcheck":
                sc_candidates["per_rule"]["mean"],
        },

        "median_candidates_per_rule": {
            "hadolint":
                dl_candidates["per_rule"]["median"],
            "shellcheck":
                sc_candidates["per_rule"]["median"],
        },

        "distinct_parent_srs_mean": {
            "hadolint":
                dl[
                    "distinct_parent_sr_per_rule"
                ]["statistics"]["mean"],

            "shellcheck":
                sc[
                    "distinct_parent_sr_per_rule"
                ]["statistics"]["mean"],
        },

        "target_type": {
            "hadolint":
                dl["target_type"],

            "shellcheck":
                sc["target_type"],
        },
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("HADOLINT / SHELLCHECK → IEC 62443-3-3")
    print("Candidate Analysis")
    print("=" * 70)

    print()
    print(f"DL input: {DL_FILE}")
    print(f"SC input: {SC_FILE}")

    dl_mapping = load_mapping(
        DL_FILE
    )

    sc_mapping = load_mapping(
        SC_FILE
    )

    dl_analysis = analyze_mapping(
        dl_mapping,
        "Hadolint (DL)",
    )

    sc_analysis = analyze_mapping(
        sc_mapping,
        "ShellCheck (SC)",
    )

    # --------------------------------------------------------
    # Print detailed reports
    # --------------------------------------------------------

    print_analysis(
        dl_analysis
    )

    print_analysis(
        sc_analysis
    )

    # --------------------------------------------------------
    # Comparison
    # --------------------------------------------------------

    comparison = build_comparison(
        dl_analysis,
        sc_analysis,
    )

    print()
    print("=" * 70)
    print("DL vs SC COMPARISON")
    print("=" * 70)

    print()
    print(
        f"DL rules          : "
        f"{comparison['rules']['hadolint']}"
    )

    print(
        f"SC rules          : "
        f"{comparison['rules']['shellcheck']}"
    )

    print()

    print(
        f"DL candidates     : "
        f"{comparison['total_candidates']['hadolint']}"
    )

    print(
        f"SC candidates     : "
        f"{comparison['total_candidates']['shellcheck']}"
    )

    print(
        f"Combined          : "
        f"{comparison['total_candidates']['combined']}"
    )

    print()

    print(
        f"DL candidates/rule: "
        f"{comparison['mean_candidates_per_rule']['hadolint']:.2f}"
    )

    print(
        f"SC candidates/rule: "
        f"{comparison['mean_candidates_per_rule']['shellcheck']:.2f}"
    )

    print()

    print(
        f"DL median/rule    : "
        f"{comparison['median_candidates_per_rule']['hadolint']:.2f}"
    )

    print(
        f"SC median/rule    : "
        f"{comparison['median_candidates_per_rule']['shellcheck']:.2f}"
    )

    print()

    print(
        f"DL distinct SR/rule: "
        f"{comparison['distinct_parent_srs_mean']['hadolint']:.2f}"
    )

    print(
        f"SC distinct SR/rule: "
        f"{comparison['distinct_parent_srs_mean']['shellcheck']:.2f}"
    )

    # --------------------------------------------------------
    # Save JSON
    # --------------------------------------------------------

    summary = {
        "method": {
            "relative_threshold":
                dl_mapping.get(
                    "metadata",
                    {}
                ).get(
                    "relative_threshold"
                ),

            "power":
                dl_mapping.get(
                    "metadata",
                    {}
                ).get(
                    "power"
                ),

            "similarity":
                dl_mapping.get(
                    "metadata",
                    {}
                ).get(
                    "similarity"
                ),
        },

        "hadolint": dl_analysis,
        "shellcheck": sc_analysis,
        "comparison": comparison,
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            summary,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    print()
    print(
        f"Summary saved to:\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()