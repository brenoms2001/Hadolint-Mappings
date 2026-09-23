import csv
import json
from collections import Counter
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path("data")

# Current input: Gemini preliminary auditor result.
# To annotate the full sample again, change INPUT_FILE to
# iec_gold_standard_sample.json. The script supports both formats.
INPUT_FILE = (
    BASE_DIR
    / "output/mappings/iec/inspection/gold_standard/"
    / "gemini_audit/iec_gold_standard_gemini_audit.json"
)

OUTPUT_DIR = (
    BASE_DIR
    / "output/mappings/iec/inspection/gold_standard/"
    / "annotations"
)

OUTPUT_JSON = OUTPUT_DIR / "iec_gold_standard_annotated.json"
OUTPUT_CSV = OUTPUT_DIR / "iec_gold_standard_annotated.csv"
OUTPUT_XLSX = OUTPUT_DIR / "iec_gold_standard_annotated.xlsx"
OUTPUT_MD = OUTPUT_DIR / "iec_gold_standard_annotation_report.md"

ALLOWED_LABELS = [
    "relevant",
    "partially_relevant",
    "irrelevant",
]

ALLOWED_CONFIDENCE = [1, 2, 3, 4, 5]

# When the input is the Gemini audit, we want to review ONLY
# the pairs that were actually evaluated by Gemini.
# This avoids accidentally expanding the 10 test cases to the
# 531 candidates from the gold standard.
# REVIEW_SCOPE = "gemini_evaluated"

# The original no_match is a decision about the WHOLE rule and requires
# knowing all the relevant candidates of that rule. Therefore,
# it is NOT offered in Gemini-evaluated mode, which normally contains
# only a subset of the candidates.
ALLOW_RULE_NO_MATCH = False


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
        json.dump(data, f, indent=2, ensure_ascii=False)


def safe_text(value):
    """Converts any value into safe text for the terminal."""
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def export_cell_value(value):
    """
    Converts structured values to types accepted by Excel.

    openpyxl does not accept list/dict directly in a cell.
    We keep numbers and strings as they are and serialize compound
    structures in a readable way.

    Example:
        [32, 33] -> "32, 33"
        {"a": 1} -> '{"a": 1}'
    """
    if value is None:
        return None

    if isinstance(value, list):
        if not value:
            return ""

        # Simple page/number lists are more readable
        # as a comma-separated list.
        if all(not isinstance(item, (dict, list)) for item in value):
            return ", ".join(str(item) for item in value)

        return json.dumps(value, ensure_ascii=False)

    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)

    return value


def make_association_id(source, source_id, rank, target_id):
    return f"{source}:{source_id}:rank_{rank}:{target_id}"


def make_association_key(record):
    return (
        record.get("source"),
        record.get("source_id"),
        record.get("rank"),
        record.get("target_id"),
    )


def is_valid_human_label(value):
    return value in ALLOWED_LABELS


# ============================================================
# INPUT FORMAT DETECTION
# ============================================================

def detect_input_format(sample):
    if not isinstance(sample, dict):
        raise ValueError("The JSON file must contain an object at the root.")

    if isinstance(sample.get("results"), list):
        return "gemini_audit"

    if isinstance(sample.get("rules"), dict):
        return "gold_standard_sample"

    if isinstance(sample.get("records"), list):
        return "flat_records"

    raise ValueError(
        "Unrecognized input format. Expected a file with "
        "'results', 'rules' or 'records'."
    )


def validate_input(sample, input_format):
    if "metadata" not in sample:
        raise ValueError("The input does not have the 'metadata' key.")

    if input_format == "gemini_audit":
        if not sample["results"]:
            raise ValueError("The Gemini audit does not contain results.")
        return

    if input_format == "gold_standard_sample":
        rules = sample["rules"]
        for source in ("hadolint", "shellcheck"):
            if source not in rules:
                raise ValueError(f"The sample has no rules['{source}'].")
            if not isinstance(rules[source], list):
                raise ValueError(f"rules['{source}'] must be a list.")
        return

    if input_format == "flat_records":
        if not sample["records"]:
            raise ValueError("The records file does not contain records.")


# ============================================================
# METADATA
# ============================================================

def normalize_metadata(metadata, input_format):
    metadata = dict(metadata or {})

    # The Gemini audit uses sample_* for the matching configuration.
    if input_format == "gemini_audit":
        aliases = {
            "standard": "sample_standard",
            "threshold": "sample_threshold",
            "top_k": "sample_top_k",
            "power": "sample_power",
            "method": "sample_method",
        }
        for canonical, audit_key in aliases.items():
            if canonical not in metadata and audit_key in metadata:
                metadata[canonical] = metadata[audit_key]

        metadata["annotation_input_format"] = "gemini_audit"
        metadata["review_scope"] = REVIEW_SCOPE
        metadata["human_review_required"] = True
    else:
        metadata["annotation_input_format"] = input_format
        metadata.setdefault("review_scope", "all_candidates")

    metadata.setdefault("label_status", "unreviewed")
    return metadata


# ============================================================
# CONVERSION TO FLAT RECORDS
# ============================================================

def build_records_from_gemini_audit(sample):
    """
    Converts the auditor's results[] to the flat format used
    by the annotator.

    IMPORTANT: all contextual audit fields are preserved,
    including the rule rationale, the requirement rationale and the
    Gemini preliminary evaluation.
    """
    records = []

    for result in sample.get("results", []):
        if not isinstance(result, dict):
            continue

        source = result.get("source")
        source_id = result.get("source_id")
        rank = result.get("rank")
        target_id = result.get("target_id")

        if not source or not source_id or rank is None or not target_id:
            raise ValueError(
                "Gemini result without a complete identity: "
                f"{result!r}"
            )

        record = dict(result)
        record["association_id"] = result.get(
            "pair_id",
            make_association_id(source, source_id, rank, target_id),
        )

        # Explicit normalization of the human state.
        record["human_label"] = result.get("human_label")
        record["human_confidence"] = result.get("human_confidence")
        record["human_notes"] = result.get("human_notes")

        records.append(record)

    return records


def build_records_from_flat_sample(sample, input_format):
    if input_format == "flat_records":
        records = []
        for raw in sample.get("records", []):
            if not isinstance(raw, dict):
                continue
            record = dict(raw)
            record.setdefault(
                "association_id",
                make_association_id(
                    record.get("source"),
                    record.get("source_id"),
                    record.get("rank"),
                    record.get("target_id"),
                ),
            )
            records.append(record)
        return records

    records = []
    rules = sample["rules"]

    for source in ("hadolint", "shellcheck"):
        for rule in rules[source]:
            source_id = rule.get("source_id")
            source_rule = rule.get("source_rule", {})

            if not source_id:
                if isinstance(source_rule, dict):
                    source_id = source_rule.get("id")

            if not source_id:
                raise ValueError(f"Rule {source} without source_id.")

            matches = rule.get("matches", [])
            if not isinstance(matches, list):
                raise ValueError(
                    f"matches of {source}/{source_id} must be a list."
                )

            for match in matches:
                if not isinstance(match, dict):
                    continue

                rank = match.get("rank")
                target_id = match.get("target_id")

                source_title = None
                if isinstance(source_rule, dict):
                    source_title = source_rule.get("title")

                record = {
                    "association_id": make_association_id(
                        source, source_id, rank, target_id
                    ),
                    "source": source,
                    "source_id": source_id,
                    "source_title": source_title,
                    "source_rule": source_rule,
                    "candidate_count": rule.get(
                        "candidate_count", len(matches)
                    ),
                    "top1_relative_score": rule.get("top1_relative_score"),
                    "top2_relative_score": rule.get("top2_relative_score"),
                    "top1_top2_gap": rule.get("top1_top2_gap"),
                    "gap_bin": rule.get("gap_bin"),
                    "rank": rank,
                    "target_id": target_id,
                    "target_type": match.get("target_type"),
                    "parent_sr": match.get("parent_sr"),
                    "foundational_requirement": match.get(
                        "foundational_requirement"
                    ),
                    "target_title": match.get("target_title"),
                    "target_text": match.get("target_text"),
                    "target_rationale": match.get("target_rationale"),
                    "raw_cosine": match.get("raw_cosine"),
                    "relative_score": match.get("relative_score"),
                    "human_label": match.get("human_label"),
                    "human_confidence": match.get("human_confidence"),
                    "human_notes": match.get("human_notes"),
                    "rule_no_match": bool(rule.get("human_no_match", False)),
                    "no_match_reason": rule.get("human_no_match_reason"),
                }
                records.append(record)

    return records


def build_records(sample, input_format):
    if input_format == "gemini_audit":
        return build_records_from_gemini_audit(sample)
    return build_records_from_flat_sample(sample, input_format)


# ============================================================
# MERGE / RESUMPTION
# ============================================================

def extract_existing_annotations(old_data):
    """Extracts only human annotations from a previous output."""
    old_format = detect_input_format(old_data)
    old_records = build_records(old_data, old_format)

    annotations = {}
    for record in old_records:
        key = make_association_key(record)
        annotations[key] = {
            "human_label": record.get("human_label"),
            "human_confidence": record.get("human_confidence"),
            "human_notes": record.get("human_notes"),
        }
    return annotations


def merge_human_annotations(records, old_data):
    if old_data is None:
        return records

    old_annotations = extract_existing_annotations(old_data)
    transferred = 0

    for record in records:
        annotation = old_annotations.get(make_association_key(record))
        if annotation is None:
            continue

        if is_valid_human_label(annotation.get("human_label")):
            record["human_label"] = annotation.get("human_label")
            record["human_confidence"] = annotation.get("human_confidence")
            record["human_notes"] = annotation.get("human_notes")
            transferred += 1

    print(f"Human annotations preserved: {transferred}")
    return records


def records_to_output_sample(input_sample, input_format, records):
    """
    The output is always an object with results[] when we are
    reviewing the Gemini audit. This avoids trying to fit the 10 audit
    pairs into the 531 candidates of the original sample.
    """
    metadata = normalize_metadata(
        input_sample.get("metadata", {}), input_format
    )

    return {
        "metadata": metadata,
        "results": records,
    }


# ============================================================
# INTERACTIVE DISPLAY
# ============================================================

def print_rule_header(record):
    print()
    print("=" * 82)
    print(
        f"{safe_text(record.get('source')).upper()} "
        f"{safe_text(record.get('source_id'))}"
    )
    print(f"Association ID : {safe_text(record.get('association_id'))}")
    print("=" * 82)

    print("\nSOURCE RULE")
    print("-" * 82)
    print(safe_text(record.get("source_title")) or "(no title)")

    source_rule = record.get("source_rule")
    if isinstance(source_rule, dict):
        problematic = source_rule.get("problematic_code")
        correct = source_rule.get("correct_code")
        rationale = source_rule.get("rationale")
        exceptions = source_rule.get("exceptions")

        if problematic:
            print("\nProblematic code:")
            print(problematic)
        if correct:
            print("\nCorrect code:")
            print(correct)
        if rationale:
            print("\nRule rationale:")
            print(rationale)
        if exceptions:
            print("\nExceptions:")
            print(exceptions)
    else:
        # The enriched audit already brings these fields at the result level.
        for label, key in (
            ("Problematic code", "problematic_code"),
            ("Correct code", "correct_code"),
            ("Rule rationale", "rationale"),
            ("Exceptions", "exceptions"),
        ):
            value = record.get(key)
            if value:
                print(f"\n{label}:")
                print(value)

    print("\nCANDIDATO IEC 62443")
    print("-" * 82)
    print(f"Rank                : {safe_text(record.get('rank'))}")
    print(f"Target              : {safe_text(record.get('target_id'))}")
    print(f"Tipo                : {safe_text(record.get('target_type'))}")
    print(f"Parent SR           : {safe_text(record.get('parent_sr'))}")
    print(
        "Foundational Req.   : "
        f"{safe_text(record.get('foundational_requirement'))}"
    )
    print(f"Title                : {safe_text(record.get('target_title'))}")

    print("\nNormative text:")
    print(safe_text(record.get("target_text")) or "(no text)")

    target_rationale = record.get("target_rationale")
    if target_rationale:
        print("\nIEC requirement rationale:")
        print(target_rationale)

    pages = record.get("rationale_source_pages")
    if pages:
        print(f"\nRationale pages      : {safe_text(pages)}")

    print("\nMATCH METRICS")
    print("-" * 82)
    print(f"Raw cosine          : {safe_text(record.get('raw_cosine'))}")
    print(f"Relative score      : {safe_text(record.get('relative_score'))}")
    print(f"Top-1 relative      : {safe_text(record.get('top1_relative_score'))}")
    print(f"Top-2 relative      : {safe_text(record.get('top2_relative_score'))}")
    print(f"Top-1/Top-2 gap     : {safe_text(record.get('top1_top2_gap'))}")
    print(f"Gap bin             : {safe_text(record.get('gap_bin'))}")

    # Audit preliminar do Gemini.
    if record.get("llm_verdict") is not None:
        print("\nAUDITORIA PRELIMINAR — GEMINI")
        print("-" * 82)
        print(f"Verdict             : {safe_text(record.get('llm_verdict'))}")
        print(f"Relation type       : {safe_text(record.get('llm_relation_type'))}")
        print(f"Directness          : {safe_text(record.get('llm_directness'))}")
        print(f"Confidence          : {safe_text(record.get('llm_confidence'))}")
        print(
            "Security objective  : "
            f"{safe_text(record.get('llm_security_objective'))}"
        )
        print("Justification:")
        print(safe_text(record.get("llm_justification")) or "(no justification)")
        caveat = record.get("llm_caveat")
        if caveat:
            print("\nCaveat:")
            print(caveat)

    print("\nHUMAN STATE")
    print("-" * 82)
    print(
        f"Current label       : "
        f"{safe_text(record.get('human_label')) or '(not annotated)'}"
    )
    print(
        f"Current confidence  : "
        f"{safe_text(record.get('human_confidence')) or '(not annotated)'}"
    )
    if record.get("human_notes"):
        print(f"Current notes       : {record.get('human_notes')}")


def ask_label(current=None, allow_rule_no_match=False):
    print()
    print("[r] relevant")
    print("[p] partially_relevant")
    print("[i] irrelevant")
    if allow_rule_no_match:
        print("[n] no relevant candidate for this rule")
    print("[s] keep/annotate later")
    print("[q] quit")

    if current:
        print(f"Current: {current}")

    while True:
        value = input("\nLabel: ").strip().lower()

        if value == "q":
            return "QUIT"
        if value == "s":
            return None
        if value == "n" and allow_rule_no_match:
            return "no_match"

        mapping = {
            "r": "relevant",
            "p": "partially_relevant",
            "i": "irrelevant",
        }
        if value in mapping:
            return mapping[value]
        if value in ALLOWED_LABELS:
            return value

        print("Invalid value.")


def ask_confidence(current=None):
    print()
    print("Confidence:")
    print("  1 = very low")
    print("  2 = low")
    print("  3 = moderate")
    print("  4 = high")
    print("  5 = very high")

    if current is not None:
        print(f"Current: {current}")

    while True:
        value = input("\nConfidence [1-5]: ").strip()
        if value == "":
            return current
        try:
            value = int(value)
        except ValueError:
            print("Enter a number from 1 to 5.")
            continue
        if value in ALLOWED_CONFIDENCE:
            return value
        print("Confidence must be between 1 and 5.")


def ask_notes(current=None):
    print()
    if current:
        print(f"Current notes: {current}")
    value = input("Notes (Enter to keep/empty): ")
    return current if value == "" else value


def annotate_record(record):
    print_rule_header(record)

    label = ask_label(
        record.get("human_label"),
        allow_rule_no_match=ALLOW_RULE_NO_MATCH,
    )

    if label == "QUIT":
        return "QUIT"
    if label is None:
        return record
    if label == "no_match":
        return "NO_MATCH"

    record["human_label"] = label
    record["human_confidence"] = ask_confidence(
        record.get("human_confidence")
    )
    record["human_notes"] = ask_notes(
        record.get("human_notes")
    )
    return record


# ============================================================
# STATISTICS / STATUS
# ============================================================

def count_labeled(records):
    return sum(
        1 for r in records if is_valid_human_label(r.get("human_label"))
    )


def count_by_label(records):
    counts = Counter()
    for record in records:
        label = record.get("human_label")
        if is_valid_human_label(label):
            counts[label] += 1
    return {
        "relevant": counts.get("relevant", 0),
        "partially_relevant": counts.get("partially_relevant", 0),
        "irrelevant": counts.get("irrelevant", 0),
    }


def count_rules(records):
    return len({
        (r.get("source"), r.get("source_id"))
        for r in records
    })


def count_decided_rules(records):
    by_rule = {}
    for record in records:
        key = (record.get("source"), record.get("source_id"))
        by_rule.setdefault(key, []).append(record)

    decided = 0
    for rule_records in by_rule.values():
        if all(is_valid_human_label(r.get("human_label")) for r in rule_records):
            decided += 1
    return decided


def calculate_statistics(records):
    result = {
        "total_records": len(records),
        "labeled_records": count_labeled(records),
        "unlabeled_records": len(records) - count_labeled(records),
        "label_counts": count_by_label(records),
        "rule_count": count_rules(records),
        "decided_rule_count": count_decided_rules(records),
        "sources": {},
    }

    for source in ("hadolint", "shellcheck"):
        source_records = [r for r in records if r.get("source") == source]
        result["sources"][source] = {
            "records": len(source_records),
            "labeled": count_labeled(source_records),
            "unlabeled": len(source_records) - count_labeled(source_records),
            "label_counts": count_by_label(source_records),
            "rules": len({r.get("source_id") for r in source_records}),
        }

    return result


def update_metadata(metadata, records):
    stats = calculate_statistics(records)
    metadata["label_status"] = (
        "completed"
        if stats["total_records"] > 0
        and stats["labeled_records"] == stats["total_records"]
        else "in_progress"
        if stats["labeled_records"] > 0
        else "unreviewed"
    )
    metadata["annotated_candidate_count"] = stats["labeled_records"]
    metadata["total_candidate_count"] = stats["total_records"]
    metadata["decided_rule_count"] = stats["decided_rule_count"]
    metadata["total_rule_count"] = stats["rule_count"]
    metadata["reviewed_source_pairs"] = stats["total_records"]
    return metadata


def print_progress(records):
    total = len(records)
    labeled = count_labeled(records)
    decided = count_decided_rules(records)
    rules = count_rules(records)

    print()
    print("-" * 72)
    if total:
        print(
            f"Progresso: {labeled}/{total} candidates annotated "
            f"({labeled / total * 100:.2f}%)"
        )
    print(f"Rules decided: {decided}/{rules}")
    print("-" * 72)


# ============================================================
# CSV EXPORT
# ============================================================

CSV_FIELDS = [
    "association_id",
    "pair_id",
    "source",
    "source_id",
    "source_title",
    "problematic_code",
    "correct_code",
    "rationale",
    "exceptions",
    "rank",
    "target_id",
    "target_type",
    "parent_sr",
    "foundational_requirement",
    "target_title",
    "target_text",
    "target_rationale",
    "rationale_source_pages",
    "target_rationale_available",
    "raw_cosine",
    "relative_score",
    "top1_relative_score",
    "top2_relative_score",
    "top1_top2_gap",
    "gap_bin",
    "llm_model",
    "llm_prompt_version",
    "llm_verdict",
    "llm_relation_type",
    "llm_directness",
    "llm_confidence",
    "llm_security_objective",
    "llm_justification",
    "llm_caveat",
    "human_label",
    "human_confidence",
    "human_notes",
]


def write_csv(records, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            writer.writerow({field: record.get(field) for field in CSV_FIELDS})


# ============================================================
# XLSX EXPORT
# ============================================================

def write_xlsx(records, metadata, stats, path):
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment
        from openpyxl.utils import get_column_letter
    except ImportError as exc:
        raise RuntimeError(
            "openpyxl is not installed. Install it with: pip install openpyxl"
        ) from exc

    path.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "Review"

    headers = CSV_FIELDS
    ws.append(headers)

    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(wrap_text=True, vertical="top")

    for record in records:
        ws.append([
            export_cell_value(record.get(field))
            for field in headers
        ])

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    # The worksheet is meant for human reading. Textual columns receive
    # a reasonable width and wrap to allow comparing rule/rationale/IEC/Gemini.
    wide_columns = {
        "source_title": 28,
        "problematic_code": 32,
        "correct_code": 32,
        "rationale": 55,
        "target_title": 30,
        "target_text": 65,
        "target_rationale": 65,
        "llm_justification": 60,
        "llm_caveat": 45,
        "human_notes": 45,
    }

    for idx, header in enumerate(headers, start=1):
        width = wide_columns.get(header, min(max(len(header) + 2, 12), 24))
        ws.column_dimensions[get_column_letter(idx)].width = width

    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------
    summary = wb.create_sheet("Summary")
    summary.append(["IEC 62443 Gold Standard — Human Review"])
    summary[1][0].font = Font(bold=True, size=14)
    summary.append([])

    metadata_rows = [
        ("Input format", metadata.get("annotation_input_format")),
        ("Review scope", metadata.get("review_scope")),
        ("Standard", metadata.get("standard")),
        ("Threshold", metadata.get("threshold")),
        ("Top-K", metadata.get("top_k")),
        ("Power", metadata.get("power")),
        ("Method", metadata.get("method")),
        ("Status", metadata.get("label_status")),
        ("Total candidate pairs", stats["total_records"]),
        ("Human-labeled pairs", stats["labeled_records"]),
        ("Unlabeled pairs", stats["unlabeled_records"]),
        ("Decided rules", stats["decided_rule_count"]),
        ("Total rules represented", stats["rule_count"]),
    ]

    for key, value in metadata_rows:
        summary.append([key, value])

    summary.append([])
    summary.append(["Label", "Count"])
    summary.append(["relevant", stats["label_counts"]["relevant"]])
    summary.append([
        "partially_relevant",
        stats["label_counts"]["partially_relevant"],
    ])
    summary.append(["irrelevant", stats["label_counts"]["irrelevant"]])

    for row in summary.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    summary.column_dimensions["A"].width = 30
    summary.column_dimensions["B"].width = 70

    # --------------------------------------------------------
    # Gemini view — only if the input includes the auditor's date.
    # --------------------------------------------------------
    if any(r.get("llm_verdict") is not None for r in records):
        gemini = wb.create_sheet("Gemini_vs_Human")
        gemini_headers = [
            "association_id",
            "source",
            "source_id",
            "target_id",
            "rank",
            "llm_verdict",
            "llm_relation_type",
            "llm_directness",
            "llm_confidence",
            "llm_justification",
            "human_label",
            "human_confidence",
            "human_notes",
        ]
        gemini.append(gemini_headers)
        for cell in gemini[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        for record in records:
            gemini.append([record.get(field) for field in gemini_headers])
        gemini.freeze_panes = "A2"
        gemini.auto_filter.ref = gemini.dimensions
        for idx, header in enumerate(gemini_headers, start=1):
            gemini.column_dimensions[get_column_letter(idx)].width = (
                60 if header in {"llm_justification", "human_notes"} else 24
            )
        for row in gemini.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")

    wb.save(path)


# ============================================================
# MARKDOWN
# ============================================================

def generate_markdown(metadata, records, stats):
    lines = []
    lines.append("# IEC 62443 Gold Standard — Human Annotation Report")
    lines.append("")
    lines.append("## Review configuration")
    lines.append("")
    lines.append(f"- Input format: `{metadata.get('annotation_input_format')}`")
    lines.append(f"- Review scope: `{metadata.get('review_scope')}`")
    lines.append(f"- Standard: `{metadata.get('standard', 'unknown')}`")
    lines.append(f"- Threshold: `{metadata.get('threshold', 'unknown')}`")
    lines.append(f"- Top-K: `{metadata.get('top_k', 'unknown')}`")
    lines.append(f"- Power: `{metadata.get('power', 'unknown')}`")
    lines.append(f"- Method: `{metadata.get('method', 'unknown')}`")
    lines.append(f"- Status: `{metadata.get('label_status', 'unknown')}`")
    lines.append("")

    if metadata.get("review_scope") == "gemini_evaluated":
        lines.append(
"> This file contains only the pairs actually evaluated by "
"> Gemini. Human evaluation remains independent and authoritative."
        )
        lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Candidate pairs | {stats['total_records']} |")
    lines.append(f"| Human labeled | {stats['labeled_records']} |")
    lines.append(f"| Human unlabeled | {stats['unlabeled_records']} |")
    lines.append(f"| Rules represented | {stats['rule_count']} |")
    lines.append(f"| Rules fully reviewed | {stats['decided_rule_count']} |")
    lines.append("")

    counts = stats["label_counts"]
    lines.append("| Label | Count |")
    lines.append("|---|---:|")
    lines.append(f"| relevant | {counts['relevant']} |")
    lines.append(f"| partially_relevant | {counts['partially_relevant']} |")
    lines.append(f"| irrelevant | {counts['irrelevant']} |")
    lines.append("")

    lines.append("## Candidate review")
    lines.append("")

    for i, record in enumerate(records, start=1):
        lines.append(
            f"### {i}. {record.get('source')} / {record.get('source_id')} "
            f"→ {record.get('target_id')} (rank {record.get('rank')})"
        )
        lines.append("")
        lines.append(f"- Association: `{record.get('association_id')}`")
        lines.append(f"- Rule title: {record.get('source_title') or '(no title)'}")

        if record.get("problematic_code"):
            lines.append(f"- Problematic code: `{record.get('problematic_code')}`")
        if record.get("correct_code"):
            lines.append(f"- Correct code: `{record.get('correct_code')}`")
        if record.get("rationale"):
            lines.append(f"- Rule rationale: {record.get('rationale')}")

        lines.append("")
        lines.append("**IEC requirement**")
        lines.append("")
        lines.append(
            f"- Title: **{record.get('target_title') or '(no title)'}**"
        )
        lines.append(f"- Type: `{record.get('target_type')}`")
        lines.append(f"- Parent SR: `{record.get('parent_sr')}`")
        lines.append(f"- Foundational requirement: `{record.get('foundational_requirement')}`")
        lines.append("")
        lines.append(record.get("target_text") or "(no text)")

        if record.get("target_rationale"):
            lines.append("")
            lines.append("**IEC rationale**")
            lines.append("")
            lines.append(record.get("target_rationale"))

        lines.append("")
        lines.append("**Gemini preliminary audit**")
        lines.append("")
        lines.append(f"- Verdict: `{record.get('llm_verdict')}`")
        lines.append(f"- Relation type: `{record.get('llm_relation_type')}`")
        lines.append(f"- Directness: `{record.get('llm_directness')}`")
        lines.append(f"- Confidence: `{record.get('llm_confidence')}`")
        if record.get("llm_justification"):
            lines.append(f"- Justification: {record.get('llm_justification')}")
        if record.get("llm_caveat"):
            lines.append(f"- Caveat: {record.get('llm_caveat')}")

        lines.append("")
        lines.append("**Human annotation**")
        lines.append("")
        lines.append(f"- Label: `{record.get('human_label')}`")
        lines.append(f"- Confidence: `{record.get('human_confidence')}`")
        if record.get("human_notes"):
            lines.append(f"- Notes: {record.get('human_notes')}")
        lines.append("")

    return "\n".join(lines)


# ============================================================
# SAVE
# ============================================================

def save_outputs(output_sample, records):
    metadata = output_sample["metadata"]
    stats = calculate_statistics(records)
    update_metadata(metadata, records)

    output_sample["metadata"] = metadata
    output_sample["results"] = records

    save_json(OUTPUT_JSON, output_sample)
    write_csv(records, OUTPUT_CSV)
    write_xlsx(records, metadata, stats, OUTPUT_XLSX)

    markdown = generate_markdown(metadata, records, stats)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(markdown)

    return output_sample, stats


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 78)
    print("IEC 62443 GOLD STANDARD ANNOTATOR")
    print("=" * 78)

    print()
    print(f"Input: {INPUT_FILE}")
    print(f"Output directory: {OUTPUT_DIR}")

    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------
    input_sample = load_json(INPUT_FILE)
    input_format = detect_input_format(input_sample)
    validate_input(input_sample, input_format)

    print()
    print(f"Detected format: {input_format}")

    # --------------------------------------------------------
    # OUTPUT ANTERIOR
    # --------------------------------------------------------
    old_output = None
    if OUTPUT_JSON.exists():
        print()
        print("Existing annotation output found.")
        print(f"Resuming from: {OUTPUT_JSON}")
        old_output = load_json(OUTPUT_JSON)

        old_format = detect_input_format(old_output)
        print(f"Format of the previous output: {old_format}")

    # --------------------------------------------------------
    # RECORDS
    # --------------------------------------------------------
    print()
    print("Building review records...")
    records = build_records(input_sample, input_format)
    records = merge_human_annotations(records, old_output)

    if not records:
        raise ValueError("No pair available for review.")

    print(f"  Candidate pairs available: {len(records)}")

    if input_format == "gemini_audit":
        print(
            "  REVIEW SCOPE: only the pairs present in the Gemini audit."
        )
        print(
            "  'no_match' rule disabled: the audit may contain only a "
            "subset of the rule candidates."
        )

    # --------------------------------------------------------
    # METADATA / OUTPUT MODEL
    # --------------------------------------------------------
    metadata = normalize_metadata(
        input_sample.get("metadata", {}), input_format
    )
    output_sample = records_to_output_sample(
        input_sample,
        input_format,
        records,
    )
    output_sample["metadata"] = metadata

    print()
    print("Metadados")
    print("-" * 70)
    print(f"Standard  : {metadata.get('standard', 'unknown')}")
    print(f"Threshold : {metadata.get('threshold', 'unknown')}")
    print(f"Top-K     : {metadata.get('top_k', 'unknown')}")
    print(f"Power     : {metadata.get('power', 'unknown')}")
    print(f"Method    : {metadata.get('method', 'unknown')}")
    print(f"Scope      : {metadata.get('review_scope', 'unknown')}")
    print(f"Status    : {metadata.get('label_status', 'unknown')}")

    # --------------------------------------------------------
    # EXISTING PROGRESS
    # --------------------------------------------------------
    existing = count_labeled(records)
    if existing:
        print()
        print(f"Existing annotations: {existing}/{len(records)}")

    # --------------------------------------------------------
    # INTERACTION
    # --------------------------------------------------------
    print()
    print("=" * 78)
    print("ANNOTATION START")
    print("=" * 78)
    print()
    print("You will evaluate the rule → IEC requirement association.")
    print("In Gemini mode, only the pairs audited by Gemini will be shown.")
    print()
    print("Labels:")
    print("  relevant")
    print("  partially_relevant")
    print("  irrelevant")
    if not ALLOW_RULE_NO_MATCH:
        print()
        print(
"Note: 'no_match' is disabled in this mode because "
"a partial audit does not necessarily contain all the candidates of the rule."
        )
    print()
    print("Type 'q' to save and exit.")

    for index, record in enumerate(records):
        if is_valid_human_label(record.get("human_label")):
            continue

        print()
        print(f"[{index + 1}/{len(records)}]")

        result = annotate_record(record)

        if result == "QUIT":
            print()
            print("Exiting annotation...")
            break

        if result is None:
            continue

        if result == "NO_MATCH":
            # Can only happen if ALLOW_RULE_NO_MATCH is enabled.
            raise RuntimeError(
                "no_match was selected, but this mode should not allow that option."
            )

        records[index] = result

        print_progress(records)
        save_outputs(output_sample, records)

    # --------------------------------------------------------
    # FINAL SAVE
    # --------------------------------------------------------
    output_sample, stats = save_outputs(output_sample, records)

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------
    print()
    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print()
    print(f"Candidate pairs : {stats['total_records']}")
    print(f"Labeled         : {stats['labeled_records']}")
    print(f"Unlabeled       : {stats['unlabeled_records']}")
    print(f"Rules           : {stats['rule_count']}")
    print(f"Rules decided   : {stats['decided_rule_count']}")

    print()
    print("Labels:")
    for label, count in stats["label_counts"].items():
        print(f"  {label:20s}: {count}")

    print()
    print("Status:")
    print(f"  {output_sample['metadata'].get('label_status')}")

    print()
    print("FILES GENERATED")
    print("=" * 78)
    print(f"JSON : {OUTPUT_JSON}")
    print(f"CSV  : {OUTPUT_CSV}")
    print(f"XLSX : {OUTPUT_XLSX}")
    print(f"MD   : {OUTPUT_MD}")
    print("=" * 78)


if __name__ == "__main__":
    main()
