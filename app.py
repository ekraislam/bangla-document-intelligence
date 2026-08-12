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
    page_title="Bangla Document Intelligence — Claude Artifact UI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# 2. Claude AI Artifact Panel Model Design System (CSS Engine)
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Noto+Sans+Bengali:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Force Dark Canvas Viewport Overrides */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"] {
        background-color: #0b0b0e !important;
        color: #f4f4f5 !important;
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
        max-width: 1400px !important;
        background-color: #0b0b0e !important;
    }

    /* KEYFRAME ANIMATIONS */
    @keyframes titleShimmer {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes greenPulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 8px rgba(52, 211, 153, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
    }

    @keyframes panelFadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Claude Top Header Banner Card */
    .claude-banner-card {
        background: #141417;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.5);
        animation: panelFadeIn 0.5s ease-out forwards;
    }

    .claude-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        flex-wrap: wrap;
        gap: 12px;
    }

    .claude-brand-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin: 0;
        background: linear-gradient(90deg, #ffffff 0%, #e4e4e7 40%, #d97706 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: titleShimmer 8s ease infinite;
    }

    .claude-subtitle {
        font-size: 1rem;
        color: #a1a1aa;
        margin: 0;
        line-height: 1.6;
        max-width: 850px;
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
        gap: 8px;
    }

    .pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #34d399;
        animation: greenPulse 2s infinite;
    }

    /* Claude Split-Screen Panels */
    .claude-panel {
        background: #141417 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.5);
        animation: panelFadeIn 0.6s ease-out forwards;
    }

    /* Claude Artifact Output Panel Styling */
    .artifact-canvas-panel {
        background: #16161a !important;
        border: 1px solid rgba(217, 119, 6, 0.25) !important;
        border-radius: 22px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.6);
        animation: panelFadeIn 0.7s ease-out forwards;
    }

    .artifact-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 16px;
        border-b: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 20px;
    }

    .artifact-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(217, 119, 6, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.3);
        color: #f59e0b;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 8px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    /* Streamlit File Uploader Dark Override */
    [data-testid="stFileUploader"] {
        background-color: #18181c !important;
        border: 2px dashed rgba(217, 119, 6, 0.35) !important;
        border-radius: 16px !important;
        padding: 18px !important;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: rgba(245, 158, 11, 0.6) !important;
    }

    [data-testid="stFileUploader"] section {
        background-color: transparent !important;
    }

    [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] p {
        color: #a1a1aa !important;
    }

    /* Metric Stat Cards Pill */
    .stat-pill-box {
        background: #1a1a1f !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px;
        padding: 16px 12px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .stat-pill-box:hover {
        transform: translateY(-2px);
        border-color: rgba(245, 158, 11, 0.4) !important;
    }

    .stat-pill-val {
        font-size: 1.65rem;
        font-weight: 800;
        color: #f59e0b !important;
        line-height: 1.2;
    }

    .stat-pill-lbl {
        font-size: 0.75rem;
        color: #a1a1aa !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }

    /* Primary Glowing Button (Claude Warm Amber Gradient) */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 20px -4px rgba(217, 119, 6, 0.45) !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 24px -4px rgba(245, 158, 11, 0.6) !important;
    }

    /* Monospace Text Area Reader */
    .stTextArea textarea {
        font-family: 'JetBrains Mono', 'Noto Sans Bengali', monospace !important;
        background-color: #0e0e11 !important;
        color: #f4f4f5 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 14px !important;
        padding: 18px !important;
        font-size: 0.98rem !important;
        line-height: 1.7 !important;
    }

    .stTextArea textarea:focus {
        border-color: #f59e0b !important;
        box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.25) !important;
    }

    /* Search Results Panel */
    .search-results-panel {
        background-color: #0e0e11;
        color: #f4f4f5;
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 14px;
        padding: 20px;
        max-height: 320px;
        overflow-y: auto;
        font-family: 'Noto Sans Bengali', sans-serif;
        white-space: pre-wrap;
        line-height: 1.75;
        font-size: 0.98rem;
    }

    /* High Contrast Rules */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    p, span, label {
        color: #e4e4e7;
    }

    [data-testid="stSidebar"] {
        background-color: #141417 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 3. Helper Functions & Cache
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
    """Lazy load and cache EasyOCR engine instance."""
    return BanglaOCREngine(languages=config.OCR_LANGUAGES, gpu=config.USE_GPU)


# -----------------------------------------------------------------------------
# 4. Main Application Interface
# -----------------------------------------------------------------------------
def main():
    # -------------------------------------------------------------------------
    # Top Claude Header Card
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="claude-banner-card">
        <div class="claude-header-row">
            <h1 class="claude-brand-title">Bangla Document Intelligence</h1>
            <span class="status-badge"><span class="pulse-dot"></span> EasyOCR Engine Ready</span>
        </div>
        <p class="claude-subtitle">
            Enterprise optical character recognition for Bangla and English documents. Extract structured, editable text from multi-page PDFs or image scans with real-time in-memory keyword search.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Clean Sidebar (System Overview)
    with st.sidebar:
        st.markdown("<h3 style='margin-bottom: 4px;'>📄 System Overview</h3>", unsafe_allow_html=True)
        st.caption("Bangla Document Intelligence v2.5")
        st.markdown("---")
        st.markdown("""
        <div style="font-size: 0.88rem; color: #a1a1aa; line-height: 1.8;">
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

        # File Metadata Grid (100% Real Calculated Data)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("File Name", file_name)
        m2.metric("File Format", file_ext)
        m3.metric("File Size", file_size_str)
        m4.metric("Total Pages", len(images))

        st.markdown("---")

        # -------------------------------------------------------------------------
        # Claude Split-Screen Artifact Panel Workspace (Two Columns)
        # -------------------------------------------------------------------------
        col1, col2 = st.columns([1, 1], gap="large")

        # --- LEFT PANEL: Input Document & Viewport ---
        with col1:
            st.markdown('<div class="claude-panel">', unsafe_allow_html=True)
            st.markdown("<h3 style='margin-top: 0;'>📄 Input Viewport</h3>", unsafe_allow_html=True)

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

        # --- RIGHT PANEL: Claude Artifact Output Canvas ---
        with col2:
            st.markdown('<div class="artifact-canvas-panel">', unsafe_allow_html=True)
            
            # ARTIFACT HEADER BAR
            st.markdown("""
            <div class="artifact-header-bar">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="artifact-tag">✦ Artifact Canvas</span>
                    <h3 style="margin: 0; font-size: 1.1rem;">Extracted Intelligence</h3>
                </div>
            </div>
            """, unsafe_allow_html=True)

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

                # Real Document Statistics Dashboard (100% Real Data)
                char_count = len(extracted_text)
                word_count = len(extracted_text.split())
                line_count = len([line for line in extracted_text.splitlines() if line.strip()])
                page_count = len(images)

                st.markdown("##### 📊 Artifact Document Statistics")
                s1, s2, s3, s4 = st.columns(4)

                with s1:
                    st.markdown(f"""
                    <div class="stat-pill-box">
                        <div class="stat-pill-val">{char_count:,}</div>
                        <div class="stat-pill-lbl">Characters</div>
                    </div>
                    """, unsafe_allow_html=True)
                with s2:
                    st.markdown(f"""
                    <div class="stat-pill-box">
                        <div class="stat-pill-val">{word_count:,}</div>
                        <div class="stat-pill-lbl">Words</div>
                    </div>
                    """, unsafe_allow_html=True)
                with s3:
                    st.markdown(f"""
                    <div class="stat-pill-box">
                        <div class="stat-pill-val">{line_count:,}</div>
                        <div class="stat-pill-lbl">Lines</div>
                    </div>
                    """, unsafe_allow_html=True)
                with s4:
                    st.markdown(f"""
                    <div class="stat-pill-box">
                        <div class="stat-pill-val">{page_count}</div>
                        <div class="stat-pill-lbl">Pages</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Editable Monospace Reader/Editor inside Artifact Canvas
                edited_text = st.text_area(
                    "Extracted Text Reader",
                    value=extracted_text,
                    height=280,
                    help="Edit extracted text directly inside this reader."
                )

                # Artifact Action Toolbar
                btn1, btn2, btn3 = st.columns([1, 1, 1])
                with btn1:
                    st.download_button(
                        label="📥 Export TXT",
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

                st.caption(f"💾 **Auto-Saved Output**: `{saved_path}`")

                # Search inside Artifact
                st.markdown("---")
                st.markdown("### 🔍 Search Inside Artifact")

                search_query = st.text_input(
                    "Search query",
                    placeholder="Enter Bangla (e.g. বাংলা) or English keyword...",
                    key="claude_artifact_search_input"
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
                    <p style="font-size: 0.92rem; color: #a1a1aa;">Click <strong>Extract Bangla Text</strong> above to generate artifact content.</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="claude-panel" style="text-align: center; padding: 48px 24px;">
            <h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 6px;">Document Workspace Ready</h3>
            <p style="font-size: 0.92rem; color: #a1a1aa; margin: 0;">Upload a Bangla PDF or scanned image file above to begin text extraction.</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
