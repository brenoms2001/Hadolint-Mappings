# IEC 62443 Gold Standard Dataset

## Configuration

- Standard: `IEC 62443-3-3`
- Threshold: `0.68`
- Top-K: `10`
- Power: `5.5`
- Method: `cosine similarity -> clamp negative -> power transform -> L-infinity normalization -> threshold -> top-K`
- Source dataset: `data/output/datasets/hadolint_rules_structured.json`
- Target dataset: `data/output/datasets/iec62443_clean.json`

## Dataset summary

- Candidate records: `4134`

### Hadolint

- Rules: `75`
- Candidates: `529`
- Average candidates: `7.05`
- Distinct targets: `67`
- Distinct parent SRs: `40`

#### Top 10 IEC targets

- `SR 1.11` — 36
- `SR 3.2` — 34
- `SR 3.7` — 31
- `SR 3.2 RE 1` — 25
- `SR 3.8 RE 3` — 24
- `SR 3.6` — 22
- `SR 1.5 RE 1` — 19
- `SR 1.4` — 18
- `SR 5.2 RE 3` — 17
- `SR 2.12 RE 1` — 17

### ShellCheck

- Rules: `519`
- Candidates: `3605`
- Average candidates: `6.95`
- Distinct targets: `87`
- Distinct parent SRs: `46`

#### Top 10 IEC targets

- `SR 3.5` — 351
- `SR 3.7` — 310
- `SR 5.2 RE 3` — 259
- `SR 3.2 RE 1` — 255
- `SR 1.11` — 176
- `SR 2.11` — 140
- `SR 3.3` — 137
- `SR 3.6` — 136
- `SR 1.4` — 127
- `SR 2.12 RE 1` — 120

## Human-review schema

Each candidate contains three empty fields for manual annotation:

- `human_label`
- `human_confidence`
- `human_notes`

The automatic similarity result and matching configuration are preserved unchanged.
