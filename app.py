import streamlit as st
from PIL import Image
import io
import time
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
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. Custom CSS Theme (Dark Premium AI SaaS Aesthetic)
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Noto+Sans+Bengali:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Noto Sans Bengali', sans-serif;
        background-color: #0b0f19;
        color: #f1f5f9;
    }

    /* Main Container Spacing */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Hero Banner Styling */
    .hero-container {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 27, 75, 0.9) 50%, rgba(14, 165, 233, 0.15) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 20px;
        padding: 32px 36px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
    }

    .hero-top-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
        flex-wrap: wrap;
        gap: 12px;
    }

    .badge-group {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .tech-pill {
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(129, 140, 248, 0.3);
        color: #c7d2fe;
        font-size: 0.76rem;
        font-weight: 700;
        padding: 5px 12px;
        border-radius: 9999px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .status-indicator {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(52, 211, 153, 0.3);
        color: #34d399;
        font-size: 0.82rem;
        font-weight: 700;
        padding: 5px 14px;
        border-radius: 9999px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .hero-main-title {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin: 0 0 8px 0;
        background: linear-gradient(to right, #ffffff, #e2e8f0, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-sub-title {
        font-size: 1.05rem;
        color: #94a3b8;
        max-width: 800px;
        margin: 0;
        line-height: 1.6;
    }

    /* Info Cards */
    .info-card-container {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 16px;
        padding: 16px 22px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
        box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.3);
    }

    .info-item {
        display: flex;
        flex-direction: column;
    }

    .info-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .info-val {
        font-size: 0.98rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-top: 2px;
    }

    /* Stat Cards */
    .stat-card-box {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 14px;
        padding: 18px 12px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .stat-card-box:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.5);
    }
    .stat-card-val {
        font-size: 1.75rem;
        font-weight: 800;
        color: #38bdf8;
        line-height: 1.2;
    }
    .stat-card-lbl {
        font-size: 0.78rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }

    /* Text Area Styling */
    .stTextArea textarea {
        font-family: 'Noto Sans Bengali', 'JetBrains Mono', monospace !important;
        background-color: #060911 !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 14px !important;
        padding: 16px !important;
        font-size: 1rem !important;
        line-height: 1.7 !important;
    }

    /* Search Results Container */
    .search-results-panel {
        background-color: #060911;
        color: #e2e8f0;
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 14px;
        padding: 20px;
        max-height: 320px;
        overflow-y: auto;
        font-family: 'Noto Sans Bengali', 'Plus Jakarta Sans', sans-serif;
        white-space: pre-wrap;
        line-height: 1.75;
        font-size: 0.98rem;
    }

    /* Empty States Styling */
    .empty-state-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px dashed rgba(148, 163, 184, 0.25);
        border-radius: 16px;
        padding: 48px 24px;
        text-align: center;
        margin: 20px 0;
    }
    .empty-state-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 6px;
    }
    .empty-state-desc {
        font-size: 0.95rem;
        color: #94a3b8;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: #060911;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Primary Button Override */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%) !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 20px -5px rgba(79, 70, 229, 0.4) !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 14px 28px -6px rgba(6, 182, 212, 0.5) !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 3. Helper Functions & OCR Engine Cache
# -----------------------------------------------------------------------------
def format_bytes(size_in_bytes: int) -> str:
    """Format raw byte size into human-readable string (KB / MB)."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} Bytes"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"


@st.cache_resource
def get_ocr_engine():
    """Lazy-load and cache EasyOCR engine instance."""
    return BanglaOCREngine(languages=config.OCR_LANGUAGES, gpu=config.USE_GPU)


# -----------------------------------------------------------------------------
# 4. Main Application Interface
# -----------------------------------------------------------------------------
def main():
    # -------------------------------------------------------------------------
    # 1. TOP HERO SECTION
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="hero-container">
        <div class="hero-top-row">
            <div class="badge-group">
                <span class="tech-pill">Bangla OCR</span>
                <span class="tech-pill">EasyOCR</span>
                <span class="tech-pill">PDF Processing</span>
                <span class="tech-pill">Text Search</span>
                <span class="tech-pill">CPU Optimized</span>
            </div>
            <div class="status-indicator">● OCR Engine Ready</div>
        </div>
        <h1 class="hero-main-title">Bangla Document Intelligence</h1>
        <p class="hero-sub-title">
            Extract, understand and search Bangla documents with CPU-friendly OCR.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. SIDEBAR
    # -------------------------------------------------------------------------
    with st.sidebar:
        st.markdown("### 📄 Bangla Document Intelligence")
        st.success("🟢 **Status**: OCR Engine — Active")
        
        st.markdown("---")
        st.markdown("### ⚙️ System Information")
        st.markdown("""
        - **Processing Mode**: CPU
        - **Supported Languages**: Bangla + English
        - **Document Types**: PDF / PNG / JPG / JPEG
        """)

        st.markdown("---")
        st.markdown("### 🔄 Workflow Steps")
        st.markdown("""
        `01` Upload  
        `02` Preview  
        `03` OCR  
        `04` Review  
        `05` Search  
        `06` Export  
        """)

        st.markdown("---")
        st.markdown("### 🏗️ Architecture")
        st.caption("Document → PDF/Image Processor → EasyOCR → Text → Search")

    # -------------------------------------------------------------------------
    # 3. DOCUMENT UPLOAD CARD
    # -------------------------------------------------------------------------
    uploaded_file = st.file_uploader(
        "Drop your document here",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Upload a Bangla PDF or scanned image (PDF, PNG, JPG, JPEG)."
    )

    # -------------------------------------------------------------------------
    # 9. EMPTY STATES Handling (No Document Uploaded)
    # -------------------------------------------------------------------------
    if uploaded_file is None:
        st.markdown("""
        <div class="empty-state-card">
            <div class="empty-state-title">Your document workspace is ready</div>
            <div class="empty-state-desc">Upload a Bangla document to begin.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Document Processed & Loaded
    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name
    file_size_str = format_bytes(len(file_bytes))
    file_ext = file_name.split(".")[-1].upper()

    with st.spinner("Processing document layout..."):
        if file_ext.lower() == "pdf":
            images = pdf_to_images(file_bytes)
        else:
            img = load_image(file_bytes)
            images = [img]

    # File Information Card
    st.markdown(f"""
    <div class="info-card-container">
        <div class="info-item">
            <span class="info-label">File Name</span>
            <span class="info-val">📄 {file_name}</span>
        </div>
        <div class="info-item">
            <span class="info-label">File Type</span>
            <span class="info-val">🏷️ {file_ext}</span>
        </div>
        <div class="info-item">
            <span class="info-label">File Size</span>
            <span class="info-val">⚖️ {file_size_str}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Number of Pages</span>
            <span class="info-val">📑 {len(images)} Page{'s' if len(images) > 1 else ''}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Status</span>
            <span class="info-val" style="color: #34d399;">Ready for OCR</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 4. DOCUMENT WORKSPACE (Two-Column Layout)
    # -------------------------------------------------------------------------
    col1, col2 = st.columns([1, 1], gap="large")

    # --- LEFT: Document Preview ---
    with col1:
        st.markdown("### Document Preview")
        
        if len(images) > 1:
            page_idx = st.slider("Select Page", 1, len(images), 1) - 1
        else:
            page_idx = 0

        # Page Number Indicator & Image Preview
        st.image(
            images[page_idx],
            caption=f"Page {page_idx + 1} of {len(images)}",
            width="stretch"
        )

    # --- RIGHT: OCR Workspace ---
    with col2:
        st.markdown("### Extract Bangla Text")

        if st.button("✨ Run Bangla OCR", type="primary", width="stretch"):
            with st.spinner("Performing Bangla OCR extraction... (Please wait)"):
                ocr = get_ocr_engine()
                results = ocr.process_document_pages(images)
                extracted_text = results["full_text"]

                # Store in session state
                st.session_state["extracted_text"] = extracted_text
                st.session_state["extracted_file_name"] = file_name

                # Save UTF-8 text file using existing util
                saved_path = save_extracted_text(extracted_text, file_name)
                st.session_state["saved_path"] = saved_path

        # ---------------------------------------------------------------------
        # Empty State: Uploaded but OCR not run yet
        # ---------------------------------------------------------------------
        if "extracted_text" not in st.session_state or st.session_state.get("extracted_file_name") != file_name:
            st.markdown("""
            <div class="empty-state-card">
                <div class="empty-state-title">Ready for OCR extraction</div>
                <div class="empty-state-desc">Click Run Bangla OCR to extract text.</div>
            </div>
            """, unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # OCR Extracted Content Available
        # ---------------------------------------------------------------------
        if "extracted_text" in st.session_state and st.session_state.get("extracted_file_name") == file_name:
            extracted_text = st.session_state["extracted_text"]

            # -----------------------------------------------------------------
            # 5. OCR STATISTICS
            # -----------------------------------------------------------------
            char_count = len(extracted_text)
            word_count = len(extracted_text.split())
            line_count = len([line for line in extracted_text.splitlines() if line.strip()])
            page_count = len(images)

            st.markdown("---")
            st.markdown("#### OCR Statistics")
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

            with stat_col1:
                st.markdown(f"""
                <div class="stat-card-box">
                    <div class="stat-card-val">{char_count:,}</div>
                    <div class="stat-card-lbl">Characters</div>
                </div>
                """, unsafe_allow_html=True)
            with stat_col2:
                st.markdown(f"""
                <div class="stat-card-box">
                    <div class="stat-card-val">{word_count:,}</div>
                    <div class="stat-card-lbl">Words</div>
                </div>
                """, unsafe_allow_html=True)
            with stat_col3:
                st.markdown(f"""
                <div class="stat-card-box">
                    <div class="stat-card-val">{line_count:,}</div>
                    <div class="stat-card-lbl">Lines</div>
                </div>
                """, unsafe_allow_html=True)
            with stat_col4:
                st.markdown(f"""
                <div class="stat-card-box">
                    <div class="stat-card-val">{page_count}</div>
                    <div class="stat-card-lbl">Pages</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # -----------------------------------------------------------------
            # 6. EXTRACTED TEXT EDITOR
            # -----------------------------------------------------------------
            st.markdown("#### Extracted Text")
            st.caption("Review and edit the OCR output.")

            edited_text = st.text_area(
                "Extracted Text Editor",
                value=extracted_text,
                height=300,
                label_visibility="collapsed"
            )

            # -----------------------------------------------------------------
            # 7. ACTION BAR
            # -----------------------------------------------------------------
            action_col1, action_col2, action_col3 = st.columns([1, 1, 1])

            with action_col1:
                st.download_button(
                    label="📥 Download TXT",
                    data=edited_text,
                    file_name=f"extracted_{file_name}.txt",
                    mime="text/plain",
                    width="stretch"
                )
            with action_col2:
                with st.expander("📋 Copy Text"):
                    st.code(edited_text, language="text")
            with action_col3:
                if st.button("🗑️ Clear", width="stretch"):
                    st.session_state.pop("extracted_text", None)
                    st.session_state.pop("saved_path", None)
                    st.rerun()

            # -----------------------------------------------------------------
            # 8. SEARCH SECTION
            # -----------------------------------------------------------------
            st.markdown("---")
            st.markdown("### Search Inside Document")

            search_query = st.text_input(
                "Search query",
                placeholder="Search Bangla or English words...",
                label_visibility="collapsed",
                key="search_query_input"
            )

            if search_query:
                highlighted_html, count = search_and_highlight(edited_text, search_query)

                if count > 0:
                    st.success(f"Found **{count}** match{'es' if count > 1 else ''} for query: '{search_query}'")
                else:
                    st.warning(f"No matches found for query: '{search_query}'")

                st.markdown(
                    f'<div class="search-results-panel">{highlighted_html}</div>',
                    unsafe_allow_html=True
                )


if __name__ == "__main__":
    main()
