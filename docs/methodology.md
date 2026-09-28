# Methodology

## Scope

This project studies semantic mapping between Hadolint/ShellCheck static-analysis rules and IEC 62443-3-3 security requirements.

## Source rules

The structured source dataset contains:

- 75 Hadolint rules
- 520 ShellCheck rules
- 595 source rules total

The canonical structured source dataset is:

`data/output/datasets/hadolint_rules_structured.json`

## IEC 62443-3-3 target set

The target set contains:

- 100 requirements total
- 51 SR
- 49 RE

The enriched IEC dataset is:

`data/output/datasets/iec62443_with_rationale.json`

Its metadata identifies:

- standard: IEC 62443-3-3
- extraction method: LLM-assisted page-block extraction
- model: `gemini-3.1-flash-lite`

## Embeddings

Canonical embedding model:

`BAAI/bge-large-en-v1.5`

Embedding dimension:

1024

Embeddings are normalized.

The historical `generate_embedding.ipynb` established the text-construction
methodology. The tracked canonical executable is now
`generate_embeddings.py`; exact grammar and execution instructions are in
`docs/embedding_generation.md`.

Canonical source embedding text uses, in order, `id`, `title`, labeled
`problematic_code`, and labeled `correct_code`, separated by two newlines.
Falsy fields are omitted and the final text is stripped. Rationale, exceptions,
and raw Markdown are excluded.

Canonical IEC embedding text uses `id`, `title`, and normative `text`, separated
by two newlines. IEC rationale is excluded.

The model and tokenizer are pinned to revision
`d4aa6901d3a41ba39fb536a557fa166f842b0e09`. Definitive normalized float32
embeddings have been generated and validated for all 595 source rules and all
100 IEC requirements. Their hashes are frozen in
`manifests/canonical_artifacts.json`.

## Candidate generation

For each source rule:

1. compute cosine similarity;
2. clamp negative similarities to zero;
3. apply a power transform with exponent 5.5;
4. perform per-source-rule L-infinity normalization;
5. retain candidates whose relative score is at least 0.68;
6. sort by relative score descending and then by frozen IEC dataset order;
7. retain at most the top 10 candidates.

Canonical parameters:

- `power = 5.5`
- `threshold = 0.68`
- `top_k = 10`

Canonical method string:

`cosine similarity -> clamp negative -> power transform -> L-infinity normalization -> threshold -> top-K`

## Canonical candidate set

Canonical candidate dataset:

`data/output/mappings/iec/inspection/gold_standard/iec_gold_standard_candidates.json`

Definitive canonical totals:

- source rules: 595
- candidate associations: 4149
- Hadolint associations: 566
- ShellCheck associations: 3583
- SR associations: 2240
- RE associations: 1909
- source rules with zero candidates: 0

Historical validated totals from the exploratory/development 594-rule source
population:

- source rules: 594
- candidate associations: 4134
- Hadolint associations: 529
- ShellCheck associations: 3605
- SR associations: 2214
- RE associations: 1920

The candidate file metadata records:

- threshold: 0.68
- top_k: 10
- power: 5.5
- method: canonical method string above
- source dataset: `data/output/datasets/hadolint_rules_structured.json`
- target dataset: `data/output/datasets/iec62443_clean.json`

## Human-evaluation sample

A sample dataset has been used for human-evaluation workflow development.

Its verified metadata includes:

- random seed: 42
- Hadolint rules sampled: 25
- ShellCheck rules sampled: 50
- candidate count: 531
- allowed labels:
  - `relevant`
  - `partially_relevant`
  - `irrelevant`

The sample is not a replacement for the full candidate dataset.

## Gemini preliminary pair audit

Gemini is used as a preliminary auditor of candidate associations.

It is not the gold-standard authority.

Canonical audit configuration used in the current workflow:

- model: `gemini-3.1-flash-lite`
- temperature: 0
- batch size: 5
- max retries: 5
- request delay: 5 seconds
- backoff base: 10 seconds
- validation retries: 2
- prompt version: `iec-gemini-preliminary-audit-v3-enriched-context`

Full pair-audit result count:

- total: 4134
- YES: 78
- MAYBE: 481
- NO: 3575

Human review remains authoritative.

The historical totals above describe only the 594-rule/4134-pair development
run. The canonical 595-rule/4149-pair auditor is execution-ready but has not
called Gemini. Its executable authority is `config/gemini_pair_audit.yaml`.
The exact v3 prompt is frozen at `prompts/gemini_pair_audit_v3.txt`, and the
ordered canonical pair and batch manifests are frozen under `manifests/`.

Canonical execution uses two identities: the historical rank-bearing
`prompt_pair_id` sent to Gemini and a rank-independent `canonical_pair_id` used
for provenance, checkpointing, and exact result-set validation. Canonical
outputs are isolated from `gemini_audit/full/`, which remains historical.

## Security-relevance analysis

A separate historical rule-level LLM-assisted analysis classified the earlier
594-rule exploratory/development source population as:

- `security_related`
- `non_security`
- `uncertain`

Current preliminary totals:

- security_related: 86
- non_security: 504
- uncertain: 4

This analysis is auxiliary.

It must not change candidate generation or gold-standard construction.

## Source curation and null exceptions

The canonical source parser is structurally complete and rule-ID agnostic.
Source curation is external to general parser logic.

An embedding field may be curated only when its exact UTF-8 value is present
verbatim in the pinned official source blob, its semantic role is unambiguous,
and its source span, frozen commit, authority, reason, curation type, and value
SHA-256 are recorded. Curation must not invent, summarize, rewrite, repair, or
infer content.

`SC2039.problematic_code` and `SC2039.correct_code` are approved methodological
null exceptions. Relevant material exists, but the frozen page does not define
an unambiguous split into the two canonical fields. Both values remain null to
avoid researcher-created semantic reconstruction. These acknowledged nulls do
not block source-dataset publication.

### Current exploratory rule-level findings

Within the existing 4134-candidate configuration:

- 74 of 86 security-related rules had at least one Gemini pair verdict YES/MAYBE: 86.05%
- 296 of 504 non-security rules had at least one YES/MAYBE: 58.73%
- coverage ratio: approximately 1.465
- mean positive-candidate rate:
  - security-related: 30.45%
  - non-security: 16.43%
- mean-rate ratio: approximately 1.853
- median positive-candidate rate:
  - security-related: 26.79%
  - non-security: 10.00%

These are exploratory LLM-assisted results, not independently validated human findings.

## Human authority

Pair-level human labels are:

- `relevant`
- `partially_relevant`
- `irrelevant`

Human confidence:

- integer scale 1–5

Human notes:

- optional free text

Security-relevance validation, if performed, should be treated as a separate human task from pair annotation.

## Reproducibility principle

The repository must make it possible to reconstruct:

source data
→ enrichment
→ embeddings
→ matching
→ candidate generation
→ preliminary Gemini pair audit
→ auxiliary analyses
→ human review
→ final/gold-standard analyses

Repository cleanup must not alter this scientific chain.
