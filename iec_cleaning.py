#!/usr/bin/env python3
"""
iec_cleaning.py

LLM-assisted extraction of IEC 62443-3-3 System Requirements (SRs)
and Requirement Enhancements (REs).

Architecture:

PDF
 ↓
Page-by-page text extraction
 ↓
Context windows with overlap
 ↓
Gemini Flash semantic extraction
 ↓
Checkpoint after every processed block
 ↓
Canonical ID validation
 ↓
Deterministic deduplication
 ↓
Fragment consolidation
 ↓
Structural validation
 ↓
Final JSON

The LLM is responsible for semantic interpretation.
Python is responsible for deterministic orchestration,
checkpointing, validation and deduplication.
"""

import os
import json
import time
import re
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

import pymupdf

# Google GenAI SDK
from google import genai
from google.genai import types


# ======================================================================
# CONFIGURATION
# ======================================================================

PDF_PATH = Path(
    "data/output/datasets/iec62443_requirements_full.pdf"
)

OUTPUT_DIR = Path("data/output/datasets")

RAW_EXTRACTION_PATH = OUTPUT_DIR / "iec62443_extraction_review.txt"

CHECKPOINT_PATH = OUTPUT_DIR / "iec62443_llm_checkpoint.json"

BLOCK_RESULTS_PATH = OUTPUT_DIR / "iec62443_llm_blocks.json"

DEBUG_PATH = OUTPUT_DIR / "iec62443_debug.json"

FINAL_JSON_PATH = OUTPUT_DIR / "iec62443_clean.json"


# ----------------------------------------------------------------------
# GEMINI
# ----------------------------------------------------------------------

MODEL_NAME = "gemini-3.1-flash-lite"

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "\nGEMINI_API_KEY environment variable is not set.\n\n"
        "For Bash/Linux:\n"
        'export GEMINI_API_KEY="YOUR_API_KEY"\n\n'
        "Then run:\n"
        "python3 iec_cleaning.py\n"
    )

client = genai.Client(api_key=API_KEY)


# ----------------------------------------------------------------------
# BLOCK PROCESSING
# ----------------------------------------------------------------------

# Number of pages in the central processing unit.
CENTRAL_PAGES_PER_BLOCK = 2

# Number of pages before and after the central block supplied as context.
CONTEXT_PAGES = 1

# Delay between successful API calls.
REQUEST_DELAY_SECONDS = 1.0

# Retry configuration.
MAX_RETRIES = 5
INITIAL_RETRY_DELAY = 5


# ======================================================================
# EXPECTED IEC 62443-3-3 SYSTEM REQUIREMENTS
# ======================================================================

EXPECTED_SRS = {
    1: 13,
    2: 12,
    3: 9,
    4: 3,
    5: 4,
    6: 2,
    7: 8,
}

EXPECTED_SR_IDS = {
    f"SR {fr}.{number}"
    for fr, maximum in EXPECTED_SRS.items()
    for number in range(1, maximum + 1)
}


FR_NAMES = {
    1: "Identification and authentication control",
    2: "Use control",
    3: "System integrity",
    4: "Data confidentiality",
    5: "Restricted data flow",
    6: "Timely response to events",
    7: "Resource availability",
}


# ======================================================================
# CANONICAL ID VALIDATION
# ======================================================================

# These regexes are intentionally used ONLY to validate IDs returned
# by the LLM. They are NOT used to discover requirements in the PDF.

SR_ID_PATTERN = re.compile(
    r"^SR\s+([1-7])\.(\d+)$",
    re.IGNORECASE,
)

RE_ID_PATTERN = re.compile(
    r"^SR\s+([1-7])\.(\d+)\s+RE\s+(\d+)$",
    re.IGNORECASE,
)


def normalize_whitespace(text):
    """
    Normalize arbitrary whitespace without changing semantic content.
    """
    if not isinstance(text, str):
        return ""

    return re.sub(r"\s+", " ", text).strip()


def normalize_id(raw_id):
    """
    Normalize an SR or RE identifier into canonical form.

    Examples:
        sr 1.1
        SR1.1
        SR 1.1 RE1

    become:

        SR 1.1
        SR 1.1 RE 1
    """

    if not isinstance(raw_id, str):
        return None

    text = raw_id.strip().upper()

    text = re.sub(r"\s+", " ", text)

    text = re.sub(
        r"^SR\s*([1-7])\s*\.\s*(\d+)\s*$",
        r"SR \1.\2",
        text,
    )

    text = re.sub(
        r"^SR\s*([1-7])\s*\.\s*(\d+)\s*RE\s*(\d+)\s*$",
        r"SR \1.\2 RE \3",
        text,
    )

    if SR_ID_PATTERN.fullmatch(text):
        return text

    if RE_ID_PATTERN.fullmatch(text):
        return text

    return None


def get_parent_sr_id(requirement_id):
    """
    Return the parent SR for an SR or RE.

    SR 1.1       -> SR 1.1
    SR 1.1 RE 2  -> SR 1.1
    """

    requirement_id = normalize_id(requirement_id)

    if requirement_id is None:
        return None

    if " RE " not in requirement_id:
        return requirement_id

    return requirement_id.split(" RE ")[0]


def get_fr_number(requirement_id):
    """
    Extract Foundational Requirement number from an ID.
    """

    parent = get_parent_sr_id(requirement_id)

    if not parent:
        return None

    match = SR_ID_PATTERN.fullmatch(parent)

    if not match:
        return None

    return int(match.group(1))


# ======================================================================
# FILE HELPERS
# ======================================================================

def ensure_output_directory():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path, default):
    """
    Safely load JSON or return a default value.
    """

    if not path.exists():
        return default

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError) as error:
        print(f"⚠️ Could not load {path}: {error}")
        return default


def save_json(data, path):
    """
    Atomically save JSON to reduce corruption risk.
    """

    temporary_path = Path(str(path) + ".tmp")

    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    temporary_path.replace(path)


def utc_timestamp():
    return datetime.now(timezone.utc).isoformat()


# ======================================================================
# PDF EXTRACTION
# ======================================================================

def extract_pdf_pages(pdf_path):
    """
    Extract text independently from every PDF page.
    """

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"\n❌ PDF not found:\n   {pdf_path}\n"
        )

    print(f"📄 Opening: {pdf_path}")

    document = pymupdf.open(pdf_path)

    pages = []

    try:
        for index in range(len(document)):

            text = document[index].get_text("text")

            pages.append({
                "page_index": index,
                "page_number": index + 1,
                "text": text,
            })

    finally:
        document.close()

    return pages


def save_raw_extraction(pages):
    """
    Save complete page-by-page extraction for manual inspection.
    """

    with open(RAW_EXTRACTION_PATH, "w", encoding="utf-8") as file:

        for page in pages:

            file.write("\n")
            file.write("=" * 80)
            file.write("\n")

            file.write(
                f"PAGE {page['page_number']}\n"
            )

            file.write("=" * 80)
            file.write("\n\n")

            file.write(page["text"])

            file.write("\n\n")

    print(
        "\n📝 Raw extraction saved to:\n"
        f"   {RAW_EXTRACTION_PATH}"
    )


# ======================================================================
# BLOCK CREATION
# ======================================================================

def create_blocks(pages):
    """
    Create deterministic page blocks.

    Every block has:

    - central pages:
        pages that are considered the primary responsibility
        of this block.

    - context pages:
        neighboring pages supplied to the model only to provide
        semantic continuity.

    A requirement may therefore appear in more than one API response,
    but canonical IDs allow deterministic consolidation later.
    """

    blocks = []

    total_pages = len(pages)

    block_id = 0

    for start in range(
        0,
        total_pages,
        CENTRAL_PAGES_PER_BLOCK,
    ):

        central_start = start

        central_end = min(
            start + CENTRAL_PAGES_PER_BLOCK,
            total_pages,
        )

        context_start = max(
            0,
            central_start - CONTEXT_PAGES,
        )

        context_end = min(
            total_pages,
            central_end + CONTEXT_PAGES,
        )

        central_page_numbers = [
            pages[index]["page_number"]
            for index in range(
                central_start,
                central_end,
            )
        ]

        context_page_numbers = [
            pages[index]["page_number"]
            for index in range(
                context_start,
                context_end,
            )
        ]

        page_payload = []

        for index in range(
            context_start,
            context_end,
        ):

            page = pages[index]

            page_role = (
                "CENTRAL"
                if central_start <= index < central_end
                else "CONTEXT"
            )

            page_payload.append(
                f"\n"
                f"===== PAGE {page['page_number']} "
                f"[{page_role}] =====\n\n"
                f"{page['text']}"
            )

        blocks.append({
            "block_id": block_id,
            "central_pages": central_page_numbers,
            "context_pages": context_page_numbers,
            "text": "\n".join(page_payload),
        })

        block_id += 1

    return blocks


# ======================================================================
# LLM PROMPT
# ======================================================================

SYSTEM_INSTRUCTION = """
You are an information extraction system.

Your task is to extract IEC 62443-3-3 security requirements from
a supplied excerpt of the standard.

You MUST return ONLY JSON.

Do not explain your reasoning.
Do not add Markdown.
Do not invent requirements.
Do not infer missing text from external knowledge.

The input contains pages marked as:

[CENTRAL]
    These are the pages primarily assigned to this extraction block.

[CONTEXT]
    These pages are provided only to understand material that begins
    or ends around the CENTRAL pages.

IMPORTANT BOUNDARY RULE:

A requirement may begin before a CENTRAL page or end after it.

If you can identify the requirement's canonical ID from the supplied
context, you may extract the complete requirement using all available
text.

It is acceptable for the same requirement to appear in multiple blocks.
The calling program will deduplicate by canonical ID.

Extract only:

1. System Requirements (SR)

2. Requirement Enhancements (RE)

Canonical IDs:

SR:
    SR X.Y

RE:
    SR X.Y RE Z

For every extracted item provide:

id:
    Canonical requirement identifier.

type:
    Either "SR" or "RE".

title:
    The official requirement title when clearly present.

text:
    ONLY the normative requirement statement.

Do NOT include:

- rationale and supplemental guidance;
- examples;
- explanatory discussion;
- security level tables;
- page headers or footers;
- copyright notices;
- licensing notices;
- publication metadata;
- "Void";
- references unless they are necessary inside the normative statement.

For SRs:

The normative text generally contains the primary requirement statement
before sections such as:

"Rationale and supplemental guidance"

"Requirement enhancements"

"Security levels"

For REs:

Extract the enhancement statement itself.

If the title or requirement cannot be reliably identified from the
provided text, do not invent it.

Return exactly this JSON structure:

{
  "requirements": [
    {
      "id": "SR 1.1",
      "type": "SR",
      "title": "Human user identification and authentication",
      "text": "The control system shall ..."
    }
  ]
}
"""


def build_prompt(block):
    """
    Build a deterministic extraction request.
    """

    central_pages = ", ".join(
        str(page)
        for page in block["central_pages"]
    )

    context_pages = ", ".join(
        str(page)
        for page in block["context_pages"]
    )

    return f"""
IEC 62443-3-3 EXTRACTION BLOCK

Block ID:
{block["block_id"]}

Central pages:
{central_pages}

All supplied pages:
{context_pages}

Extract IEC 62443-3-3 SRs and REs that can be reliably identified
from this material.

Remember:

- CENTRAL pages are the primary extraction target.
- CONTEXT pages exist to prevent requirements from being incorrectly
  split at page boundaries.
- Do not invent missing requirements.
- Return only valid JSON.

DOCUMENT EXCERPT:

{block["text"]}
"""


# ======================================================================
# GEMINI RESPONSE HANDLING
# ======================================================================

def extract_json_from_response(response):
    """
    Parse Gemini response safely.
    """

    response_text = getattr(response, "text", None)

    if not response_text:
        raise ValueError(
            "Model returned an empty response."
        )

    response_text = response_text.strip()

    # First attempt: direct JSON.
    try:
        return json.loads(response_text)

    except json.JSONDecodeError:
        pass

    # Second attempt: tolerate accidental Markdown fences.
    cleaned = response_text

    if cleaned.startswith("```"):
        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned,
        )

    return json.loads(cleaned)


def call_gemini(block):
    """
    Call Gemini with retries and exponential backoff.
    """

    prompt = build_prompt(block)

    retry_delay = INITIAL_RETRY_DELAY

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0,
                    response_mime_type="application/json",
                ),
            )

            data = extract_json_from_response(response)

            if not isinstance(data, dict):
                raise ValueError(
                    "Model JSON root is not an object."
                )

            requirements = data.get("requirements")

            if requirements is None:
                requirements = []

            if not isinstance(requirements, list):
                raise ValueError(
                    "'requirements' is not a list."
                )

            return {
                "status": "completed",
                "requirements": requirements,
                "processed_at": utc_timestamp(),
            }

        except KeyboardInterrupt:
            raise

        except Exception as error:

            print(
                f"\n⚠️ Block {block['block_id']} "
                f"attempt {attempt}/{MAX_RETRIES} failed:"
            )

            print(f"   {type(error).__name__}: {error}")

            if attempt == MAX_RETRIES:
                return {
                    "status": "failed",
                    "error": str(error),
                    "requirements": [],
                    "processed_at": utc_timestamp(),
                }

            print(
                f"   ⏳ Retrying in "
                f"{retry_delay} seconds..."
            )

            time.sleep(retry_delay)

            retry_delay *= 2


# ======================================================================
# CHECKPOINT MANAGEMENT
# ======================================================================

def create_empty_checkpoint():
    """
    Initial checkpoint structure.
    """

    return {
        "metadata": {
            "created_at": utc_timestamp(),
            "model": MODEL_NAME,
            "pdf": str(PDF_PATH),
            "version": "llm-page-block-extraction-v1",
        },
        "blocks": {},
    }


def load_checkpoint():
    """
    Load previous progress or initialize a new checkpoint.
    """

    checkpoint = load_json(
        CHECKPOINT_PATH,
        None,
    )

    if checkpoint is None:

        checkpoint = create_empty_checkpoint()

        print(
            "\n🆕 No checkpoint found. "
            "Starting a new extraction."
        )

    else:

        print(
            "\n▶️ Existing checkpoint found. "
            "Resuming extraction."
        )

    checkpoint.setdefault("metadata", {})
    checkpoint.setdefault("blocks", {})

    return checkpoint


def is_block_completed(checkpoint, block_id):
    """
    Determine whether a block was successfully processed.
    """

    block = checkpoint["blocks"].get(str(block_id))

    if not block:
        return False

    return block.get("status") == "completed"


def save_checkpoint(checkpoint):
    """
    Persist extraction progress.
    """

    checkpoint["metadata"]["updated_at"] = utc_timestamp()

    save_json(
        checkpoint,
        CHECKPOINT_PATH,
    )


# ======================================================================
# REQUIREMENT SANITIZATION
# ======================================================================

def sanitize_requirement(item, block):
    """
    Convert a model result into a validated canonical record.

    Invalid or out-of-scope results are rejected.
    """

    if not isinstance(item, dict):
        return None

    raw_id = item.get("id")

    requirement_id = normalize_id(raw_id)

    if requirement_id is None:
        return None

    item_type = str(
        item.get("type", "")
    ).strip().upper()

    expected_type = (
        "RE"
        if " RE " in requirement_id
        else "SR"
    )

    # The canonical ID determines the real type.
    item_type = expected_type

    parent_id = get_parent_sr_id(
        requirement_id
    )

    # Reject SRs outside the known IEC 62443-3-3 SR set.
    if expected_type == "SR":

        if parent_id not in EXPECTED_SR_IDS:
            return None

    # RE parent must belong to the expected SR universe.
    if expected_type == "RE":

        if parent_id not in EXPECTED_SR_IDS:
            return None

    title = normalize_whitespace(
        item.get("title", "")
    )

    text = normalize_whitespace(
        item.get("text", "")
    )

    if not text:
        return None

    # Basic cleanup of obvious PDF artifacts.
    text = re.sub(
        r"\bVoid\b",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = normalize_whitespace(text)

    if not text:
        return None

    return {
        "id": requirement_id,
        "type": item_type,
        "title": title,
        "text": text,
        "parent_sr": parent_id,
        "fr": get_fr_number(
            requirement_id
        ),
        "source_block": block["block_id"],
        "central_pages": block["central_pages"],
        "context_pages": block["context_pages"],
    }


# ======================================================================
# DEDUPLICATION AND CONSOLIDATION
# ======================================================================

def is_substantially_same_text(a, b):
    """
    Conservative duplicate check.

    Returns True when normalized text is identical or one text fully
    contains the other.
    """

    a = normalize_whitespace(a).lower()
    b = normalize_whitespace(b).lower()

    if a == b:
        return True

    if a in b or b in a:
        return True

    return False


def merge_texts(texts):
    """
    Consolidate multiple candidate fragments.

    Strategy:

    1. normalize;
    2. remove exact duplicates;
    3. remove texts contained inside larger texts;
    4. select the longest remaining text.

    We intentionally avoid blindly concatenating all fragments because
    overlapping page windows can duplicate sentences.
    """

    cleaned = []

    for text in texts:

        text = normalize_whitespace(text)

        if not text:
            continue

        if any(
            is_substantially_same_text(
                text,
                existing,
            )
            for existing in cleaned
        ):
            continue

        cleaned.append(text)

    if not cleaned:
        return ""

    cleaned.sort(
        key=len,
        reverse=True,
    )

    # The longest candidate is generally preferred because overlapping
    # windows tend to produce truncated and complete versions of the
    # same requirement.
    return cleaned[0]


def choose_best_title(titles):
    """
    Choose the best available title.

    Prefer the longest non-empty normalized title.
    """

    candidates = []

    for title in titles:

        title = normalize_whitespace(title)

        if title:
            candidates.append(title)

    if not candidates:
        return ""

    candidates.sort(
        key=len,
        reverse=True,
    )

    return candidates[0]


def consolidate_requirements(records):
    """
    Deterministically group all LLM results by canonical ID.
    """

    grouped = defaultdict(list)

    for record in records:

        grouped[record["id"]].append(record)

    consolidated = {}

    for requirement_id, candidates in grouped.items():

        texts = [
            candidate["text"]
            for candidate in candidates
        ]

        titles = [
            candidate["title"]
            for candidate in candidates
        ]

        source_blocks = sorted({
            candidate["source_block"]
            for candidate in candidates
        })

        source_pages = sorted({
            page
            for candidate in candidates
            for page in candidate["context_pages"]
        })

        first = candidates[0]

        consolidated[requirement_id] = {
            "id": requirement_id,
            "type": first["type"],
            "title": choose_best_title(titles),
            "text": merge_texts(texts),
            "parent_sr": first["parent_sr"],
            "foundational_requirement": first["fr"],
            "source_blocks": source_blocks,
            "source_pages": source_pages,
            "candidate_count": len(candidates),
        }

    return consolidated


# ======================================================================
# VALIDATION
# ======================================================================

def sort_requirement_id(requirement_id):
    """
    Stable sorting key for SRs and REs.
    """

    normalized = normalize_id(requirement_id)

    if " RE " in normalized:

        sr_part, re_number = normalized.split(
            " RE "
        )

        match = SR_ID_PATTERN.fullmatch(
            sr_part
        )

        return (
            int(match.group(1)),
            int(match.group(2)),
            1,
            int(re_number),
        )

    match = SR_ID_PATTERN.fullmatch(
        normalized
    )

    return (
        int(match.group(1)),
        int(match.group(2)),
        0,
        0,
    )


def validate_dataset(requirements):
    """
    Perform structural validation.
    """

    sr_ids = {
        requirement_id
        for requirement_id, item
        in requirements.items()
        if item["type"] == "SR"
    }

    re_ids = {
        requirement_id
        for requirement_id, item
        in requirements.items()
        if item["type"] == "RE"
    }

    missing_srs = sorted(
        EXPECTED_SR_IDS - sr_ids,
        key=sort_requirement_id,
    )

    unexpected_srs = sorted(
        sr_ids - EXPECTED_SR_IDS,
        key=sort_requirement_id,
    )

    orphan_res = []

    for requirement_id in re_ids:

        parent = requirements[
            requirement_id
        ]["parent_sr"]

        if parent not in sr_ids:

            orphan_res.append(
                requirement_id
            )

    empty_texts = []

    for requirement_id, item in requirements.items():

        if not normalize_whitespace(
            item.get("text", "")
        ):

            empty_texts.append(
                requirement_id
            )

    short_texts = []

    for requirement_id, item in requirements.items():

        if len(item["text"]) < 30:

            short_texts.append(
                requirement_id
            )

    return {
        "sr_count": len(sr_ids),
        "re_count": len(re_ids),
        "total_count": len(requirements),
        "missing_srs": missing_srs,
        "unexpected_srs": unexpected_srs,
        "orphan_res": sorted(
            orphan_res,
            key=sort_requirement_id,
        ),
        "empty_texts": sorted(
            empty_texts,
            key=sort_requirement_id,
        ),
        "short_texts": sorted(
            short_texts,
            key=sort_requirement_id,
        ),
    }


def print_validation(requirements, validation):

    print("\n")
    print("=" * 70)
    print("EXTRACTION VALIDATION")
    print("=" * 70)

    print(
        f"\nSRs extracted : "
        f"{validation['sr_count']}"
    )

    print(
        f"REs extracted : "
        f"{validation['re_count']}"
    )

    print(
        f"Total entries : "
        f"{validation['total_count']}"
    )

    print("\nSR completeness:")

    if validation["missing_srs"]:

        print(
            f"  ⚠️ Missing "
            f"{len(validation['missing_srs'])} SRs:"
        )

        for requirement_id in validation["missing_srs"]:
            print(
                f"     - {requirement_id}"
            )

    else:

        print(
            "  ✅ All 51 expected SRs "
            "were extracted."
        )

    if validation["unexpected_srs"]:

        print("\nUnexpected SRs:")

        for requirement_id in validation["unexpected_srs"]:
            print(
                f"  ⚠️ {requirement_id}"
            )

    print(
        "\nBy Foundational Requirement:"
    )

    for fr in range(1, 8):

        sr_count = sum(
            1
            for item in requirements.values()
            if (
                item["type"] == "SR"
                and item[
                    "foundational_requirement"
                ] == fr
            )
        )

        re_count = sum(
            1
            for item in requirements.values()
            if (
                item["type"] == "RE"
                and item[
                    "foundational_requirement"
                ] == fr
            )
        )

        expected = EXPECTED_SRS[fr]

        symbol = (
            "✅"
            if sr_count == expected
            else "⚠️"
        )

        print(
            f"  {symbol} FR {fr} - "
            f"{FR_NAMES[fr]}: "
            f"{sr_count} SRs, "
            f"{re_count} REs "
            f"(expected {expected} SRs)"
        )

    print("\nRE parent validation:")

    if validation["orphan_res"]:

        print(
            f"  ⚠️ Found "
            f"{len(validation['orphan_res'])} "
            f"REs with missing parent SRs:"
        )

        for requirement_id in validation["orphan_res"]:

            parent = get_parent_sr_id(
                requirement_id
            )

            print(
                f"     - {requirement_id} "
                f"(missing parent: {parent})"
            )

    else:

        print(
            "  ✅ All REs have valid "
            "parent SRs."
        )

    print("\nText completeness:")

    if validation["empty_texts"]:

        print(
            f"  ⚠️ Empty texts: "
            f"{len(validation['empty_texts'])}"
        )

        for requirement_id in validation["empty_texts"]:

            print(
                f"     - {requirement_id}"
            )

    else:

        print(
            "  ✅ All entries contain "
            "normative text."
        )

    print("\nShort extracted texts:")

    if validation["short_texts"]:

        for requirement_id in validation["short_texts"]:

            print(
                f"  ⚠️ {requirement_id}"
            )

    else:

        print(
            "  ✅ No suspiciously short texts."
        )


# ======================================================================
# FINAL DATASET
# ======================================================================

def build_final_dataset(requirements):
    """
    Build a clean research-oriented JSON structure.
    """

    sorted_ids = sorted(
        requirements.keys(),
        key=sort_requirement_id,
    )

    entries = []

    for requirement_id in sorted_ids:

        item = requirements[requirement_id]

        entries.append({
            "id": item["id"],
            "type": item["type"],
            "title": item["title"],
            "text": item["text"],
            "parent_sr": item["parent_sr"],
            "foundational_requirement":
                item["foundational_requirement"],
        })

    return {
        "metadata": {
            "standard": "IEC 62443-3-3",
            "extraction_method":
                "LLM-assisted page-block extraction",
            "model": MODEL_NAME,
            "generated_at": utc_timestamp(),
            "source_pdf": str(PDF_PATH),
        },
        "requirements": entries,
    }


# ======================================================================
# DEBUG EXPORT
# ======================================================================

def save_debug_data(
    blocks,
    checkpoint,
    consolidated,
):
    """
    Save detailed extraction provenance.
    """

    debug_data = {
        "metadata": {
            "generated_at": utc_timestamp(),
            "model": MODEL_NAME,
            "source_pdf": str(PDF_PATH),
        },
        "blocks": [],
        "consolidated_requirements":
            consolidated,
    }

    for block in blocks:

        block_result = checkpoint[
            "blocks"
        ].get(
            str(block["block_id"]),
            {},
        )

        debug_data["blocks"].append({
            "block_id": block["block_id"],
            "central_pages":
                block["central_pages"],
            "context_pages":
                block["context_pages"],
            "status":
                block_result.get("status"),
            "requirements":
                block_result.get(
                    "requirements",
                    [],
                ),
            "error":
                block_result.get("error"),
        })

    save_json(
        debug_data,
        DEBUG_PATH,
    )

    print(
        "\n🛠️ Debug JSON saved to:\n"
        f"   {DEBUG_PATH}"
    )


# ======================================================================
# MAIN
# ======================================================================

def main():

    ensure_output_directory()

    print(
        "\n🚀 Starting IEC 62443-3-3 "
        "LLM-assisted extraction..."
    )

    print(
        "\n📚 Source corpus:\n"
        f"   {PDF_PATH}"
    )

    # --------------------------------------------------------------
    # PDF
    # --------------------------------------------------------------

    pages = extract_pdf_pages(PDF_PATH)

    print(
        f"📄 PDF contains "
        f"{len(pages)} pages."
    )

    save_raw_extraction(pages)

    # --------------------------------------------------------------
    # BLOCKS
    # --------------------------------------------------------------

    blocks = create_blocks(pages)

    print(
        f"\n📦 Created {len(blocks)} "
        f"processing blocks."
    )

    # --------------------------------------------------------------
    # CHECKPOINT
    # --------------------------------------------------------------

    checkpoint = load_checkpoint()

    # --------------------------------------------------------------
    # PROCESS BLOCKS
    # --------------------------------------------------------------

    try:

        for index, block in enumerate(
            blocks,
            start=1,
        ):

            block_id = block["block_id"]

            if is_block_completed(
                checkpoint,
                block_id,
            ):

                print(
                    f"⏭️ Block {index}/{len(blocks)} "
                    f"(ID {block_id}) "
                    f"already completed."
                )

                continue

            print(
                f"\n📦 Processing block "
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

            result = call_gemini(block)

            checkpoint["blocks"][
                str(block_id)
            ] = result

            save_checkpoint(checkpoint)

            extracted_count = len(
                result.get(
                    "requirements",
                    [],
                )
            )

            if result["status"] == "completed":

                print(
                    f"   ✅ Block completed. "
                    f"Model returned "
                    f"{extracted_count} candidate "
                    f"requirements."
                )

            else:

                print(
                    f"   ❌ Block failed after retries."
                )

            if index < len(blocks):

                time.sleep(
                    REQUEST_DELAY_SECONDS
                )

    except KeyboardInterrupt:

        print(
            "\n\n🛑 Execution interrupted by user."
        )

        save_checkpoint(checkpoint)

        print(
            "💾 Completed blocks remain saved "
            "in the checkpoint."
        )

        print(
            "▶️ Run the script again "
            "to resume."
        )

        return

    # --------------------------------------------------------------
    # COLLECT RESULTS
    # --------------------------------------------------------------

    print(
        "\n🔄 Consolidating extracted "
        "requirements..."
    )

    all_records = []

    for block in blocks:

        result = checkpoint["blocks"].get(
            str(block["block_id"]),
            {},
        )

        if result.get("status") != "completed":
            continue

        for item in result.get(
            "requirements",
            [],
        ):

            sanitized = sanitize_requirement(
                item,
                block,
            )

            if sanitized:

                all_records.append(
                    sanitized
                )

    consolidated = consolidate_requirements(
        all_records
    )

    # --------------------------------------------------------------
    # DEBUG
    # --------------------------------------------------------------

    save_debug_data(
        blocks,
        checkpoint,
        consolidated,
    )

    save_json(
        {
            "records": all_records,
        },
        BLOCK_RESULTS_PATH,
    )

    # --------------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------------

    validation = validate_dataset(
        consolidated
    )

    print_validation(
        consolidated,
        validation,
    )

    # --------------------------------------------------------------
    # FINAL JSON
    # --------------------------------------------------------------

    final_dataset = build_final_dataset(
        consolidated
    )

    save_json(
        final_dataset,
        FINAL_JSON_PATH,
    )

    print(
        "\n💾 Final JSON saved to:\n"
        f"   {FINAL_JSON_PATH}"
    )

    # --------------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------------

    structural_problems = any([
        validation["missing_srs"],
        validation["unexpected_srs"],
        validation["orphan_res"],
        validation["empty_texts"],
    ])

    print("\n" + "=" * 70)

    if structural_problems:

        print(
            "⚠️ EXTRACTION COMPLETED, "
            "BUT STRUCTURAL VALIDATION "
            "FOUND PROBLEMS"
        )

        print(
            "\nThe JSON was saved for inspection, "
            "but should not yet be considered "
            "the final research dataset."
        )

    else:

        print(
            "✅ STRUCTURAL VALIDATION PASSED"
        )

        print(
            "\n🚀 IEC 62443-3-3 extraction "
            "completed successfully!"
        )

    print("=" * 70)


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":
    main()