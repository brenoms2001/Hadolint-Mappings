#!/usr/bin/env python3

"""
IEC 62443-3-3 rationale extraction and dataset enrichment.

This script DOES NOT modify the validated requirement extraction.

Inputs:
    - IEC 62443-3-3 PDF corpus
    - iec62443_clean.json

Output:
    - iec62443_with_rationale.json

Strategy:
    1. Load validated SR/RE dataset.
    2. Extract PDF pages as text.
    3. Create overlapping processing blocks.
    4. Ask an LLM to extract ONLY:
         "Rationale and supplemental guidance"
       associated with valid SR IDs.
    5. Consolidate overlapping candidates deterministically.
    6. Merge rationales into the validated dataset.
    7. Preserve the original requirement fields unchanged.
"""

import json
import os
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import pymupdf

from google import genai


# =============================================================================
# CONFIGURATION
# =============================================================================

PDF_PATH = Path(
    "data/output/datasets/iec62443_requirements_full.pdf"
)

CLEAN_DATASET_PATH = Path(
    "data/output/datasets/iec62443_clean.json"
)

OUTPUT_PATH = Path(
    "data/output/datasets/iec62443_with_rationale.json"
)

CHECKPOINT_PATH = Path(
    "data/output/datasets/iec62443_rationale_checkpoint.json"
)

DEBUG_PATH = Path(
    "data/output/datasets/iec62443_rationale_debug.json"
)

RAW_TEXT_PATH = Path(
    "data/output/datasets/iec62443_rationale_extraction_review.txt"
)


# Gemini model.

MODEL_NAME = "gemini-3.1-flash-lite"


# Processing block configuration.

CENTRAL_PAGES_PER_BLOCK = 2
CONTEXT_PAGES_BEFORE = 1
CONTEXT_PAGES_AFTER = 1


# Retry configuration.

MAX_RETRIES = 5
BASE_RETRY_SECONDS = 10


# =============================================================================
# DATASET HELPERS
# =============================================================================

def load_json(path: Path) -> Any:
    """Load JSON from disk."""

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data: Any, path: Path) -> None:
    """Save JSON with UTF-8 formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )


def get_entries(dataset: Any) -> List[Dict[str, Any]]:
    """
    Support common dataset structures.

    Expected primary format:
        [
            {...},
            {...}
        ]

    Also supports:
        {"requirements": [...]}
        {"entries": [...]}
    """

    if isinstance(dataset, list):
        return dataset

    if isinstance(dataset, dict):

        if isinstance(dataset.get("requirements"), list):
            return dataset["requirements"]

        if isinstance(dataset.get("entries"), list):
            return dataset["entries"]

    raise ValueError(
        "Unsupported iec62443_clean.json structure. "
        "Expected a list or a dictionary containing "
        "'requirements' or 'entries'."
    )


def get_entry_text(entry: Dict[str, Any]) -> str:
    """
    Retrieve the normative requirement text without assuming
    the exact field name used by the existing dataset.
    """

    for field in (
        "text",
        "requirement",
        "requirement_text",
        "content"
    ):
        value = entry.get(field)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


def get_sr_ids(entries: List[Dict[str, Any]]) -> List[str]:
    """
    Return all validated SR IDs.

    RE IDs are excluded.
    """

    sr_ids = []

    for entry in entries:

        entry_id = str(entry.get("id", "")).strip()
        entry_type = str(entry.get("type", "")).strip().upper()

        if not entry_id:
            continue

        if entry_type == "SR":
            sr_ids.append(entry_id)
            continue

        # Fallback based on ID structure.
        if re.fullmatch(r"SR\s+\d+\.\d+", entry_id):
            sr_ids.append(entry_id)

    return sorted(
        set(sr_ids),
        key=sr_sort_key
    )


def sr_sort_key(sr_id: str):
    """
    Numeric sorting for IDs such as:

        SR 1.1
        SR 1.10
        SR 2.1
    """

    match = re.fullmatch(
        r"SR\s+(\d+)\.(\d+)",
        sr_id.strip()
    )

    if not match:
        return (999, 999)

    return (
        int(match.group(1)),
        int(match.group(2))
    )


# =============================================================================
# PDF EXTRACTION
# =============================================================================

def extract_pdf_pages(pdf_path: Path) -> List[str]:
    """
    Extract text from each PDF page independently.

    Page separation is preserved because block boundaries are useful
    for contextual extraction and debugging.
    """

    print(f"📄 Opening: {pdf_path}")

    document = pymupdf.open(pdf_path)

    pages = []

    for page_index in range(len(document)):

        page = document[page_index]

        text = page.get_text(
            "text",
            sort=True
        )

        pages.append(text)

    document.close()

    return pages


def save_raw_text(pages: List[str], output_path: Path) -> None:
    """Save extracted PDF text for manual inspection."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        for page_number, text in enumerate(
            pages,
            start=1
        ):

            file.write("\n")
            file.write("=" * 80)
            file.write("\n")
            file.write(
                f"PDF PAGE {page_number}"
            )
            file.write("\n")
            file.write("=" * 80)
            file.write("\n\n")

            file.write(text)
            file.write("\n")


# =============================================================================
# BLOCK CREATION
# =============================================================================

def create_blocks(
    pages: List[str]
) -> List[Dict[str, Any]]:
    """
    Create overlapping processing blocks.

    Example:

        Central pages:
            [3, 4]

        Context:
            [2, 3, 4, 5]

    The model receives context pages but is instructed to extract
    rationales belonging to SRs materially present in the central pages.
    """

    blocks = []

    total_pages = len(pages)

    block_id = 0

    start = 0

    while start < total_pages:

        central_start = start

        central_end = min(
            start + CENTRAL_PAGES_PER_BLOCK,
            total_pages
        )

        context_start = max(
            0,
            central_start - CONTEXT_PAGES_BEFORE
        )

        context_end = min(
            total_pages,
            central_end + CONTEXT_PAGES_AFTER
        )

        central_page_numbers = list(
            range(
                central_start + 1,
                central_end + 1
            )
        )

        context_page_numbers = list(
            range(
                context_start + 1,
                context_end + 1
            )
        )

        page_sections = []

        for page_index in range(
            context_start,
            context_end
        ):

            page_sections.append(
                f"""
===== PDF PAGE {page_index + 1} =====

{pages[page_index]}
""".strip()
            )

        blocks.append(
            {
                "block_id": block_id,
                "central_pages": central_page_numbers,
                "context_pages": context_page_numbers,
                "text": "\n\n".join(
                    page_sections
                )
            }
        )

        block_id += 1

        start += CENTRAL_PAGES_PER_BLOCK

    return blocks


# =============================================================================
# GEMINI CLIENT
# =============================================================================

def create_client():

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set."
        )

    return genai.Client(
        api_key=api_key
    )


# =============================================================================
# LLM PROMPT
# =============================================================================

def build_prompt(
    block: Dict[str, Any],
    valid_sr_ids: List[str]
) -> str:
    """
    Build a constrained rationale extraction prompt.

    Critical rules:

        - IDs come from the validated dataset.
        - The model must NOT invent SR IDs.
        - Only rationale is extracted.
        - Requirement text itself is NOT extracted.
        - Requirement enhancements are NOT rationale.
        - Security levels are NOT rationale.
    """

    valid_ids_text = "\n".join(
        f"- {sr_id}"
        for sr_id in valid_sr_ids
    )

    return f"""
You are extracting structured information from an IEC 62443-3-3 document.

TASK
====

Extract ONLY the text belonging to the section:

"Rationale and supplemental guidance"

for System Requirements (SRs).

IMPORTANT:
The validated dataset already contains the correct SR IDs and normative
requirements. You MUST NOT reconstruct requirements and MUST NOT invent IDs.

VALID SR IDs
============

{valid_ids_text}

CURRENT PROCESSING BLOCK
========================

Block ID: {block["block_id"]}

Central PDF pages:
{block["central_pages"]}

Context PDF pages:
{block["context_pages"]}

EXTRACTION RULES
================

1. Extract rationale ONLY when it belongs to one of the VALID SR IDs.

2. A rationale belongs to the SR section containing the heading:

   "Rationale and supplemental guidance"

3. Extract ONLY the explanatory text after that heading.

4. STOP extraction when the next major subsection begins, including:

   - "Requirement enhancements"
   - "Security levels"
   - a new SR heading
   - a new requirement section

5. DO NOT include:

   - the normative Requirement text;
   - Requirement enhancements;
   - Security levels;
   - requirement enhancement text;
   - SL-C(...) tables/lists;
   - page numbers;
   - copyright/license notices;
   - headers/footers;
   - OCR garbage;
   - text belonging to another SR.

6. If the rationale continues across pages, extract the portion visible
   in this block. Another overlapping block may provide the remaining text.

7. Context pages are provided to identify boundaries.
   Do not reject a rationale merely because its SR heading appears on a
   context page rather than a central page.

8. Do not invent missing content.

9. Return an empty list if this block contains no rationale.

OUTPUT FORMAT
=============

Return ONLY valid JSON.

Use exactly this structure:

{{
  "rationales": [
    {{
      "id": "SR X.Y",
      "text": "Exact rationale and supplemental guidance text extracted from the document.",
      "source_pages": [1, 2],
      "confidence": 0.0
    }}
  ]
}}

The "id" MUST be one of the VALID SR IDs.

The "text" field must contain rationale only.
The "source_pages" field must contain PDF page numbers.
The "confidence" value must be between 0.0 and 1.0.

DOCUMENT TEXT
=============

{block["text"]}
""".strip()


# =============================================================================
# MODEL RESPONSE HANDLING
# =============================================================================

def clean_json_response(text: str) -> str:
    """
    Remove Markdown fences if the model wraps JSON in them.
    """

    text = text.strip()

    if text.startswith("```"):

        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"\s*```$",
            "",
            text
        )

    return text.strip()


def call_model(
    client,
    prompt: str
) -> Dict[str, Any]:
    """
    Call Gemini and parse JSON.

    AFC/function calling is intentionally not used.
    """

    last_error = None

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            response_text = getattr(
                response,
                "text",
                None
            )

            if not response_text:
                raise ValueError(
                    "Model returned an empty response."
                )

            cleaned_response = clean_json_response(
                response_text
            )

            data = json.loads(
                cleaned_response
            )

            if not isinstance(data, dict):
                raise ValueError(
                    "Model response is not a JSON object."
                )

            return data

        except Exception as error:

            last_error = error

            print(
                f"\n⚠️ Attempt {attempt}/{MAX_RETRIES} failed:"
            )

            print(
                f"   {type(error).__name__}: {error}"
            )

            if attempt < MAX_RETRIES:

                wait_seconds = (
                    BASE_RETRY_SECONDS * attempt
                )

                # Respect explicit retry hints when present.
                retry_match = re.search(
                    r"retry in ([\d.]+)\s*s",
                    str(error),
                    flags=re.IGNORECASE
                )

                if retry_match:

                    suggested = float(
                        retry_match.group(1)
                    )

                    wait_seconds = max(
                        wait_seconds,
                        suggested + 2
                    )

                print(
                    f"   ⏳ Retrying in "
                    f"{wait_seconds:.1f} seconds..."
                )

                time.sleep(wait_seconds)

    raise RuntimeError(
        f"Model failed after {MAX_RETRIES} attempts: "
        f"{last_error}"
    )


# =============================================================================
# CANDIDATE VALIDATION
# =============================================================================

def normalize_text(text: str) -> str:
    """
    Normalize whitespace for comparison.
    """

    text = text.replace(
        "\u00ad",
        ""
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def is_valid_rationale_text(text: str) -> bool:
    """
    Basic contamination checks.

    These checks reject clearly invalid output but deliberately avoid
    aggressive heuristics that could reject valid IEC text.
    """

    if not isinstance(text, str):
        return False

    text = normalize_text(text)

    if len(text) < 20:
        return False

    forbidden_markers = [
        "Requirement enhancements",
        "Security levels",
        "Copyright",
        "Not for Resale",
        "Provided by IHS"
    ]

    for marker in forbidden_markers:

        if marker.lower() in text.lower():
            return False

    return True


def validate_candidates(
    response_data: Dict[str, Any],
    valid_sr_ids: set,
    block: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Validate model candidates before checkpointing them.
    """

    rationales = response_data.get(
        "rationales",
        []
    )

    if not isinstance(rationales, list):
        return []

    validated = []

    for candidate in rationales:

        if not isinstance(candidate, dict):
            continue

        sr_id = str(
            candidate.get("id", "")
        ).strip()

        if sr_id not in valid_sr_ids:
            continue

        text = candidate.get(
            "text",
            ""
        )

        if not is_valid_rationale_text(text):
            continue

        source_pages = candidate.get(
            "source_pages",
            []
        )

        if not isinstance(source_pages, list):
            source_pages = []

        normalized_pages = []

        for page in source_pages:

            if isinstance(page, int):

                normalized_pages.append(
                    page
                )

        confidence = candidate.get(
            "confidence",
            None
        )

        if not isinstance(
            confidence,
            (int, float)
        ):
            confidence = None

        validated.append(
            {
                "id": sr_id,
                "text": normalize_text(text),
                "source_pages": sorted(
                    set(normalized_pages)
                ),
                "confidence": confidence,
                "block_id": block["block_id"],
                "central_pages": block[
                    "central_pages"
                ],
                "context_pages": block[
                    "context_pages"
                ]
            }
        )

    return validated


# =============================================================================
# CHECKPOINTING
# =============================================================================

def load_checkpoint() -> Dict[str, Any]:
    """
    Load previous progress if available.
    """

    if not CHECKPOINT_PATH.exists():

        return {
            "completed_blocks": [],
            "candidates": []
        }

    data = load_json(
        CHECKPOINT_PATH
    )

    if not isinstance(data, dict):

        return {
            "completed_blocks": [],
            "candidates": []
        }

    data.setdefault(
        "completed_blocks",
        []
    )

    data.setdefault(
        "candidates",
        []
    )

    return data


def save_checkpoint(
    checkpoint: Dict[str, Any]
) -> None:

    save_json(
        checkpoint,
        CHECKPOINT_PATH
    )


# =============================================================================
# CONSOLIDATION
# =============================================================================

def remove_contained_duplicates(
    texts: List[str]
) -> List[str]:
    """
    Remove exact duplicates and variants completely contained
    inside longer variants.
    """

    unique = []

    for text in texts:

        normalized = normalize_text(text)

        if normalized and normalized not in unique:
            unique.append(normalized)

    # Longest first.
    unique.sort(
        key=len,
        reverse=True
    )

    kept = []

    for candidate in unique:

        candidate_lower = candidate.lower()

        contained = False

        for existing in kept:

            if candidate_lower in existing.lower():

                contained = True
                break

        if not contained:

            kept.append(candidate)

    return kept


def suffix_prefix_overlap(
    first: str,
    second: str,
    minimum_overlap: int = 80
) -> int:
    """
    Find a word-level suffix/prefix overlap.

    Used to reconstruct rationales split across blocks.
    """

    first_words = first.split()
    second_words = second.split()

    maximum = min(
        len(first_words),
        len(second_words)
    )

    for size in range(
        maximum,
        0,
        -1
    ):

        first_suffix = " ".join(
            first_words[-size:]
        )

        second_prefix = " ".join(
            second_words[:size]
        )

        if (
            normalize_text(
                first_suffix
            ).lower()
            ==
            normalize_text(
                second_prefix
            ).lower()
        ):

            overlap_text = normalize_text(
                first_suffix
            )

            if len(overlap_text) >= minimum_overlap:

                return size

    return 0


def merge_two_texts(
    first: str,
    second: str
) -> str:
    """
    Merge two rationale fragments while avoiding duplicated overlap.
    """

    first = normalize_text(first)
    second = normalize_text(second)

    if not first:
        return second

    if not second:
        return first

    if second.lower() in first.lower():
        return first

    if first.lower() in second.lower():
        return second

    overlap = suffix_prefix_overlap(
        first,
        second
    )

    if overlap > 0:

        second_words = second.split()

        return normalize_text(
            first
            + " "
            + " ".join(
                second_words[overlap:]
            )
        )

    return normalize_text(
        first + " " + second
    )


def consolidate_rationales(
    candidates: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """
    Consolidate candidates by SR ID.

    Strategy:

        1. Group candidates by SR.
        2. Remove duplicates and contained variants.
        3. Prefer candidates ordered by PDF page/block order.
        4. Merge overlapping fragments.
    """

    grouped = defaultdict(list)

    for candidate in candidates:

        grouped[
            candidate["id"]
        ].append(candidate)

    consolidated = {}

    for sr_id, sr_candidates in grouped.items():

        # Sort by earliest source page and block.
        sr_candidates.sort(
            key=lambda item: (
                min(
                    item["source_pages"]
                )
                if item["source_pages"]
                else 9999,
                item["block_id"]
            )
        )

        raw_texts = [
            candidate["text"]
            for candidate in sr_candidates
        ]

        texts = remove_contained_duplicates(
            raw_texts
        )

        # Restore approximate document order.
        ordered_texts = []

        for candidate in sr_candidates:

            candidate_text = normalize_text(
                candidate["text"]
            )

            for surviving_text in texts:

                if (
                    candidate_text.lower()
                    ==
                    surviving_text.lower()
                    and surviving_text
                    not in ordered_texts
                ):

                    ordered_texts.append(
                        surviving_text
                    )

        merged = ""

        for text in ordered_texts:

            merged = merge_two_texts(
                merged,
                text
            )

        all_pages = sorted(
            {
                page
                for candidate in sr_candidates
                for page in candidate[
                    "source_pages"
                ]
            }
        )

        confidences = [
            candidate["confidence"]
            for candidate in sr_candidates
            if isinstance(
                candidate["confidence"],
                (int, float)
            )
        ]

        average_confidence = (
            sum(confidences)
            / len(confidences)
            if confidences
            else None
        )

        consolidated[sr_id] = {
            "text": merged,
            "source_pages": all_pages,
            "candidate_count": len(
                sr_candidates
            ),
            "average_confidence": (
                average_confidence
            )
        }

    return consolidated


# =============================================================================
# DATASET MERGING
# =============================================================================

def add_rationales_to_dataset(
    original_dataset: Any,
    entries: List[Dict[str, Any]],
    rationales: Dict[str, Dict[str, Any]]
) -> Any:
    """
    Add rationale information without changing existing requirement data.
    """

    enriched_entries = []

    for entry in entries:

        enriched = dict(entry)

        entry_id = str(
            entry.get("id", "")
        ).strip()

        entry_type = str(
            entry.get("type", "")
        ).strip().upper()

        is_sr = (
            entry_type == "SR"
            or re.fullmatch(
                r"SR\s+\d+\.\d+",
                entry_id
            )
        )

        if is_sr:

            rationale_data = rationales.get(
                entry_id
            )

            if rationale_data:

                enriched["rationale"] = (
                    rationale_data["text"]
                )

                enriched[
                    "rationale_source_pages"
                ] = rationale_data[
                    "source_pages"
                ]

            else:

                enriched["rationale"] = None

                enriched[
                    "rationale_source_pages"
                ] = []

        else:

            # REs do not automatically inherit the parent SR rationale.
            enriched["rationale"] = None
            enriched[
                "rationale_source_pages"
            ] = []

        enriched_entries.append(
            enriched
        )

    # Preserve the original top-level structure.
    if isinstance(original_dataset, list):

        return enriched_entries

    if isinstance(original_dataset, dict):

        result = dict(original_dataset)

        if isinstance(
            result.get("requirements"),
            list
        ):

            result["requirements"] = (
                enriched_entries
            )

            return result

        if isinstance(
            result.get("entries"),
            list
        ):

            result["entries"] = enriched_entries

            return result

    return enriched_entries


# =============================================================================
# VALIDATION
# =============================================================================

def validate_output(
    entries: List[Dict[str, Any]],
    valid_sr_ids: List[str]
) -> Dict[str, Any]:
    """
    Validate rationale coverage.

    Missing rationale is not automatically an error because a few SRs
    may legitimately have unusual structure. It is reported explicitly.
    """

    sr_entries = []

    for entry in entries:

        entry_id = str(
            entry.get("id", "")
        ).strip()

        entry_type = str(
            entry.get("type", "")
        ).strip().upper()

        if (
            entry_type == "SR"
            or re.fullmatch(
                r"SR\s+\d+\.\d+",
                entry_id
            )
        ):

            sr_entries.append(entry)

    extracted = []

    missing = []

    contaminated = []

    for entry in sr_entries:

        entry_id = str(
            entry.get("id", "")
        )

        rationale = entry.get(
            "rationale"
        )

        if not isinstance(
            rationale,
            str
        ) or not rationale.strip():

            missing.append(entry_id)
            continue

        extracted.append(entry_id)

        for marker in (
            "Requirement enhancements",
            "Security levels",
            "Not for Resale",
            "Provided by IHS"
        ):

            if marker.lower() in rationale.lower():

                contaminated.append(
                    {
                        "id": entry_id,
                        "marker": marker
                    }
                )

    return {
        "expected_sr_count": len(
            valid_sr_ids
        ),
        "extracted_rationale_count": len(
            extracted
        ),
        "missing_rationales": sorted(
            missing,
            key=sr_sort_key
        ),
        "contamination_warnings": contaminated
    }


# =============================================================================
# DEBUG OUTPUT
# =============================================================================

def build_debug_output(
    blocks: List[Dict[str, Any]],
    candidates: List[Dict[str, Any]],
    consolidated: Dict[str, Dict[str, Any]],
    validation: Dict[str, Any]
) -> Dict[str, Any]:

    return {
        "configuration": {
            "pdf_path": str(PDF_PATH),
            "clean_dataset_path": str(
                CLEAN_DATASET_PATH
            ),
            "model": MODEL_NAME,
            "central_pages_per_block": (
                CENTRAL_PAGES_PER_BLOCK
            ),
            "context_pages_before": (
                CONTEXT_PAGES_BEFORE
            ),
            "context_pages_after": (
                CONTEXT_PAGES_AFTER
            )
        },
        "blocks": [
            {
                "block_id": block["block_id"],
                "central_pages": block[
                    "central_pages"
                ],
                "context_pages": block[
                    "context_pages"
                ]
            }
            for block in blocks
        ],
        "candidate_count": len(
            candidates
        ),
        "candidates": candidates,
        "consolidated_rationales": (
            consolidated
        ),
        "validation": validation
    }


# =============================================================================
# MAIN
# =============================================================================

def main():

    print()
    print(
        "🚀 Starting IEC 62443-3-3 "
        "rationale extraction..."
    )
    print()

    print("📚 Source PDF:")
    print(f"   {PDF_PATH}")

    print()

    print("📚 Validated requirement dataset:")
    print(f"   {CLEAN_DATASET_PATH}")

    print()

    # -------------------------------------------------------------------------
    # Load validated dataset
    # -------------------------------------------------------------------------

    original_dataset = load_json(
        CLEAN_DATASET_PATH
    )

    entries = get_entries(
        original_dataset
    )

    valid_sr_ids = get_sr_ids(
        entries
    )

    valid_sr_id_set = set(
        valid_sr_ids
    )

    print(
        f"✅ Loaded {len(entries)} "
        f"validated dataset entries."
    )

    print(
        f"✅ Identified {len(valid_sr_ids)} "
        f"validated SR IDs."
    )

    # -------------------------------------------------------------------------
    # Extract PDF
    # -------------------------------------------------------------------------

    pages = extract_pdf_pages(
        PDF_PATH
    )

    print(
        f"📄 PDF contains {len(pages)} pages."
    )

    save_raw_text(
        pages,
        RAW_TEXT_PATH
    )

    print()
    print(
        "📝 Raw extraction saved to:"
    )
    print(
        f"   {RAW_TEXT_PATH}"
    )

    # -------------------------------------------------------------------------
    # Create blocks
    # -------------------------------------------------------------------------

    blocks = create_blocks(
        pages
    )

    print()
    print(
        f"📦 Created {len(blocks)} "
        f"processing blocks."
    )

    # -------------------------------------------------------------------------
    # Checkpoint
    # -------------------------------------------------------------------------

    checkpoint = load_checkpoint()

    completed_blocks = set(
        checkpoint.get(
            "completed_blocks",
            []
        )
    )

    all_candidates = checkpoint.get(
        "candidates",
        []
    )

    if completed_blocks:

        print()
        print(
            "🔄 Checkpoint found."
        )

        print(
            f"   Completed blocks: "
            f"{len(completed_blocks)}"
        )

        print(
            f"   Saved candidates: "
            f"{len(all_candidates)}"
        )

    else:

        print()
        print(
            "🆕 No checkpoint found. "
            "Starting a new extraction."
        )

    # -------------------------------------------------------------------------
    # Create client
    # -------------------------------------------------------------------------

    client = create_client()

    # -------------------------------------------------------------------------
    # Process blocks
    # -------------------------------------------------------------------------

    for index, block in enumerate(
        blocks,
        start=1
    ):

        block_id = block["block_id"]

        if block_id in completed_blocks:

            print()
            print(
                f"⏭️ Skipping block "
                f"{index}/{len(blocks)} "
                f"(ID {block_id})"
            )

            continue

        print()
        print(
            f"📦 Processing block "
            f"{index}/{len(blocks)} "
            f"(ID {block_id})"
        )

        print(
            f"   Central pages: "
            f"{block['central_pages']}"
        )

        print(
            f"   Context pages: "
            f"{block['context_pages']}"
        )

        prompt = build_prompt(
            block,
            valid_sr_ids
        )

        response_data = call_model(
            client,
            prompt
        )

        candidates = validate_candidates(
            response_data,
            valid_sr_id_set,
            block
        )

        all_candidates.extend(
            candidates
        )

        completed_blocks.add(
            block_id
        )

        checkpoint = {
            "completed_blocks": sorted(
                completed_blocks
            ),
            "candidates": all_candidates
        }

        save_checkpoint(
            checkpoint
        )

        print(
            f"   ✅ Block completed. "
            f"Model returned "
            f"{len(candidates)} "
            f"valid rationale candidates."
        )

        # Small pacing delay to reduce rate-limit pressure.
        time.sleep(1)

    # -------------------------------------------------------------------------
    # Consolidate
    # -------------------------------------------------------------------------

    print()
    print(
        "🔄 Consolidating rationale candidates..."
    )

    consolidated = consolidate_rationales(
        all_candidates
    )

    # -------------------------------------------------------------------------
    # Merge
    # -------------------------------------------------------------------------

    enriched_dataset = add_rationales_to_dataset(
        original_dataset,
        entries,
        consolidated
    )

    enriched_entries = get_entries(
        enriched_dataset
    )

    # -------------------------------------------------------------------------
    # Validate
    # -------------------------------------------------------------------------

    validation = validate_output(
        enriched_entries,
        valid_sr_ids
    )

    # -------------------------------------------------------------------------
    # Debug
    # -------------------------------------------------------------------------

    debug_data = build_debug_output(
        blocks,
        all_candidates,
        consolidated,
        validation
    )

    save_json(
        debug_data,
        DEBUG_PATH
    )

    print()
    print(
        "🛠️ Debug JSON saved to:"
    )
    print(
        f"   {DEBUG_PATH}"
    )

    # -------------------------------------------------------------------------
    # Save final dataset
    # -------------------------------------------------------------------------

    save_json(
        enriched_dataset,
        OUTPUT_PATH
    )

    print()
    print(
        "💾 Enriched dataset saved to:"
    )
    print(
        f"   {OUTPUT_PATH}"
    )

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "RATIONALE EXTRACTION VALIDATION"
    )
    print("=" * 70)

    print()

    print(
        f"Expected SRs              : "
        f"{validation['expected_sr_count']}"
    )

    print(
        f"Rationales extracted      : "
        f"{validation['extracted_rationale_count']}"
    )

    print(
        f"Missing rationales        : "
        f"{len(validation['missing_rationales'])}"
    )

    print(
        f"Contamination warnings    : "
        f"{len(validation['contamination_warnings'])}"
    )

    if validation["missing_rationales"]:

        print()
        print(
            "⚠️ SRs without extracted rationale:"
        )

        for sr_id in validation[
            "missing_rationales"
        ]:

            print(f"   - {sr_id}")

    if validation[
        "contamination_warnings"
    ]:

        print()
        print(
            "⚠️ Possible rationale contamination:"
        )

        for warning in validation[
            "contamination_warnings"
        ]:

            print(
                f"   - {warning['id']}: "
                f"{warning['marker']}"
            )

    print()
    print("=" * 70)

    if (
        not validation["missing_rationales"]
        and not validation[
            "contamination_warnings"
        ]
    ):

        print(
            "✅ RATIONALE EXTRACTION "
            "COMPLETED SUCCESSFULLY"
        )

    else:

        print(
            "⚠️ RATIONALE EXTRACTION "
            "COMPLETED WITH ITEMS FOR REVIEW"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()