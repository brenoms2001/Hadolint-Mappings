#!/usr/bin/env python3

"""Build the canonical structured Hadolint/ShellCheck source dataset.

The extractor reads Markdown blobs directly from the two frozen Git trees.
It does not depend on the checked-out files in either nested repository.
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
import datetime as dt
import hashlib
import html
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Callable, Iterable


ROOT = Path(__file__).resolve().parent
OUTPUT_FILE = ROOT / "data/output/datasets/hadolint_rules_structured.json"
DIAGNOSTICS_FILE = (
    ROOT / "data/output/datasets/hadolint_rules_structured_diagnostics.json"
)
VALIDATION_FILE = (
    ROOT / "data/output/datasets/hadolint_rules_structured_validation.json"
)
PROVENANCE_FILE = (
    ROOT / "data/output/datasets/hadolint_rules_structured_provenance.json"
)
COMPARISON_FILE = (
    ROOT / "data/output/datasets/hadolint_rules_parser_comparison.json"
)
CURATION_FILE = ROOT / "data/input/hadolint/source_rule_curations.json"
MISSING_FIELD_REVIEW_FILE = (
    ROOT / "data/input/hadolint/missing_embedding_field_reviews.json"
)

PARSER_SPECIFICATION_VERSION = "canonical-source-parser-v1"
SOURCE_CUTOFF = "2026-09-26T23:59:59Z"
SCHEMA_FIELDS = (
    "id",
    "source",
    "title",
    "problematic_code",
    "correct_code",
    "rationale",
    "exceptions",
    "raw_markdown",
)
SEMANTIC_FIELDS = (
    "problematic_code",
    "correct_code",
    "rationale",
    "exceptions",
)
EMBEDDING_FIELDS = ("title", "problematic_code", "correct_code")
CURATABLE_FIELDS = {"title", "problematic_code", "correct_code"}
GENERIC_TITLE_HEADINGS = {
    "example",
    "examples",
    "example code",
    "optional",
    "notes",
    "references",
    "related resources",
    "see also",
}


@dataclasses.dataclass(frozen=True)
class SourceSpec:
    source: str
    url: str
    repository: Path
    ref: str
    commit: str
    tree: str
    pattern: re.Pattern[str]
    expected_manifest_count: int


SOURCE_SPECS = (
    SourceSpec(
        source="hadolint",
        url="https://github.com/hadolint/hadolint.wiki.git",
        repository=ROOT / "data/input/hadolint/wiki_hadolint_temp",
        ref="refs/heads/master",
        commit="4b16cf803e2ebb3fd1eba5ecabd6f5905c20e17b",
        tree="6ed8089e31349e226f324a5ca3127401a55b4f37",
        pattern=re.compile(r"^DL\d{4}\.md$", re.IGNORECASE),
        expected_manifest_count=75,
    ),
    SourceSpec(
        source="shellcheck",
        url="https://github.com/koalaman/shellcheck.wiki.git",
        repository=ROOT / "data/input/hadolint/wiki_shellcheck_temp",
        ref="refs/heads/master",
        commit="aca6b23fa48dd73df2d6b96d0eac43af294270a3",
        tree="f0b4dd5cea0b2ac99c48bc12d55b2893b1a77650",
        pattern=re.compile(r"^SC\d{4}\.md$", re.IGNORECASE),
        expected_manifest_count=520,
    ),
)


class ParserError(RuntimeError):
    """Fatal source or parser invariant failure."""


class CorpusValidationError(ParserError):
    """One or more frozen source blobs failed canonical parsing."""

    def __init__(self, report: dict):
        self.report = report
        failures = report["failures"]
        super().__init__(
            f"Frozen corpus validation failed with {len(failures)} fatal error(s)"
        )


@dataclasses.dataclass(frozen=True)
class Fence:
    start: int
    end: int
    marker: str
    length: int
    info: str


@dataclasses.dataclass(frozen=True)
class Heading:
    start: int
    end: int
    level: int
    label: str
    visible: str
    category: str | None
    qualified: bool


@dataclasses.dataclass(frozen=True)
class SectionOccurrence:
    category: str
    heading: Heading
    body: str | None
    fence_count: int
    fence_languages: tuple[str, ...]


@dataclasses.dataclass
class RuleDiagnostics:
    source: str
    source_id: str
    title_heading_level: int | None
    section_occurrences: dict[str, int]
    qualified_occurrences: dict[str, int]
    fence_count: int
    fence_languages: dict[str, int]
    applied_curations: list[dict]
    warnings: list[dict]


@dataclasses.dataclass
class ExtractionResult:
    rules: dict[str, dict]
    diagnostics: list[RuleDiagnostics]
    source_manifest: dict


FENCE_OPEN_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})(.*)$")
ATX_HEADING_RE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+|$)(.*)$")
SETEXT_RE = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
SECTION_BASE_RE = re.compile(
    r"^(problematic code|correct code|rationale|exceptions?)"
    r"(?=$|[\s:#(\[\-\u2013\u2014])"
)


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def run_git(repository: Path, *args: str, binary: bool = False):
    command = ["git", "-C", str(repository), *args]
    try:
        return subprocess.check_output(command, text=not binary)
    except subprocess.CalledProcessError as exc:
        raise ParserError(f"Git command failed: {' '.join(command)}") from exc


def heading_label_from_atx(content: str) -> str:
    content = re.sub(r"[ \t]+#+[ \t]*$", "", content)
    return content.strip()


def visible_heading_text(value: str) -> str:
    text = value
    text = re.sub(r"!\[([^]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"(`+)(.*?)\1", lambda match: match.group(2), text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", r"\1", text)
    text = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"\1", text)
    text = re.sub(r"~~(.*?)~~", r"\1", text)
    text = re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~])", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_heading_for_match(value: str) -> str:
    value = unicodedata.normalize("NFKC", visible_heading_text(value)).casefold()
    value = re.sub(r"[\s_-]+", " ", value)
    return value.strip()


def classify_heading(value: str) -> tuple[str | None, bool]:
    normalized = normalize_heading_for_match(value)
    match = SECTION_BASE_RE.match(normalized)
    if not match:
        return None, False

    base = match.group(1)
    category = {
        "problematic code": "problematic_code",
        "correct code": "correct_code",
        "rationale": "rationale",
        "exception": "exceptions",
        "exceptions": "exceptions",
    }[base]
    remainder = normalized[match.end():].strip()
    qualified = remainder not in {"", ":"}
    return category, qualified


def scan_fences(lines: list[str], rule_id: str) -> list[Fence]:
    fences: list[Fence] = []
    index = 0
    while index < len(lines):
        match = FENCE_OPEN_RE.match(lines[index])
        if not match:
            index += 1
            continue

        marker_run = match.group(2)
        marker = marker_run[0]
        info = match.group(3).strip()
        if marker == "`" and "`" in info:
            raise ParserError(
                f"{rule_id}:{index + 1}: ambiguous backtick fence info string"
            )

        closing = re.compile(
            rf"^ {{0,3}}{re.escape(marker)}{{{len(marker_run)},}}[ \t]*$"
        )
        end = index + 1
        while end < len(lines) and not closing.match(lines[end]):
            end += 1
        if end == len(lines):
            raise ParserError(f"{rule_id}:{index + 1}: unmatched fenced block")

        fences.append(
            Fence(
                start=index,
                end=end,
                marker=marker,
                length=len(marker_run),
                info=info,
            )
        )
        index = end + 1
    return fences


def scan_headings(lines: list[str], fences: list[Fence]) -> list[Heading]:
    fenced_lines = {
        line_number
        for fence in fences
        for line_number in range(fence.start, fence.end + 1)
    }
    headings: list[Heading] = []
    consumed: set[int] = set()

    for index, line in enumerate(lines):
        if index in fenced_lines or index in consumed:
            continue

        match = ATX_HEADING_RE.match(line)
        if match:
            label = heading_label_from_atx(match.group(2))
            if not label:
                continue
            category, qualified = classify_heading(label)
            headings.append(
                Heading(
                    start=index,
                    end=index,
                    level=len(match.group(1)),
                    label=label,
                    visible=visible_heading_text(label),
                    category=category,
                    qualified=qualified,
                )
            )
            continue

        if index + 1 >= len(lines) or index + 1 in fenced_lines:
            continue
        underline = SETEXT_RE.match(lines[index + 1])
        if not underline or not line.strip() or line.startswith("    ") or line.startswith("\t"):
            continue

        label = line.strip()
        category, qualified = classify_heading(label)
        headings.append(
            Heading(
                start=index,
                end=index + 1,
                level=1 if underline.group(1)[0] == "=" else 2,
                label=label,
                visible=visible_heading_text(label),
                category=category,
                qualified=qualified,
            )
        )
        consumed.add(index + 1)

    return sorted(headings, key=lambda heading: heading.start)


def select_title(headings: list[Heading], rule_id: str) -> Heading:
    first_section = next(
        (heading.start for heading in headings if heading.category),
        sys.maxsize,
    )
    candidates = [
        heading
        for heading in headings
        if heading.start < first_section
        and heading.category is None
        and normalize_heading_for_match(heading.visible) not in GENERIC_TITLE_HEADINGS
    ]
    h1_candidates = [heading for heading in candidates if heading.level == 1]
    if len(h1_candidates) > 1:
        lines = ", ".join(str(heading.start + 1) for heading in h1_candidates)
        raise ParserError(f"{rule_id}: ambiguous H1 title candidates at lines {lines}")
    if h1_candidates:
        return h1_candidates[0]

    h2_candidates = [heading for heading in candidates if heading.level == 2]
    if h2_candidates:
        return h2_candidates[0]
    if candidates:
        minimum_level = min(heading.level for heading in candidates)
        return next(heading for heading in candidates if heading.level == minimum_level)
    raise ParserError(f"{rule_id}: no semantic title heading found")


def trim_blank_lines(lines: list[str]) -> list[str]:
    start = 0
    end = len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


def normalize_section_body(
    lines: list[str],
    start: int,
    end: int,
    fences: list[Fence],
) -> tuple[str | None, int, tuple[str, ...]]:
    relevant_fences = [
        fence for fence in fences if start <= fence.start and fence.end < end
    ]
    fence_by_start = {fence.start: fence for fence in relevant_fences}
    chunks: list[str] = []
    prose: list[str] = []

    def flush_prose() -> None:
        nonlocal prose
        normalized = trim_blank_lines(prose)
        if normalized:
            chunks.append("\n".join(normalized))
        prose = []

    index = start
    while index < end:
        fence = fence_by_start.get(index)
        if fence is None:
            prose.append(lines[index])
            index += 1
            continue

        flush_prose()
        payload = lines[fence.start + 1:fence.end]
        if payload:
            chunks.append("\n".join(payload))
        index = fence.end + 1
    flush_prose()

    body = "\n\n".join(chunk for chunk in chunks if chunk != "") or None
    languages = tuple(
        fence.info.split(None, 1)[0]
        for fence in relevant_fences
        if fence.info
    )
    return body, len(relevant_fences), languages


def extract_occurrences(
    lines: list[str],
    headings: list[Heading],
    fences: list[Fence],
) -> list[SectionOccurrence]:
    occurrences: list[SectionOccurrence] = []
    semantic_headings = [heading for heading in headings if heading.category]

    for heading in semantic_headings:
        end = len(lines)
        for following in headings:
            if following.start <= heading.start:
                continue
            if following.category or following.level <= heading.level:
                end = following.start
                break
        body, fence_count, languages = normalize_section_body(
            lines,
            heading.end + 1,
            end,
            fences,
        )
        occurrences.append(
            SectionOccurrence(
                category=heading.category or "",
                heading=heading,
                body=body,
                fence_count=fence_count,
                fence_languages=languages,
            )
        )
    return occurrences


def aggregate_occurrences(
    occurrences: list[SectionOccurrence],
    category: str,
) -> str | None:
    selected = [item for item in occurrences if item.category == category]
    nonempty = [item for item in selected if item.body]
    if not nonempty:
        return None

    include_labels = len(selected) > 1 or any(
        item.heading.qualified for item in selected
    )
    rendered = []
    for item in nonempty:
        if include_labels:
            rendered.append(f"{item.heading.label}\n{item.body}")
        else:
            rendered.append(item.body or "")
    return "\n\n".join(rendered)


def warning(
    source: str,
    rule_id: str,
    code: str,
    field: str | None,
    line: int | None,
    message: str,
) -> dict:
    return {
        "source": source,
        "source_id": rule_id,
        "code": code,
        "field": field,
        "line": line,
        "message": message,
    }


def extract_rule_with_diagnostics(
    rule_id: str,
    source: str,
    markdown: str,
    allow_missing_title: bool = False,
) -> tuple[dict, RuleDiagnostics]:
    if source not in {"hadolint", "shellcheck"}:
        raise ParserError(f"{rule_id}: invalid source {source!r}")
    expected_prefix = "DL" if source == "hadolint" else "SC"
    if not re.fullmatch(rf"{expected_prefix}\d{{4}}", rule_id):
        raise ParserError(f"{rule_id}: ID/source prefix disagreement")

    raw_markdown = normalize_newlines(markdown)
    lines = raw_markdown.split("\n")
    fences = scan_fences(lines, rule_id)
    headings = scan_headings(lines, fences)
    try:
        title_heading = select_title(headings, rule_id)
    except ParserError as exc:
        if allow_missing_title and str(exc).endswith("no semantic title heading found"):
            title_heading = None
        else:
            raise
    occurrences = extract_occurrences(lines, headings, fences)

    fields = {
        category: aggregate_occurrences(occurrences, category)
        for category in SEMANTIC_FIELDS
    }
    warnings: list[dict] = []
    for category in ("problematic_code", "correct_code", "rationale"):
        if fields[category] is None:
            warnings.append(
                warning(
                    source,
                    rule_id,
                    "missing_semantic_field",
                    category,
                    None,
                    f"No nonempty {category} section was extracted.",
                )
            )
    for item in occurrences:
        if item.body is None:
            warnings.append(
                warning(
                    source,
                    rule_id,
                    "empty_semantic_section",
                    item.category,
                    item.heading.start + 1,
                    "Recognized semantic heading has an empty body.",
                )
            )

    counts = collections.Counter(item.category for item in occurrences)
    qualified = collections.Counter(
        item.category for item in occurrences if item.heading.qualified
    )
    languages = collections.Counter(
        language
        for item in occurrences
        for language in item.fence_languages
    )
    diagnostics = RuleDiagnostics(
        source=source,
        source_id=rule_id,
        title_heading_level=title_heading.level if title_heading else None,
        section_occurrences={field: counts[field] for field in SEMANTIC_FIELDS},
        qualified_occurrences={field: qualified[field] for field in SEMANTIC_FIELDS},
        fence_count=sum(item.fence_count for item in occurrences),
        fence_languages=dict(sorted(languages.items())),
        applied_curations=[],
        warnings=warnings,
    )
    rule = {
        "id": rule_id,
        "source": source,
        "title": title_heading.visible if title_heading else None,
        "problematic_code": fields["problematic_code"],
        "correct_code": fields["correct_code"],
        "rationale": fields["rationale"],
        "exceptions": fields["exceptions"],
        "raw_markdown": raw_markdown,
    }
    return rule, diagnostics


def extract_rule(rule_id: str, source: str, markdown: str) -> dict:
    """Public pure parser used by focused tests and downstream tooling."""
    return extract_rule_with_diagnostics(rule_id, source, markdown)[0]


def load_curations(
    path: Path = CURATION_FILE,
    source_specs: Iterable[SourceSpec] = SOURCE_SPECS,
) -> tuple[dict[tuple[str, str, str], dict], str]:
    try:
        content = path.read_bytes()
        document = json.loads(content.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ParserError(f"Invalid source-curation artifact: {path}") from exc

    if set(document) != {"schema_version", "overrides"}:
        raise ParserError("Source-curation artifact has unexpected top-level fields")
    if document["schema_version"] != 2 or not isinstance(document["overrides"], list):
        raise ParserError("Unsupported source-curation schema")

    specs = {spec.source: spec for spec in source_specs}
    required = {
        "source",
        "source_id",
        "field",
        "value",
        "reason",
        "authority",
        "frozen_source_commit",
        "allow_replace_non_null",
        "source_evidence",
        "curation_type",
        "value_sha256",
    }
    overrides = {}
    for index, entry in enumerate(document["overrides"]):
        if not isinstance(entry, dict) or set(entry) != required:
            raise ParserError(f"Curation entry {index} has an invalid field set")
        source = entry["source"]
        source_id = entry["source_id"]
        field = entry["field"]
        if source not in specs:
            raise ParserError(f"Curation entry {index} has invalid source {source!r}")
        prefix = "DL" if source == "hadolint" else "SC"
        if not isinstance(source_id, str) or not re.fullmatch(
            rf"{prefix}\d{{4}}", source_id
        ):
            raise ParserError(f"Curation entry {index} has invalid source_id")
        if field not in CURATABLE_FIELDS:
            raise ParserError(f"Curation entry {index} targets unsupported field {field!r}")
        if entry["frozen_source_commit"] != specs[source].commit:
            raise ParserError(
                f"Curation entry {index} does not match the frozen {source} commit"
            )
        if not isinstance(entry["value"], str) or not entry["value"].strip():
            raise ParserError(f"Curation entry {index} has an empty value")
        if not isinstance(entry["reason"], str) or not entry["reason"].strip():
            raise ParserError(f"Curation entry {index} has an empty reason")
        authority = entry["authority"]
        if (
            not isinstance(authority, dict)
            or set(authority) != {"name", "url"}
            or not all(isinstance(value, str) and value for value in authority.values())
        ):
            raise ParserError(f"Curation entry {index} has invalid authority provenance")
        if not isinstance(entry["allow_replace_non_null"], bool):
            raise ParserError(
                f"Curation entry {index} has invalid allow_replace_non_null"
            )
        if entry["value_sha256"] != sha256_text(entry["value"]):
            raise ParserError(f"Curation entry {index} has a value hash mismatch")
        curation_type = entry["curation_type"]
        evidence = entry["source_evidence"]
        if curation_type == "frozen_source_exact_span":
            expected_evidence_fields = {
                "path",
                "start_line",
                "end_line",
                "exact_text",
            }
            if not isinstance(evidence, dict) or set(evidence) != expected_evidence_fields:
                raise ParserError(f"Curation entry {index} has invalid source evidence")
            expected_path = f"{source_id}.md"
            if evidence["path"] != expected_path:
                raise ParserError(f"Curation entry {index} has invalid evidence path")
            start_line = evidence["start_line"]
            end_line = evidence["end_line"]
            if (
                not isinstance(start_line, int)
                or not isinstance(end_line, int)
                or start_line < 1
                or end_line < start_line
                or evidence["exact_text"] != entry["value"]
            ):
                raise ParserError(f"Curation entry {index} has invalid source span")
            markdown, _ = load_source_blob(specs[source], expected_path)
            lines = normalize_newlines(markdown).splitlines()
            if end_line > len(lines):
                raise ParserError(f"Curation entry {index} source span is out of range")
            selected_lines = "\n".join(lines[start_line - 1:end_line])
            if entry["value"] not in selected_lines:
                raise ParserError(
                    f"Curation entry {index} value is not present in its frozen source span"
                )
            if authority["url"] != specs[source].url:
                raise ParserError(
                    f"Curation entry {index} authority is not the frozen official source"
                )
        elif curation_type == "official_rule_metadata":
            if field != "title" or not isinstance(evidence, dict) or set(evidence) != {
                "location",
                "source_url",
            }:
                raise ParserError(f"Curation entry {index} has invalid metadata evidence")
            if not all(isinstance(value, str) and value for value in evidence.values()):
                raise ParserError(f"Curation entry {index} has empty metadata evidence")
        else:
            raise ParserError(f"Curation entry {index} has invalid curation_type")
        key = (source, source_id, field)
        if key in overrides:
            raise ParserError(f"Duplicate source-curation override: {key}")
        overrides[key] = entry
    return overrides, sha256_bytes(content)


def apply_curations(
    rule: dict,
    diagnostics: RuleDiagnostics,
    overrides: dict[tuple[str, str, str], dict],
    source_commit: str,
) -> set[tuple[str, str, str]]:
    applied = set()
    prefix = (rule["source"], rule["id"])
    for key in sorted(overrides):
        if key[:2] != prefix:
            continue
        entry = overrides[key]
        if entry["frozen_source_commit"] != source_commit:
            raise ParserError(f"Curation commit mismatch while applying {key}")
        field = entry["field"]
        current = rule[field]
        if current is not None and not entry["allow_replace_non_null"]:
            raise ParserError(
                f"Curation {key} would replace a non-null extracted value"
            )
        rule[field] = entry["value"]
        diagnostics.applied_curations.append(
            {
                "field": field,
                "reason": entry["reason"],
                "authority": entry["authority"],
                "frozen_source_commit": entry["frozen_source_commit"],
                "source_evidence": entry["source_evidence"],
                "curation_type": entry["curation_type"],
                "value_sha256": entry["value_sha256"],
                "replaced_non_null": current is not None,
            }
        )
        applied.add(key)
    return applied


def audit_missing_embedding_fields(
    result: ExtractionResult,
    path: Path = MISSING_FIELD_REVIEW_FILE,
) -> dict:
    try:
        content = path.read_bytes()
        document = json.loads(content.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ParserError(f"Invalid missing-field review artifact: {path}") from exc

    required_top = {
        "schema_version",
        "frozen_source_commits",
        "classifications",
        "methodological_exceptions",
        "reviews",
    }
    if set(document) != required_top or document["schema_version"] != 2:
        raise ParserError("Unsupported missing-field review schema")
    expected_commits = {spec.source: spec.commit for spec in SOURCE_SPECS}
    if document["frozen_source_commits"] != expected_commits:
        raise ParserError("Missing-field reviews do not match frozen source commits")
    if set(document["classifications"]) != {"A", "B"}:
        raise ParserError("Missing-field reviews have invalid classifications")

    reviewed = {}
    for index, review in enumerate(document["reviews"]):
        if set(review) != {"source", "source_id", "fields"}:
            raise ParserError(f"Missing-field review {index} has invalid fields")
        source = review["source"]
        source_id = review["source_id"]
        if source not in expected_commits or source_id not in result.rules:
            raise ParserError(f"Missing-field review {index} has invalid identity")
        if result.rules[source_id]["source"] != source:
            raise ParserError(f"Missing-field review {index} has source mismatch")
        if not isinstance(review["fields"], dict) or not review["fields"]:
            raise ParserError(f"Missing-field review {index} has no fields")
        for field, decision in review["fields"].items():
            if field not in {"problematic_code", "correct_code"}:
                raise ParserError(
                    f"Missing-field review {index} targets unsupported field {field}"
                )
            if set(decision) != {"classification", "evidence"}:
                raise ParserError(f"Missing-field review {index} has invalid decision")
            if decision["classification"] not in {"A", "B"}:
                raise ParserError(f"Missing-field review {index} has invalid category")
            if not isinstance(decision["evidence"], str) or not decision["evidence"]:
                raise ParserError(f"Missing-field review {index} lacks evidence")
            key = (source, source_id, field)
            if key in reviewed:
                raise ParserError(f"Duplicate missing-field review: {key}")
            reviewed[key] = decision

    applied_curations = {}
    for diagnostic in result.diagnostics:
        for curation in diagnostic.applied_curations:
            if curation["field"] not in {"problematic_code", "correct_code"}:
                continue
            key = (diagnostic.source, diagnostic.source_id, curation["field"])
            if curation["replaced_non_null"]:
                raise ParserError(f"Missing-field curation replaced a non-null value: {key}")
            applied_curations[key] = curation

    exception_fields = {
        "source",
        "source_id",
        "field",
        "policy",
        "relevant_content_exists",
        "assignment_ambiguous",
        "curation_applied",
        "retained_value",
        "reason",
        "frozen_source_commit",
        "source_location",
        "authority",
    }
    exceptions = {}
    for index, exception in enumerate(document["methodological_exceptions"]):
        if not isinstance(exception, dict) or set(exception) != exception_fields:
            raise ParserError(f"Methodological exception {index} has invalid fields")
        source = exception["source"]
        source_id = exception["source_id"]
        field = exception["field"]
        key = (source, source_id, field)
        if (
            source not in expected_commits
            or source_id not in result.rules
            or result.rules[source_id]["source"] != source
            or field not in {"problematic_code", "correct_code"}
            or exception["frozen_source_commit"] != expected_commits[source]
        ):
            raise ParserError(f"Methodological exception {index} has invalid identity")
        if (
            exception["policy"] != "retain_null_ambiguous_semantic_assignment"
            or exception["relevant_content_exists"] is not True
            or exception["assignment_ambiguous"] is not True
            or exception["curation_applied"] is not False
            or exception["retained_value"] is not None
            or not isinstance(exception["reason"], str)
            or not exception["reason"]
            or not isinstance(exception["source_location"], str)
            or not exception["source_location"]
            or not isinstance(exception["authority"], str)
            or not exception["authority"]
        ):
            raise ParserError(f"Methodological exception {index} is invalid")
        if key in exceptions:
            raise ParserError(f"Duplicate methodological exception: {key}")
        exceptions[key] = exception

    actual_missing = {
        (rule["source"], rule_id, field)
        for rule_id, rule in result.rules.items()
        for field in ("problematic_code", "correct_code")
        if rule[field] is None
    }
    originally_missing = actual_missing | set(applied_curations)
    reviewed_keys = set(reviewed)
    if originally_missing != reviewed_keys:
        missing_reviews = sorted(originally_missing - reviewed_keys)
        stale_reviews = sorted(reviewed_keys - originally_missing)
        raise ParserError(
            "Missing-field review coverage mismatch: "
            f"missing={missing_reviews}, stale={stale_reviews}"
        )

    entries = []
    used_exceptions = set()
    unresolved_category_b = []
    for source, source_id, field in sorted(reviewed):
        key = (source, source_id, field)
        decision = reviewed[(source, source_id, field)]
        value = result.rules[source_id][field]
        if decision["classification"] == "A":
            if value is not None or key in applied_curations or key in exceptions:
                raise ParserError(f"Category A missing field was not retained as null: {key}")
            resolution = "genuinely_absent_retained_null"
        elif key in applied_curations:
            if value is None or key in exceptions:
                raise ParserError(f"Invalid curated category B state: {key}")
            if applied_curations[key]["curation_type"] != "frozen_source_exact_span":
                raise ParserError(f"Category B curation is not an exact source span: {key}")
            resolution = "explicit_source_curation"
        elif key in exceptions:
            if value is not None:
                raise ParserError(f"Methodological exception did not retain null: {key}")
            used_exceptions.add(key)
            resolution = "methodological_null_exception"
        else:
            resolution = "unresolved_category_b"
            unresolved_category_b.append(key)
        entries.append(
            {
                "source": source,
                "source_id": source_id,
                "field": field,
                **decision,
                "resolution": resolution,
            }
        )
    unused_exceptions = sorted(set(exceptions) - used_exceptions)
    if unused_exceptions:
        raise ParserError(f"Unused methodological exceptions: {unused_exceptions}")
    category_b = [entry for entry in entries if entry["classification"] == "B"]
    return {
        "review_version": 2,
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256_bytes(content),
        "reviewed_missing_fields": len(entries),
        "counts_by_classification": dict(
            sorted(collections.Counter(entry["classification"] for entry in entries).items())
        ),
        "category_b_count": len(category_b),
        "counts_by_resolution": dict(
            sorted(collections.Counter(entry["resolution"] for entry in entries).items())
        ),
        "applied_source_curation_count": len(applied_curations),
        "methodological_exception_count": len(exceptions),
        "unresolved_category_b_count": len(unresolved_category_b),
        "unresolved_category_b": [
            {"source": source, "source_id": source_id, "field": field}
            for source, source_id, field in unresolved_category_b
        ],
        "category_b_ids_by_field": {
            field: sorted(
                entry["source_id"]
                for entry in category_b
                if entry["field"] == field
            )
            for field in ("problematic_code", "correct_code")
        },
        "methodological_exceptions": [
            exceptions[key] for key in sorted(exceptions)
        ],
        "publication_allowed": not unresolved_category_b,
        "entries": entries,
    }


def apply_missing_field_audit(validation: dict, audit: dict) -> dict:
    validation["missing_embedding_field_audit"] = audit
    validation["publication_allowed"] = audit["publication_allowed"]
    if not validation["publication_allowed"]:
        validation["passed"] = False
        validation["failures"].append(
            "Relevant embedding-field content is present in unrecognized source structures"
        )
    return validation


def verify_source_repository(spec: SourceSpec) -> None:
    if not spec.repository.is_dir():
        raise ParserError(f"Missing source repository: {spec.repository}")
    actual_tree = run_git(spec.repository, "rev-parse", f"{spec.commit}^{{tree}}").strip()
    if actual_tree != spec.tree:
        raise ParserError(
            f"{spec.source}: expected tree {spec.tree}, found {actual_tree}"
        )
    remote_urls = run_git(spec.repository, "remote", "get-url", "--all", "origin").splitlines()
    if spec.url not in remote_urls:
        raise ParserError(
            f"{spec.source}: official URL {spec.url} not configured as origin"
        )


def source_entries(spec: SourceSpec) -> list[dict]:
    output = run_git(spec.repository, "ls-tree", "-r", spec.commit)
    entries = []
    for line in output.splitlines():
        metadata, path = line.split("\t", 1)
        mode, object_type, blob_sha = metadata.split()
        if "/" in path or not spec.pattern.fullmatch(path):
            continue
        if mode != "100644" or object_type != "blob":
            raise ParserError(f"{spec.source}: non-regular source entry {path}")
        entries.append({"path": path, "blob_sha": blob_sha})
    entries.sort(key=lambda item: item["path"].casefold())
    if len(entries) != spec.expected_manifest_count:
        raise ParserError(
            f"{spec.source}: frozen manifest has {len(entries)} matching files; "
            f"expected {spec.expected_manifest_count}"
        )
    return entries


def load_source_blob(spec: SourceSpec, path: str) -> tuple[str, str]:
    raw = run_git(spec.repository, "show", f"{spec.commit}:{path}", binary=True)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ParserError(f"{spec.source}:{path}: invalid UTF-8") from exc
    return text, sha256_bytes(raw)


def add_unique_rule(rules: dict[str, dict], rule: dict) -> None:
    rule_id = rule["id"].upper()
    if rule_id in rules:
        raise ParserError(f"Duplicate normalized rule ID: {rule_id}")
    if rule_id != rule["id"]:
        raise ParserError(f"Rule ID is not normalized: {rule['id']}")
    rules[rule_id] = rule


def extract_all(
    source_specs: Iterable[SourceSpec] = SOURCE_SPECS,
    curation_path: Path = CURATION_FILE,
) -> ExtractionResult:
    source_specs = tuple(source_specs)
    overrides, curation_sha256 = load_curations(
        path=curation_path,
        source_specs=source_specs,
    )
    rules: dict[str, dict] = {}
    diagnostics: list[RuleDiagnostics] = []
    manifest_sources = []
    fatal_errors = []
    seen_ids = set()
    applied_overrides = set()

    for spec in source_specs:
        verify_source_repository(spec)
        entries = source_entries(spec)
        manifest_entries = []
        for entry in entries:
            path = entry["path"]
            rule_id = Path(path).stem.upper()
            markdown, byte_sha = load_source_blob(spec, path)
            manifest_entries.append(
                {
                    "path": path,
                    "rule_id": rule_id,
                    "blob_sha": entry["blob_sha"],
                    "source_bytes_sha256": byte_sha,
                    "normalized_markdown_sha256": sha256_text(
                        normalize_newlines(markdown)
                    ),
                }
            )
            if rule_id in seen_ids:
                fatal_errors.append(
                    {
                        "source": spec.source,
                        "source_id": rule_id,
                        "path": path,
                        "code": "duplicate_normalized_id",
                        "message": f"Duplicate normalized rule ID: {rule_id}",
                    }
                )
                continue
            seen_ids.add(rule_id)
            try:
                title_key = (spec.source, rule_id, "title")
                rule, rule_diagnostics = extract_rule_with_diagnostics(
                    rule_id,
                    spec.source,
                    markdown,
                    allow_missing_title=title_key in overrides,
                )
                applied_overrides.update(
                    apply_curations(
                        rule,
                        rule_diagnostics,
                        overrides,
                        spec.commit,
                    )
                )
                if not isinstance(rule["title"], str) or not rule["title"]:
                    raise ParserError(f"{rule_id}: title remains missing after curation")
                add_unique_rule(rules, rule)
                diagnostics.append(rule_diagnostics)
            except ParserError as exc:
                fatal_errors.append(
                    {
                        "source": spec.source,
                        "source_id": rule_id,
                        "path": path,
                        "code": "canonical_parse_failure",
                        "message": str(exc),
                    }
                )
        manifest_sources.append(
            {
                "source": spec.source,
                "url": spec.url,
                "ref": spec.ref,
                "commit": spec.commit,
                "tree": spec.tree,
                "observed_count": len(entries),
                "entries": manifest_entries,
            }
        )

    ordered_rules = {rule_id: rules[rule_id] for rule_id in sorted(rules)}
    diagnostics.sort(key=lambda item: (item.source, item.source_id))
    id_list_hash = sha256_text("\n".join(sorted(seen_ids)) + "\n")
    manifest = {
        "manifest_version": 1,
        "source_cutoff": SOURCE_CUTOFF,
        "sources": manifest_sources,
        "observed_counts": {
            **{
                source["source"]: source["observed_count"]
                for source in manifest_sources
            },
            "total": sum(source["observed_count"] for source in manifest_sources),
        },
        "ordered_rule_ids_sha256": id_list_hash,
        "source_curations": {
            "path": str(curation_path.relative_to(ROOT)),
            "sha256": curation_sha256,
            "configured_count": len(overrides),
            "applied_count": len(applied_overrides),
        },
    }
    unused_overrides = sorted(set(overrides) - applied_overrides)
    for source, source_id, field in unused_overrides:
        fatal_errors.append(
            {
                "source": source,
                "source_id": source_id,
                "path": str(curation_path.relative_to(ROOT)),
                "code": "unused_source_curation",
                "message": f"Unused source-curation override for {field}",
            }
        )
    if fatal_errors:
        fatal_errors.sort(
            key=lambda item: (item["source"], item["source_id"], item["code"])
        )
        raise CorpusValidationError(
            {
                "validation_version": 1,
                "parser_specification_version": PARSER_SPECIFICATION_VERSION,
                "passed": False,
                "failures": fatal_errors,
                "source_manifest": manifest,
                "source_manifest_sha256": sha256_bytes(json_bytes(manifest)),
                "successfully_parsed_rules": len(rules),
                "publication_blocked": True,
            }
        )
    return ExtractionResult(ordered_rules, diagnostics, manifest)


def validate_dataset(result: ExtractionResult) -> dict:
    failures = []
    field_coverage = {field: 0 for field in SEMANTIC_FIELDS}
    for key, rule in result.rules.items():
        if tuple(rule) != SCHEMA_FIELDS:
            failures.append(f"{key}: unexpected field order/set")
        if key != rule.get("id"):
            failures.append(f"{key}: key/id mismatch")
        if rule.get("source") not in {"hadolint", "shellcheck"}:
            failures.append(f"{key}: invalid source")
        expected_prefix = "DL" if rule.get("source") == "hadolint" else "SC"
        if not key.startswith(expected_prefix):
            failures.append(f"{key}: source prefix mismatch")
        if not isinstance(rule.get("title"), str) or not rule["title"]:
            failures.append(f"{key}: empty title")
        if not isinstance(rule.get("raw_markdown"), str):
            failures.append(f"{key}: invalid raw_markdown")
        for field in SEMANTIC_FIELDS:
            value = rule.get(field)
            if value is not None and not isinstance(value, str):
                failures.append(f"{key}: invalid {field} type")
            if value:
                field_coverage[field] += 1

    manifest_total = result.source_manifest["observed_counts"]["total"]
    if len(result.rules) != manifest_total:
        failures.append("Dataset count does not match frozen source manifest")
    if list(result.rules) != sorted(result.rules):
        failures.append("Dataset IDs are not lexically ordered")

    warnings = [
        item
        for diagnostic in result.diagnostics
        for item in diagnostic.warnings
    ]
    warnings.sort(
        key=lambda item: (
            item["source"],
            item["source_id"],
            item["line"] if item["line"] is not None else -1,
            item["code"],
            item["field"] or "",
        )
    )
    occurrence_totals = {
        field: sum(item.section_occurrences[field] for item in result.diagnostics)
        for field in SEMANTIC_FIELDS
    }
    qualified_totals = {
        field: sum(item.qualified_occurrences[field] for item in result.diagnostics)
        for field in SEMANTIC_FIELDS
    }
    repeated_rule_counts = {
        field: sum(
            item.section_occurrences[field] > 1 for item in result.diagnostics
        )
        for field in SEMANTIC_FIELDS
    }
    fence_languages = collections.Counter()
    for diagnostic in result.diagnostics:
        fence_languages.update(diagnostic.fence_languages)

    return {
        "validation_version": 1,
        "parser_specification_version": PARSER_SPECIFICATION_VERSION,
        "passed": not failures,
        "failures": failures,
        "counts": result.source_manifest["observed_counts"],
        "source_manifest_sha256": sha256_bytes(json_bytes(result.source_manifest)),
        "field_coverage": field_coverage,
        "section_occurrences": occurrence_totals,
        "qualified_occurrences": qualified_totals,
        "rules_with_repeated_sections": repeated_rule_counts,
        "fences": {
            "total": sum(item.fence_count for item in result.diagnostics),
            "language_identifiers": dict(sorted(fence_languages.items())),
        },
        "warning_count": len(warnings),
        "warning_counts_by_code": dict(
            sorted(collections.Counter(item["code"] for item in warnings).items())
        ),
        "warnings": warnings,
    }


def json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=4, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def diagnostics_document(
    result: ExtractionResult,
    missing_field_audit: dict | None = None,
) -> dict:
    document = {
        "diagnostics_version": 1,
        "parser_specification_version": PARSER_SPECIFICATION_VERSION,
        "rules": [dataclasses.asdict(item) for item in result.diagnostics],
    }
    if missing_field_audit is not None:
        document["methodological_exceptions"] = missing_field_audit[
            "methodological_exceptions"
        ]
    return document


def repository_state() -> dict:
    try:
        commit = run_git(ROOT, "rev-parse", "HEAD").strip()
        dirty = bool(run_git(ROOT, "status", "--porcelain").strip())
    except ParserError:
        commit = None
        dirty = None
    return {"commit": commit, "dirty": dirty}


def provenance_document(
    result: ExtractionResult,
    dataset_content: bytes,
    diagnostics_content: bytes,
    validation_content: bytes,
) -> dict:
    script_content = Path(__file__).read_bytes()
    return {
        "provenance_version": 1,
        "parser_specification_version": PARSER_SPECIFICATION_VERSION,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "script": {
            "path": str(Path(__file__).resolve().relative_to(ROOT)),
            "sha256": sha256_bytes(script_content),
        },
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "dependencies": "python-standard-library-only",
        },
        "repository": repository_state(),
        "source_manifest": result.source_manifest,
        "source_manifest_sha256": sha256_bytes(json_bytes(result.source_manifest)),
        "artifacts": {
            "dataset": {
                "path": str(OUTPUT_FILE.relative_to(ROOT)),
                "sha256": sha256_bytes(dataset_content),
            },
            "diagnostics": {
                "path": str(DIAGNOSTICS_FILE.relative_to(ROOT)),
                "sha256": sha256_bytes(diagnostics_content),
            },
            "validation": {
                "path": str(VALIDATION_FILE.relative_to(ROOT)),
                "sha256": sha256_bytes(validation_content),
            },
        },
    }


def normalized_whitespace(value: object) -> str:
    if value is None:
        return "null"
    return re.sub(r"\s+", " ", str(value)).strip()


def value_hash(value: object) -> str:
    return sha256_text("null" if value is None else str(value))


def load_historical_parser(git_ref: str) -> tuple[Callable, str]:
    source = run_git(ROOT, "show", f"{git_ref}:extract_hadolint_wiki.py")
    namespace = {"__name__": "historical_extract_hadolint_wiki"}
    exec(compile(source, f"{git_ref}:extract_hadolint_wiki.py", "exec"), namespace)
    parser = namespace.get("extract_rule")
    if not callable(parser):
        raise ParserError(f"{git_ref}: historical extract_rule was not found")
    return parser, sha256_text(source)


def classify_change(
    field: str,
    old_value: object,
    new_value: object,
    diagnostic: RuleDiagnostics,
) -> tuple[str, list[str]]:
    categories = []
    if field == "title":
        categories.append("title_recovery")
    if field in SEMANTIC_FIELDS and diagnostic.section_occurrences[field] > 1:
        categories.append("repeated_section_preservation")
    if field in SEMANTIC_FIELDS and diagnostic.qualified_occurrences[field] > 0:
        categories.append("section_recognition")
    if field in SEMANTIC_FIELDS and diagnostic.fence_count > 0:
        categories.append("code_fence_normalization")
    if normalized_whitespace(old_value) == normalized_whitespace(new_value):
        categories.append("whitespace_only")
    if not categories:
        categories.append("other")

    precedence = (
        "title_recovery",
        "repeated_section_preservation",
        "section_recognition",
        "code_fence_normalization",
        "whitespace_only",
        "other",
    )
    primary = next(category for category in precedence if category in categories)
    contributing = [
        category for category in precedence if category in categories and category != primary
    ]
    return primary, contributing


def historical_comparison(
    result: ExtractionResult,
    historical_ref: str,
    final_dataset_sha256: str,
    missing_field_audit: dict,
) -> dict:
    historical_parser, historical_script_sha = load_historical_parser(historical_ref)
    diagnostics_by_id = {item.source_id: item for item in result.diagnostics}
    changes = []
    historical_rules = {}
    curated_fields = {
        (diagnostic.source_id, curation["field"])
        for diagnostic in result.diagnostics
        for curation in diagnostic.applied_curations
    }
    exception_fields = {
        (exception["source_id"], exception["field"])
        for exception in missing_field_audit["methodological_exceptions"]
    }

    spec_by_source = {spec.source: spec for spec in SOURCE_SPECS}
    for rule_id, final_rule in result.rules.items():
        spec = spec_by_source[final_rule["source"]]
        markdown, _ = load_source_blob(spec, f"{rule_id}.md")
        historical_rule = historical_parser(rule_id, final_rule["source"], markdown)
        historical_rules[rule_id] = historical_rule
        for field in SCHEMA_FIELDS:
            old_value = historical_rule.get(field)
            new_value = final_rule.get(field)
            if old_value == new_value:
                continue
            category, contributing = classify_change(
                field,
                old_value,
                new_value,
                diagnostics_by_id[rule_id],
            )
            key = (rule_id, field)
            if key in curated_fields:
                change_origin = "explicit_source_curation"
            elif key in exception_fields:
                change_origin = "methodological_null_exception"
            else:
                change_origin = "parser_behavior"
            changes.append(
                {
                    "source": final_rule["source"],
                    "source_id": rule_id,
                    "field": field,
                    "historical_value_sha256": value_hash(old_value),
                    "final_value_sha256": value_hash(new_value),
                    "historical_is_null": old_value is None,
                    "final_is_null": new_value is None,
                    "change_category": category,
                    "contributing_categories": contributing,
                    "change_origin": change_origin,
                }
            )

    field_index = {field: index for index, field in enumerate(SCHEMA_FIELDS)}
    changes.sort(
        key=lambda item: (
            item["source"], item["source_id"], field_index[item["field"]]
        )
    )
    historical_content = json_bytes(
        {rule_id: historical_rules[rule_id] for rule_id in sorted(historical_rules)}
    )
    embedding_changes = [
        item for item in changes if item["field"] in EMBEDDING_FIELDS
    ]
    return {
        "metadata": {
            "report_version": 1,
            "source_cutoff": SOURCE_CUTOFF,
            "source_commits": {
                spec.source: spec.commit for spec in SOURCE_SPECS
            },
            "historical_parser_ref": historical_ref,
            "historical_parser_sha256": historical_script_sha,
            "final_parser_specification_version": PARSER_SPECIFICATION_VERSION,
            "historical_output_sha256": sha256_bytes(historical_content),
            "final_output_sha256": final_dataset_sha256,
            "changed_field_count": len(changes),
            "changed_rule_count": len({item["source_id"] for item in changes}),
            "embedding_relevant_changed_rule_count": len(
                {item["source_id"] for item in embedding_changes}
            ),
            "counts_by_field": dict(
                sorted(collections.Counter(item["field"] for item in changes).items())
            ),
            "counts_by_category": dict(
                sorted(
                    collections.Counter(
                        item["change_category"] for item in changes
                    ).items()
                )
            ),
            "counts_by_origin": dict(
                sorted(collections.Counter(item["change_origin"] for item in changes).items())
            ),
            "methodological_null_exceptions": {
                "field_count": len(exception_fields),
                "changed_field_count": sum(
                    item["change_origin"] == "methodological_null_exception"
                    for item in changes
                ),
                "fields": [
                    {"source_id": source_id, "field": field}
                    for source_id, field in sorted(exception_fields)
                ],
            },
            "changed_ids_by_embedding_field": {
                field: sorted(
                    item["source_id"]
                    for item in changes
                    if item["field"] == field
                )
                for field in EMBEDDING_FIELDS
            },
        },
        "changes": changes,
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT_FILE)
    parser.add_argument("--diagnostics", type=Path, default=DIAGNOSTICS_FILE)
    parser.add_argument("--validation", type=Path, default=VALIDATION_FILE)
    parser.add_argument("--provenance", type=Path, default=PROVENANCE_FILE)
    parser.add_argument("--comparison", type=Path, default=COMPARISON_FILE)
    parser.add_argument(
        "--historical-ref",
        default="aa054d0",
        help="Git ref used only for the one-time parser comparison artifact.",
    )
    parser.add_argument("--skip-comparison", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    try:
        result = extract_all()
    except CorpusValidationError as exc:
        atomic_write(args.validation, json_bytes(exc.report))
        raise
    validation = validate_dataset(result)
    if not validation["passed"]:
        raise ParserError("Dataset validation failed: " + "; ".join(validation["failures"]))

    missing_field_audit = audit_missing_embedding_fields(result)
    apply_missing_field_audit(validation, missing_field_audit)
    dataset_content = json_bytes(result.rules)
    diagnostics_content = json_bytes(
        diagnostics_document(result, missing_field_audit)
    )
    validation_content = json_bytes(validation)
    dataset_sha = sha256_bytes(dataset_content)

    atomic_write(args.diagnostics, diagnostics_content)
    atomic_write(args.validation, validation_content)

    provenance = provenance_document(
        result,
        dataset_content,
        diagnostics_content,
        validation_content,
    )
    provenance["artifacts"]["dataset"]["path"] = str(args.output)
    provenance["artifacts"]["diagnostics"]["path"] = str(args.diagnostics)
    provenance["artifacts"]["validation"]["path"] = str(args.validation)
    provenance["publication"] = {
        "allowed": validation["publication_allowed"],
        "dataset_written": validation["publication_allowed"],
        "candidate_dataset_sha256": dataset_sha,
    }
    provenance["missing_embedding_field_review"] = {
        "path": missing_field_audit["path"],
        "sha256": missing_field_audit["sha256"],
        "reviewed_missing_fields": missing_field_audit["reviewed_missing_fields"],
        "applied_source_curation_count": missing_field_audit[
            "applied_source_curation_count"
        ],
        "methodological_exception_count": missing_field_audit[
            "methodological_exception_count"
        ],
        "unresolved_category_b_count": missing_field_audit[
            "unresolved_category_b_count"
        ],
        "methodological_exceptions": missing_field_audit[
            "methodological_exceptions"
        ],
    }
    atomic_write(args.provenance, json_bytes(provenance))

    if not args.skip_comparison:
        comparison = historical_comparison(
            result,
            args.historical_ref,
            dataset_sha,
            missing_field_audit,
        )
        atomic_write(args.comparison, json_bytes(comparison))

    if not validation["publication_allowed"]:
        raise ParserError(
            "Dataset publication blocked by category B missing-field reviews"
        )

    atomic_write(args.output, dataset_content)

    print(f"Source rules: {len(result.rules)}")
    print(f"Warnings: {validation['warning_count']}")
    print(f"Dataset SHA-256: {dataset_sha}")


if __name__ == "__main__":
    try:
        main()
    except ParserError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
