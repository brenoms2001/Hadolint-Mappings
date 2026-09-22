# IEC 62443-3-3 Gold Standard Sample

Dataset gerado para avaliação humana dos candidatos de mapeamento semântico.

## Matching configuration

- Standard: `IEC 62443-3-3`
- Threshold: `0.68`
- Top-K: `10`
- Power: `5.5`

## Sampling configuration

- Random seed: `42`
- Hadolint rules: `25`
- ShellCheck rules: `50`
- Candidate records: `531`

## Summary

| Source | Rules | Candidates | Avg candidates/rule |
|---|---:|---:|---:|
| hadolint | 25 | 172 | 6.88 |
| shellcheck | 50 | 359 | 7.18 |

## Gap stratification

| Gap bin | Rules |
|---|---:|
| very_low_gap | 24 |
| low_gap | 17 |
| medium_gap | 20 |
| high_gap | 9 |

## Target type distribution

| Target type | Candidates |
|---|---:|
| SR | 314 |
| RE | 217 |

## Sampled rules

### HADOLINT

| Rule | Candidates | Top1 | Top1-Top2 gap | Gap bin |
|---|---:|---:|---:|---|
| DL3003 | 3 | 1.0000 | 0.1350 | medium_gap |
| DL3004 | 4 | 1.0000 | 0.1780 | medium_gap |
| DL3005 | 10 | 1.0000 | 0.0230 | very_low_gap |
| DL3016 | 10 | 1.0000 | 0.1339 | medium_gap |
| DL3025 | 7 | 1.0000 | 0.1105 | medium_gap |
| DL3031 | 8 | 1.0000 | 0.0672 | low_gap |
| DL3032 | 10 | 1.0000 | 0.0753 | low_gap |
| DL3033 | 2 | 1.0000 | 0.2613 | high_gap |
| DL3034 | 10 | 1.0000 | 0.0815 | low_gap |
| DL3036 | 4 | 1.0000 | 0.2273 | high_gap |
| DL3039 | 4 | 1.0000 | 0.1189 | medium_gap |
| DL3047 | 10 | 1.0000 | 0.0949 | low_gap |
| DL3051 | 3 | 1.0000 | 0.0253 | very_low_gap |
| DL3052 | 10 | 1.0000 | 0.0291 | very_low_gap |
| DL3053 | 1 | 1.0000 | N/A | no_gap |
| DL3055 | 10 | 1.0000 | 0.0337 | very_low_gap |
| DL3058 | 2 | 1.0000 | 0.2674 | high_gap |
| DL3059 | 5 | 1.0000 | 0.1830 | medium_gap |
| DL3060 | 10 | 1.0000 | 0.0117 | very_low_gap |
| DL3061 | 10 | 1.0000 | 0.0265 | very_low_gap |
| DL3063 | 10 | 1.0000 | 0.0081 | very_low_gap |
| DL3064 | 10 | 1.0000 | 0.0757 | low_gap |
| DL3066 | 9 | 1.0000 | 0.0086 | very_low_gap |
| DL3067 | 1 | 1.0000 | N/A | no_gap |
| DL4000 | 9 | 1.0000 | 0.0869 | low_gap |

### SHELLCHECK

| Rule | Candidates | Top1 | Top1-Top2 gap | Gap bin |
|---|---:|---:|---:|---|
| SC1016 | 4 | 1.0000 | 0.1874 | medium_gap |
| SC1027 | 6 | 1.0000 | 0.1418 | medium_gap |
| SC1028 | 6 | 1.0000 | 0.1452 | medium_gap |
| SC1037 | 10 | 1.0000 | 0.1688 | medium_gap |
| SC1040 | 4 | 1.0000 | 0.1137 | medium_gap |
| SC1043 | 3 | 1.0000 | 0.2290 | high_gap |
| SC1055 | 10 | 1.0000 | 0.0901 | low_gap |
| SC1060 | 10 | 1.0000 | 0.0307 | very_low_gap |
| SC1065 | 9 | 1.0000 | 0.0335 | very_low_gap |
| SC1083 | 5 | 1.0000 | 0.2034 | high_gap |
| SC1100 | 8 | 1.0000 | 0.0691 | low_gap |
| SC1105 | 10 | 1.0000 | 0.0345 | very_low_gap |
| SC1107 | 8 | 1.0000 | 0.1080 | medium_gap |
| SC1110 | 2 | 1.0000 | 0.2649 | high_gap |
| SC1131 | 10 | 1.0000 | 0.0175 | very_low_gap |
| SC1135 | 3 | 1.0000 | 0.2286 | high_gap |
| SC1141 | 7 | 1.0000 | 0.0263 | very_low_gap |
| SC1142 | 10 | 1.0000 | 0.0312 | very_low_gap |
| SC2001 | 4 | 1.0000 | 0.2267 | high_gap |
| SC2009 | 10 | 1.0000 | 0.1438 | medium_gap |
| SC2010 | 5 | 1.0000 | 0.0772 | low_gap |
| SC2024 | 10 | 1.0000 | 0.1095 | medium_gap |
| SC2033 | 6 | 1.0000 | 0.1360 | medium_gap |
| SC2045 | 10 | 1.0000 | 0.0121 | very_low_gap |
| SC2060 | 5 | 1.0000 | 0.1630 | medium_gap |
| SC2110 | 10 | 1.0000 | 0.0807 | low_gap |
| SC2114 | 2 | 1.0000 | 0.2553 | high_gap |
| SC2115 | 9 | 1.0000 | 0.0935 | low_gap |
| SC2123 | 6 | 1.0000 | 0.0363 | very_low_gap |
| SC2126 | 10 | 1.0000 | 0.0887 | low_gap |
| SC2140 | 10 | 1.0000 | 0.0783 | low_gap |
| SC2154 | 7 | 1.0000 | 0.1013 | medium_gap |
| SC2206 | 1 | 1.0000 | N/A | no_gap |
| SC2212 | 10 | 1.0000 | 0.0443 | very_low_gap |
| SC2226 | 5 | 1.0000 | 0.1322 | medium_gap |
| SC2247 | 1 | 1.0000 | N/A | no_gap |
| SC2267 | 10 | 1.0000 | 0.0421 | very_low_gap |
| SC2293 | 7 | 1.0000 | 0.0776 | low_gap |
| SC2312 | 10 | 1.0000 | 0.0231 | very_low_gap |
| SC2316 | 10 | 1.0000 | 0.0648 | low_gap |
| SC2319 | 5 | 1.0000 | 0.1319 | medium_gap |
| SC2326 | 6 | 1.0000 | 0.1989 | medium_gap |
| SC3014 | 10 | 1.0000 | 0.0503 | low_gap |
| SC3018 | 10 | 1.0000 | 0.0116 | very_low_gap |
| SC3024 | 8 | 1.0000 | 0.0171 | very_low_gap |
| SC3030 | 6 | 1.0000 | 0.0750 | low_gap |
| SC3035 | 10 | 1.0000 | 0.0073 | very_low_gap |
| SC3040 | 1 | 1.0000 | N/A | no_gap |
| SC3041 | 10 | 1.0000 | 0.0275 | very_low_gap |
| SC3042 | 10 | 1.0000 | 0.0335 | very_low_gap |

## Human annotation

Cada candidato deve receber uma das seguintes classificações:

- `relevant` — relação direta e semanticamente defensável.
- `partially_relevant` — relação plausível, mas incompleta, indireta ou dependente de interpretação.
- `irrelevant` — ausência de relação relevante.

A avaliação deve considerar o significado da regra de origem e do requisito IEC, e não apenas a similaridade lexical.

Amostragem reproduzível através do `RANDOM_SEED = 42`.
