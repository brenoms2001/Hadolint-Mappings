# AGENTS.md

## Project

This repository implements research on semantic mapping between
Hadolint/ShellCheck static-analysis rules and IEC 62443-3-3
security requirements.

## Dataset

Source rules:
- 75 Hadolint
- 519 ShellCheck
- 594 total

IEC:
- 100 requirements
- 51 SR
- 49 RE

## Canonical matching configuration

- Embedding model: BAAI/bge-large-en-v1.5
- Embedding dimension: 1024
- Similarity: cosine
- Negative similarity: clamped to 0
- Power transform: 5.5
- Normalization: L-infinity per source rule
- Relative threshold: 0.68
- Top-K: 10

Do not change these values without explicit authorization.

## Gemini audit

Gemini is a preliminary auditor.

Gemini results are NOT the gold standard.

Human review remains authoritative for final labels.

Do not infer the gold standard from Gemini YES/MAYBE/NO.

## Security relevance

Security relevance is an auxiliary rule-level analysis.

It must not modify candidate generation or the canonical matching pipeline.

## Reproducibility

Prefer preserving scripts and intermediate artifacts required to
reconstruct published results.

Do not delete research artifacts solely because they are not imported
by another Python module.

## Changes

Before deleting or substantially restructuring research artifacts,
inspect their references and role in the pipeline.

When uncertain, preserve the artifact and mark it for manual review.