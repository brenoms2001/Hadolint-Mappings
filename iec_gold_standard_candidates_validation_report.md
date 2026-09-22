# Validação estatística — IEC 62443 Gold Standard Candidates

## 1. Veredito

**Status estrutural: PASS**

- Regras de origem: **594** (75 Hadolint + 519 ShellCheck)
- Requisitos IEC disponíveis para validação: **100**
- Pares candidatos: **4134**
- Threshold relativo declarado: **0.68**
- Top-K declarado: **10**

Os testes verificaram contagem por regra, ranks, duplicidade de alvo, existência dos requisitos-alvo, monotonicidade dos scores, faixa dos scores e cumprimento do threshold.

## 2. Configuração registrada

- **standard**: IEC 62443-3-3
- **threshold**: 0.68
- **top_k**: 10
- **purpose**: Human evaluation dataset for semantic mapping candidates.
- **label_status**: unreviewed
- **labels**: ['relevant', 'partially_relevant', 'irrelevant']

> Observação: o arquivo completo registra `threshold` e `top_k`, mas não registra explicitamente `power` nem a descrição completa do método. Portanto, esses dois parâmetros não podem ser auditados somente a partir do `metadata` deste arquivo.

## 3. Distribuição por fonte

| Fonte | Regras | Candidatos | Média/regra | Mediana | Min | Max | Regras com 10 | Regras < 10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| hadolint | 75 | 529 | 7.05 | 9 | 1 | 10 | 35 | 40 |
| shellcheck | 519 | 3605 | 6.95 | 7 | 1 | 10 | 205 | 314 |

## 4. Scores

| Fonte | Raw cosine min | média | mediana | max | Relative min | média | mediana | max | ≥0.80 | ≥0.90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hadolint | 0.371513 | 0.463190 | 0.463346 | 0.600301 | 0.681119 | 0.837175 | 0.821522 | 1.000000 | 291 (55.0%) | 152 (28.7%) |
| shellcheck | 0.419098 | 0.501814 | 0.499316 | 0.627089 | 0.680029 | 0.833997 | 0.818630 | 1.000000 | 2011 (55.8%) | 1047 (29.0%) |

## 5. Tipo de requisito

| Tipo | Candidatos | Percentual |
|---|---:|---:|
| SR | 2214 | 53.6% |
| RE | 1920 | 46.4% |

## 6. Foundational Requirements

| FR | Candidatos | Percentual |
|---|---:|---:|
| 1 | 710 | 17.2% |
| 2 | 641 | 15.5% |
| 3 | 1641 | 39.7% |
| 4 | 155 | 3.7% |
| 5 | 455 | 11.0% |
| 6 | 14 | 0.3% |
| 7 | 518 | 12.5% |

## 7. Requisitos-alvo mais frequentes

| Rank | Target | Candidatos |
|---:|---|---:|
| 1 | SR 3.5 | 358 |
| 2 | SR 3.7 | 341 |
| 3 | SR 3.2 RE 1 | 280 |
| 4 | SR 5.2 RE 3 | 276 |
| 5 | SR 1.11 | 212 |
| 6 | SR 3.6 | 158 |
| 7 | SR 3.3 | 150 |
| 8 | SR 2.11 | 148 |
| 9 | SR 1.4 | 145 |
| 10 | SR 2.12 RE 1 | 137 |
| 11 | SR 7.1 | 107 |
| 12 | SR 7.3 | 106 |
| 13 | SR 7.1 RE 1 | 103 |
| 14 | SR 2.4 RE 1 | 102 |
| 15 | SR 1.5 RE 1 | 94 |
| 16 | SR 1.7 RE 1 | 90 |
| 17 | SR 4.2 RE 1 | 80 |
| 18 | SR 3.8 RE 3 | 72 |
| 19 | SR 3.2 | 71 |
| 20 | SR 7.7 | 68 |

## 8. Distribuição do número de candidatos por regra

### hadolint

| Nº candidatos | Nº regras |
|---:|---:|
| 1 | 7 |
| 2 | 4 |
| 3 | 4 |
| 4 | 6 |
| 5 | 5 |
| 6 | 4 |
| 7 | 5 |
| 8 | 1 |
| 9 | 4 |
| 10 | 35 |

### shellcheck

| Nº candidatos | Nº regras |
|---:|---:|
| 1 | 29 |
| 2 | 31 |
| 3 | 46 |
| 4 | 34 |
| 5 | 37 |
| 6 | 37 |
| 7 | 46 |
| 8 | 25 |
| 9 | 29 |
| 10 | 205 |

## 9. Regras com maior número de candidatos

| Fonte | Regra | Candidatos | Top-1 target | Top-1 relative | Último relative |
|---|---|---:|---|---:|---:|
| hadolint | DL1001 | 10 | SR 1.11 | 1.000000 | 0.819172 |
| hadolint | DL3000 | 10 | SR 7.3 | 1.000000 | 0.820691 |
| hadolint | DL3001 | 10 | SR 7.1 RE 1 | 1.000000 | 0.747061 |
| hadolint | DL3002 | 10 | SR 1.11 | 1.000000 | 0.693331 |
| hadolint | DL3005 | 10 | SR 3.2 | 1.000000 | 0.764202 |
| hadolint | DL3006 | 10 | SR 3.8 RE 3 | 1.000000 | 0.733333 |
| hadolint | DL3008 | 10 | SR 3.8 RE 3 | 1.000000 | 0.695620 |
| hadolint | DL3013 | 10 | SR 3.2 | 1.000000 | 0.811664 |
| hadolint | DL3016 | 10 | SR 1.9 | 1.000000 | 0.682696 |
| hadolint | DL3017 | 10 | SR 1.11 | 1.000000 | 0.717692 |
| hadolint | DL3019 | 10 | SR 7.5 | 1.000000 | 0.681937 |
| hadolint | DL3021 | 10 | SR 1.7 RE 1 | 1.000000 | 0.745898 |
| hadolint | DL3022 | 10 | SR 2.11 | 1.000000 | 0.783875 |
| hadolint | DL3023 | 10 | SR 7.3 | 1.000000 | 0.852467 |
| hadolint | DL3029 | 10 | SR 2.4 | 1.000000 | 0.739317 |
| hadolint | DL3032 | 10 | SR 3.3 | 1.000000 | 0.764389 |
| hadolint | DL3034 | 10 | SR 7.5 | 1.000000 | 0.730295 |
| hadolint | DL3037 | 10 | SR 3.2 | 1.000000 | 0.781207 |
| hadolint | DL3038 | 10 | SR 3.2 | 1.000000 | 0.754218 |
| hadolint | DL3040 | 10 | SR 4.2 | 1.000000 | 0.744491 |

## 10. Interpretação

- Todas as **594** regras possuem pelo menos um candidato.
- O conjunto final contém **4134** pares, contra 594 regras de origem.
- 2214 candidatos são SR e 1920 são RE.
- A maior concentração está no **FR 3**, com 1641 candidatos (39.7%).
- O requisito mais frequente é **SR 3.5**, com 358 ocorrências.
- O fato de muitos scores relativos ficarem próximos do threshold é esperado: o threshold é aplicado após normalização por regra, e o conjunto foi projetado para retenção dos candidatos semanticamente mais próximos.

## 11. Pontos de atenção antes do Gemini

1. **O conjunto está estruturalmente íntegro.** Não foram encontrados candidatos apontando para requisitos inexistentes, ranks inválidos, duplicatas por regra ou scores abaixo do threshold.
2. **O metadata é incompleto para reprodutibilidade independente.** Para uma auditoria futura, vale acrescentar `power` e `method` ao metadata do arquivo completo.
3. **`parent_sr` de SRs:** o arquivo de candidatos usa `null` para SRs, enquanto o arquivo `iec62443_with_rationale.json` atualmente contém o próprio SR em `parent_sr`. Isso é uma diferença de representação entre os datasets e não foi tratada como erro do candidato.
4. **O conjunto é adequado para iniciar a auditoria Gemini**, mas o Gemini continua sendo auditor preliminar; os rótulos humanos permanecem a referência para o gold standard.

## 12. Conclusão

**Recomendação: prosseguir para a auditoria Gemini do conjunto completo.** O arquivo passou pelas verificações estruturais realizadas e apresenta 4.134 associações candidatas válidas sob o threshold 0.68/top-K 10 registrado no próprio arquivo. Antes da execução completa, recomenda-se apenas registrar no metadata a potência 5.5 e o método exato, caso o arquivo seja usado como artefato final/publicável.
