#!/usr/bin/env python3

"""
Extract structured Hadolint and ShellCheck rules from their GitHub wikis.

Output:
    data/output/datasets/hadolint_rules_structured.json

The extractor preserves the semantic sections of each wiki page:

    - id
    - source
    - title
    - problematic_code
    - correct_code
    - rationale
    - exceptions
    - raw_markdown

No embedding-oriented text normalization is performed here.

The resulting JSON is intended to be the canonical source dataset for
subsequent embedding/matching experiments.
"""

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Optional


# ============================================================
# CONFIGURATION
# ============================================================

WIKI_REPOSITORIES = {
    "hadolint": {
        "url": "https://github.com/hadolint/hadolint.wiki.git",
        "path": Path("data/input/hadolint/wiki_hadolint_temp"),
        "pattern": re.compile(r"^DL\d{4}\.md$", re.IGNORECASE),
    },
    "shellcheck": {
        "url": "https://github.com/koalaman/shellcheck.wiki.git",
        "path": Path("data/input/hadolint/wiki_shellcheck_temp"),
        "pattern": re.compile(r"^SC\d{4}\.md$", re.IGNORECASE),
    },
}

OUTPUT_FILE = Path(
    "./data/output/datasets/hadolint_rules_structured.json"
)


# ============================================================
# GENERAL HELPERS
# ============================================================

def normalize_newlines(text: str) -> str:
    """Normalize Windows/Mac line endings."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def clean_section_text(text: str) -> Optional[str]:
    """
    Clean ordinary prose while preserving its semantic content.

    This function intentionally does NOT flatten everything into a single
    NLP block and does NOT remove code blocks.
    """

    if not text:
        return None

    text = normalize_newlines(text)

    # Remove excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove trailing whitespace.
    lines = [line.rstrip() for line in text.splitlines()]

    # Remove empty lines at beginning/end.
    while lines and not lines[0].strip():
        lines.pop(0)

    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        return None

    return "\n".join(lines).strip()


def clean_title(title: str) -> str:
    """
    Clean the rule title without destroying its wording.
    """

    title = title.strip()

    # Remove surrounding markdown emphasis.
    title = re.sub(r"^\*+(.*?)\*+$", r"\1", title)
    title = re.sub(r"^_+(.*?)_+$", r"\1", title)

    # Remove trailing markdown punctuation introduced by headings.
    title = title.rstrip()

    return title.strip()


# ============================================================
# MARKDOWN SECTION PARSING
# ============================================================

SECTION_NAMES = {
    "problematic_code": {
        "problematic code",
        "problematic_code",
    },
    "correct_code": {
        "correct code",
        "correct_code",
    },
    "rationale": {
        "rationale",
    },
    "exceptions": {
        "exceptions",
        "exception",
    },
}


def normalize_heading(heading: str) -> str:
    """
    Normalize a Markdown heading for section matching.
    """

    heading = heading.strip()

    # Remove Markdown heading markers.
    heading = re.sub(r"^#+\s*", "", heading)

    # Remove optional bold/italic markers.
    heading = heading.strip("*_` ")

    # Remove trailing colon.
    heading = heading.rstrip(":").strip()

    # Normalize whitespace.
    heading = re.sub(r"\s+", " ", heading)

    return heading.lower()


def classify_section_heading(heading: str) -> Optional[str]:
    """
    Map a Markdown subsection heading to our canonical field name.
    """

    normalized = normalize_heading(heading)

    for field, aliases in SECTION_NAMES.items():
        if normalized in aliases:
            return field

    return None


def extract_rule_title(lines: list[str], rule_id: str) -> str:
    """
    Extract the rule title from the first level-2 Markdown heading.

    Hadolint/ShellCheck wiki pages generally use the rule ID as the
    filename, while the page itself starts with the rule title:

        ## Use absolute WORKDIR.

        ### Problematic code:

        ...

    Therefore, the rule_id is not used to locate the title.
    """

    # The first level-2 heading is the rule title.
    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        # Match exactly a Markdown level-2 heading:
        # ## Title
        #
        # Do not match:
        # # Title
        # ### Problematic code
        match = re.match(r"^##\s+(.+?)\s*$", stripped)

        if not match:
            continue

        title = match.group(1).strip()

        # Remove inline Markdown formatting while preserving the text.
        title = re.sub(r"`([^`]*)`", r"\1", title)
        title = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", title)
        title = re.sub(r"\*\*(.*?)\*\*", r"\1", title)
        title = re.sub(r"\*(.*?)\*", r"\1", title)
        title = re.sub(r"_(.*?)_", r"\1", title)

        return clean_title(title)

    # If no level-2 heading exists, keep the ID rather than
    # accidentally assigning code or section text as the title.
    return rule_id


# ============================================================
# SECTION EXTRACTION
# ============================================================

def find_section_boundaries(lines: list[str]) -> Dict[str, tuple[int, int]]:
    """
    Find the boundaries of the semantic sections.

    We deliberately recognize only the sections that belong to the
    structured dataset. Everything else remains available through
    raw_markdown.
    """

    section_starts = []

    for index, line in enumerate(lines):
        if not line.lstrip().startswith("#"):
            continue

        field = classify_section_heading(line)

        if field:
            section_starts.append((index, field))

    boundaries = {}

    for position, (start, field) in enumerate(section_starts):
        if position + 1 < len(section_starts):
            end = section_starts[position + 1][0]
        else:
            end = len(lines)

        boundaries[field] = (start + 1, end)

    return boundaries


def extract_sections(lines: list[str]) -> Dict[str, Optional[str]]:
    """
    Extract all recognized semantic sections.
    """

    boundaries = find_section_boundaries(lines)

    result = {
        "problematic_code": None,
        "correct_code": None,
        "rationale": None,
        "exceptions": None,
    }

    for field, (start, end) in boundaries.items():
        content = "\n".join(lines[start:end])
        result[field] = clean_section_text(content)

    return result


# ============================================================
# CODE EXTRACTION / NORMALIZATION
# ============================================================

def normalize_code_section(text: Optional[str]) -> Optional[str]:
    """
    Preserve code content while removing only the surrounding Markdown
    fence.

    We do NOT remove the code itself.
    """

    if not text:
        return None

    text = normalize_newlines(text).strip()

    lines = text.splitlines()

    # Remove opening/closing fences when present.
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]

    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    return "\n".join(lines).strip() or None


# ============================================================
# RULE EXTRACTION
# ============================================================

def extract_rule(rule_id: str, source: str, markdown: str) -> dict:
    """
    Convert one wiki page into a structured rule.
    """

    markdown = normalize_newlines(markdown)
    lines = markdown.splitlines()

    title = extract_rule_title(lines, rule_id)
    sections = extract_sections(lines)

    problematic_code = normalize_code_section(
        sections["problematic_code"]
    )

    correct_code = normalize_code_section(
        sections["correct_code"]
    )

    return {
        "id": rule_id,
        "source": source,
        "title": title,
        "problematic_code": problematic_code,
        "correct_code": correct_code,
        "rationale": sections["rationale"],
        "exceptions": sections["exceptions"],
        "raw_markdown": markdown.strip(),
    }


# ============================================================
# VALIDATION
# ============================================================

def validate_rule(rule: dict) -> list[str]:
    """
    Perform lightweight structural validation.

    This does not judge semantic correctness.
    """

    warnings = []

    required_fields = [
        "id",
        "source",
        "title",
        "problematic_code",
        "correct_code",
        "rationale",
        "exceptions",
        "raw_markdown",
    ]

    for field in required_fields:
        if field not in rule:
            warnings.append(
                f"{rule['id']}: missing field '{field}'"
            )

    if not rule.get("title"):
        warnings.append(
            f"{rule['id']}: missing title"
        )

    if not rule.get("raw_markdown"):
        warnings.append(
            f"{rule['id']}: missing raw markdown"
        )

    return warnings


# ============================================================
# GIT / WIKI HANDLING
# ============================================================

def ensure_wiki(repository_name: str, config: dict) -> bool:
    """
    Clone the wiki if it does not exist locally.

    Existing repositories are reused to preserve the workflow of the
    previous extractor.
    """

    path = config["path"]

    if path.exists():
        print(
            f"   📁 Local repository found: {path}"
        )
        return True

    print(
        f"   📥 Cloning repository:\n"
        f"      {config['url']}"
    )

    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            [
                "git",
                "clone",
                config["url"],
                str(path),
            ],
            check=True,
        )

        return True

    except subprocess.CalledProcessError as exc:
        print(
            f"   ❌ Failed to clone {repository_name} wiki."
        )
        print(f"      Git exit code: {exc.returncode}")
        return False


# ============================================================
# EXTRACTION PIPELINE
# ============================================================

def extract_repository_rules(
    repository_name: str,
    config: dict,
) -> dict[str, dict]:
    """
    Extract all matching rules from one wiki repository.
    """

    if not ensure_wiki(repository_name, config):
        return {}

    path = config["path"]
    pattern = config["pattern"]

    rules = {}

    try:
        files = sorted(path.iterdir())
    except OSError as exc:
        print(
            f"   ❌ Could not read repository directory: {exc}"
        )
        return {}

    for file_path in files:

        if not file_path.is_file():
            continue

        if not pattern.match(file_path.name):
            continue

        rule_id = file_path.stem.upper()

        try:
            markdown = file_path.read_text(
                encoding="utf-8"
            )
        except UnicodeDecodeError:
            print(
                f"   ⚠️ Could not decode {file_path.name} as UTF-8."
            )
            continue
        except OSError as exc:
            print(
                f"   ⚠️ Could not read {file_path.name}: {exc}"
            )
            continue

        rule = extract_rule(
            rule_id=rule_id,
            source=repository_name,
            markdown=markdown,
        )

        rules[rule_id] = rule

    return rules


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print("=" * 70)
    print("🚀 STARTING STRUCTURED WIKI EXTRACTION")
    print("=" * 70)

    all_rules: dict[str, dict] = {}

    statistics = {
        "hadolint": 0,
        "shellcheck": 0,
    }

    validation_warnings = []

    # --------------------------------------------------------
    # Extract Hadolint and ShellCheck
    # --------------------------------------------------------

    for repository_name, config in WIKI_REPOSITORIES.items():

        print(
            f"\n📚 Processing {repository_name.upper()} Wiki..."
        )

        rules = extract_repository_rules(
            repository_name,
            config,
        )

        print(
            f"   ✅ Extracted {len(rules)} rules."
        )

        statistics[repository_name] = len(rules)

        for rule_id, rule in rules.items():

            if rule_id in all_rules:
                print(
                    f"   ⚠️ Duplicate rule ID detected: {rule_id}"
                )
                continue

            all_rules[rule_id] = rule

            validation_warnings.extend(
                validate_rule(rule)
            )

    # --------------------------------------------------------
    # Output directory
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Export
    # --------------------------------------------------------

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as output:

        json.dump(
            all_rules,
            output,
            indent=4,
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # Report
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("🎯 STRUCTURED SOURCE DATASET REPORT")
    print("=" * 70)

    print(
        f"Hadolint rules extracted : {statistics['hadolint']}"
    )

    print(
        f"ShellCheck rules extracted: {statistics['shellcheck']}"
    )

    print(
        f"Total rules              : {len(all_rules)}"
    )

    print(
        f"Generated file           : {OUTPUT_FILE}"
    )

    # --------------------------------------------------------
    # Field statistics
    # --------------------------------------------------------

    field_counts = {
        "problematic_code": 0,
        "correct_code": 0,
        "rationale": 0,
        "exceptions": 0,
    }

    for rule in all_rules.values():

        for field in field_counts:

            if rule.get(field):
                field_counts[field] += 1

    print("\n📊 FIELD COVERAGE")
    print("-" * 70)

    for field, count in field_counts.items():

        percentage = (
            (count / len(all_rules)) * 100
            if all_rules
            else 0
        )

        print(
            f"{field:20s}: "
            f"{count:4d}/{len(all_rules):4d} "
            f"({percentage:6.2f}%)"
        )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    print("\n🧪 STRUCTURAL VALIDATION")
    print("-" * 70)

    if validation_warnings:

        print(
            f"⚠️ {len(validation_warnings)} warnings found:"
        )

        for warning in validation_warnings[:30]:
            print(f"   - {warning}")

        if len(validation_warnings) > 30:
            print(
                f"   ... and "
                f"{len(validation_warnings) - 30} more."
            )

    else:
        print(
            "✅ No structural warnings."
        )

    # --------------------------------------------------------
    # Samples
    # --------------------------------------------------------

    print("\n🔎 SAMPLE STRUCTURED RULES")
    print("-" * 70)

    sample_ids = list(all_rules.keys())[:3]

    for rule_id in sample_ids:

        rule = all_rules[rule_id]

        print(
            f"\n{rule['id']} | "
            f"{rule['title']}"
        )

        print(
            f"Source: {rule['source']}"
        )

        print(
            f"Problematic code: "
            f"{'yes' if rule['problematic_code'] else 'no'}"
        )

        print(
            f"Correct code: "
            f"{'yes' if rule['correct_code'] else 'no'}"
        )

        print(
            f"Rationale: "
            f"{'yes' if rule['rationale'] else 'no'}"
        )

        print(
            f"Exceptions: "
            f"{'yes' if rule['exceptions'] else 'no'}"
        )

    print("\n" + "=" * 70)
    print(
        "✅ STRUCTURED WIKI EXTRACTION COMPLETED"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()