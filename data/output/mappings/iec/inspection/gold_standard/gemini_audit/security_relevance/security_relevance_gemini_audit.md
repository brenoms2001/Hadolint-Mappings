# Gemini Security Relevance Audit

## Purpose

This is a preliminary Gemini audit of the security relevance of the 594 Hadolint/ShellCheck source rules. It is an auxiliary analysis and does not define the gold standard.

Human review remains authoritative.

## Rule classification

- Total rules: 594
- Security-related: 86
- Non-security: 504
- Uncertain: 4

## Gemini candidate associations

| Security classification | Verdict | Associations |
|---|---:|---:|
| non_security | MAYBE | 366 |
| non_security | NO | 3085 |
| non_security | YES | 41 |
| security_related | MAYBE | 115 |
| security_related | NO | 450 |
| security_related | YES | 37 |
| uncertain | NO | 40 |

## Interpretation

The security classification is evaluated at the source-rule level, whereas YES/MAYBE/NO is evaluated at the rule-to-IEC-candidate level. Therefore, these two dimensions must not be treated as interchangeable.

A rule classified as security-related does not imply that any particular IEC 62443 candidate is relevant. Likewise, a non-security rule receiving a semantic candidate does not become a security rule because of that candidate.

Human review remains the final authority for the gold-standard associations.