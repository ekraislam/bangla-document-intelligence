import streamlit as st
from PIL import Image
import io
import config
from src.pdf_processor import pdf_to_images, load_image
from src.ocr_engine import BanglaOCREngine
from src.utils import save_extracted_text, search_and_highlight

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Bangla Document Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# 2. Minimalist Theme CSS
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    /* Google Fonts for clean Bengali & English typography */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Noto+Sans+Bengali:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Noto Sans Bengali', sans-serif;
        background-color: #0f172a;
        color: #f8fafc;
    }

    /* Container padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }

    /* Empty state card styling */
    .empty-workspace-card {
        background-color: #1e293b;
        border: 1px dashed rgba(148, 163, 184, 0.25);
        border-radius: 12px;
        padding: 40px 20px;
        text-align: center;
        margin-top: 15px;
    }

    .empty-workspace-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 6px;
    }

    .empty-workspace-sub {
        font-size: 0.9rem;
        color: #94a3b8;
    }

    /* Search Results Container */
    .search-panel {
        background-color: #0b1329;
        color: #e2e8f0;
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 10px;
        padding: 16px;
        max-height: 280px;
        overflow-y: auto;
        font-family: 'Noto Sans Bengali', 'Plus Jakarta Sans', sans-serif;
        white-space: pre-wrap;
        line-height: 1.7;
        font-size: 0.95rem;
    }

    /* Primary button override */
    .stButton > button[kind="primary"] {
        background-color: #2563eb !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #1d4ed8 !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 3. Helper Functions & Cache
# -----------------------------------------------------------------------------
def format_bytes(size_in_bytes: int) -> str:
    """Format file size into human-readable string (KB / MB)."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} Bytes"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"


@st.cache_resource
def get_ocr_engine():
    """Lazy load and cache EasyOCR engine."""
    return BanglaOCREngine(languages=config.OCR_LANGUAGES, gpu=config.USE_GPU)


# -----------------------------------------------------------------------------
# 4. Main Application Interface
# -----------------------------------------------------------------------------
def main():
    # Header Section
    st.title("Bangla Document Intelligence")
    st.caption("Extract readable text from Bangla PDF and image documents.")
    st.markdown("---")

    # Document Upload Section
    uploaded_file = st.file_uploader(
        "Upload PDF or Image",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Select a Bangla PDF file or scanned document image."
    )

    # Empty State: No Document Uploaded
    if uploaded_file is None:
        st.markdown("""
        <div class="empty-workspace-card">
            <div class="empty-workspace-title">Workspace Ready</div>
            <div class="empty-workspace-sub">Upload a PDF or image file above to begin text extraction.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Process Document Bytes & Metadata
    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name
    file_size_str = format_bytes(len(file_bytes))
    file_ext = file_name.split(".")[-1].upper()

    with st.spinner("Loading document pages..."):
        if file_ext.lower() == "pdf":
            images = pdf_to_images(file_bytes)
        else:
            img = load_image(file_bytes)
            images = [img]

    # File Metadata Bar
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("File Name", file_name)
    m2.metric("File Type", file_ext)
    m3.metric("File Size", file_size_str)
    m4.metric("Page Count", len(images))

    st.markdown("---")

    # Main Workspace (Two-Column Layout)
    col1, col2 = st.columns([1, 1], gap="large")

    # --- LEFT: Document Preview ---
    with col1:
        st.subheader("Document Preview")
        if len(images) > 1:
            page_idx = st.slider("Select Page", 1, len(images), 1) - 1
        else:
            page_idx = 0

        st.image(
            images[page_idx],
            caption=f"Page {page_idx + 1} of {len(images)}",
            width="stretch"
        )

    # --- RIGHT: Extracted Text & Actions ---
    with col2:
        st.subheader("Extracted Text")

        if st.button("Extract Text", type="primary", width="stretch"):
            with st.spinner("Extracting text..."):
                ocr = get_ocr_engine()
                results = ocr.process_document_pages(images)
                extracted_text = results["full_text"]

                st.session_state["extracted_text"] = extracted_text
                st.session_state["extracted_file_name"] = file_name

                saved_path = save_extracted_text(extracted_text, file_name)
                st.session_state["saved_path"] = saved_path

        # If OCR has been run for current document
        if "extracted_text" in st.session_state and st.session_state.get("extracted_file_name") == file_name:
            extracted_text = st.session_state["extracted_text"]

            # Statistics (Calculated from actual text)
            char_count = len(extracted_text)
            word_count = len(extracted_text.split())
            line_count = len([line for line in extracted_text.splitlines() if line.strip()])

            s1, s2, s3 = st.columns(3)
            s1.metric("Character Count", f"{char_count:,}")
            s2.metric("Word Count", f"{word_count:,}")
            s3.metric("Line Count", f"{line_count:,}")

            edited_text = st.text_area(
                "Extracted Text Editor",
                value=extracted_text,
                height=280,
                label_visibility="collapsed"
            )

            # Simple Action Buttons
            btn1, btn2, btn3 = st.columns([1, 1, 1])
            with btn1:
                with st.expander("Copy"):
                    st.code(edited_text, language="text")
            with btn2:
                st.download_button(
                    label="Download TXT",
                    data=edited_text,
                    file_name=f"extracted_{file_name}.txt",
                    mime="text/plain",
                    width="stretch"
                )
            with btn3:
                if st.button("Clear", width="stretch"):
                    st.session_state.pop("extracted_text", None)
                    st.session_state.pop("saved_path", None)
                    st.rerun()

            # Search Section
            st.markdown("---")
            st.subheader("Search in Document")

            search_query = st.text_input(
                "Search in Document",
                placeholder="Search Bangla or English words...",
                label_visibility="collapsed",
                key="search_query_input"
            )

            if search_query:
                highlighted_html, count = search_and_highlight(edited_text, search_query)

                if count > 0:
                    st.success(f"Found **{count}** match{'es' if count > 1 else ''} for '{search_query}'")
                else:
                    st.warning(f"No matches found for '{search_query}'")

                st.markdown(
                    f'<div class="search-panel">{highlighted_html}</div>',
                    unsafe_allow_html=True
                )


if __name__ == "__main__":
    main()
