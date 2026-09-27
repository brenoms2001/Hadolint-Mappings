# AGENTS.md

## Project type

This is a scientific research repository.

Preserving methodological integrity, traceability, and reproducibility takes priority over code cleanliness.

## Required reading before modifying the repository

Read, in this order:

1. `docs/methodology.md`
2. `docs/data_contracts.md`
3. `docs/decisions.md`
4. `docs/pipeline.md`
5. `REPRODUCIBILITY.md`
6. `config/*.yaml`

## Canonical matching methodology

Do not modify methodological parameters unless explicitly authorized.

Canonical values:

- embedding model: `BAAI/bge-large-en-v1.5`
- embedding dimension: 1024
- normalized embeddings: true
- similarity: cosine
- negative similarities: clamp to zero
- power transform exponent: 5.5
- normalization: L-infinity per source rule
- relative threshold: 0.68
- top-K: 10

Canonical method:

`cosine similarity -> clamp negative -> power transform -> L-infinity normalization -> threshold -> top-K`

## Gold-standard authority

Gemini is a preliminary auditor.

Gemini output is NOT the gold standard.

Human review remains authoritative for final pair labels.

Do not infer the gold standard from Gemini `YES` / `MAYBE` / `NO`.

## Security relevance

Security relevance is an auxiliary rule-level analysis.

The current LLM-assisted classification is preliminary and must not:

- filter candidate associations;
- alter thresholding or ranking;
- modify candidate generation;
- determine human pair labels;
- be presented as author-validated unless an independent human validation has been completed.

## Research artifacts

A file does not need to be imported by another Python module to be scientifically relevant.

Before deleting, moving, or replacing a research artifact:

1. determine which stage generated it;
2. determine whether another stage consumes it;
3. determine whether it is necessary for reproducibility or auditability;
4. check whether it is referenced by documentation, scripts, or paper notes.

If uncertain, do not delete it. Mark it for manual review.

## Methodological inconsistencies

Do not silently repair anything that can change scientific results.

Report it as:

`METHODOLOGICAL REVIEW REQUIRED`

Include:
- affected file(s);
- observed behavior;
- documented expected behavior;
- likely impact.

## Secrets

Never commit:
- API keys;
- tokens;
- credentials;
- `.env`;
- machine-specific secrets.

Use `.env.example` for documentation only.

## Refactoring

Repository cleanup and scientific-method changes are separate tasks.

During cleanup:
- preserve scientific behavior;
- prefer moves over rewrites;
- update paths carefully;
- verify outputs after changes.

Do not commit automatically unless explicitly instructed.
