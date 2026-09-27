# Canonical Embedding Generation

## Status

The tracked canonical implementation is `generate_embeddings.py`.

The definitive 595-rule source and 100-requirement IEC embeddings have not yet
been generated. Generation requires a separately authorized CUDA/Colab run.

`generate_embedding.ipynb` is preserved as historical evidence. Its retained
execution generated a 594-rule source cache and a 100-requirement IEC cache; it
must not be treated as the executable source of truth for the new canonical
run.

## Recovered Historical Behavior

The historical notebook used:

- model: `BAAI/bge-large-en-v1.5`;
- device: `cuda` with a retained Tesla T4 execution;
- batch size: 64;
- `normalize_embeddings=True`;
- `convert_to_numpy=True`;
- source input order: JSON object serialization order;
- IEC input order: `requirements` list order;
- pickle structure: top-level `metadata` and ID-indexed `embeddings`;
- pickle protocol: Python default, which was protocol 4;
- source output: `cache_hadolint_structured.pkl`;
- IEC output: `cache_iec_structured.pkl`.

The current historical cache vectors are `float32[1024]`, so the canonical
generator requires float32 output.

The historical source loader preserved JSON object order, filled a falsy
embedded ID from the object key, and did not reject a truthy key/ID mismatch.
The IEC loader preserved list order. Later generation skipped non-object,
missing-ID, or empty-text entries and rejected duplicate accepted IDs. The
canonical loader retains the same text and ordering semantics but fails instead
of skipping malformed records and enforces the documented source key/ID match.

Historical cache structure was:

```text
metadata:
  dataset
  model
  dimension
  normalized
  representation
  source_file
  entry_count
embeddings:
  <ID>: <NumPy float32 vector>
```

The canonical cache preserves these top-level keys and ID-indexed vectors while
adding complete deterministic metadata. The adjacent sidecar adds runtime,
timestamp, Git, and final cache-hash provenance that cannot be self-recorded in
the pickle.

The notebook did not pin a model revision, package versions in code, or cache
hashes. Its saved package-install output records SentenceTransformers 6.0.1,
Transformers 5.16.1, and PyTorch 2.11.0+cu128. These historical execution
versions are now captured separately in `requirements-embeddings.txt` rather
than silently using the repository's general runtime dependency versions.
Definitive sidecars record the versions actually used.

## Exact Text Grammar

Text-builder version: `historical-structured-v1`.

Source components are evaluated in this order:

1. `id`;
2. `title`;
3. `"Problematic code:\n" + problematic_code`;
4. `"Correct code:\n" + correct_code`.

Falsy components, including null code fields, are omitted entirely. Components
are joined with exactly `"\n\n"`, then `.strip()` is applied to the complete
text. `source`, `rationale`, `exceptions`, and `raw_markdown` are excluded.

IEC components are evaluated in this order:

1. `id`;
2. `title`;
3. normative `text`.

The same falsy-component omission, `"\n\n"` separator, and final `.strip()`
apply. IEC rationale and rationale source pages are excluded.

Record order preserves the validated dataset serialization order. The audit
records the resulting ordered-ID-list hashes.

## Canonical Inputs

Source:

- path: `data/output/datasets/hadolint_rules_structured.json`;
- SHA-256: `708cb58293a9d081f492c1010830f6cf96b040db9d767545cc211f6c6eee37ea`;
- records: 595.

Normative IEC input:

- path: `data/output/datasets/iec62443_clean.json`;
- SHA-256: `fa44e0af3598b58bae7e6dd8057479234bd8c97cd0d9f3effee34f244c007a4c`;
- requirements: 100.

Enriched IEC verification input:

- path: `data/output/datasets/iec62443_with_rationale.json`;
- SHA-256: `33e222b4b57bb321933e113634510c19dabf2a1b5e32cc892d6455e48e2c0bdf`.

The clean and enriched files have identical ordered `id`, `title`, and
normative `text` values for all 100 requirements. The historical notebook read
the enriched file, but excluded rationale; therefore the current clean input
constructs identical IEC embedding texts.

## Model Pin

- repository: `BAAI/bge-large-en-v1.5`;
- model revision: `d4aa6901d3a41ba39fb536a557fa166f842b0e09`;
- tokenizer revision: `d4aa6901d3a41ba39fb536a557fa166f842b0e09`;
- expected dimension: 1024;
- normalized: true.

The revision is the repository SHA returned by the Hugging Face model API.
Tokenizer files are stored in the same repository and are pinned by the same
revision.

## Audit Command

This command does not load the model or write a cache:

```bash
python generate_embeddings.py audit
```

Output:

`data/output/embeddings/embedding_text_audit.json`

The audit contains each ordered ID and the SHA-256 of its exact UTF-8 embedding
text, dataset hashes, text-builder specifications and hashes, null statistics,
duplicate-text counts, and clean/enriched IEC parity.

## Authorized Colab Procedure

1. Commit the generator, tests, audit, configuration, and documentation. Push
   that exact commit to a repository accessible from Colab.
2. In a CUDA Colab runtime, clone the repository and check out that immutable
   commit. Confirm `git status --porcelain` is empty before generation.
3. Verify the source and IEC input hashes against the values above.
4. Install the embedding environment with
   `pip install -r requirements-embeddings.txt`. Verify that the CUDA-enabled
   PyTorch wheel is active; the historical run reported `2.11.0+cu128`.
5. Run `python generate_embeddings.py audit` and verify the transferred audit
   artifact is byte-identical to the repository version.
6. Confirm the historical cache files are absent from the fresh clone or have
   been separately preserved. The generator refuses to overwrite caches unless
   `--overwrite` is explicitly supplied.
7. Run:

```bash
python generate_embeddings.py generate --device cuda --batch-size 64
```

8. Verify both sidecars report 1024 dimensions, float32, normalized vectors,
   595 source vectors, 100 IEC vectors, the pinned model/tokenizer revision,
   input hashes, ordered-ID hashes, cache hashes, the checked-out Git commit,
   and a clean tree.
9. Copy back these artifacts without renaming:

```text
data/output/embeddings/cache_hadolint_structured.pkl
data/output/embeddings/cache_hadolint_structured.metadata.json
data/output/embeddings/cache_iec_structured.pkl
data/output/embeddings/cache_iec_structured.metadata.json
data/output/embeddings/embedding_text_audit.json
```

10. After transfer, recompute both cache SHA-256 values and require exact
    agreement with `output_cache_sha256` in their sidecars. Also verify the
    sidecar and audit hashes recorded for the Colab run before beginning any
    matching stage.

No Google Drive path is required or embedded in the canonical generator.

## Historical Cache Protection

Existing files are historical and were not overwritten during preparation:

- source cache SHA-256:
  `cdb4d2ad68b33e3bb1e3b3709812061355d0507f9dabd5c140b228031844734f`;
- IEC cache SHA-256:
  `e47753dec6f3b19eb8370fc9708062cb2eb40a9c90d8a12dce48130c2e91bbc9`.

The source cache contains 594 vectors and is not canonical for the finalized
595-rule source population.
