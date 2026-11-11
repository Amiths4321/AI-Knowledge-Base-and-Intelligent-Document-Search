
import hashlib
import streamlit as st


def initialize_documents():
    """Initialize the uploaded-document collection."""
    if "uploaded_documents" not in st.session_state:
        st.session_state["uploaded_documents"] = []


def display_document_upload():
    """Display the multiple-document upload interface."""

    st.header("📤 Upload Company Documents")

    uploaded_files = st.file_uploader(
        "Select PDF or TXT documents",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        help="You can select multiple PDF and TXT files."
    )

    if st.button("Add Documents", type="primary"):
        if not uploaded_files:
            st.warning("Please select at least one document.")
        else:
            added_count = 0
            duplicate_count = 0

            for uploaded_file in uploaded_files:
                file_bytes = uploaded_file.getvalue()

                # Create a unique identifier using the file content.
                document_id = hashlib.sha256(file_bytes).hexdigest()

                existing_ids = {
                    doc["id"]
                    for doc in st.session_state["uploaded_documents"]
                }

                if document_id in existing_ids:
                    duplicate_count += 1
                    continue

                document = {
                    "id": document_id,
                    "filename": uploaded_file.name,
                    "file_type": uploaded_file.name.split(".")[-1].lower(),
                    "size_bytes": len(file_bytes),
                    "file_bytes": file_bytes
                }

                st.session_state["uploaded_documents"].append(document)
                added_count += 1

            if added_count:
                st.success(f"{added_count} document(s) added successfully.")

            if duplicate_count:
                st.info(f"{duplicate_count} duplicate document(s) skipped.")

    st.divider()
    st.subheader("📚 Uploaded Documents")

    documents = st.session_state["uploaded_documents"]

    if not documents:
        st.info("No documents uploaded yet.")
        return

    for document in list(documents):
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.write(f"📄 **{document['filename']}**")
            st.caption(
                f"Type: {document['file_type'].upper()} | "
                f"Size: {document['size_bytes'] / 1024:.2f} KB"
            )

        with col2:
            st.write("Uploaded")

        with col3:
            if st.button(
                "Remove",
                key=f"remove_{document['id']}"
            ):
                st.session_state["uploaded_documents"] = [
                    doc
                    for doc in st.session_state["uploaded_documents"]
                    if doc["id"] != document["id"]
                ]
                st.rerun()
