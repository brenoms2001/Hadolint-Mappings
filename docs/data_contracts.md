# Data Contracts

## `hadolint_rules_structured.json`

Canonical path:

`data/output/datasets/hadolint_rules_structured.json`

Important structural rule:

This file is a flat JSON object keyed directly by rule ID.

Correct conceptual structure:

```json
{
  "DL3002": {
    "id": "DL3002",
    "source": "hadolint",
    "...": "..."
  },
  "SC1019": {
    "id": "SC1019",
    "source": "shellcheck",
    "...": "..."
  }
}
```

Do NOT assume:

```json
{
  "hadolint": {},
  "shellcheck": {}
}
```

Relevant rule fields include:

- `id`
- `source`
- `title`
- `problematic_code`
- `correct_code`
- `rationale`
- `exceptions`

The definitive frozen population contains 595 rules: 75 Hadolint and 520
ShellCheck. Exact source curations are applied before publication through the
external provenance artifact
`data/input/hadolint/source_rule_curations.json`; they do not change the flat
dataset schema.

Any loader should verify that the dictionary key agrees with `rule["id"]`.

## `iec62443_with_rationale.json`

Canonical path:

`data/output/datasets/iec62443_with_rationale.json`

Top-level structure:

- `metadata`
- `requirements`

Requirement fields include:

- `id`
- `type`
- `title`
- `text`
- `parent_sr`
- `foundational_requirement`
- `rationale`
- `rationale_source_pages`

### Rationale availability

SR rationale data is available.

RE rationale may be null.

A null RE rationale is a data-availability condition and must not automatically be treated as malformed input.

## Canonical embedding caches

Canonical paths:

- `data/output/embeddings/cache_hadolint_structured.pkl`
- `data/output/embeddings/cache_iec_structured.pkl`

Each pickle retains the historical top-level structure of `metadata` and an
ID-indexed `embeddings` dictionary. Each definitive cache has an adjacent
`.metadata.json` sidecar containing input, text-builder, model revision,
runtime, Git, vector-validation, timestamp, and output-hash provenance.

The files at these paths are the definitive embeddings for the finalized
595-rule source population and 100-requirement IEC target population. Exact
hashes are recorded in `manifests/canonical_artifacts.json`.

## Candidate dataset

Canonical path:

`data/output/mappings/iec/inspection/gold_standard/iec_gold_standard_candidates.json`

Top-level structure:

- `metadata`
- `sources`

`metadata` includes canonical matching parameters.

`sources` contains separate Hadolint/ShellCheck mappings.

Each source-rule entry includes:

- `source_rule`
- `candidate_count`
- `matches`

Each match includes fields such as:

- `rank`
- `target_id`
- `target_type`
- `parent_sr`
- `foundational_requirement`
- `target_title`
- `target_text`
- `raw_cosine`
- `relative_score`
- `human_label`
- `human_confidence`
- `human_notes`

### `parent_sr` nuance

The IEC enrichment dataset and generated candidate artifacts may represent `parent_sr` differently for SR records.

Do not normalize or "fix" this representation without checking downstream assumptions and documenting the methodological effect.

## Human-evaluation sample

Sample format differs from the full candidate format.

Top-level keys:

- `metadata`
- `rules`
- `records`

Do not write code that assumes the sample and full candidate JSONs have identical structure.

## Gemini pair audit

The existing 4134-result pair audit belongs to the historical 594-rule
development candidate set. It is not an audit of the definitive 4149-pair
canonical candidate set.

Human fields must remain distinguishable from LLM fields.

Do not overwrite human labels with Gemini verdicts.

## Security-relevance audit

Rule-level security relevance is independent from pair-level candidate relevance.

Expected classification values:

- `security_related`
- `non_security`
- `uncertain`

Security categories:

- authentication
- authorization_access_control
- least_privilege
- secrets_credentials
- input_validation
- injection_command_execution
- information_exposure
- integrity
- availability
- secure_configuration
- dependency_supply_chain
- network_security
- other_security

Do not infer a rule's security-relevance classification from pair-level Gemini verdicts.
