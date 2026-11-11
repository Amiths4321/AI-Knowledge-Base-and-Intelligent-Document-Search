
import fitz


def extract_pdf_text(file_bytes):
    """Extract text from all pages of a PDF."""
    extracted_pages = []

    pdf_document = fitz.open(
        stream=file_bytes,
        filetype="pdf"
    )

    try:
        for page_number, page in enumerate(pdf_document, start=1):
            page_text = page.get_text("text").strip()

            if page_text:
                extracted_pages.append({
                    "page": page_number,
                    "text": page_text
                })
    finally:
        pdf_document.close()

    return extracted_pages


def extract_txt_text(file_bytes):
    """Extract text from a TXT file."""
    text = file_bytes.decode("utf-8", errors="replace").strip()

    if not text:
        return []

    return [{
        "page": 1,
        "text": text
    }]


def process_document(document):
    """Extract and clean text from an uploaded document."""

    file_type = document["file_type"]
    file_bytes = document["file_bytes"]

    if file_type == "pdf":
        pages = extract_pdf_text(file_bytes)

    elif file_type == "txt":
        pages = extract_txt_text(file_bytes)

    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    # Normalize whitespace and remove empty text entries.
    cleaned_pages = []

    for page in pages:
        cleaned_text = " ".join(page["text"].split())

        if cleaned_text:
            cleaned_pages.append({
                "page": page["page"],
                "text": cleaned_text
            })

    return cleaned_pages
