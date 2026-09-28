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
Canonical candidate dataset (4149 pairs)
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

Canonical matching and candidate generation now use the definitive 595-rule
population. Existing LLM, sample, annotation, concentration, and quality
artifacts remain historical outputs from the earlier 594-rule population and
were not silently regenerated.

### Canonical embedding preparation

- tracked generator: `generate_embeddings.py`
- text audit: `data/output/embeddings/embedding_text_audit.json`
- source texts: 595
- IEC texts: 100
- exact model/tokenizer revision pinned
- definitive caches: generated, validated, and hash-frozen
- source vectors: 595 float32[1024]
- IEC vectors: 100 float32[1024]

### Candidate generation
- 595 source rules
- 4149 candidate associations
- Hadolint associations: 566
- ShellCheck associations: 3583
- SR associations: 2240
- RE associations: 1909
- zero-candidate source rules: 0
- threshold = 0.68
- top_k = 10
- power = 5.5

### Historical preliminary Gemini pair audit
- source population: 594 rules
- 4134 results
- YES = 78
- MAYBE = 481
- NO = 3575

### Preliminary security relevance
- security_related = 86
- non_security = 504
- uncertain = 4

No LLM audit or human annotation has been run for the definitive 4149-pair
candidate set.

### Canonical preliminary pair-audit preparation

- status: execution-ready; Gemini not yet called
- executable: `audit_gold_standard_gemini.py`
- executable config: `config/gemini_pair_audit.yaml`
- frozen prompt: `prompts/gemini_pair_audit_v3.txt`
- ordered pair manifest: 4149 unique canonical pair IDs
- ordered batch manifest: 830 batches, comprising 829 batches of 5 and one of 4
- historical 4134-pair results and checkpoints: rejected for canonical resume
- output namespace: isolated under `gemini_audit/canonical/`
