# New session - 2026-09-26T16:55:48.253Z

**Session ID:** ses_f215b08e3ffel9ttSkEBXAbZgU
**Created:** 9/26/2026, 1:55:48 PM
**Updated:** 9/26/2026, 2:17:59 PM

---

## User

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

---

## Assistant (Plan · gpt-5.6-sol-pro · 63.5s)

---

## User

olá

---

## Assistant (Plan · gpt-5.6 · 16.5s)

---

## User

olá

---

## Assistant (Plan · GPT-6 Sol · 9.9s)

_Thinking:_

**Reading AGENTS files**

**Tool: read**

---

## Assistant (Plan · GPT-6 Sol · 4.5s)

**Tool: read**

---

## User

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

---

## Assistant (Plan · GPT-6 Sol · 5.3s)

_Thinking:_



**Tool: read**

---

## Assistant (Plan · GPT-6 Sol · 3.1s)

**Tool: read**

---

## Assistant (Plan · GPT-6 Sol · 3.1s)

**Tool: read**

---

## Assistant (Plan · GPT-6 Sol · 3.0s)

**Tool: read**

---

## Assistant (Plan · GPT-6 Sol · 3.1s)

**Tool: read**

---

## Assistant (Plan · GPT-6 Sol · 4.5s)

**Tool: glob**

---

## Assistant (Plan · GPT-6 Sol · 3.5s)

**Tool: read**

---

## Assistant (Plan · GPT-6 Sol · 3.0s)

**Tool: read**

---

## Assistant (Plan · GPT-6 Sol · 2.9s)

**Tool: read**

---

## Assistant (Plan · GPT-6 Sol · 7.9s)

_Thinking:_

**Inspecting repository inventory**

Olá! Vou continuar a auditoria somente de leitura. Já li `AGENTS.md` e os documentos e arquivos de configuração exigidos; agora vou mapear os arquivos e conferir o pipeline implementado.

**Tool: todowrite**

---

## Assistant (Plan · GPT-6 Sol · 8.8s)

**Tool: glob**

**Tool: glob**

**Tool: bash**

**Tool: bash**

**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 10.9s)

_Thinking:_

**Reading scripts in batches**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 11.3s)

_Thinking:_

**Inspecting prompt content**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

---

## Assistant (Plan · GPT-6 Sol · 5.9s)

_Thinking:_

**Searching scripts for keys**

**Tool: todowrite**

---

## Assistant (Plan · GPT-6 Sol · 9.4s)

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

---

## Assistant (Plan · GPT-6 Sol · 10.2s)

_Thinking:_

**Searching script patterns**

Encontrei a cadeia principal e duas pendências de rastreabilidade: os prompts externos ainda são placeholders, e `.gitignore` os ignora por causa da regra `*.txt`. Vou verificar as saídas e os scripts de auditoria antes de concluir o relatório.

**Tool: grep**

**Tool: read**

**Tool: read**

**Tool: read**

---

## Assistant (Plan · GPT-6 Sol · 16.1s)

_Thinking:_

**Searching for key defects**

**Tool: grep**

**Tool: grep**

**Tool: grep**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

---

## Assistant (Plan · GPT-6 Sol · 10.2s)

_Thinking:_

**Checking script headers/notebooks**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 10.8s)

_Thinking:_

**Inspecting submodule status**

_Thinking:_

**Checking audit outputs**

**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 18.5s)

_Thinking:_

**Checking metadata and counts**

**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 9.5s)

_Thinking:_

**Parsing notebook metadata**

**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 8.6s)

_Thinking:_

**Inspecting notebook cells**

**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 12.7s)

_Thinking:_

**Preparing pickle metadata inspection**

**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 7.3s)

_Thinking:_

**Inspecting metadata opcodes**

**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 6.1s)

_Thinking:_

**Checking file hashes**

**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 8.7s)

_Thinking:_

**Checking directory listings**

**Tool: read**

**Tool: read**

**Tool: glob**

**Tool: glob**

**Tool: grep**

**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 14.3s)

_Thinking:_



**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 12.3s)

_Thinking:_

**Auditing methodological discrepancies**

_Thinking:_

**Reviewing validation gaps**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: read**

---

## Assistant (Plan · GPT-6 Sol · 10.4s)

_Thinking:_

**Reading extraction_debug.json**

**Tool: read**

**Tool: read**

**Tool: read**

**Tool: grep**

**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 16.6s)

_Thinking:_

**Preparing artifact classifications**

**Tool: bash**

**Tool: bash**

**Tool: grep**

---

## Assistant (Plan · GPT-6 Sol · 11.8s)

_Thinking:_

**Reviewing root file inventory**

**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 16.1s)

_Thinking:_

**Reviewing output metadata**

**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 27.0s)

_Thinking:_

**Reading audit script endings**

_Thinking:_

**Checking audit output counts**

_Thinking:_

**Parsing Python files**

**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 12.6s)

_Thinking:_

**Checking audit status**

**Tool: todowrite**

---

## Assistant (Plan · GPT-6 Sol · 13.4s)

_Thinking:_

**Comparing sample v2 IDs**

**Tool: bash**

**Tool: bash**

**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 10.4s)

_Thinking:_

**Checking tracked notebook outputs**

**Tool: bash**

---

## Assistant (Plan · GPT-6 Sol · 21.6s)

_Thinking:_

**Verifying debug artifacts**

_Thinking:_

**Classifying artifact candidates**

_Thinking:_

**Checking wiki gitlinks**

_Thinking:_

**Reviewing audit artifacts**

Confirmei as contagens do conjunto canônico (594 regras, 4.134 pares e 594 classificações auxiliares) e uma limitação importante: o arquivo de anotações existente contém 10 pares, todos sem rótulo humano. Também identifiquei um erro no anotador atual que exige revisão metodológica; não executei nenhum script de geração ou limpeza.

**Tool: todowrite**

---

## Assistant (Plan · GPT-6 Sol · 24.8s)

_Thinking:_

**Building script classification table**

_Thinking:_

**Reviewing report outputs**

**Tool: todowrite**

---

## Assistant (Plan · GPT-6 Sol · 152.4s)

_Thinking:_



# Read-only repository audit

**The repository contains a complete, structurally consistent 4,134-pair candidate set and a complete preliminary Gemini pair audit, but no completed human gold standard.** The existing annotation artifact contains 10 pilot pairs and **zero human labels**. I made no repository changes and did not execute any pipeline scripts.

Paths below are relative to the repository root. For the inventory, these prefixes shorten repeated paths:

- `D/` = `data/output/datasets/`
- `M/` = `data/output/mappings/`
- `I/` = `data/output/mappings/iec/inspection/`
- `G/` = `data/output/mappings/iec/inspection/gold_standard/`
- `A/` = `data/output/mappings/iec/inspection/gold_standard/gemini_audit/`

## 1. Current repository structure

- **Root:** 20 Python scripts covering acquisition, IEC extraction, matching, evaluation, and analysis. Root also contains research documentation and migration materials.
- **`data/input/`:** IEC PDF, CWE XML, and two locally populated wiki repositories.
- **`data/output/datasets/`:** source rules, IEC extraction and enrichment, historical CIS/CWE datasets, and extraction diagnostics.
- **`data/output/embeddings/`:** four ignored pickle caches. Two structured caches supply the canonical IEC matching scripts.
- **`data/output/mappings/`:** historical CIS/CWE and 0.60 IEC experiments; canonical 0.68 IEC matching, candidate, audit, and analysis artifacts.
- **`notebooks/`:** earlier cleaning and embedding/mapping work, using a different model and some inputs no longer present.
- **`config/`, `docs/`, `prompts/`, `manifests/`:** recently supplied methodology and reproducibility materials. The prompt `.txt` files currently contain placeholders.

Git status showed a modified `AGENTS.md` and untracked migration materials; these were treated as existing work. `.env/` is a roughly **5.6 GB ignored virtual environment**. The two wiki directories are recorded as Git *gitlinks*, but there is no `.gitmodules` file to tell a fresh clone how to obtain them.

### File classifications

The classifications distinguish an artifact's research role from whether Git currently tracks it.

| Classification | Files |
|---|---|
| **CORE / NECESSARY** | `extract_hadolint_wiki.py`, `extract_iec_requirements_pages.py`, `iec_cleaning.py`, `iec_extract_rationale.py`, `iec_audit.py`, `inspect_iec_matches.py`, `build_gold_standard.py`, `sample_gold_standard.py`, `audit_gold_standard_gemini.py`, `audit_security_relevance_gemini.py`, `analyze_security_relevance_rule_level.py`, `analyze_iec_concentration.py`, `analyze_iec_match_quality.py` |
| **REPRODUCIBILITY** | `requirements.txt`, `config/*.yaml`, `manifests/canonical_artifacts.json` **(hashes still null)**, `D/iec62443_llm_blocks.json`, `D/iec62443_debug.json` **(consumed by `iec_audit.py`)**, `D/iec62443_rationale_debug.json`, `D/iec62443_audit.json`, `D/iec62443_audit_report.txt`; structured embedding caches `data/output/embeddings/cache_hadolint_structured.pkl` and `cache_iec_structured.pkl` **(essential current inputs, though ignored)** |
| **INPUT DATA** | `data/input/iec62443/iec-62443-3-3.pdf`, `data/input/hadolint/wiki_hadolint_temp`, `data/input/hadolint/wiki_shellcheck_temp`; `data/input/cwe/cwec_v4.19.1.xml` for the historical CWE branch |
| **FINAL RESULT** | `D/hadolint_rules_structured.json`, `D/iec62443_with_rationale.json`, `G/iec_gold_standard_candidates.json`, `A/full/iec_gold_standard_gemini_audit.json` **(final output of a preliminary audit)**, `A/security_relevance/security_relevance_gemini_audit.json` **(final output of an auxiliary preliminary analysis)**, `A/security_relevance/security_relevance_rule_level_analysis.json` **(exploratory result)** |
| **USEFUL INTERMEDIATE RESULT** | `D/iec62443_requirements_full.pdf`, `D/iec62443_clean.json`, `I/iec_matches_068_top10.json` and `.csv`, `G/iec_gold_standard_candidates.csv`, `G/iec_gold_standard_sample.json` and `.csv`; CSV/XLSX/Markdown exports alongside full Gemini and security-relevance results; `I/concentration/*` and `I/quality/*` analysis outputs; `D/iec62443_extraction_review.txt` and `D/iec62443_rationale_extraction_review.txt` |
| **DOCUMENTATION** | `AGENTS.md`, `README.md`, `REPRODUCIBILITY.md`, `MIGRATION_CHECKLIST.md`, `OPENCODE_READ_ONLY_AUDIT.md`, `docs/*.md`, `prompts/README.md`, `iec_gold_standard_candidates_validation_report.md`, `G/iec_gold_standard_report.md`, `G/iec_gold_standard_sample_report.md`, `.gitignore`, `gitignore.fragment` |
| **EXPERIMENTAL / HISTORICAL** | `notebooks/*.ipynb`, `calculate_similarity.py` and `analyze_mapping_candidates.py` with `M/iec/*candidates_60.json` and `M/iec/candidate_analysis_summary.json`; `analyze_threshold_topk.py` and `M/iec/threshold_topk_analysis.json`; `D/hadolint_rules.json`, `D/cwe.json`, `D/cis_docker_benchmark.json`; `M/hadolint_cis_full.json`, `M/hadolint_cwe_full.json`, `M/cis/*`, `M/cwe/*`; `data/output/embeddings/cache_cis.pkl` and `cache_cwe.pkl`; `inspect_pdf_pages.py`, `diagnose_res.py` and their page-index/RE diagnostic outputs; `A/iec_gold_standard_gemini_audit.{json,csv,xlsx}`, its report, and the corresponding `_v2` pilot files; `analyze_gemini_audit_global.py` **(an analysis script whose declared outputs are absent)** |
| **TEMPORARY / CHECKPOINT** | `.env/`, `__pycache__/`, `D/iec62443_llm_checkpoint.json`, `D/iec62443_rationale_checkpoint.json`, `A/full/iec_gold_standard_gemini_audit_checkpoint.json` and `_progress.xlsx`, both pilot Gemini checkpoints, and `A/security_relevance/security_relevance_gemini_audit_checkpoint.json`. The research checkpoints should be retained until provenance and recovery needs are decided. |
| **MANUAL REVIEW REQUIRED** | `annotate_gold_standard.py` and `G/annotations/*` **(current script issue; 10 unreviewed pairs)**; `D/iec62443_requirements.pdf` **(40-page PDF with no identified producer)**; `D/iec62443_extraction_debug.json` **(different, apparently earlier extraction format; producer unknown)**; `G/iec_gold_standard_candidates.md` **(ignored derived dump; contents not established as redundant)**; both `prompts/*.txt` **(placeholders)**; `hadolint_match_research_handoff_v1.zip` **(overlaps the supplied documents but also contains `.env.example`, absent at the root)** |

No research file was classified **OBSOLETE** solely because it is not imported.

## 2. Reconstructed pipeline

1. **Acquire source rules.** `extract_hadolint_wiki.py` reads the local Hadolint and ShellCheck wikis and writes the flat, ID-keyed `D/hadolint_rules_structured.json`: **75 + 519 = 594 rules**.
2. **Extract IEC requirements.** `extract_iec_requirements_pages.py` selects PDF pages 28–80 into `D/iec62443_requirements_full.pdf` (**53 pages**). `iec_cleaning.py` performs page-block Gemini extraction, writing checkpoint/block/debug evidence and `D/iec62443_clean.json`: **51 SR + 49 RE**. `iec_audit.py` checks the clean data against its debug provenance. Its saved audit passes structural checks but records **13 warnings and one review-status entry**.
3. **Enrich IEC text.** `iec_extract_rationale.py` reads the clean dataset and extracted PDF, and writes `D/iec62443_with_rationale.json`. All 51 SRs have rationale; RE rationale is null. Its checkpoint and debug artifacts preserve expensive extraction evidence.
4. **Generate embeddings.** The current matching scripts load `cache_hadolint_structured.pkl` and `cache_iec_structured.pkl`. Their inspected metadata records `BAAI/bge-large-en-v1.5`, 1,024 dimensions, and normalized vectors; it describes representations as `id+title+problematic_code+correct_code` and `id+title+normative_text`. **No current script generating these structured caches was found.** The notebooks generate *different*, earlier caches using `all_mpnet_base_v2`.
5. **Generate canonical matches.** `inspect_iec_matches.py` reads the structured caches, structured rules, and **`D/iec62443_clean.json`**. It applies cosine → negative clamp → power 5.5 → per-rule maximum normalization → threshold 0.68 → top 10, writing `I/iec_matches_068_top10.{json,csv}`.
6. **Build evaluation candidates.** `build_gold_standard.py` validates those matches against the source and clean IEC datasets and writes `G/iec_gold_standard_candidates.json`, CSV, and report. The JSON contains **594 rules and 4,134 pairs**: 529 Hadolint, 3,605 ShellCheck; 2,214 SR, 1,920 RE. Its human fields are null. The matches and candidate JSONs have the same pair IDs, ranks, cosine values, and relative scores.
7. **Sample and preliminarily audit.** `sample_gold_standard.py` produces a seed-42, gap-stratified **75-rule/531-pair** sample. `audit_gold_standard_gemini.py` currently consumes the **full** candidate JSON plus enriched IEC rationales, producing a 4,134-result preliminary audit: **78 YES, 481 MAYBE, 3,575 NO**. Earlier 10-pair pilot outputs also remain.
8. **Human review.** `annotate_gold_standard.py` points to a **10-pair pilot audit**, not the full audit. Its existing output has **0/10 human labels**. As currently written, its Gemini-input path also references an undefined `REVIEW_SCOPE`; there is no evidence here of a completed human gold standard or downstream human-label analysis.
9. **Auxiliary and descriptive analyses.** `audit_security_relevance_gemini.py` classifies the 594 rules independently of candidate generation, then crosses its preliminary classes with the completed pair audit: **86 security-related, 504 non-security, 4 uncertain**. `analyze_security_relevance_rule_level.py` produces exploratory rule-level results. Concentration and quality scripts analyze canonical matches; `analyze_gemini_audit_global.py` specifies analyses of the full audit XLSX, but its output directory is absent. The older 0.60 IEC and CIS/CWE branches are distinct experiments.

## 3. Canonical artifacts

These paths agree with the substantive outputs and, where specified, `docs/methodology.md` and `manifests/canonical_artifacts.json`:

| Artifact | Path | Observed status |
|---|---|---|
| Source rules | `data/output/datasets/hadolint_rules_structured.json` | 594 flat ID-keyed rules |
| IEC normative requirements | `data/output/datasets/iec62443_clean.json` | 100 requirements; actual canonical **matching input** |
| IEC enriched requirements | `data/output/datasets/iec62443_with_rationale.json` | 100 requirements; pair-audit contextual input |
| Structured embeddings | `data/output/embeddings/cache_hadolint_structured.pkl`, `cache_iec_structured.pkl` | Current matching inputs; ignored, generation script absent |
| Canonical match output | `data/output/mappings/iec/inspection/iec_matches_068_top10.json` | 4,134 matches; direct candidate-builder input |
| Canonical candidate set | `data/output/mappings/iec/inspection/gold_standard/iec_gold_standard_candidates.json` | 4,134 **unreviewed** pairs |
| Full preliminary pair audit | `data/output/mappings/iec/inspection/gold_standard/gemini_audit/full/iec_gold_standard_gemini_audit.json` | 4,134 Gemini verdicts; human labels null |
| Auxiliary preliminary rule audit | `data/output/mappings/iec/inspection/gold_standard/gemini_audit/security_relevance/security_relevance_gemini_audit.json` | 594 rule classifications |
| Exploratory cross-analysis | `data/output/mappings/iec/inspection/gold_standard/gemini_audit/security_relevance/security_relevance_rule_level_analysis.json` | Rule-level analysis, not human validation |

The full audit's stored input/dataset hashes match the current files; the security audit's stored source and pair-audit hashes also match. The separate bootstrap manifest still has **null SHA-256 entries**.

## 4. Dependency map

| Script / stage | Inputs | Outputs | Downstream consumer |
|---|---|---|---|
| `extract_hadolint_wiki.py` / acquisition | Two wiki repositories | `D/hadolint_rules_structured.json` | Matching, candidate builder, Gemini audits |
| `inspect_pdf_pages.py`; `extract_iec_requirements_pages.py` / PDF preparation | Original IEC PDF | Page-index `.txt`; `D/iec62443_requirements_full.pdf` | IEC extraction and enrichment use the full PDF |
| `iec_cleaning.py` / IEC extraction | Full requirements PDF; Gemini | `D/iec62443_clean.json`, `iec62443_llm_blocks.json`, `iec62443_debug.json`, checkpoint and review text | IEC audit, rationale extraction, matching |
| `iec_audit.py` / extraction validation | Clean JSON **and** `D/iec62443_debug.json` | `D/iec62443_audit.json`, audit report | Research validation record |
| `iec_extract_rationale.py` / enrichment | Clean JSON, full requirements PDF; Gemini | `D/iec62443_with_rationale.json`, rationale checkpoint/debug/review text | Gemini pair audit; historical 0.60 similarity branch |
| **No current generator found** / structured embeddings | Provenance indicated by cache metadata, but source code absent | Two `cache_*_structured.pkl` files | `inspect_iec_matches.py`, `analyze_threshold_topk.py`, `calculate_similarity.py` |
| `inspect_iec_matches.py` / canonical matching | Structured caches, structured rules, **clean IEC** | `I/iec_matches_068_top10.{json,csv}` | `build_gold_standard.py`, quality, concentration |
| `build_gold_standard.py` / candidate construction | Matches JSON, structured rules, clean IEC | `G/iec_gold_standard_candidates.{json,csv}`, report | Sampling, full Gemini audit |
| `sample_gold_standard.py` / evaluation sample | Candidates JSON | `G/iec_gold_standard_sample.{json,csv}`, report | Optional sample-format audit or annotation |
| `audit_gold_standard_gemini.py` / preliminary pair audit | Full candidates, structured rules, **enriched IEC**; Gemini | `A/full/iec_gold_standard_gemini_audit.{json,csv,xlsx,md}`, checkpoint/progress | Security cross-analysis, global analysis |
| `annotate_gold_standard.py` / human annotation | Currently `A/iec_gold_standard_gemini_audit.json` **10-pair pilot**; prior annotation output for resumption | `G/annotations/iec_gold_standard_annotated.{json,csv,xlsx}`, report | No implemented final gold-standard analysis identified |
| `audit_security_relevance_gemini.py` / auxiliary classification | Structured rules; full pair audit for its cross-analysis | `A/security_relevance/security_relevance_gemini_audit.{json,csv,xlsx,md}`, checkpoint | Rule-level analysis |
| `analyze_security_relevance_rule_level.py` / exploratory analysis | Security audit JSON; full pair audit JSON | `A/security_relevance/security_relevance_rule_level_analysis.{json,csv,md}` | Paper/exploratory reporting |
| `analyze_iec_concentration.py`; `analyze_iec_match_quality.py` / diagnostics | Canonical matches JSON; quality script also reads source/clean IEC | `I/concentration/*`; `I/quality/*` | Research inspection |
| `analyze_gemini_audit_global.py` / descriptive analysis | Full audit XLSX, or `/mnt/data/` fallback | Declared `A/global/*` **not present** | No observed consumer |
| `calculate_similarity.py`; `analyze_mapping_candidates.py` / older IEC branch | Structured caches, structured rules, **enriched IEC**; then 0.60 output JSONs | `M/iec/{hadolint,shellcheck}_iec_candidates_60.json`, `candidate_analysis_summary.json` | Historical analysis, **not** the canonical builder |
| `analyze_threshold_topk.py` / parameter study | Structured caches, structured rules, clean IEC | `M/iec/threshold_topk_analysis.json` | Parameter exploration |
| `notebooks/cleaning.ipynb`; `notebooks/processing.ipynb` / historical branches | Wikis, CWE XML, external CIS data and now-missing IEC CSVs; earlier model | Historical datasets, caches, CIS/CWE rankings | Historical research record |
| `diagnose_res.py` / diagnostic | IEC extraction-review text | `D/iec62443_re_debug.txt` | Manual inspection |

## 5. Cleanup candidates

**No research-artifact deletion is supported without further provenance review.** The actionable candidates are Git hygiene rules and resolution of specific unknowns; the precise path, action, evidence, and risk for each are in the **exact cleanup plan (§10)**.

Highest-priority decisions are:

- **Keep and restore reproducible access to the structured embedding caches** before treating them as disposable `*.pkl` files.
- **Keep `iec62443_debug.json` available:** `iec_audit.py` consumes it, although `*debug*` ignores it.
- **Review, rather than delete, completed checkpoints:** their result arrays equal the corresponding final JSON result arrays, but their metadata and recovery role differ.
- **Preserve the pilot versions:** the v2 and v3 pilots evaluated the same 10 pair IDs but **changed two verdicts**.
- **Resolve unknown provenance** for the 40-page `iec62443_requirements.pdf` and older-format `iec62443_extraction_debug.json`.

## 6. Duplicate or superseded-looking artifacts

- **Canonical matches versus candidate JSON:** same 4,134 scored/ranked associations; the candidate builder adds source context and empty human fields. Both are needed to trace the transformation.
- **Full audit checkpoint versus full audit JSON:** all **4,134 `results` entries are equal**, though whole-file hashes and metadata differ. Keep pending an archival/recovery decision. The full `_progress.xlsx` is a separate live-run view of the final workbook.
- **Security checkpoint versus security audit JSON:** all **594 `results` entries are equal**; the final JSON additionally contains cross-analysis and final metadata.
- **10-pair pilot v3 versus v2:** same pair IDs, **two changed verdicts**, and different prompt versions. They are historical comparisons, not byte-for-byte duplicates. Each corresponding pilot checkpoint contains the same results as its final pilot JSON.
- **Existing annotation JSON versus v3 pilot:** same 10 pair IDs, with annotation-oriented fields, but **no human labels**. It is not a gold standard.
- **JSON versus CSV/XLSX/Markdown exports:** alternate representations intended for inspection or review, not grounds for deletion without checking their use.
- **`hadolint_rules.json` versus structured rules:** older source representation has **589 versus 594** entries; it feeds historical notebooks, not the canonical matching run.
- **`iec62443_clean.json` versus enriched IEC:** normative text agrees entry-by-entry; the enriched file adds SR rationales. The clean file remains the actual canonical matching input.
- **`hadolint_match_research_handoff_v1.zip`:** overlaps current migration documents but contains an `.env.example` not present at the root. Its disposition requires review.

## 7. GitHub hygiene

- **Credentials:** scripts use the `GEMINI_API_KEY` environment variable. The notebook's `API_KEY` assignment is a literal placeholder. A scan of repository text files found no credential-like strings matching the checked API-key patterns; that does not establish the contents of the ignored local `.env/` environment. Keep keys and credentials out of Git.
- **Currently ignored:** `.env/`, `__pycache__/`, all `*.pkl`, all `*.txt`, `*debug*`, `*checkpoint*`, progress XLSX, specified pilot v2 outputs, and the candidate Markdown dump.
- **Ignore rules needing review:** `*.txt` also hides both required prompt files and extraction/audit review records. `*debug*` hides an actual input to `iec_audit.py`. `gitignore.fragment` proposes narrower environment, cache, IDE, OS, and log rules but has not been incorporated.
- **Large artifacts:** `.env/` is about **5.6 GB** and should remain local. Research `data/` totals about **122 MB**; the full pair JSON, its checkpoint, and security JSON are substantial but have distinct research roles.
- **IDE/log files:** no `.vscode/`, `.idea/`, `.DS_Store`, repository `.log`, `.tmp`, or `.bak` files were observed outside the environment.
- **Wiki provenance:** the wiki paths are pinned Git gitlinks, but the missing `.gitmodules` mapping impedes acquisition by a fresh clone. Their local names ending `_temp` do not make their pinned inputs disposable.

## 8. Methodological discrepancies

Each item below is a **METHODOLOGICAL REVIEW REQUIRED** finding; none was corrected.

1. **Structured embedding generation is not reconstructible from repository code.**  
   **Files:** `data/output/embeddings/cache_hadolint_structured.pkl`, `cache_iec_structured.pkl`; `notebooks/processing.ipynb`; `docs/methodology.md`, `REPRODUCIBILITY.md`.  
   **Observed:** canonical scripts require the structured BGE caches, whose metadata names cloud-drive source paths; the available notebook generates earlier, differently named caches using `all_mpnet_base_v2`. Structured caches are Git-ignored.  
   **Expected:** reproducible 1,024-dimensional, normalized `BAAI/bge-large-en-v1.5` embeddings with recorded input representation.  
   **Likely impact:** a fresh researcher cannot regenerate or independently verify the vectors behind 4,134 scores.  
   **Investigation:** locate the exact cache-generation code, model revision, text construction, input hashes, and a preservation mechanism before moving or discarding caches.

2. **The documented human-review chain has not reached a gold standard.**  
   **Files:** `annotate_gold_standard.py:13–20,45,195`; `G/annotations/iec_gold_standard_annotated.json`; `docs/pipeline.md`.  
   **Observed:** the annotator targets the 10-pair pilot; its Gemini-format metadata path uses commented-out/undefined `REVIEW_SCOPE`. The existing annotation output is `unreviewed`, **0/10 labeled**.  
   **Expected:** human labels, not Gemini verdicts, establish the final pair gold standard; scope must identify the configuration reviewed.  
   **Likely impact:** calling the current annotation output a validated gold standard would misstate the evidence; a new run may fail before review.  
   **Investigation:** establish the intended full-versus-sample human protocol, verify which script version generated the existing artifact, and validate annotation resumption and scope before any labeling run.

3. **The similarly named 0.60 IEC path is not canonical matching.**  
   **Files:** `calculate_similarity.py:69–77,545–579`; `M/iec/hadolint_iec_candidates_60.json`, `shellcheck_iec_candidates_60.json`; `config/matching.yaml`.  
   **Observed:** the script retains all candidates at relative score ≥0.60; top 10 is diagnostic only.  
   **Expected:** the canonical candidate set uses ≥0.68 **and then** at most 10.  
   **Likely impact:** substituting the 0.60 outputs changes the candidate population and invalidates transfer of labels or reported counts.  
   **Investigation:** retain these as explicitly historical/experimental and check any paper or analysis references for accidental substitution.

4. **Matching-input provenance needs explicit reconciliation.**  
   **Files:** `inspect_iec_matches.py:22–28,451–466`; `build_gold_standard.py:23–26`; `calculate_similarity.py:61–66`; structured IEC cache metadata; `docs/methodology.md:19–29,85–93`.  
   **Observed:** the 4,134-pair path reads **clean IEC** and records it as target. The separate 0.60 path reads **enriched IEC**. The structured IEC cache claims an enriched source file but describes its embedded representation as `id+title+normative_text`; enriched rationales enter the **Gemini audit** as context.  
   **Expected:** the canonical target's text representation and data lineage should be unambiguous; the documented candidate metadata specifies clean IEC.  
   **Likely impact:** unclear provenance could lead a replication to embed rationales or use a different target set, changing scores and pairs. It does **not**, by itself, prove the existing canonical scores are wrong.  
   **Investigation:** retrieve the structured-cache generator and verify the exact embedded text against both IEC datasets; record why clean IEC supplies candidate fields while enriched IEC supplies audit context.

5. **Pinned wiki inputs are not fetchable from the recorded gitlinks alone.**  
   **Files:** Git gitlinks `data/input/hadolint/wiki_hadolint_temp`, `wiki_shellcheck_temp`; absent `.gitmodules`; `extract_hadolint_wiki.py:38–48,392–405`.  
   **Observed:** both local repos have pinned commits and remotes, but `git submodule status` fails because no `.gitmodules` mapping exists. The extractor reuses an existing directory without checking its commit.  
   **Expected:** reproducible acquisition of the 594-rule source snapshot.  
   **Likely impact:** a fresh checkout may lack the wiki pages or extract a different revision.  
   **Investigation:** document the two observed remote URLs and pinned commits, and decide how the baseline will make those exact snapshots retrievable.

6. **Prompts and configuration are not yet the runnable experimental record described by the docs.**  
   **Files:** `prompts/gemini_pair_audit_v3.txt`, `prompts/security_relevance_v1.txt`, `.gitignore:13`, `config/*.yaml`, `audit_gold_standard_gemini.py:107,1111–1299`, `audit_security_relevance_gemini.py:87,110–151,353–462`; `REPRODUCIBILITY.md:37–57`.  
   **Observed:** both required prompt files say **PLACEHOLDER** and are ignored by `*.txt`; scripts construct prompts and set parameters in Python rather than loading the YAML or text files.  
   **Expected:** exact versioned prompt bodies and configuration sufficient to reproduce the preliminary audits.  
   **Likely impact:** the external prompt/config files cannot presently serve as independent provenance, and their values could drift from the scripts.  
   **Investigation:** preserve the exact script prompt templates and dynamic payload construction verbatim; compare them with output metadata, then document runtime authority before changing files or ignore rules.

7. **Some reproducibility records disagree with current artifacts.**  
   **Files:** `iec_gold_standard_candidates_validation_report.md:24,150–159`; `G/iec_gold_standard_candidates.json`; `manifests/canonical_artifacts.json`.  
   **Observed:** the validation report says candidate metadata lacks `power` and `method`, but the current JSON contains **5.5** and the complete method string. Manifest hashes remain null.  
   **Expected:** reports and manifest describe the actual canonical bytes.  
   **Likely impact:** provenance readers can draw incorrect conclusions about which version was validated, even though observed candidate counts agree.  
   **Investigation:** establish when the report and JSON versions were produced, preserve that history, and populate hashes only from verified canonical artifacts in a subsequent authorized task.

## 9. Proposed final structure

Retain the repository's **root-script execution convention** and actual branch separation:

```text
root scripts                         acquisition → IEC → embeddings/matching
                                     → candidates → Gemini → annotation → analyses
config/   docs/   prompts/   manifests/   REPRODUCIBILITY.md
data/input/
  hadolint/                          pinned wiki source snapshots
  iec62443/                          original IEC PDF
  cwe/                               historical CWE input
data/output/datasets/                structured rules; clean/enriched IEC;
                                     extraction and audit evidence
data/output/embeddings/              preserved structured-cache provenance;
                                     separate historical CIS/CWE caches
data/output/mappings/
  iec/                               historical 0.60 experiment and parameter study
    inspection/                      canonical 0.68 matches, quality, concentration
      gold_standard/                 unreviewed candidates and sample
        gemini_audit/full/           complete preliminary pair audit
        gemini_audit/security_relevance/
                                    auxiliary audit and rule-level analysis
        annotations/                 human-review work, explicitly marked by status
  cis/  cwe/                         historical research branches
notebooks/                           historical pipeline
```

This is chiefly a **role and provenance proposal**, not a recommendation to move live scripts: current scripts have mixed root-relative and `__file__`-relative paths.

## 10. Exact cleanup plan — proposed operations only

`TO: N/A` means leave the file in place for **keep/manual review**, or no destination is involved for **gitignore**. A gitignore action is a proposed future rule decision, **not** removal of a research artifact.

| FROM | TO | ACTION | RATIONALE | RISK |
|---|---|---|---|---|
| `data/output/datasets/hadolint_rules_structured.json` | N/A | keep | Documented 594-rule canonical source and input to matching/audits. | high |
| `data/output/datasets/iec62443_clean.json` | N/A | keep | Actual input to canonical matching and candidate construction. | high |
| `data/output/datasets/iec62443_with_rationale.json` | N/A | keep | Enriched 100-requirement dataset used by Gemini pair audit. | high |
| `data/output/datasets/iec62443_debug.json` | N/A | keep | `iec_audit.py` directly loads it; `*debug*` currently ignores it. | high |
| `data/output/datasets/iec62443_llm_blocks.json` | N/A | keep | Preserves sanitized block-level extraction records. | medium |
| `data/output/datasets/iec62443_rationale_debug.json` | N/A | keep | Preserves rationale candidates, consolidation, and validation. | medium |
| `data/output/embeddings/cache_hadolint_structured.pkl` | N/A | manual review | Required matching input; ignored and generator absent. Decide archival/provenance before Git disposition. | high |
| `data/output/embeddings/cache_iec_structured.pkl` | N/A | manual review | Required matching input; embedded-text provenance needs confirmation. | high |
| `data/output/mappings/iec/inspection/iec_matches_068_top10.json` | N/A | keep | Direct 4,134-match input to candidate builder. | high |
| `data/output/mappings/iec/inspection/gold_standard/iec_gold_standard_candidates.json` | N/A | keep | Documented canonical 4,134-pair, unreviewed candidate set. | high |
| `data/output/mappings/iec/inspection/gold_standard/iec_gold_standard_sample.json` | N/A | keep | Seed-42, 531-pair sampling/protocol artifact. | medium |
| `data/output/mappings/iec/inspection/gold_standard/gemini_audit/full/iec_gold_standard_gemini_audit.json` | N/A | keep | Complete preliminary 4,134-pair output; referenced downstream. | high |
| `data/output/mappings/iec/inspection/gold_standard/gemini_audit/security_relevance/security_relevance_gemini_audit.json` | N/A | keep | Complete auxiliary 594-rule output and cross-analysis input. | high |
| `data/output/mappings/iec/inspection/gold_standard/annotations/iec_gold_standard_annotated.json` | N/A | manual review | Only 10 pilot pairs, all human labels null; must not be presented as a final gold standard. | high |
| `annotate_gold_standard.py` | N/A | manual review | Current input is the 10-pair pilot and `REVIEW_SCOPE` is undefined on that path. | high |
| `data/input/hadolint/wiki_hadolint_temp` | N/A | manual review | Pinned input gitlink; `.gitmodules` mapping absent. Preserve snapshot while resolving acquisition. | high |
| `data/input/hadolint/wiki_shellcheck_temp` | N/A | manual review | Same gitlink/acquisition problem for ShellCheck. | high |
| `data/output/datasets/iec62443_requirements.pdf` | N/A | manual review | 40-page alternate PDF; no producer/consumer found, unlike the 53-page `requirements_full.pdf`. | medium |
| `data/output/datasets/iec62443_extraction_debug.json` | N/A | manual review | SR-keyed earlier-looking raw-block format; provenance not established. | high |
| `data/output/mappings/iec/inspection/gold_standard/iec_gold_standard_candidates.md` | N/A | manual review | Ignored derived dump; establish whether it contains unique review history before considering deletion. | medium |
| `data/output/mappings/iec/inspection/gold_standard/gemini_audit/full/iec_gold_standard_gemini_audit_checkpoint.json` | N/A | manual review | Same 4,134 results as final JSON, but different metadata and potential recovery value. | medium |
| `data/output/mappings/iec/inspection/gold_standard/gemini_audit/full/iec_gold_standard_gemini_audit_progress.xlsx` | N/A | gitignore | Explicit batch-progress view; already ignored; final XLSX is separately retained. | low |
| `data/output/mappings/iec/inspection/gold_standard/gemini_audit/security_relevance/security_relevance_gemini_audit_checkpoint.json` | N/A | manual review | Same 594 results as final audit, but checkpoint provenance/recovery needs a decision. | medium |
| `data/output/mappings/iec/inspection/gold_standard/gemini_audit/iec_gold_standard_gemini_audit_v2.json` | N/A | keep | Historical prompt-v2 10-pair pilot; two verdicts differ from v3. Preserve experiment history. | medium |
| `data/output/mappings/iec/inspection/gold_standard/gemini_audit/iec_gold_standard_gemini_audit.json` | N/A | keep | Historical prompt-v3 pilot and source of existing annotation artifact. | medium |
| `data/output/datasets/iec62443_llm_checkpoint.json` | N/A | manual review | Expensive IEC extraction checkpoint; establish recovery/audit retention before removal. | medium |
| `data/output/datasets/iec62443_rationale_checkpoint.json` | N/A | manual review | Expensive rationale-extraction candidates and completed-block record. | medium |
| `prompts/gemini_pair_audit_v3.txt` | N/A | manual review | Required reproducibility path is an ignored placeholder; exact script prompt must be preserved. | high |
| `prompts/security_relevance_v1.txt` | N/A | manual review | Same issue for the auxiliary audit prompt. | high |
| `.gitignore` | N/A | manual review | `*.txt` hides prompts; `*debug*` hides audit input; narrowing rules requires provenance decisions. | high |
| `gitignore.fragment` | N/A | manual review | Contains proposed hygiene rules, not yet reconciled with research-artifact exceptions. | low |
| `manifests/canonical_artifacts.json` | N/A | keep | Useful bootstrap manifest, explicitly noncanonical until actual hashes are populated. | medium |
| `hadolint_match_research_handoff_v1.zip` | N/A | manual review | Overlapping documentation plus a root-absent `.env.example`; not proven redundant. | medium |
| `.env/` | N/A | gitignore | Local virtual environment, about 5.6 GB; already ignored. | low |
| `__pycache__/` | N/A | gitignore | Regenerable Python bytecode; already ignored. | low |
| `data/output/embeddings/cache_cis.pkl` | N/A | manual review | Ignored cache of the historical CIS branch; retain until branch reproducibility is decided. | medium |
| `data/output/embeddings/cache_cwe.pkl` | N/A | manual review | Ignored cache of the historical CWE branch; retain until branch reproducibility is decided. | medium |

**No cleanup was executed.**

---

