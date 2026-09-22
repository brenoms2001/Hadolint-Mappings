import re

INPUT_FILE = "./data/output/datasets/iec62443_extraction_review.txt"
OUTPUT_FILE = "./data/output/datasets/iec62443_re_debug.txt"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    text = f.read()

lines = text.splitlines()

matches = []

for i, line in enumerate(lines):
    if re.search(r"\bRE\b|Requirement Enhancement", line, re.IGNORECASE):
        start = max(0, i - 5)
        end = min(len(lines), i + 11)

        context = "\n".join(
            f"{j+1:05d}: {lines[j]}"
            for j in range(start, end)
        )

        matches.append(
            "\n" + "=" * 100 + "\n"
            f"MATCH AT LINE {i+1}\n"
            + "=" * 100 + "\n"
            + context
        )

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(matches))

print(f"Found {len(matches)} lines containing RE-related markers.")
print(f"Saved diagnostic output to: {OUTPUT_FILE}")