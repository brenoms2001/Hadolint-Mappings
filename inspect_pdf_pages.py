import pymupdf
import os

PDF_PATH = "./data/input/iec62443/iec-62443-3-3.pdf"
OUTPUT = "./data/output/datasets/iec62443_page_index.txt"

doc = pymupdf.open(PDF_PATH)

os.makedirs(
    os.path.dirname(OUTPUT),
    exist_ok=True
)

with open(
    OUTPUT,
    "w",
    encoding="utf-8"
) as f:

    for page_number, page in enumerate(
        doc,
        start=1
    ):

        text = page.get_text("text")

        # Normalize line breaks only for the preview.
        preview = " ".join(
            text.split()
        )

        # Keep the preview reasonably short.
        preview = preview[:700]

        f.write(
            "\n"
            + "=" * 80
            + "\n"
        )

        f.write(
            f"PAGE {page_number}\n"
        )

        f.write(
            "=" * 80
            + "\n"
        )

        f.write(
            preview
            + "\n"
        )

doc.close()

print(
    f"✅ Page index generated:\n"
    f"   {OUTPUT}"
)