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
# 2. Ultra-Stunning Glassmorphic Dark Design System (CSS Engine)
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    /* Import Google Fonts for Pristine English & Bengali Typography */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Noto+Sans+Bengali:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Force Dark Canvas Viewport Overrides */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"] {
        background-color: #07090e !important;
        color: #f8fafc !important;
        font-family: 'Plus Jakarta Sans', 'Noto Sans Bengali', sans-serif !important;
    }

    /* Completely Hide Streamlit Toolbar, Deploy Button & Header Bar */
    [data-testid="stHeader"], header, footer, #MainMenu, div[data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1380px !important;
        background-color: #07090e !important;
    }

    /* Hero Header Banner Card with Top Glowing Accent Bar */
    .hero-card {
        background: rgba(17, 22, 37, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 32px 36px;
        margin-bottom: 28px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
        position: relative;
        overflow: hidden;
    }

    .hero-accent-bar {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
    }

    .hero-top-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        flex-wrap: wrap;
        gap: 12px;
    }

    .hero-badge {
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(129, 140, 248, 0.3);
        color: #c7d2fe;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 5px 14px;
        border-radius: 9999px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .status-badge {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(52, 211, 153, 0.3);
        color: #34d399;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 5px 14px;
        border-radius: 9999px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin: 0 0 10px 0;
        background: linear-gradient(to right, #ffffff, #e2e8f0, #a855f7, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        font-size: 1.02rem;
        color: #94a3b8;
        margin: 0;
        line-height: 1.65;
        max-width: 850px;
    }

    /* Glass Panels */
    .glass-card {
        background: rgba(17, 22, 37, 0.75) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.5);
    }

    /* Streamlit File Uploader Dark Override */
    [data-testid="stFileUploader"] {
        background-color: rgba(11, 15, 25, 0.8) !important;
        border: 2px dashed rgba(99, 102, 241, 0.3) !important;
        border-radius: 18px !important;
        padding: 18px !important;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: rgba(129, 140, 248, 0.6) !important;
    }

    [data-testid="stFileUploader"] section {
        background-color: transparent !important;
    }

    [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] p {
        color: #94a3b8 !important;
    }

    /* Metric Stat Cards */
    .stat-card-box {
        background: rgba(11, 15, 25, 0.75) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 16px;
        padding: 18px 14px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .stat-card-box:hover {
        transform: translateY(-3px);
        border-color: rgba(168, 85, 247, 0.5) !important;
    }

    .stat-card-val {
        font-size: 1.75rem;
        font-weight: 800;
        color: #38bdf8 !important;
        line-height: 1.2;
    }

    .stat-card-lbl {
        font-size: 0.76rem;
        color: #94a3b8 !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }

    /* Primary Glowing Button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
        border-radius: 14px !important;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.45) !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 14px 30px -6px rgba(139, 92, 246, 0.6) !important;
    }

    /* Monospace Text Area */
    .stTextArea textarea {
        font-family: 'JetBrains Mono', 'Noto Sans Bengali', monospace !important;
        background-color: #080b13 !important;
        color: #f8fafc !important;
        border: 1px solid rgba(148, 163, 184, 0.25) !important;
        border-radius: 16px !important;
        padding: 18px !important;
        font-size: 0.98rem !important;
        line-height: 1.7 !important;
    }

    .stTextArea textarea:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.25) !important;
    }

    /* Search Results Container */
    .search-results-panel {
        background-color: #080b13;
        color: #f8fafc;
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 14px;
        padding: 20px;
        max-height: 320px;
        overflow-y: auto;
        font-family: 'Noto Sans Bengali', sans-serif;
        white-space: pre-wrap;
        line-height: 1.75;
        font-size: 0.98rem;
    }

    /* High Contrast Text Rules */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    p, span, label {
        color: #e2e8f0;
    }

    [data-testid="stSidebar"] {
        background-color: #0c0f1a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 3. Helper Functions & Engine Cache
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
    """Lazy load and cache EasyOCR engine instance."""
    return BanglaOCREngine(languages=config.OCR_LANGUAGES, gpu=config.USE_GPU)


# -----------------------------------------------------------------------------
# 4. Main Application Interface
# -----------------------------------------------------------------------------
def main():
    # -------------------------------------------------------------------------
    # Top Hero Header Banner
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="hero-card">
        <div class="hero-accent-bar"></div>
        <div class="hero-top-row">
            <span class="hero-badge">⚡ Intelligent Bangla Document Engine</span>
            <span class="status-badge">● EasyOCR Engine Ready</span>
        </div>
        <h1 class="hero-title">Bangla Document Intelligence</h1>
        <p class="hero-subtitle">
            High-precision optical character recognition for Bangla and English documents. Extract structured, editable text from multi-page PDFs or image scans with real-time in-memory keyword search.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Clean Sidebar (System Overview)
    with st.sidebar:
        st.markdown("<h3 style='margin-bottom: 4px;'>📄 System Overview</h3>", unsafe_allow_html=True)
        st.caption("Bangla Document Intelligence v2.5")
        st.markdown("---")
        st.markdown("""
        <div style="font-size: 0.88rem; color: #94a3b8; line-height: 1.8;">
            <div>• <strong>Mode</strong>: CPU Optimized</div>
            <div>• <strong>Languages</strong>: Bangla + English</div>
            <div>• <strong>Formats</strong>: PDF, PNG, JPG, JPEG</div>
            <div>• <strong>Storage</strong>: Local UTF-8 Output</div>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Drag-and-Drop Document Upload Section
    # -------------------------------------------------------------------------
    uploaded_file = st.file_uploader(
        "Upload PDF or Image Document",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Select a Bangla PDF or scanned image file."
    )

    # Empty State: No Document Uploaded
    if uploaded_file is not None:
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

        # File Metadata Grid (100% Real Data)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("File Name", file_name)
        m2.metric("File Format", file_ext)
        m3.metric("File Size", file_size_str)
        m4.metric("Total Pages", len(images))

        st.markdown("---")

        # -------------------------------------------------------------------------
        # Main Workspace Grid (Two Columns)
        # -------------------------------------------------------------------------
        col1, col2 = st.columns([1, 1], gap="large")

        # --- LEFT COLUMN: Document Viewport ---
        with col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("<h3 style='margin-top: 0;'>🖼️ Document Viewport</h3>", unsafe_allow_html=True)

            ctrl1, ctrl2 = st.columns([1, 1])
            with ctrl1:
                if len(images) > 1:
                    page_idx = st.slider("Select Page Viewport", 1, len(images), 1) - 1
                else:
                    page_idx = 0
            with ctrl2:
                zoom_level = st.slider("Viewport Zoom", 50, 200, 100, step=10, format="%d%%")

            preview_img = images[page_idx]
            if zoom_level != 100:
                new_w = int(preview_img.width * (zoom_level / 100.0))
                new_h = int(preview_img.height * (zoom_level / 100.0))
                display_img = preview_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            else:
                display_img = preview_img

            st.image(
                display_img,
                caption=f"Page {page_idx + 1} of {len(images)} ({file_name})",
                width="stretch"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        # --- RIGHT COLUMN: OCR Extraction & Intelligence ---
        with col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("<h3 style='margin-top: 0;'>📝 Extracted Intelligence</h3>", unsafe_allow_html=True)

            if st.button("✨ Extract Bangla Text", type="primary", width="stretch"):
                with st.spinner("Extracting Bangla & English text via EasyOCR... (Please wait)"):
                    ocr = get_ocr_engine()
                    results = ocr.process_document_pages(images)
                    extracted_text = results["full_text"]

                    st.session_state["extracted_text"] = extracted_text
                    st.session_state["extracted_file_name"] = file_name

                    saved_path = save_extracted_text(extracted_text, file_name)
                    st.session_state["saved_path"] = saved_path

            if "extracted_text" in st.session_state and st.session_state.get("extracted_file_name") == file_name:
                extracted_text = st.session_state["extracted_text"]
                saved_path = st.session_state.get("saved_path")

                st.success(f"✅ Extraction completed! Saved to `{saved_path.name}`")

                # OCR Statistics Dashboard (100% Real Calculated Data)
                char_count = len(extracted_text)
                word_count = len(extracted_text.split())
                line_count = len([line for line in extracted_text.splitlines() if line.strip()])
                page_count = len(images)

                st.markdown("##### 📊 Document Statistics")
                s1, s2, s3, s4 = st.columns(4)

                with s1:
                    st.markdown(f"""
                    <div class="stat-card-box">
                        <div class="stat-card-val">{char_count:,}</div>
                        <div class="stat-card-lbl">Characters</div>
                    </div>
                    """, unsafe_allow_html=True)
                with s2:
                    st.markdown(f"""
                    <div class="stat-card-box">
                        <div class="stat-card-val">{word_count:,}</div>
                        <div class="stat-card-lbl">Words</div>
                    </div>
                    """, unsafe_allow_html=True)
                with s3:
                    st.markdown(f"""
                    <div class="stat-card-box">
                        <div class="stat-card-val">{line_count:,}</div>
                        <div class="stat-card-lbl">Lines</div>
                    </div>
                    """, unsafe_allow_html=True)
                with s4:
                    st.markdown(f"""
                    <div class="stat-card-box">
                        <div class="stat-card-val">{page_count}</div>
                        <div class="stat-card-lbl">Pages</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Editable Monospace Reader/Editor
                edited_text = st.text_area(
                    "Extracted Text Editor",
                    value=extracted_text,
                    height=280,
                    help="Edit extracted text directly inside this editor."
                )

                # Action Toolbar
                btn1, btn2, btn3 = st.columns([1, 1, 1])
                with btn1:
                    st.download_button(
                        label="📥 Download TXT",
                        data=edited_text,
                        file_name=f"extracted_{file_name}.txt",
                        mime="text/plain",
                        width="stretch"
                    )
                with btn2:
                    with st.expander("📋 Copy Text"):
                        st.code(edited_text, language="text")
                with btn3:
                    if st.button("🗑️ Clear Workspace", width="stretch"):
                        st.session_state.pop("extracted_text", None)
                        st.session_state.pop("saved_path", None)
                        st.rerun()

                st.caption(f"💾 **Auto-Saved Path**: `{saved_path}`")

                # Real-Time Text Search Section
                st.markdown("---")
                st.markdown("### 🔍 Search Inside Document")

                search_query = st.text_input(
                    "Search query",
                    placeholder="Enter Bangla (e.g. বাংলা) or English keyword...",
                    key="search_ui_input"
                )

                if search_query:
                    highlighted_html, count = search_and_highlight(edited_text, search_query)

                    if count > 0:
                        st.success(f"Found **{count}** match{'es' if count > 1 else ''} for query: **'{search_query}'**")
                    else:
                        st.warning(f"No occurrences found for query: **'{search_query}'**")

                    st.markdown(
                        f'<div class="search-results-panel">{highlighted_html}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown("""
                <div style="text-align: center; padding: 36px 12px;">
                    <p style="font-size: 0.92rem; color: #94a3b8;">Click <strong>Extract Bangla Text</strong> above to process document pages.</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 48px 24px;">
            <h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 6px;">Document Workspace Ready</h3>
            <p style="font-size: 0.92rem; color: #94a3b8; margin: 0;">Upload a Bangla PDF or scanned image file above to begin text extraction.</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
