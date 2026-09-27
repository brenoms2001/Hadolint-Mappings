# Experiment Log

Use this file for concise, dated records of methodological or experimental changes.

Do not rewrite old entries after results have been generated. Append new entries.

## Known milestones to backfill from repository history

- Structured source-rule dataset completed.
- IEC 62443-3-3 requirement dataset prepared.
- Enriched IEC rationale dataset generated.
- Canonical matching configuration established:
  - power 5.5
  - threshold 0.68
  - top-K 10
- Full canonical candidate dataset validated:
  - 594 rules
  - 4134 candidates
- Full Gemini preliminary pair audit completed:
  - 78 YES
  - 481 MAYBE
  - 3575 NO
- Independent LLM-assisted security-relevance audit completed:
  - 86 security_related
  - 504 non_security
  - 4 uncertain
- Rule-level cross-analysis completed:
  - 86.05% vs 58.73% rule coverage
  - mean positive rate 30.45% vs 16.43%

## Entry template

### YYYY-MM-DD — short title

**Change / experiment**

Describe what changed or what was executed.

**Inputs**

List canonical input artifacts.

**Configuration**

Record parameters, model, prompt version, seed, etc.

**Outputs**

List generated artifacts.

**Result**

Record key numerical outcomes.

**Methodological impact**

State one of:

- none
- analysis-only
- changes candidate generation
- changes annotation protocol
- requires author review

**Commit**

`<git commit hash>`
