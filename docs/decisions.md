# Methodological Decisions

This file records decisions that agents must not silently reinterpret.

## D001 — Gemini pair audit is preliminary

Gemini evaluates candidate associations before human review.

Its verdicts are not gold-standard labels.

Human review remains authoritative.

## D002 — Security relevance is independent

The security-relevance classification is a rule-level auxiliary analysis.

It does not alter the canonical matching pipeline.

## D003 — Do not filter non-security rules

Rules classified as `non_security` remain part of the candidate universe and research analysis.

Security relevance is not a candidate-generation filter.

## D004 — Human pair labels

Human pair annotation uses:

- `relevant`
- `partially_relevant`
- `irrelevant`

Human confidence uses a 1–5 scale.

Notes are optional.

## D005 — Security-relevance human validation is a separate task

If security relevance is validated by an author, it should be treated separately from pair-level gold-standard annotation.

Prefer an independent review in which the human reviewer does not see the Gemini security-relevance label before deciding, to reduce anchoring.

## D006 — Preliminary security labels must be named honestly

Until human validation is completed, paper text and artifacts should identify the classification as LLM-assisted or preliminary.

Avoid wording that presents the 86/504/4 split as an author-established ground truth.

## D007 — Candidate generation remains canonical

Do not change:

- embedding model
- cosine similarity
- negative clamp
- exponent 5.5
- per-source L-infinity normalization
- threshold 0.68
- top-K 10

without explicit methodological authorization.

## D008 — Preserve full Gemini results

Even if human review is prioritized using Gemini results, the complete preliminary audit should be preserved for analysis.

## D009 — Human labels do not automatically transfer across matching configurations

Human judgments apply to the candidate associations/configuration actually reviewed.

Changing matching methodology may require a new validation decision.

## D010 — Research cleanup must not rewrite history

Old or intermediate artifacts may be important for traceability.

A cleanup agent must distinguish:
- redundant temporary files;
- superseded but historically relevant artifacts;
- canonical artifacts.

Uncertainty means preserve and request manual review.

## D011 — Canonical source curation and SC2039 null exception

The definitive frozen source population is 75 Hadolint rules plus 520
ShellCheck rules, for 595 total. Counts of 594 remain valid only when explicitly
describing historical exploratory/development artifacts.

The canonical parser is structurally complete and must remain rule-ID agnostic.
Exact source-derived curations may populate `title`, `problematic_code`, or
`correct_code` only through the external curation artifact with frozen-source
span and hash provenance. Synthesized content is prohibited.

`SC2039.problematic_code` and `SC2039.correct_code` remain null as approved
methodological exceptions because the source does not define an unambiguous
semantic split. These exceptions are not category A and do not block
publication once explicitly validated.

## D012 — Canonical embedding executable and representation

`generate_embedding.ipynb` remains historical evidence. The tracked canonical
executable is `generate_embeddings.py`.

The source representation preserves the notebook's exact component order,
labels, two-newline separators, falsy-field omission, and final stripping. It
excludes rationale, exceptions, and raw Markdown. The IEC representation uses
only ID, title, and normative text and excludes rationale.

The canonical model and tokenizer revision is
`d4aa6901d3a41ba39fb536a557fa166f842b0e09`. Definitive embeddings must not be
treated as generated until an authorized CUDA run creates caches and complete
metadata sidecars from the frozen inputs.
