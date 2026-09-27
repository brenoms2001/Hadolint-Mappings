# Reproducibility

## Objective

A new researcher or agent should be able to determine:

1. which source datasets were used;
2. which transformations were applied;
3. which configuration generated the canonical candidate set;
4. which LLM model/prompt produced each preliminary audit;
5. which outputs are canonical;
6. which labels were produced by humans;
7. which analyses are auxiliary or exploratory.

## Minimum reproducibility record

For every result-producing stage, preserve:

- input paths;
- output paths;
- script path;
- software/model version where relevant;
- configuration;
- random seed where relevant;
- prompt text and prompt version for LLM stages;
- timestamp;
- row/rule/pair counts;
- validation checks;
- git commit.

## Canonical matching configuration

See:

`config/matching.yaml`

## Canonical embedding generation

The executable implementation is `generate_embeddings.py`; the recovered text
grammar, immutable model revision, input hashes, cache contract, and Colab
procedure are documented in `docs/embedding_generation.md`.
The historical notebook execution environment is pinned separately in
`requirements-embeddings.txt`.

Before model execution, run:

```bash
python generate_embeddings.py audit
```

The deterministic audit records every ordered ID and exact embedding-text
SHA-256 without downloading or running the model. Definitive cache sidecars
must record the input and output hashes, ordered-ID hash, text-builder identity,
model/tokenizer revision, dimension, normalization, dtype, count, batch size,
device, software versions, generator hash, Git state, and UTC timestamp.

The definitive final-population embeddings have not yet been generated.

## LLM pair audit configuration

See:

`config/gemini_pair_audit.yaml`

The exact prompt text must be preserved verbatim in:

`prompts/gemini_pair_audit_v3.txt`

Do not reconstruct the prompt from memory if the original script still exists.

## Security-relevance configuration

See:

`config/security_relevance.yaml`

The exact prompt text must be preserved verbatim in:

`prompts/security_relevance_v1.txt`

## Artifact integrity

After repository migration, populate SHA-256 hashes in:

`manifests/canonical_artifacts.json`

Hashes must be computed from the actual canonical repository artifacts, not from copied or renamed conversational uploads.

## Git discipline

Before structural cleanup:

1. ensure secrets are excluded;
2. commit the research baseline;
3. create a tag such as `research-baseline-v1`;
4. perform cleanup on a separate branch;
5. compare scientific outputs before and after cleanup.
