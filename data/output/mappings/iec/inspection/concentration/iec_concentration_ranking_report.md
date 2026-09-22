# IEC 62443 Match Concentration, Ranking and Separation

## Configuration

- Threshold: `0.68`
- Top-K: `10`
- Power: `5.5`
- Candidate records: `4134`

## Global Summary

| Source | Rules | Candidates | Distinct targets | Distinct SRs |
|---|---:|---:|---:|---:|
| HADOLINT | 75 | 529 | 67 | 40 |
| SHELLCHECK | 519 | 3605 | 87 | 46 |

## HADOLINT — Target Ranking

| Rank | Target | Type | Parent SR | Count | % | Mean score |
|---:|---|---|---|---:|---:|---:|
| 1 | SR 1.11 | SR | SR 1.11 | 36 | 6.81% | 0.8769 |
| 2 | SR 3.2 | SR | SR 3.2 | 34 | 6.43% | 0.8894 |
| 3 | SR 3.7 | SR | SR 3.7 | 31 | 5.86% | 0.8730 |
| 4 | SR 3.2 RE 1 | RE | SR 3.2 | 25 | 4.73% | 0.8636 |
| 5 | SR 3.8 RE 3 | RE | SR 3.8 | 24 | 4.54% | 0.8341 |
| 6 | SR 3.6 | SR | SR 3.6 | 22 | 4.16% | 0.8311 |
| 7 | SR 1.5 RE 1 | RE | SR 1.5 | 19 | 3.59% | 0.7990 |
| 8 | SR 1.4 | SR | SR 1.4 | 18 | 3.40% | 0.9082 |
| 9 | SR 2.12 RE 1 | RE | SR 2.12 | 17 | 3.21% | 0.8388 |
| 10 | SR 5.2 RE 3 | RE | SR 5.2 | 17 | 3.21% | 0.8056 |
| 11 | SR 2.4 | SR | SR 2.4 | 15 | 2.84% | 0.8174 |
| 12 | SR 5.2 RE 1 | RE | SR 5.2 | 15 | 2.84% | 0.8361 |
| 13 | SR 1.7 RE 1 | RE | SR 1.7 | 13 | 2.46% | 0.7948 |
| 14 | SR 3.3 | SR | SR 3.3 | 13 | 2.46% | 0.8472 |
| 15 | SR 7.1 | SR | SR 7.1 | 13 | 2.46% | 0.8325 |
| 16 | SR 7.3 | SR | SR 7.3 | 13 | 2.46% | 0.8717 |
| 17 | SR 7.7 | SR | SR 7.7 | 13 | 2.46% | 0.8359 |
| 18 | SR 2.4 RE 1 | RE | SR 2.4 | 12 | 2.27% | 0.7968 |
| 19 | SR 4.2 | SR | SR 4.2 | 10 | 1.89% | 0.9136 |
| 20 | SR 3.2 RE 2 | RE | SR 3.2 | 9 | 1.70% | 0.7981 |

## HADOLINT — Parent SR Ranking

| Rank | Parent SR | Matches | % | Distinct targets |
|---:|---|---:|---:|---:|
| 1 | SR 3.2 | 68 | 12.85% | 3 |
| 2 | SR 3.8 | 40 | 7.56% | 4 |
| 3 | SR 5.2 | 37 | 6.99% | 3 |
| 4 | SR 1.11 | 36 | 6.81% | 1 |
| 5 | SR 3.7 | 31 | 5.86% | 1 |
| 6 | SR 2.4 | 27 | 5.10% | 2 |
| 7 | SR 3.3 | 26 | 4.91% | 3 |
| 8 | SR 7.3 | 23 | 4.35% | 3 |
| 9 | SR 3.6 | 22 | 4.16% | 1 |
| 10 | SR 7.1 | 22 | 4.16% | 3 |
| 11 | SR 1.5 | 21 | 3.97% | 2 |
| 12 | SR 1.4 | 18 | 3.40% | 1 |
| 13 | SR 2.12 | 18 | 3.40% | 2 |
| 14 | SR 1.7 | 16 | 3.02% | 2 |
| 15 | SR 4.2 | 13 | 2.46% | 2 |
| 16 | SR 7.7 | 13 | 2.46% | 1 |
| 17 | SR 2.11 | 10 | 1.89% | 2 |
| 18 | SR 1.13 | 7 | 1.32% | 1 |
| 19 | SR 1.2 | 7 | 1.32% | 2 |
| 20 | SR 3.4 | 7 | 1.32% | 2 |

## HADOLINT — Concentration

### Target ID

- HHI: `0.031307`
- Gini: `0.522360`
- Entropy: `5.4067` bits
- Normalized entropy: `0.8913`
- Top-1 share: `6.81%`
- Top-5 share: `28.36%`
- Top-10 share: `45.94%`

### Parent SR

- HHI: `0.053548`
- Gini: `0.533318`
- Entropy: `4.6253` bits
- Normalized entropy: `0.8691`
- Top-1 share: `12.85%`
- Top-5 share: `40.08%`
- Top-10 share: `62.76%`

## SHELLCHECK — Target Ranking

| Rank | Target | Type | Parent SR | Count | % | Mean score |
|---:|---|---|---|---:|---:|---:|
| 1 | SR 3.5 | SR | SR 3.5 | 351 | 9.74% | 0.9230 |
| 2 | SR 3.7 | SR | SR 3.7 | 310 | 8.60% | 0.8623 |
| 3 | SR 5.2 RE 3 | RE | SR 5.2 | 259 | 7.18% | 0.8572 |
| 4 | SR 3.2 RE 1 | RE | SR 3.2 | 255 | 7.07% | 0.8452 |
| 5 | SR 1.11 | SR | SR 1.11 | 176 | 4.88% | 0.8301 |
| 6 | SR 2.11 | SR | SR 2.11 | 140 | 3.88% | 0.8280 |
| 7 | SR 3.3 | SR | SR 3.3 | 137 | 3.80% | 0.8088 |
| 8 | SR 3.6 | SR | SR 3.6 | 136 | 3.77% | 0.8388 |
| 9 | SR 1.4 | SR | SR 1.4 | 127 | 3.52% | 0.8625 |
| 10 | SR 2.12 RE 1 | RE | SR 2.12 | 120 | 3.33% | 0.8099 |
| 11 | SR 7.1 RE 1 | RE | SR 7.1 | 95 | 2.64% | 0.8152 |
| 12 | SR 7.1 | SR | SR 7.1 | 94 | 2.61% | 0.8037 |
| 13 | SR 7.3 | SR | SR 7.3 | 93 | 2.58% | 0.8179 |
| 14 | SR 2.4 RE 1 | RE | SR 2.4 | 90 | 2.50% | 0.7860 |
| 15 | SR 1.7 RE 1 | RE | SR 1.7 | 77 | 2.14% | 0.7929 |
| 16 | SR 4.2 RE 1 | RE | SR 4.2 | 77 | 2.14% | 0.8276 |
| 17 | SR 1.5 RE 1 | RE | SR 1.5 | 75 | 2.08% | 0.8186 |
| 18 | SR 7.6 RE 1 | RE | SR 7.6 | 64 | 1.78% | 0.8164 |
| 19 | SR 2.9 RE 1 | RE | SR 2.9 | 57 | 1.58% | 0.8210 |
| 20 | SR 5.2 RE 2 | RE | SR 5.2 | 55 | 1.53% | 0.8163 |

## SHELLCHECK — Parent SR Ranking

| Rank | Parent SR | Matches | % | Distinct targets |
|---:|---|---:|---:|---:|
| 1 | SR 5.2 | 359 | 9.96% | 4 |
| 2 | SR 3.5 | 351 | 9.74% | 1 |
| 3 | SR 3.7 | 310 | 8.60% | 1 |
| 4 | SR 3.2 | 303 | 8.40% | 3 |
| 5 | SR 2.11 | 195 | 5.41% | 3 |
| 6 | SR 7.1 | 194 | 5.38% | 3 |
| 7 | SR 1.11 | 176 | 4.88% | 1 |
| 8 | SR 3.3 | 170 | 4.72% | 3 |
| 9 | SR 3.8 | 140 | 3.88% | 4 |
| 10 | SR 3.6 | 136 | 3.77% | 1 |
| 11 | SR 2.12 | 135 | 3.74% | 2 |
| 12 | SR 1.4 | 127 | 3.52% | 1 |
| 13 | SR 4.2 | 125 | 3.47% | 2 |
| 14 | SR 2.4 | 121 | 3.36% | 2 |
| 15 | SR 7.3 | 118 | 3.27% | 3 |
| 16 | SR 1.7 | 93 | 2.58% | 3 |
| 17 | SR 1.5 | 75 | 2.08% | 1 |
| 18 | SR 7.6 | 70 | 1.94% | 2 |
| 19 | SR 2.9 | 65 | 1.80% | 2 |
| 20 | SR 1.2 | 60 | 1.66% | 2 |

## SHELLCHECK — Concentration

### Target ID

- HHI: `0.042729`
- Gini: `0.700304`
- Entropy: `5.1215` bits
- Normalized entropy: `0.7949`
- Top-1 share: `9.74%`
- Top-5 share: `37.48%`
- Top-10 share: `55.78%`

### Parent SR

- HHI: `0.055863`
- Gini: `0.628577`
- Entropy: `4.5056` bits
- Normalized entropy: `0.8157`
- Top-1 share: `9.96%`
- Top-5 share: `42.11%`
- Top-10 share: `64.74%`

## DL × SC Comparison

| Metric | DL | SC |
|---|---:|---:|
| Distinct target IDs | 67 | 87 |
| Distinct parent SRs | 40 | 46 |
| Target Top-5 share | 28.3554 | 37.4757 |
| Target Top-10 share | 45.9357 | 55.7836 |
| Parent SR Top-5 share | 40.0756 | 42.1082 |
| Parent SR Top-10 share | 62.7599 | 64.7434 |
| Target HHI | 0.0313 | 0.0427 |
| Parent SR HHI | 0.0535 | 0.0559 |

## Interpretation Notes

- `target_id` mede concentração no nível do requisito IEC individual.
- `parent_sr` agrega cada RE ao seu SR pai, permitindo medir concentração por requisito de segurança.
- Para um target que já é um SR, o próprio `target_id` é utilizado como `parent_sr` efetivo.
- HHI e Gini maiores indicam maior concentração.
- Entropia normalizada maior indica distribuição mais diversificada.
- Top-N share mostra qual fração de todos os candidatos está concentrada nos N targets mais frequentes.
