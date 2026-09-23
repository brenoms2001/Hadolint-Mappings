import csv
import hashlib
import json
import os
import time
from collections import Counter
from pathlib import Path

from google import genai
from google.genai import types
from openpyxl import Workbook
from openpyxl.utils import get_column_letter


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path("data")

INPUT_PATH = (
    BASE_DIR
    / "output/mappings/iec/inspection/gold_standard/"
    / "iec_gold_standard_candidates.json"
)

HADOLINT_DATASET_PATH = (
    BASE_DIR
    / "output/datasets/hadolint_rules_structured.json"
)

IEC_DATASET_PATH = (
    BASE_DIR
    / "output/datasets/iec62443_with_rationale.json"
)

OUTPUT_DIR = (
    BASE_DIR
    / "output/mappings/iec/inspection/gold_standard/"
    / "gemini_audit"
    / "full"
)

OUTPUT_JSON = (
    OUTPUT_DIR
    / "iec_gold_standard_gemini_audit.json"
)

OUTPUT_CSV = (
    OUTPUT_DIR
    / "iec_gold_standard_gemini_audit.csv"
)

OUTPUT_XLSX = (
    OUTPUT_DIR
    / "iec_gold_standard_gemini_audit.xlsx"
)

# XLSX updated after each completed batch.
# Used for inspection during a long run; the XLSX above
# remains the final artifact of the complete execution.
OUTPUT_XLSX_PROGRESS = (
    OUTPUT_DIR
    / "iec_gold_standard_gemini_audit_progress.xlsx"
)

OUTPUT_MD = (
    OUTPUT_DIR
    / "iec_gold_standard_gemini_audit.md"
)

CHECKPOINT_PATH = (
    OUTPUT_DIR
    / "iec_gold_standard_gemini_audit_checkpoint.json"
)


# ============================================================
# GEMINI
# ============================================================

MODEL_NAME = "gemini-3.1-flash-lite"

# Normal execution batch.
BATCH_SIZE = 5

TEMPERATURE = 0.0

# Maximum number of attempts for transient errors.
MAX_RETRIES = 5

# Number of attempts for semantically/structurally
# invalid responses before splitting the batch.
#
# Exemplo:
#   batch of 5 -> attempt 1 -> invalid
#              -> attempt 2 -> invalid
#              -> divide em 2 + 3
VALIDATION_RETRIES = 2

REQUEST_DELAY = 5.0
BACKOFF_BASE = 10.0

# None = todos os candidates.
MAX_PAIRS = None

PROMPT_VERSION = (
    "iec-gemini-preliminary-audit-v3-enriched-context"
)

def get_client():

    api_key = os.getenv("GEMINI_API_KEY", "")

    if not api_key:
        raise RuntimeError(
            "No Gemini API key found. "
            "Set the GEMINI_API_KEY environment variable."
        )

    return genai.Client(
        api_key=api_key
    )


# ============================================================
# UTILITIES
# ============================================================

def sha256_file(path: Path) -> str:
    """Computes the SHA-256 of the file."""

    digest = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def load_json(path: Path):
    """Carrega JSON."""

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def save_json(path: Path, data):
    """Salva JSON formatado."""

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


def safe_text(value):
    """Converts arbitrary values to safe text."""

    if value is None:
        return ""

    if isinstance(value, str):
        return value

    return str(value)


def _safe_excel_value(value):
    """
    Excel does not directly accept lists/dicts in cells.

    Complex structures are serialized as JSON.
    """

    if value is None:
        return ""

    if isinstance(
        value,
        (list, dict),
    ):
        return json.dumps(
            value,
            ensure_ascii=False,
        )

    return value


def chunked(items, size):
    """Splits a list into batches."""

    for i in range(
        0,
        len(items),
        size,
    ):
        yield items[i:i + size]


def make_pair_id(
    source,
    source_id,
    rank,
    target_id,
):
    """Stable identifier of an association."""

    return (
        f"{source}:"
        f"{source_id}:"
        f"rank_{rank}:"
        f"{target_id}"
    )


def classify_gap(gap):
    """
    Descriptive-only classification of the gap.

    It does not participate in candidate generation nor modifies
    the original matching.
    """

    if gap is None:
        return None

    if gap >= 0.20:
        return "high_gap"

    if gap >= 0.10:
        return "medium_gap"

    if gap >= 0.05:
        return "low_gap"

    return "very_low_gap"


# ============================================================
# INPUT
# ============================================================

def validate_input(data):
    """
    Accepts:

    1. sample format:
       metadata + records

    2. full format:
       metadata + sources
    """

    if not isinstance(
        data,
        dict,
    ):
        raise ValueError(
            "Input must be a JSON object."
        )

    if "metadata" not in data:
        raise ValueError(
            "Input has no 'metadata'."
        )

    if not isinstance(
        data["metadata"],
        dict,
    ):
        raise ValueError(
            "'metadata' must be an object."
        )

    has_records = "records" in data
    has_sources = "sources" in data

    if not has_records and not has_sources:
        raise ValueError(
            "Input must contain either "
            "'records' or 'sources'."
        )

    if has_records:
        if not isinstance(
            data["records"],
            list,
        ):
            raise ValueError(
                "'records' must be a list."
            )

    if has_sources:

        if not isinstance(
            data["sources"],
            dict,
        ):
            raise ValueError(
                "'sources' must be an object."
            )

        for source, source_rules in data[
            "sources"
        ].items():

            if not isinstance(
                source_rules,
                dict,
            ):
                raise ValueError(
                    f"Input source '{source}' "
                    "must contain an object."
                )

    return True


def load_input():
    """Loads and validates the input file."""

    print(
        f"Loading: {INPUT_PATH}"
    )

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: "
            f"{INPUT_PATH}"
        )

    data = load_json(
        INPUT_PATH
    )

    validate_input(
        data
    )

    return data


# ============================================================
# DATASETS
# ============================================================

def build_hadolint_rule_index(dataset):
    """
    Builds:

        (source, rule_id) -> source rule

    The current dataset is keyed by rule ID.
    """

    if not isinstance(
        dataset,
        dict,
    ):
        raise ValueError(
            "Hadolint dataset must be "
            "a dictionary keyed by rule ID."
        )

    index = {}

    for rule_id, rule in dataset.items():

        if not isinstance(
            rule,
            dict,
        ):
            continue

        source = rule.get(
            "source",
            "hadolint",
        )

        index[
            (source, rule_id)
        ] = rule

        # Explicit fallback.
        index[
            ("hadolint", rule_id)
        ] = rule

    return index


def build_iec_requirement_index(dataset):
    """
    Builds:

        target_id -> IEC requirement
    """

    requirements = dataset.get(
        "requirements"
    )

    if not isinstance(
        requirements,
        list,
    ):
        raise ValueError(
            "IEC dataset must contain "
            "a 'requirements' list."
        )

    index = {}

    for requirement in requirements:

        if not isinstance(
            requirement,
            dict,
        ):
            continue

        target_id = requirement.get(
            "id"
        )

        if target_id:
            index[
                target_id
            ] = requirement

    return index


def load_datasets():

    print(
        "Loading Hadolint dataset: "
        f"{HADOLINT_DATASET_PATH}"
    )

    hadolint_data = load_json(
        HADOLINT_DATASET_PATH
    )

    print(
        "Loading IEC dataset: "
        f"{IEC_DATASET_PATH}"
    )

    iec_data = load_json(
        IEC_DATASET_PATH
    )

    hadolint_index = (
        build_hadolint_rule_index(
            hadolint_data
        )
    )

    iec_index = (
        build_iec_requirement_index(
            iec_data
        )
    )

    print(
        "Hadolint rules indexed: "
        f"{len(hadolint_index)}"
    )

    print(
        "IEC requirements indexed: "
        f"{len(iec_index)}"
    )

    return (
        hadolint_index,
        iec_index,
    )


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_record(
    record,
    hadolint_index,
    iec_index,
    rule_matches=None,
):
    """
    Normalizes an individual candidate.

    Existing data in the candidate takes priority.
    Enriched datasets are used as a fallback.
    """

    source = (
        record.get("source")
        or record.get("source_type")
        or ""
    )

    source_id = (
        record.get("source_id")
        or record.get("rule_id")
        or ""
    )

    source_rule = record.get(
        "source_rule"
    )

    if not isinstance(
        source_rule,
        dict,
    ):
        source_rule = {}

    indexed_rule = hadolint_index.get(
        (
            source,
            source_id,
        )
    )

    if (
        indexed_rule is None
        and source == "hadolint"
    ):
        indexed_rule = hadolint_index.get(
            (
                "hadolint",
                source_id,
            )
        )

    if not isinstance(
        indexed_rule,
        dict,
    ):
        indexed_rule = {}

    merged_source_rule = {
        **indexed_rule,
        **source_rule,
    }

    rank = record.get(
        "rank"
    )

    target_id = record.get(
        "target_id"
    )

    target = iec_index.get(
        target_id,
        {},
    )

    target_type = (
        record.get("target_type")
        or target.get("type")
    )

    parent_sr = (
        record.get("parent_sr")
        if "parent_sr" in record
        else target.get("parent_sr")
    )

    foundational_requirement = (
        record.get(
            "foundational_requirement"
        )
        if "foundational_requirement"
        in record
        else target.get(
            "foundational_requirement"
        )
    )

    target_title = (
        record.get("target_title")
        or target.get("title")
    )

    target_text = (
        record.get("target_text")
        or target.get("text")
    )

    target_rationale = target.get(
        "rationale"
    )

    rationale_source_pages = target.get(
        "rationale_source_pages"
    )

    # --------------------------------------------------------
    # Gap
    # --------------------------------------------------------

    top1_relative_score = record.get(
        "top1_relative_score"
    )

    top2_relative_score = record.get(
        "top2_relative_score"
    )

    top1_top2_gap = record.get(
        "top1_top2_gap"
    )

    gap_bin = record.get(
        "gap_bin"
    )

    if rule_matches:

        sorted_matches = sorted(
            rule_matches,
            key=lambda x: (
                x.get(
                    "rank",
                    999999,
                ),
                -(
                    x.get(
                        "relative_score"
                    )
                    or 0.0
                ),
            ),
        )

        scores = [
            match.get(
                "relative_score"
            )
            for match in sorted_matches
            if match.get(
                "relative_score"
            )
            is not None
        ]

        if (
            top1_relative_score is None
            and scores
        ):
            top1_relative_score = (
                scores[0]
            )

        if (
            top2_relative_score is None
            and len(scores) >= 2
        ):
            top2_relative_score = (
                scores[1]
            )

        if (
            top1_top2_gap is None
            and top1_relative_score
            is not None
            and top2_relative_score
            is not None
        ):
            top1_top2_gap = (
                top1_relative_score
                - top2_relative_score
            )

        if (
            gap_bin is None
            and top1_top2_gap is not None
        ):
            gap_bin = classify_gap(
                top1_top2_gap
            )

    pair_id = make_pair_id(
        source=source,
        source_id=source_id,
        rank=rank,
        target_id=target_id,
    )

    return {
        "pair_id": pair_id,

        "source": source,
        "source_id": source_id,

        "source_title": (
            merged_source_rule.get(
                "title"
            )
        ),

        "problematic_code": (
            merged_source_rule.get(
                "problematic_code"
            )
        ),

        "correct_code": (
            merged_source_rule.get(
                "correct_code"
            )
        ),

        "rationale": (
            merged_source_rule.get(
                "rationale"
            )
        ),

        "exceptions": (
            merged_source_rule.get(
                "exceptions"
            )
        ),

        "raw_markdown": (
            merged_source_rule.get(
                "raw_markdown"
            )
        ),

        "rank": rank,

        "target_id": target_id,
        "target_type": target_type,
        "parent_sr": parent_sr,

        "foundational_requirement": (
            foundational_requirement
        ),

        "target_title": target_title,
        "target_text": target_text,

        "target_rationale": (
            target_rationale
        ),

        "rationale_source_pages": (
            rationale_source_pages
        ),

        "raw_cosine": record.get(
            "raw_cosine"
        ),

        "relative_score": record.get(
            "relative_score"
        ),

        "top1_relative_score": (
            top1_relative_score
        ),

        "top2_relative_score": (
            top2_relative_score
        ),

        "top1_top2_gap": (
            top1_top2_gap
        ),

        "gap_bin": gap_bin,

        "target_rationale_available": bool(
            target_rationale
        ),

        "human_label": record.get(
            "human_label"
        ),

        "human_confidence": record.get(
            "human_confidence"
        ),

        "human_notes": record.get(
            "human_notes"
        ),
    }


# ============================================================
# BUILD RECORDS
# ============================================================

def build_records(
    input_data,
    hadolint_index,
    iec_index,
):
    """
    Converts sample or full candidates into a flat list.
    """

    normalized_records = []

    # --------------------------------------------------------
    # Sample
    # --------------------------------------------------------

    if "records" in input_data:

        print(
            "Input format detected: "
            "records/sample"
        )

        for record in input_data[
            "records"
        ]:

            normalized = normalize_record(
                record,
                hadolint_index,
                iec_index,
            )

            normalized_records.append(
                normalized
            )

    # --------------------------------------------------------
    # Full candidates
    # --------------------------------------------------------

    elif "sources" in input_data:

        print(
            "Input format detected: "
            "full candidates"
        )

        sources = input_data[
            "sources"
        ]

        for source, source_rules in (
            sources.items()
        ):

            for source_id, rule_data in (
                source_rules.items()
            ):

                if not isinstance(
                    rule_data,
                    dict,
                ):
                    continue

                source_rule = (
                    rule_data.get(
                        "source_rule",
                        {},
                    )
                )

                matches = (
                    rule_data.get(
                        "matches",
                        [],
                    )
                )

                if not isinstance(
                    matches,
                    list,
                ):
                    continue

                for match in matches:

                    if not isinstance(
                        match,
                        dict,
                    ):
                        continue

                    raw_record = {
                        **match,

                        "source": (
                            source_rule.get(
                                "source"
                            )
                            or source
                        ),

                        "source_id": (
                            source_rule.get(
                                "id"
                            )
                            or source_id
                        ),

                        "source_rule": (
                            source_rule
                        ),
                    }

                    normalized = (
                        normalize_record(
                            raw_record,
                            hadolint_index,
                            iec_index,
                            rule_matches=matches,
                        )
                    )

                    normalized_records.append(
                        normalized
                    )

    else:
        raise ValueError(
            "Unsupported input format."
        )

    # --------------------------------------------------------
    # Deduplicate
    # --------------------------------------------------------

    deduplicated = {}

    for record in normalized_records:

        pair_id = record[
            "pair_id"
        ]

        if pair_id in deduplicated:
            continue

        deduplicated[
            pair_id
        ] = record

    records = list(
        deduplicated.values()
    )

    records.sort(
        key=lambda x: (
            x.get(
                "source",
                "",
            ),
            x.get(
                "source_id",
                "",
            ),
            x.get(
                "rank",
                999999,
            ),
            x.get(
                "target_id",
                "",
            ),
        )
    )

    return records


# ============================================================
# METADATA
# ============================================================

def experiment_metadata(
    input_data
):
    """Reproducible metadata."""

    metadata = input_data.get(
        "metadata",
        {},
    )

    return {
        "model": MODEL_NAME,

        "batch_size": BATCH_SIZE,

        "temperature": TEMPERATURE,

        "prompt_version": PROMPT_VERSION,

        "adaptive_batch_splitting": True,

        "validation_retries_before_split": (
            VALIDATION_RETRIES
        ),

        "max_retries_transient_errors": (
            MAX_RETRIES
        ),

        "input_path": str(
            INPUT_PATH
        ),

        "input_hash": sha256_file(
            INPUT_PATH
        ),

        "hadolint_dataset_path": (
            str(
                HADOLINT_DATASET_PATH
            )
        ),

        "hadolint_dataset_hash": (
            sha256_file(
                HADOLINT_DATASET_PATH
            )
        ),

        "iec_dataset_path": str(
            IEC_DATASET_PATH
        ),

        "iec_dataset_hash": (
            sha256_file(
                IEC_DATASET_PATH
            )
        ),

        "standard": metadata.get(
            "standard",
            "IEC 62443-3-3",
        ),

        "matching_threshold": (
            metadata.get(
                "threshold"
            )
        ),

        "matching_top_k": (
            metadata.get(
                "top_k"
            )
        ),

        "matching_power": (
            metadata.get(
                "power"
            )
        ),

        "matching_method": (
            metadata.get(
                "method"
            )
        ),

        "input_metadata": metadata,

        "purpose": (
            "Preliminary Gemini audit of "
            "candidate associations. "
            "Human review remains authoritative "
            "for the gold standard."
        ),

        "human_review_required": True,
    }


# ============================================================
# PROMPT
# ============================================================

def build_prompt(batch):

    payload = []

    for record in batch:

        payload.append(
            {
                "pair_id": record[
                    "pair_id"
                ],

                "source": record[
                    "source"
                ],

                "source_id": record[
                    "source_id"
                ],

                "source_title": record[
                    "source_title"
                ],

                "problematic_code": record[
                    "problematic_code"
                ],

                "correct_code": record[
                    "correct_code"
                ],

                "rationale": record[
                    "rationale"
                ],

                "exceptions": record[
                    "exceptions"
                ],

                "rank": record[
                    "rank"
                ],

                "target_id": record[
                    "target_id"
                ],

                "target_type": record[
                    "target_type"
                ],

                "parent_sr": record[
                    "parent_sr"
                ],

                "foundational_requirement": (
                    record[
                        "foundational_requirement"
                    ]
                ),

                "target_title": record[
                    "target_title"
                ],

                "target_text": record[
                    "target_text"
                ],

                "target_rationale": record[
                    "target_rationale"
                ],

                "rationale_source_pages": (
                    record[
                        "rationale_source_pages"
                    ]
                ),

                "raw_cosine": record[
                    "raw_cosine"
                ],

                "relative_score": record[
                    "relative_score"
                ],

                "top1_relative_score": (
                    record[
                        "top1_relative_score"
                    ]
                ),

                "top2_relative_score": (
                    record[
                        "top2_relative_score"
                    ]
                ),

                "top1_top2_gap": record[
                    "top1_top2_gap"
                ],

                "gap_bin": record[
                    "gap_bin"
                ],
            }
        )

    payload_json = json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""
You are performing a PRELIMINARY semantic audit of candidate
associations between static-analysis rules and IEC 62443-3-3
security requirements.

This is NOT the final gold-standard annotation.

The final gold standard must be determined by human review.
Your role is to identify whether each candidate association
appears semantically justified, partially justified, or
unsupported, so that human review can be prioritized and the
automated matching process can be analyzed.

For each candidate, evaluate the relationship between:

1. The static-analysis rule:
   - title
   - problematic code
   - correct code
   - rationale
   - exceptions

and

2. The IEC 62443-3-3 requirement:
   - type
   - title
   - requirement text
   - rationale, when available
   - foundational requirement
   - parent SR

Consider the actual security objective of the rule and the
actual security objective of the IEC requirement.

Do NOT treat lexical similarity or the embedding score as proof
of semantic equivalence.

The candidate may be:

YES:
The rule directly or strongly supports the security objective
expressed by the IEC requirement.

MAYBE:
There is a plausible or indirect relationship, but the
relationship is contextual, partial, weak, or dependent on
interpretation.

NO:
The candidate does not represent a meaningful security
relationship between the rule and the IEC requirement.

For each candidate also provide:

- relation_type
- directness
- confidence from 1 to 5
- security_objective
- concise justification
- caveat when applicable

Use exactly the supplied pair_id for each candidate.

Return one result for every supplied candidate and do not omit
or invent candidates.

Candidates:

{payload_json}
"""

    return prompt


# ============================================================
# GEMINI RESPONSE SCHEMA
# ============================================================

GEMINI_RESPONSE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "pair_id": {
                "type": "string"
            },

            "verdict": {
                "type": "string",
                "enum": [
                    "YES",
                    "MAYBE",
                    "NO",
                ],
            },

            "relation_type": {
                "type": "string"
            },

            "directness": {
                "type": "string"
            },

            "confidence": {
                "type": "integer"
            },

            "security_objective": {
                "type": "string"
            },

            "justification": {
                "type": "string"
            },

            "caveat": {
                "type": "string"
            },
        },

        "required": [
            "pair_id",
            "verdict",
            "relation_type",
            "directness",
            "confidence",
            "security_objective",
            "justification",
            "caveat",
        ],
    },
}


# ============================================================
# GEMINI ERRORS
# ============================================================

def is_transient_error(error):
    """Identifies recoverable infrastructure errors."""

    text = str(error).lower()

    transient_patterns = [
        "503",
        "service unavailable",
        "temporarily unavailable",
        "deadline exceeded",
        "timeout",
        "connection reset",
        "internal server error",
        "unavailable",
    ]

    return any(
        pattern in text
        for pattern in transient_patterns
    )


def is_quota_error(error):
    """Identifies quota/rate-limit."""

    text = str(error).lower()

    quota_patterns = [
        "429",
        "quota",
        "rate limit",
        "resource exhausted",
        "too many requests",
    ]

    return any(
        pattern in text
        for pattern in quota_patterns
    )


class GeminiBatchError(RuntimeError):
    """
    Controlled error of batch processing.

    The error keeps the original cause so the caller can
    decide whether to split the batch or interrupt the execution.
    """

    def __init__(
        self,
        message,
        original_error=None,
        error_kind=None,
    ):
        super().__init__(
            message
        )

        self.original_error = (
            original_error
        )

        self.error_kind = (
            error_kind
        )


# ============================================================
# GEMINI VALIDATION
# ============================================================

def validate_gemini_results(
    batch,
    results,
):
    """
    Validates the Gemini response against the batch.

    Failures here are treated as an invalid response.
    """

    if not isinstance(
        results,
        list,
    ):
        raise ValueError(
            "Gemini response is not a list."
        )

    expected_ids = [
        record[
            "pair_id"
        ]
        for record in batch
    ]

    returned_ids = [
        result.get(
            "pair_id"
        )
        for result in results
    ]

    expected_set = set(
        expected_ids
    )

    returned_set = set(
        returned_ids
    )

    if len(returned_ids) != len(
        returned_set
    ):
        raise ValueError(
            "Gemini returned duplicate pair_ids."
        )

    missing = (
        expected_set
        - returned_set
    )

    extra = (
        returned_set
        - expected_set
    )

    if missing:
        raise ValueError(
            "Gemini omitted pair_ids: "
            + ", ".join(
                sorted(missing)
            )
        )

    if extra:
        raise ValueError(
            "Gemini returned unexpected pair_ids: "
            + ", ".join(
                sorted(extra)
            )
        )

    valid_verdicts = {
        "YES",
        "MAYBE",
        "NO",
    }

    for result in results:

        verdict = result.get(
            "verdict"
        )

        if verdict not in valid_verdicts:
            raise ValueError(
                f"Invalid Gemini verdict: "
                f"{verdict}"
            )

        confidence = result.get(
            "confidence"
        )

        if not isinstance(
            confidence,
            int,
        ):
            raise ValueError(
                "Gemini confidence must "
                "be an integer."
            )

        if not 1 <= confidence <= 5:
            raise ValueError(
                "Gemini confidence must "
                "be between 1 and 5."
            )


# ============================================================
# GEMINI CALL
# ============================================================

def call_gemini(batch):
    """
    Runs a Gemini call for a batch.

    Strategy:

    1. Transient errors:
       up to MAX_RETRIES.

    2. Invalid/incomplete responses:
       up to VALIDATION_RETRIES.

    3. After that, raises GeminiBatchError.

    The caller decides if the batch should be split.
    """

    prompt = build_prompt(
        batch
    )

    last_error = None

    validation_attempts = 0
    transient_attempts = 0

    while True:

        try:

            response = get_client().models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=TEMPERATURE,
                    response_mime_type=(
                        "application/json"
                    ),
                    response_schema=(
                        GEMINI_RESPONSE_SCHEMA
                    ),
                ),
            )

            text = response.text

            if not text:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            results = json.loads(
                text
            )

            validate_gemini_results(
                batch,
                results,
            )

            return results

        except Exception as error:

            last_error = error

            # ------------------------------------------------
            # Quota:
            # never try to get around it by splitting.
            # ------------------------------------------------

            if is_quota_error(
                error
            ):
                raise GeminiBatchError(
                    "Gemini quota/rate-limit error.",
                    original_error=error,
                    error_kind="quota",
                ) from error

            # ------------------------------------------------
            # Transient error:
            # retry using backoff.
            # ------------------------------------------------

            if is_transient_error(
                error
            ):

                transient_attempts += 1

                if (
                    transient_attempts
                    >= MAX_RETRIES
                ):
                    raise GeminiBatchError(
                        "Gemini transient error "
                        "persisted after maximum retries.",
                        original_error=error,
                        error_kind="transient",
                    ) from error

                delay = (
                    BACKOFF_BASE
                    * (
                        2
                        ** (
                            transient_attempts - 1
                        )
                    )
                )

                print(
                    f"Gemini transient attempt "
                    f"{transient_attempts}/"
                    f"{MAX_RETRIES} failed."
                )

                print(
                    f"  {error}"
                )

                print(
                    f"Retrying same batch "
                    f"in {delay:.1f}s..."
                )

                time.sleep(
                    delay
                )

                continue

            # ------------------------------------------------
            # Invalid response:
            # limited retry.
            # ------------------------------------------------

            validation_attempts += 1

            if (
                validation_attempts
                >= VALIDATION_RETRIES
            ):
                raise GeminiBatchError(
                    "Gemini returned an invalid "
                    "or incomplete structured response "
                    "after validation retries.",
                    original_error=error,
                    error_kind="validation",
                ) from error

            delay = (
                BACKOFF_BASE
                * (
                    2
                    ** (
                        validation_attempts - 1
                    )
                )
            )

            print(
                f"Gemini validation attempt "
                f"{validation_attempts}/"
                f"{VALIDATION_RETRIES} failed."
            )

            print(
                f"  {error}"
            )

            print(
                f"Retrying same batch "
                f"in {delay:.1f}s..."
            )

            time.sleep(
                delay
            )


# ============================================================
# ADAPTIVE BATCH PROCESSING
# ============================================================

def process_batch_adaptive(
    batch,
    depth=0,
):
    """
    Processes a batch using adaptive splitting.

    Flow:

        valid batch
            -> returns results

        invalid batch after retries
            -> splits in two

        invalid singleton
            -> stops with error

    The split is an operational robustness strategy.
    It does not modify:
        - the candidates;
        - the prompt;
        - the model;
        - the temperature;
        - the schema;
        - the semantic criteria of the audit.
    """

    if not batch:
        return []

    print(
        f"  Processing adaptive batch: "
        f"{len(batch)} pair(s), "
        f"depth={depth}"
    )

    try:

        return call_gemini(
            batch
        )

    except GeminiBatchError as error:

        # ----------------------------------------------------
        # Quota:
        # do not split.
        # ----------------------------------------------------

        if error.error_kind == "quota":

            raise RuntimeError(
                "Gemini quota/rate-limit error. "
                "Stopping execution without "
                "altering the batch."
            ) from error

        # ----------------------------------------------------
        # Singleton:
        # there is no more possible split.
        # ----------------------------------------------------

        if len(batch) == 1:

            pair_id = batch[0][
                "pair_id"
            ]

            raise RuntimeError(
                "Gemini failed to process a "
                f"singleton pair after retries.\n"
                f"Pair ID: {pair_id}\n"
                f"Failure kind: {error.error_kind}\n"
                f"Original error: "
                f"{error.original_error}"
            ) from error

        # ----------------------------------------------------
        # Split the batch.
        # ----------------------------------------------------

        midpoint = len(batch) // 2

        left_batch = batch[
            :midpoint
        ]

        right_batch = batch[
            midpoint:
        ]

        print("")
        print(
            "  Adaptive batch splitting triggered."
        )

        print(
            f"  Original batch: "
            f"{len(batch)} pairs"
        )

        print(
            f"  Left batch:      "
            f"{len(left_batch)} pairs"
        )

        print(
            f"  Right batch:     "
            f"{len(right_batch)} pairs"
        )

        if error.original_error:

            print(
                f"  Reason: "
                f"{error.original_error}"
            )

        # ----------------------------------------------------
        # Process each half independently.
        # ----------------------------------------------------

        left_results = (
            process_batch_adaptive(
                left_batch,
                depth=depth + 1,
            )
        )

        right_results = (
            process_batch_adaptive(
                right_batch,
                depth=depth + 1,
            )
        )

        return (
            left_results
            + right_results
        )


# ============================================================
# MERGE
# ============================================================

def merge_result(
    record,
    gemini_result,
):
    """Combines original evidence + Gemini."""

    return {
        **record,

        "llm_model": MODEL_NAME,

        "llm_prompt_version": (
            PROMPT_VERSION
        ),

        "llm_verdict": (
            gemini_result[
                "verdict"
            ]
        ),

        "llm_relation_type": (
            gemini_result[
                "relation_type"
            ]
        ),

        "llm_directness": (
            gemini_result[
                "directness"
            ]
        ),

        "llm_confidence": (
            gemini_result[
                "confidence"
            ]
        ),

        "llm_security_objective": (
            gemini_result[
                "security_objective"
            ]
        ),

        "llm_justification": (
            gemini_result[
                "justification"
            ]
        ),

        "llm_caveat": (
            gemini_result[
                "caveat"
            ]
        ),
    }


# ============================================================
# CHECKPOINT
# ============================================================

def load_or_create_checkpoint(
    metadata,
):
    """
    Loads a checkpoint only if the configuration is identical.
    """

    if not CHECKPOINT_PATH.exists():

        return {
            "metadata": metadata,
            "results": [],
        }

    print(
        f"Loading checkpoint: "
        f"{CHECKPOINT_PATH}"
    )

    checkpoint = load_json(
        CHECKPOINT_PATH
    )

    checkpoint_metadata = (
        checkpoint.get(
            "metadata",
            {},
        )
    )

    keys_to_validate = [
        "model",
        "batch_size",
        "temperature",
        "prompt_version",
        "input_path",
        "input_hash",
        "hadolint_dataset_hash",
        "iec_dataset_hash",
        "standard",
        "matching_threshold",
        "matching_top_k",
        "matching_power",
        "matching_method",
    ]

    for key in keys_to_validate:

        checkpoint_value = (
            checkpoint_metadata.get(
                key
            )
        )

        current_value = (
            metadata.get(
                key
            )
        )

        if checkpoint_value != current_value:

            raise RuntimeError(
                "Existing checkpoint does not "
                "match current configuration "
                f"for '{key}'.\n"
                f"Checkpoint: {checkpoint_value}\n"
                f"Current:    {current_value}"
            )

    if not isinstance(
        checkpoint.get(
            "results"
        ),
        list,
    ):
        raise RuntimeError(
            "Checkpoint 'results' "
            "must be a list."
        )

    return checkpoint


def save_checkpoint(
    metadata,
    results,
):
    """Saves intermediate progress."""

    save_json(
        CHECKPOINT_PATH,
        {
            "metadata": metadata,
            "results": results,
        },
    )


# ============================================================
# JSON
# ============================================================

def save_audit_json(
    metadata,
    results,
):

    output = {
        "metadata": {
            **metadata,

            "status": "completed",

            "result_count": len(
                results
            ),

            "completed_at_unix": (
                time.time()
            ),
        },

        "results": results,
    }

    save_json(
        OUTPUT_JSON,
        output,
    )


# ============================================================
# CSV
# ============================================================

def save_csv(results):

    if not results:
        return

    fieldnames = []
    seen = set()

    for result in results:

        for key in result.keys():

            if key not in seen:

                seen.add(
                    key
                )

                fieldnames.append(
                    key
                )

    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for result in results:

            row = {}

            for key in fieldnames:

                value = result.get(
                    key
                )

                if isinstance(
                    value,
                    (list, dict),
                ):
                    value = json.dumps(
                        value,
                        ensure_ascii=False,
                    )

                row[key] = value

            writer.writerow(
                row
            )


# ============================================================
# XLSX
# ============================================================

def autosize_worksheet(ws):

    for column_cells in ws.columns:

        max_length = 0

        column_letter = (
            get_column_letter(
                column_cells[
                    0
                ].column
            )
        )

        for cell in column_cells:

            value = safe_text(
                cell.value
            )

            max_length = max(
                max_length,
                len(value),
            )

        ws.column_dimensions[
            column_letter
        ].width = min(
            max_length + 2,
            80,
        )


def save_excel(
    metadata,
    results,
    output_path=OUTPUT_XLSX,
):
    """Generates an XLSX from the current state of the audit.

    output_path keeps a progress file separate from the
    final XLSX artifact. The file is written atomically so an
    interruption during the write does not destroy the previous version.
    """

    wb = Workbook()

    # --------------------------------------------------------
    # Review
    # --------------------------------------------------------

    ws = wb.active
    ws.title = "Review"

    columns = [
        "pair_id",
        "source",
        "source_id",
        "source_title",
        "rank",
        "target_id",
        "target_type",
        "parent_sr",
        "foundational_requirement",
        "target_title",
        "target_text",
        "target_rationale",
        "rationale_source_pages",
        "problematic_code",
        "correct_code",
        "rationale",
        "exceptions",
        "raw_cosine",
        "relative_score",
        "top1_relative_score",
        "top2_relative_score",
        "top1_top2_gap",
        "gap_bin",
        "target_rationale_available",
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

    ws.append(
        columns
    )

    sorted_results = sorted(
        results,
        key=lambda x: (
            {
                "YES": 0,
                "MAYBE": 1,
                "NO": 2,
            }.get(
                x.get(
                    "llm_verdict"
                ),
                3,
            ),

            x.get(
                "source",
                "",
            ),

            x.get(
                "source_id",
                "",
            ),

            x.get(
                "rank",
                999999,
            ),
        ),
    )

    for result in sorted_results:

        ws.append(
            [
                _safe_excel_value(
                    result.get(
                        column
                    )
                )
                for column in columns
            ]
        )

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    autosize_worksheet(
        ws
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = wb.create_sheet(
        "Summary"
    )

    verdict_counts = Counter(
        result.get(
            "llm_verdict"
        )
        for result in results
    )

    source_counts = Counter(
        result.get(
            "source"
        )
        for result in results
    )

    summary.append(
        [
            "Metric",
            "Value",
        ]
    )

    summary.append(
        [
            "Total candidates",
            len(results),
        ]
    )

    summary.append(
        [
            "YES",
            verdict_counts.get(
                "YES",
                0,
            ),
        ]
    )

    summary.append(
        [
            "MAYBE",
            verdict_counts.get(
                "MAYBE",
                0,
            ),
        ]
    )

    summary.append(
        [
            "NO",
            verdict_counts.get(
                "NO",
                0,
            ),
        ]
    )

    summary.append(
        [
            "Hadolint candidates",
            source_counts.get(
                "hadolint",
                0,
            ),
        ]
    )

    summary.append(
        [
            "ShellCheck candidates",
            source_counts.get(
                "shellcheck",
                0,
            ),
        ]
    )

    summary.append(
        [
            "Human reviewed",
            sum(
                1
                for result in results
                if result.get(
                    "human_label"
                )
            ),
        ]
    )

    autosize_worksheet(
        summary
    )

    # --------------------------------------------------------
    # Disagreements
    # --------------------------------------------------------

    disagreements = wb.create_sheet(
        "Disagreements"
    )

    disagreement_columns = [
        "pair_id",
        "source",
        "source_id",
        "rank",
        "target_id",
        "target_title",
        "llm_verdict",
        "llm_confidence",
        "llm_justification",
        "human_label",
        "human_confidence",
        "human_notes",
    ]

    disagreements.append(
        disagreement_columns
    )

    for result in results:

        human_label = result.get(
            "human_label"
        )

        if not human_label:
            continue

        llm_verdict = result.get(
            "llm_verdict"
        )

        if (
            human_label
            == llm_verdict
        ):
            continue

        disagreements.append(
            [
                _safe_excel_value(
                    result.get(
                        column
                    )
                )
                for column in disagreement_columns
            ]
        )

    autosize_worksheet(
        disagreements
    )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata_ws = wb.create_sheet(
        "Metadata"
    )

    metadata_ws.append(
        [
            "Key",
            "Value",
        ]
    )

    for key, value in metadata.items():

        metadata_ws.append(
            [
                key,
                _safe_excel_value(
                    value
                ),
            ]
        )

    autosize_worksheet(
        metadata_ws
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_path = output_path.with_name(
        output_path.name + ".tmp"
    )

    try:
        wb.save(temp_path)
        os.replace(
            temp_path,
            output_path,
        )
    finally:
        if temp_path.exists():
            temp_path.unlink()


# ============================================================
# MARKDOWN
# ============================================================

def save_markdown(
    metadata,
    results,
):

    verdict_counts = Counter(
        result.get(
            "llm_verdict"
        )
        for result in results
    )

    source_counts = Counter(
        result.get(
            "source"
        )
        for result in results
    )

    human_reviewed = sum(
        1
        for result in results
        if result.get(
            "human_label"
        )
    )

    lines = []

    lines.append(
        "# IEC 62443-3-3 Gemini Preliminary Audit"
    )

    lines.append("")

    lines.append(
        "> **Important:** Gemini is used only "
        "as a preliminary auditor. Human review "
        "remains authoritative for the gold standard."
    )

    lines.append("")

    lines.append(
        "## Execution"
    )

    lines.append("")

    lines.append(
        f"- Model: `{metadata.get('model')}`"
    )

    lines.append(
        f"- Prompt version: "
        f"`{metadata.get('prompt_version')}`"
    )

    lines.append(
        f"- Batch size: "
        f"`{metadata.get('batch_size')}`"
    )

    lines.append(
        f"- Adaptive batch splitting: "
        f"`{metadata.get('adaptive_batch_splitting')}`"
    )

    lines.append(
        f"- Validation retries before split: "
        f"`{metadata.get('validation_retries_before_split')}`"
    )

    lines.append(
        f"- Input: "
        f"`{metadata.get('input_path')}`"
    )

    lines.append(
        f"- Input hash: "
        f"`{metadata.get('input_hash')}`"
    )

    lines.append(
        f"- Standard: "
        f"`{metadata.get('standard')}`"
    )

    lines.append(
        f"- Matching threshold: "
        f"`{metadata.get('matching_threshold')}`"
    )

    lines.append(
        f"- Matching Top-K: "
        f"`{metadata.get('matching_top_k')}`"
    )

    lines.append(
        f"- Matching power: "
        f"`{metadata.get('matching_power')}`"
    )

    lines.append(
        f"- Matching method: "
        f"`{metadata.get('matching_method')}`"
    )

    lines.append("")

    lines.append(
        "## Summary"
    )

    lines.append("")

    lines.append(
        f"- Total candidates: "
        f"**{len(results)}**"
    )

    lines.append(
        f"- YES: "
        f"**{verdict_counts.get('YES', 0)}**"
    )

    lines.append(
        f"- MAYBE: "
        f"**{verdict_counts.get('MAYBE', 0)}**"
    )

    lines.append(
        f"- NO: "
        f"**{verdict_counts.get('NO', 0)}**"
    )

    lines.append(
        f"- Hadolint candidates: "
        f"**{source_counts.get('hadolint', 0)}**"
    )

    lines.append(
        f"- ShellCheck candidates: "
        f"**{source_counts.get('shellcheck', 0)}**"
    )

    lines.append(
        f"- Human-reviewed candidates: "
        f"**{human_reviewed}**"
    )

    lines.append("")

    # --------------------------------------------------------
    # YES / MAYBE
    # --------------------------------------------------------

    lines.append(
        "## Preliminary YES / MAYBE"
    )

    lines.append("")

    interesting = [
        result
        for result in results
        if result.get(
            "llm_verdict"
        )
        in {
            "YES",
            "MAYBE",
        }
    ]

    if not interesting:

        lines.append(
            "No YES/MAYBE candidates."
        )

    else:

        for result in interesting:

            lines.append(
                f"### {result.get('pair_id')}"
            )

            lines.append("")

            lines.append(
                f"- Source rule: "
                f"`{result.get('source_id')}` — "
                f"{result.get('source_title')}"
            )

            lines.append(
                f"- Rank: "
                f"`{result.get('rank')}`"
            )

            lines.append(
                f"- IEC target: "
                f"`{result.get('target_id')}` — "
                f"{result.get('target_title')}"
            )

            lines.append(
                f"- Relative score: "
                f"`{result.get('relative_score')}`"
            )

            lines.append(
                f"- Gemini verdict: "
                f"**{result.get('llm_verdict')}**"
            )

            lines.append(
                f"- Confidence: "
                f"`{result.get('llm_confidence')}/5`"
            )

            lines.append(
                f"- Relation type: "
                f"`{result.get('llm_relation_type')}`"
            )

            lines.append(
                f"- Directness: "
                f"`{result.get('llm_directness')}`"
            )

            lines.append("")

            lines.append(
                f"**Security objective:** "
                f"{result.get('llm_security_objective')}"
            )

            lines.append("")

            lines.append(
                f"**Justification:** "
                f"{result.get('llm_justification')}"
            )

            caveat = result.get(
                "llm_caveat"
            )

            if caveat:

                lines.append("")

                lines.append(
                    f"**Caveat:** {caveat}"
                )

            lines.append("")

    # --------------------------------------------------------
    # Disagreements
    # --------------------------------------------------------

    lines.append(
        "## Human / Gemini Disagreements"
    )

    lines.append("")

    disagreements = [
        result
        for result in results
        if result.get(
            "human_label"
        )
        and result.get(
            "human_label"
        )
        != result.get(
            "llm_verdict"
        )
    ]

    if not disagreements:

        lines.append(
            "No human/Gemini disagreements recorded."
        )

    else:

        for result in disagreements:

            lines.append(
                f"- `{result.get('pair_id')}`: "
                f"Gemini=`{result.get('llm_verdict')}`, "
                f"Human=`{result.get('human_label')}`"
            )

    lines.append("")

    OUTPUT_MD.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


# ============================================================
# OUTPUT
# ============================================================

def print_outputs(results):

    counts = Counter(
        result.get(
            "llm_verdict"
        )
        for result in results
    )

    print("")
    print("=" * 60)
    print("GEMINI AUDIT SUMMARY")
    print("=" * 60)

    print(
        f"Total results: "
        f"{len(results)}"
    )

    print(
        f"YES:   "
        f"{counts.get('YES', 0)}"
    )

    print(
        f"MAYBE: "
        f"{counts.get('MAYBE', 0)}"
    )

    print(
        f"NO:    "
        f"{counts.get('NO', 0)}"
    )

    print("")
    print("Outputs:")

    print(
        f"  JSON: {OUTPUT_JSON}"
    )

    print(
        f"  CSV:  {OUTPUT_CSV}"
    )

    print(
        f"  XLSX final:     {OUTPUT_XLSX}"
    )

    print(
        f"  XLSX progress: {OUTPUT_XLSX_PROGRESS}"
    )

    print(
        f"  MD:   {OUTPUT_MD}"
    )

    print("")


# ============================================================
# MAIN
# ============================================================

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 60)
    print(
        "IEC 62443-3-3 GEMINI "
        "PRELIMINARY AUDIT"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # Input
    # --------------------------------------------------------

    print("")
    print(
        "Loading gold-standard candidates..."
    )

    input_data = load_input()

    print(
        "Input metadata keys: "
        f"{len(input_data.get('metadata', {}))}"
    )

    # --------------------------------------------------------
    # Datasets
    # --------------------------------------------------------

    (
        hadolint_index,
        iec_index,
    ) = load_datasets()

    # --------------------------------------------------------
    # Records
    # --------------------------------------------------------

    print("")
    print(
        "Building candidate records..."
    )

    records = build_records(
        input_data,
        hadolint_index,
        iec_index,
    )

    print(
        "Candidate records available: "
        f"{len(records)}"
    )

    if not records:
        raise RuntimeError(
            "No candidate records found."
        )

    # --------------------------------------------------------
    # Limit
    # --------------------------------------------------------

    if MAX_PAIRS is None:

        selected_records = records

    else:

        selected_records = records[
            :MAX_PAIRS
        ]

    print(
        "Pairs selected for this run: "
        f"{len(selected_records)}"
    )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata = (
        experiment_metadata(
            input_data
        )
    )

    # --------------------------------------------------------
    # Checkpoint
    # --------------------------------------------------------

    checkpoint = (
        load_or_create_checkpoint(
            metadata
        )
    )

    existing_results = (
        checkpoint.get(
            "results",
            [],
        )
    )

    results_by_id = {
        result["pair_id"]: result
        for result in existing_results
        if result.get(
            "pair_id"
        )
    }

    print(
        "Checkpoint results already available: "
        f"{len(results_by_id)}"
    )

    remaining_records = [
        record
        for record in selected_records
        if record["pair_id"]
        not in results_by_id
    ]

    print(
        "Remaining pairs to audit: "
        f"{len(remaining_records)}"
    )

    # --------------------------------------------------------
    # Batches
    # --------------------------------------------------------

    batches = list(
        chunked(
            remaining_records,
            BATCH_SIZE,
        )
    )

    total_batches = len(
        batches
    )

    print(
        "Gemini batches remaining: "
        f"{total_batches}"
    )

    # --------------------------------------------------------
    # Gemini
    # --------------------------------------------------------

    for batch_index, batch in enumerate(
        batches,
        start=1,
    ):

        print("")
        print(
            f"Batch {batch_index}/"
            f"{total_batches} "
            f"({len(batch)} pairs)"
        )

        try:

            gemini_results = (
                process_batch_adaptive(
                    batch
                )
            )

            # ------------------------------------------------
            # Additional safeguard. 
            #
            # Even if the sub-batches were processed
            # separately, the aggregated set must contain
            # exactly the IDs from the original batch.
            # ------------------------------------------------

            validate_gemini_results(
                batch,
                gemini_results,
            )

            by_id = {
                result[
                    "pair_id"
                ]: result
                for result in gemini_results
            }

            for record in batch:

                pair_id = record[
                    "pair_id"
                ]

                merged = merge_result(
                    record,
                    by_id[pair_id],
                )

                results_by_id[
                    pair_id
                ] = merged

            # ------------------------------------------------
            # Checkpoint
            # ------------------------------------------------

            checkpoint_results = list(
                results_by_id.values()
            )

            checkpoint_results.sort(
                key=lambda x: (
                    x.get(
                        "source",
                        "",
                    ),
                    x.get(
                        "source_id",
                        "",
                    ),
                    x.get(
                        "rank",
                        999999,
                    ),
                )
            )

            save_checkpoint(
                metadata,
                checkpoint_results,
            )

            # ------------------------------------------------
            # XLSX preliminar
            #
            # The checkpoint remains the recovery source
            # of the execution. This XLSX is only a readable
            # representation of the current state and is updated each batch.
            # ------------------------------------------------

            progress_metadata = dict(
                metadata
            )

            progress_metadata[
                "status"
            ] = "running"

            progress_metadata[
                "result_count"
            ] = len(
                checkpoint_results
            )

            progress_metadata[
                "completed_batches"
            ] = batch_index

            progress_metadata[
                "total_batches_at_start"
            ] = total_batches

            progress_metadata[
                "progress_percentage"
            ] = round(
                (
                    len(checkpoint_results)
                    / len(selected_records)
                    * 100
                )
                if selected_records
                else 100.0,
                2,
            )

            save_excel(
                progress_metadata,
                checkpoint_results,
                OUTPUT_XLSX_PROGRESS,
            )

            print(
                f"Batch {batch_index} completed."
            )

            print(
                "  Preliminary XLSX updated: "
                f"{OUTPUT_XLSX_PROGRESS}"
            )

        except Exception as error:

            print("")
            print(
                f"ERROR in batch "
                f"{batch_index}/"
                f"{total_batches}:"
            )

            print(
                error
            )

            print("")
            print(
                "Progress has been preserved "
                "in the checkpoint."
            )

            raise

        if (
            batch_index < total_batches
            and REQUEST_DELAY > 0
        ):

            time.sleep(
                REQUEST_DELAY
            )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    final_results = list(
        results_by_id.values()
    )

    final_results.sort(
        key=lambda x: (
            x.get(
                "source",
                "",
            ),
            x.get(
                "source_id",
                "",
            ),
            x.get(
                "rank",
                999999,
            ),
            x.get(
                "target_id",
                "",
            ),
        )
    )

    selected_ids = {
        record[
            "pair_id"
        ]
        for record in selected_records
    }

    final_results = [
        result
        for result in final_results
        if result.get(
            "pair_id"
        )
        in selected_ids
    ]

    if len(final_results) != len(
        selected_records
    ):
        raise RuntimeError(
            "Final result count does not "
            "match the number of selected "
            "candidate pairs.\n"
            f"Expected: "
            f"{len(selected_records)}\n"
            f"Found: "
            f"{len(final_results)}"
        )

    # --------------------------------------------------------
    # Outputs
    # --------------------------------------------------------

    metadata["status"] = (
        "completed"
    )

    metadata["result_count"] = (
        len(final_results)
    )

    save_audit_json(
        metadata,
        final_results,
    )

    save_csv(
        final_results
    )

    save_excel(
        metadata,
        final_results,
    )

    save_markdown(
        metadata,
        final_results,
    )

    print_outputs(
        final_results
    )


if __name__ == "__main__":
    main()