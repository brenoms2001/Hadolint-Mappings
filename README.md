# Hadolint/ShellCheck → IEC 62443-3-3 semantic mapping

Research repository on the semantic mapping between container
static-analysis security rules (75 Hadolint + 520 ShellCheck = 595)
and the 100 requirements of IEC 62443-3-3 (51 SR + 49 RE).

## Pipeline

```
source input (IEC PDF, Hadolint/ShellCheck wikis, CWE XML)
  -> rich datasets (SR/RE extraction + rationale enrichment + audit)
  -> embeddings (BAAI/bge-large-en-v1.5, 1024-d, normalized)
  -> similarity matching (cosine -> clamp negative -> power 5.5
                          -> L-infinity per source rule -> threshold 0.68
                          -> top-K 10)
  -> canonical unreviewed candidates (4 149 associations)
  -> optional preliminary Gemini audit (not yet run for canonical candidates)
  -> human review (authoritative)
  -> auxiliary analyses (match quality, concentration,
                        security relevance rule-level)
```

## Canonical matching configuration

- Embedding model: `BAAI/bge-large-en-v1.5`, dimension 1024
- Similarity: cosine; negative similarity clamped to 0
- Power transform: 5.5
- Normalization: L-infinity per source rule
- Relative threshold: 0.68
- Deterministic secondary ordering: frozen IEC dataset order
- Top-K: 10

The retained 594-rule/4,134-pair outputs and their Gemini analyses are
historical development artifacts, not the definitive canonical candidate set.

These values are fixed; do not change them without explicit
authorization. See `AGENTS.md`.

## Repository layout

- Scripts at the root (production, analysis, validation and a few
  diagnostic helpers).
- `data/input/` — raw sources (IEC PDF, wiki clones, CWE XML).
- `data/output/datasets/` — clean and enriched datasets, extraction
  artifacts.
- `data/output/embeddings/` — precomputed embedding caches (`.pkl`).
- `data/output/mappings/` — matching results; canonical research
  outputs are versioned, intermediates are gitignored.
- `notebooks/` — original (historical) cleaning/embedding pipeline.

## Key scripts

| Script | Role |
|---|---|
| `extract_hadolint_wiki.py` | extracts structured Hadolint/ShellCheck rules from the wikis |
| `iec_cleaning.py` | LLM-assisted SR/RE extraction from the IEC PDF |
| `iec_extract_rationale.py` | rationale enrichment of the IEC requirements |
| `iec_audit.py` | validates `iec62443_clean.json` |
| `inspect_iec_matches.py` | canonical matching (0.68 / top-K 10 / power 5.5) |
| `build_gold_standard.py` | builds `iec_gold_standard_candidates.json` |
| `sample_gold_standard.py` | samples rules for human review |
| `audit_gold_standard_gemini.py` | Gemini preliminary audit of candidates |
| `annotate_gold_standard.py` | human review tool (final authority) |
| `audit_security_relevance_gemini.py` / `analyze_security_relevance_rule_level.py` | auxiliary security relevance analysis |

Scripts are run from the repository root.

## Requirements

```
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

Gemini API access is required for the extraction and audit steps;
the key is read from the `GEMINI_API_KEY` environment variable.
Never commit API keys.

## Gold standard authority

Gemini is a preliminary auditor only. Human review remains the
authoritative source for final gold standard labels.
