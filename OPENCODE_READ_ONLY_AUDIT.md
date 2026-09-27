# OpenCode — Read-Only Repository Audit Prompt

Read `AGENTS.md` and every document it requires before doing anything else.

Then inspect the entire repository and reconstruct the actual research pipeline.

## Hard constraint

DO NOT modify, move, delete, rename, reformat, or generate repository files during this task.

This is a read-only audit.

## Goals

Determine:

1. the actual pipeline implemented in the repository;
2. which scripts belong to each pipeline stage;
3. canonical inputs and outputs;
4. intermediate artifacts required for reproducibility;
5. duplicate or obsolete-looking artifacts;
6. checkpoint, debug, temporary, and machine-specific files;
7. files that should not be committed;
8. inconsistencies between code and the documented canonical methodology;
9. files whose purpose cannot be determined confidently.

## Required classifications

For every relevant file, classify it as one of:

- CORE / NECESSARY
- REPRODUCIBILITY
- INPUT DATA
- FINAL RESULT
- USEFUL INTERMEDIATE RESULT
- DOCUMENTATION
- EXPERIMENTAL / HISTORICAL
- TEMPORARY / CHECKPOINT
- DUPLICATE
- OBSOLETE
- MANUAL REVIEW REQUIRED

Do not classify a file as obsolete merely because it is not imported.

## Methodological safety

Do not silently correct anything that can affect scientific results.

Report such discrepancies as:

`METHODOLOGICAL REVIEW REQUIRED`

For each discrepancy include:

- file/path;
- observed implementation;
- documented expected behavior;
- likely scientific impact;
- suggested investigation.

## Required report

Produce:

### 1. Current repository structure

Summarize the actual structure.

### 2. Reconstructed pipeline

Map each research stage to scripts and artifacts.

### 3. Canonical artifacts

List the files that appear to correspond to the canonical datasets/results documented in the repository.

### 4. Dependency map

For each important script:
- inputs;
- outputs;
- downstream consumers;
- pipeline stage.

### 5. Cleanup candidates

For every candidate:

- path
- proposed action: keep / move / delete / gitignore / manual review
- evidence
- risk: low / medium / high

### 6. Duplicate/superseded artifacts

Explain why each appears duplicated or superseded.

### 7. GitHub hygiene

Identify:
- secrets;
- caches;
- generated local artifacts;
- large regenerable outputs;
- IDE files;
- logs;
- checkpoints.

### 8. Methodological discrepancies

Do not fix them.

### 9. Proposed final structure

Base it on the ACTUAL discovered pipeline, not a generic template.

### 10. Exact cleanup plan

For each proposed operation:

FROM:
`<path>`

TO:
`<path or N/A>`

ACTION:
`keep / move / delete / gitignore / manual review`

RATIONALE:
`<specific evidence>`

RISK:
`low / medium / high`

Stop after the report. Do not execute the cleanup.
