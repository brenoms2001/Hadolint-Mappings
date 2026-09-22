# Security Relevance — Rule-Level Analysis

This analysis aggregates Gemini candidate verdicts at the source-rule level.

A rule is considered to have positive candidate coverage when at least one of its IEC 62443 candidate associations was classified as YES or MAYBE by Gemini.

## Rule-level coverage

| Security classification | Rules | With YES/MAYBE | Without YES/MAYBE | Coverage |
|---|---:|---:|---:|---:|
| security_related | 86 | 74 | 12 | 86.05% |
| non_security | 504 | 296 | 208 | 58.73% |
| uncertain | 4 | 0 | 4 | 0.00% |

## Positive association rate per rule

| Security classification | Mean positive rate | Median positive rate |
|---|---:|---:|
| security_related | 30.45% | 26.79% |
| non_security | 16.43% | 10.00% |
| uncertain | 0.00% | 0.00% |

## Security-related vs non-security

- Rule positive-coverage ratio: `1.465115`
- Mean positive-rate ratio: `1.852953`
- Candidate-level YES-rate ratio: `5.234746`

These ratios are descriptive comparisons and are not statistical effect estimates.

## Rules with the most positive associations

| Rule | Classification | Candidates | YES | MAYBE | Positive | Positive rate |
|---|---|---:|---:|---:|---:|---:|
| SC2310 | security_related | 9 | 3 | 3 | 6 | 66.67% |
| SC2117 | security_related | 10 | 2 | 4 | 6 | 60.00% |
| DL3057 | security_related | 10 | 0 | 5 | 5 | 50.00% |
| DL3062 | security_related | 7 | 1 | 3 | 4 | 57.14% |
| DL3012 | non_security | 9 | 0 | 4 | 4 | 44.44% |
| SC1098 | security_related | 9 | 1 | 3 | 4 | 44.44% |
| SC2089 | security_related | 9 | 1 | 3 | 4 | 44.44% |
| SC2084 | non_security | 10 | 1 | 3 | 4 | 40.00% |
| SC2150 | security_related | 10 | 0 | 4 | 4 | 40.00% |
| SC2155 | non_security | 10 | 1 | 3 | 4 | 40.00% |
| SC2156 | security_related | 10 | 1 | 3 | 4 | 40.00% |
| SC2312 | security_related | 10 | 1 | 3 | 4 | 40.00% |
| SC2202 | non_security | 4 | 0 | 3 | 3 | 75.00% |
| SC2319 | non_security | 5 | 1 | 2 | 3 | 60.00% |
| SC2332 | non_security | 5 | 0 | 3 | 3 | 60.00% |
| SC2086 | security_related | 6 | 1 | 2 | 3 | 50.00% |
| DL3025 | security_related | 7 | 1 | 2 | 3 | 42.86% |
| SC2249 | security_related | 7 | 1 | 2 | 3 | 42.86% |
| SC2059 | security_related | 8 | 1 | 2 | 3 | 37.50% |
| SC2076 | non_security | 8 | 1 | 2 | 3 | 37.50% |
| SC1090 | non_security | 9 | 0 | 3 | 3 | 33.33% |
| SC2048 | security_related | 9 | 1 | 2 | 3 | 33.33% |
| SC2320 | non_security | 9 | 1 | 2 | 3 | 33.33% |
| DL1001 | non_security | 10 | 0 | 3 | 3 | 30.00% |
| DL3037 | security_related | 10 | 0 | 3 | 3 | 30.00% |
| DL3041 | security_related | 10 | 0 | 3 | 3 | 30.00% |
| DL3055 | non_security | 10 | 0 | 3 | 3 | 30.00% |
| SC2021 | non_security | 10 | 1 | 2 | 3 | 30.00% |
| SC2024 | security_related | 10 | 1 | 2 | 3 | 30.00% |
| SC2053 | security_related | 10 | 1 | 2 | 3 | 30.00% |
