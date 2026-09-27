# Research Pipeline

## Conceptual pipeline

```text
Source rule acquisition
        ↓
Structured Hadolint/ShellCheck dataset
        ↓
IEC 62443-3-3 extraction / enrichment and normative target dataset
        ↓
Deterministic embedding-text audit
        ↓
Embedding generation
        ↓
Cosine similarity
        ↓
Clamp negatives to zero
        ↓
Power transform (5.5)
        ↓
Per-source L-infinity normalization
        ↓
Relative threshold (0.68)
        ↓
Top-K (10)
        ↓
Canonical candidate dataset (4134 pairs)
        ↓
Gemini preliminary pair audit
        ↓
Human pair annotation
        ↓
Gold-standard analyses
```

Auxiliary branch:

```text
Historical 594-rule exploratory/development source population
        ↓
Independent LLM-assisted security-relevance classification
        ↓
security_related / non_security / uncertain
        ↓
Rule-level exploratory cross-analysis with preliminary pair audit
        ↓
Optional independent author validation
```

The auxiliary branch must not feed back into candidate generation.

## Current verified checkpoints

The checkpoints below describe historical downstream artifacts generated from
the earlier 594-rule population. Canonical source acquisition now contains 595
rules; downstream artifacts are not silently regenerated.

### Canonical embedding preparation

- tracked generator: `generate_embeddings.py`
- text audit: `data/output/embeddings/embedding_text_audit.json`
- source texts: 595
- IEC texts: 100
- exact model/tokenizer revision pinned
- definitive caches: not yet generated
- historical structured caches: preserved and not overwritten

### Candidate generation
- 594 source rules
- 4134 candidate associations
- threshold = 0.68
- top_k = 10
- power = 5.5

### Preliminary Gemini pair audit
- 4134 results
- YES = 78
- MAYBE = 481
- NO = 3575

### Preliminary security relevance
- security_related = 86
- non_security = 504
- uncertain = 4

## Repository-audit goal

The next migration task is to map real repository files to each stage above without changing scientific behavior.
