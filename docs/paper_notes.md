# Paper Notes

## Claims currently supportable as preliminary/exploratory

### Candidate set

Under the definitive canonical matching execution:

- 595 source rules produced 4149 candidate associations.
- 566 associations came from Hadolint rules.
- 3583 came from ShellCheck rules.
- 2240 targeted SR.
- 1909 targeted RE.
- 0 source rules had zero candidates.

### Preliminary Gemini pair audit

For the historical 594-rule/4134-pair development candidate set, Gemini
classified:

- 78 pairs as YES
- 481 as MAYBE
- 3575 as NO

This is a historical preliminary LLM audit, not an audit of the definitive
4149-pair candidate set and not the human gold standard.

### Security relevance

An LLM-assisted rule-level classification identified:

- 86 security-related rules
- 504 non-security rules
- 4 uncertain rules

Until author validation is completed, avoid wording such as:

> "86 rules are security-related."

Prefer:

> "An LLM-assisted classification identified 86 of the 594 source rules as security-related."

### Exploratory cross-analysis

At rule level:

- 86.05% of preliminary security-related rules had at least one YES/MAYBE association.
- 58.73% of preliminary non-security rules had at least one YES/MAYBE association.
- coverage ratio ≈ 1.465.

Mean positive-candidate rate:

- security-related: 30.45%
- non-security: 16.43%
- ratio ≈ 1.853.

Median positive-candidate rate:

- security-related: 26.79%
- non-security: 10.00%.

These results are exploratory because both dimensions currently involve Gemini and may share common-model bias.

## Threats to validity to preserve

- Gemini is not independent human validation.
- Pair observations are clustered by source rule.
- Security-relevance classification is preliminary until author-reviewed.
- Candidate findings depend on the canonical matching configuration.
- Human labels cannot automatically be transferred to a different candidate-generation configuration.
- Prompt/model behavior may affect LLM-assisted analyses.
