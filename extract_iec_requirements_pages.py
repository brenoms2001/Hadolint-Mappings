import os
import pymupdf


INPUT_PDF = "./data/input/iec62443/iec-62443-3-3.pdf"

OUTPUT_DIR = "./data/output/datasets"

OUTPUT_PDF = os.path.join(
    OUTPUT_DIR,
    "iec62443_requirements_full.pdf"
)


# ============================================================
# IMPORTANT
# ============================================================
#
# These are PDF page numbers, not IEC printed page numbers.
#
# The PDF contains 90 pages.
#
# PDF pages 34–73 contain the FR/SR/RE normative material.
#
# IEC printed pages are approximately 25–64.
# ============================================================

START_PAGE = 28
END_PAGE = 80


def main():

    print(
        "📄 Opening IEC 62443-3-3 PDF..."
    )

    if not os.path.exists(INPUT_PDF):

        raise FileNotFoundError(
            f"PDF not found: {INPUT_PDF}"
        )

    source = pymupdf.open(
        INPUT_PDF
    )

    print(
        f"📚 Original PDF: "
        f"{len(source)} pages"
    )

    print(
        f"✂️ Extracting PDF pages "
        f"{START_PAGE}–{END_PAGE}..."
    )

    output = pymupdf.open()

    # PyMuPDF uses zero-based page indices.
    output.insert_pdf(
        source,
        from_page=START_PAGE - 1,
        to_page=END_PAGE - 1
    )

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    output.save(
        OUTPUT_PDF
    )

    output.close()
    source.close()

    print(
        "\n✅ Requirement corpus created:"
    )

    print(
        f"   {OUTPUT_PDF}"
    )

    print(
        f"📄 Pages copied: "
        f"{END_PAGE - START_PAGE + 1}"
    )


if __name__ == "__main__":
    main()