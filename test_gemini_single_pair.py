import json

import audit_gold_standard_gemini as auditor


# ============================================================
# CONFIGURAÇÃO
# ============================================================

PAIR_ID = "hadolint:DL3012:rank_9:SR 1.7 RE 1"


# ============================================================
# PREPARAÇÃO
# ============================================================

print("=" * 70)
print("GEMINI SINGLE-PAIR DIAGNOSTIC")
print("=" * 70)

print("\nLoading input...")

input_data = auditor.load_input()

print("\nLoading datasets...")

hadolint_index, iec_index = (
    auditor.load_datasets()
)

print("\nBuilding candidate records...")

records = auditor.build_records(
    input_data,
    hadolint_index,
    iec_index,
)

print(
    f"Candidate records available: "
    f"{len(records)}"
)


# ============================================================
# LOCALIZAR O PAR
# ============================================================

matches = [
    record
    for record in records
    if record["pair_id"] == PAIR_ID
]

if not matches:
    raise RuntimeError(
        f"Pair not found:\n{PAIR_ID}"
    )

if len(matches) != 1:
    raise RuntimeError(
        f"Expected exactly one pair, "
        f"found {len(matches)}:\n{PAIR_ID}"
    )

record = matches[0]


# ============================================================
# MOSTRAR O CASO
# ============================================================

print("\n" + "=" * 70)
print("TARGET PAIR")
print("=" * 70)

print(f"Pair ID:      {record['pair_id']}")
print(f"Source:       {record['source']}")
print(f"Source ID:    {record['source_id']}")
print(f"Source title: {record['source_title']}")
print(f"Rank:         {record['rank']}")
print(f"Target:       {record['target_id']}")
print(f"Target title: {record['target_title']}")
print(f"Raw cosine:   {record['raw_cosine']}")
print(f"Relative:     {record['relative_score']}")

print("\nProblematic code:")
print(record["problematic_code"])

print("\nRationale:")
print(record["rationale"])

print("\nIEC requirement:")
print(record["target_text"])

print("\nIEC rationale:")
print(record["target_rationale"])


# ============================================================
# PROMPT
# ============================================================

# IMPORTANTE:
# Esta é exatamente a função usada pelo auditor principal.
# A única diferença é que o batch contém um único candidato.

prompt = auditor.build_prompt(
    [record]
)

print("\n" + "=" * 70)
print("PROMPT")
print("=" * 70)

print(
    f"Prompt length: {len(prompt)} characters"
)

print("\nBatch size: 1")


# ============================================================
# CHAMADA AO GEMINI
# ============================================================

print("\n" + "=" * 70)
print("CALLING GEMINI")
print("=" * 70)

print(
    f"Model: {auditor.MODEL_NAME}"
)

print(
    f"Temperature: {auditor.TEMPERATURE}"
)

try:

    response = auditor.client.models.generate_content(
        model=auditor.MODEL_NAME,
        contents=prompt,
        config=auditor.types.GenerateContentConfig(
            temperature=auditor.TEMPERATURE,
            response_mime_type="application/json",
            response_schema=(
                auditor.GEMINI_RESPONSE_SCHEMA
            ),
        ),
    )

except Exception as error:

    print("\n" + "=" * 70)
    print("API ERROR")
    print("=" * 70)

    print(
        f"{type(error).__name__}: {error}"
    )

    raise


# ============================================================
# RESPOSTA BRUTA
# ============================================================

print("\n" + "=" * 70)
print("RAW GEMINI RESPONSE")
print("=" * 70)

print(response.text)


# ============================================================
# PARSE
# ============================================================

try:

    results = json.loads(
        response.text
    )

except json.JSONDecodeError as error:

    print("\n" + "=" * 70)
    print("JSON PARSE ERROR")
    print("=" * 70)

    print(error)

    raise


# ============================================================
# MESMA VALIDAÇÃO DO AUDITOR
# ============================================================

print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)

try:

    auditor.validate_gemini_results(
        [record],
        results,
    )

except Exception as error:

    print(
        "\nVALIDATION FAILED:"
    )

    print(
        f"{type(error).__name__}: {error}"
    )

    print("\nParsed response:")

    print(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
        )
    )

    raise


# ============================================================
# SUCESSO
# ============================================================

print("\n" + "=" * 70)
print("RESULT")
print("=" * 70)

print(
    "SUCCESS: Gemini returned a valid "
    "result for the pair when evaluated alone."
)

print("\nResult:")

print(
    json.dumps(
        results,
        indent=2,
        ensure_ascii=False,
    )
)

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)