
import pandas as pd
import streamlit as st
from io import BytesIO


def show_dashboard(
    documents,
    chunks,
    vector_index,
    question_history
):
    """Display knowledge-base dashboard metrics."""

    st.header("📊 Knowledge Base Dashboard")

    total_documents = len(documents)
    total_chunks = len(chunks)

    total_vectors = (
        vector_index.ntotal
        if vector_index is not None
        else 0
    )

    total_questions = len(question_history)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Documents", total_documents)
    col2.metric("Chunks", total_chunks)
    col3.metric("Stored Vectors", total_vectors)
    col4.metric("Questions Asked", total_questions)

    st.subheader("📚 Document Overview")

    if documents:
        document_rows = []

        for document in documents:
            document_rows.append({
                "Filename": document.get("filename", ""),
                "Type": document.get("file_type", ""),
                "Status": document.get(
                    "extraction_status",
                    "Not processed"
                )
            })

        st.dataframe(
            pd.DataFrame(document_rows),
            use_container_width=True
        )

    else:
        st.info(
            "No documents have been uploaded in this session."
        )

    st.subheader("🔎 Question History")

    if question_history:
        st.dataframe(
            pd.DataFrame(question_history),
            use_container_width=True
        )
    else:
        st.info("No questions asked in this session yet.")


def generate_excel_report(
    documents,
    chunks,
    question_history
):
    """Generate an Excel report of the knowledge base."""

    output = BytesIO()

    document_rows = []

    for document in documents:
        document_rows.append({
            "Filename": document.get("filename", ""),
            "File Type": document.get("file_type", ""),
            "Extraction Status": document.get(
                "extraction_status",
                "Not processed"
            )
        })

    chunk_rows = []

    for chunk in chunks:
        chunk_rows.append({
            "Filename": chunk.get("filename", ""),
            "Page": chunk.get("page", ""),
            "Chunk Number": chunk.get("chunk_number", ""),
            "Content": chunk.get("text", "")
        })

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        pd.DataFrame(document_rows).to_excel(
            writer,
            sheet_name="Documents",
            index=False
        )

        pd.DataFrame(chunk_rows).to_excel(
            writer,
            sheet_name="Document Chunks",
            index=False
        )

        pd.DataFrame(question_history).to_excel(
            writer,
            sheet_name="Question History",
            index=False
        )

        for worksheet in writer.sheets.values():
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions

            for column_cells in worksheet.columns:
                max_length = max(
                    len(str(cell.value or ""))
                    for cell in column_cells
                )

                worksheet.column_dimensions[
                    column_cells[0].column_letter
                ].width = min(max_length + 2, 50)

    output.seek(0)

    return output
