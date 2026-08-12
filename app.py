import streamlit as st
from PIL import Image
import config
from src.pdf_processor import pdf_to_images, load_image
from src.ocr_engine import BanglaOCREngine
from src.utils import save_extracted_text, search_and_highlight

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Bangla Document Intelligence Dashboard",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Custom CSS for Modern AI Dashboard & Glassmorphic UI
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Noto+Sans+Bengali:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Noto Sans Bengali', sans-serif;
    }

    /* Hero Section Header Card */
    .hero-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 32px;
        color: #ffffff;
        margin-bottom: 24px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.2);
    }
    
    .hero-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.25);
        border: 1px solid rgba(129, 140, 248, 0.4);
        color: #c7d2fe;
        font-size: 0.85rem;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 9999px;
        margin-bottom: 12px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0 0 10px 0;
        background: linear-gradient(to right, #ffffff, #c7d2fe, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        max-width: 800px;
        line-height: 1.6;
        margin: 0;
    }

    /* Glassmorphic Panel Cards */
    .glass-panel {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }

    /* Metric Stat Card */
    .stat-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        border-color: rgba(129, 140, 248, 0.5);
    }
    .stat-val {
        font-size: 1.7rem;
        font-weight: 700;
        color: #818cf8;
        margin-bottom: 4px;
    }
    .stat-lbl {
        font-size: 0.82rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Search Results Container */
    .search-results-box {
        background-color: #0f172a;
        color: #e2e8f0;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px;
        max-height: 320px;
        overflow-y: auto;
        font-family: 'Noto Sans Bengali', 'Plus Jakarta Sans', sans-serif;
        white-space: pre-wrap;
        line-height: 1.7;
        font-size: 0.95rem;
    }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Hide default Streamlit header margin */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# OCR Engine Caching
# -----------------------------------------------------------------------------
@st.cache_resource
def get_ocr_engine():
    """Cache EasyOCR engine initialization to minimize memory footprint."""
    return BanglaOCREngine(languages=config.OCR_LANGUAGES, gpu=config.USE_GPU)


# -----------------------------------------------------------------------------
# Main Application
# -----------------------------------------------------------------------------
def main():
    # -------------------------------------------------------------------------
    # Hero Section
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="hero-card">
        <div class="hero-badge">⚡ Real-Time Bangla OCR & Text Search Engine</div>
        <h1 class="hero-title">Bangla Document Intelligence System</h1>
        <p class="hero-subtitle">
            High-precision optical character recognition for Bangla & English documents. Convert multi-page PDFs or image scans into structured editable text with real-time in-memory keyword search.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Sidebar: System Config & Hardware Details
    # -------------------------------------------------------------------------
    with st.sidebar:
        st.markdown("### ⚙️ System Status")
        st.success("🟢 **OCR Engine**: Active (EasyOCR)")
        
        st.markdown("---")
        st.markdown("### 💻 Hardware & Config")
        st.info(
            "💡 **Hardware Mode**: CPU Optimized\n\n"
            "🧠 **RAM Footprint**: ~1.2 GB peak\n\n"
            f"🌐 **Languages**: {', '.join(config.OCR_LANGUAGES).upper()}\n\n"
            f"📁 **Output Dir**: `{config.OUTPUT_DIR.name}/`"
        )

        st.markdown("---")
        st.markdown("### 📖 Step-by-Step Guide")
        st.markdown("""
        1. **Upload File**: Select a PDF or image (`PNG`, `JPG`, `JPEG`).
        2. **Preview Document**: Inspect layout in the left viewport.
        3. **Run Extraction**: Click **Run Bangla OCR Extraction**.
        4. **Analyze & Edit**: View stats, edit text, copy, or download.
        5. **Search**: Search Bangla & English keywords in real time.
        """)

        st.markdown("---")
        st.caption("Bangla Document Intelligence v2.0 • Phase 2")

    # -------------------------------------------------------------------------
    # Main File Upload Area
    # -------------------------------------------------------------------------
    uploaded_file = st.file_uploader(
        "📄 Drag and drop your PDF or Image document here",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Upload PDF documents or images containing Bangla and English text."
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.name
        file_ext = file_name.split(".")[-1].lower()

        # Load Document Pages
        with st.spinner("🔄 Processing document pages and layout..."):
            if file_ext == "pdf":
                images = pdf_to_images(file_bytes)
            else:
                img = load_image(file_bytes)
                images = [img]

        st.toast(f"Loaded document `{file_name}` ({len(images)} page{'s' if len(images) > 1 else ''})", icon="📄")

        # -------------------------------------------------------------------------
        # Two-Column Dashboard Layout
        # Left Panel: Document Preview | Right Panel: Extraction & Results
        # -------------------------------------------------------------------------
        col1, col2 = st.columns([1, 1], gap="medium")

        # --- Left Column: Document Preview Panel ---
        with col1:
            st.markdown("### 🖼️ Document Preview")
            
            if len(images) > 1:
                page_idx = st.slider("Select Page Viewport", 1, len(images), 1) - 1
            else:
                page_idx = 0

            # Modern Image Viewport
            st.image(
                images[page_idx],
                caption=f"Document Page {page_idx + 1} of {len(images)} ({file_name})",
                width="stretch"
            )

        # --- Right Column: OCR Extraction Panel ---
        with col2:
            st.markdown("### 📝 Text Extraction & Analysis")

            # Extract Button
            if st.button("🚀 Run Bangla OCR Extraction", type="primary", width="stretch"):
                ocr = get_ocr_engine()
                
                with st.spinner("⚡ Extracting Bangla & English text via EasyOCR... (Please wait)"):
                    results = ocr.process_document_pages(images)
                    extracted_text = results["full_text"]
                    
                    # Store in Streamlit session state
                    st.session_state["extracted_text"] = extracted_text
                    st.session_state["extracted_file_name"] = file_name
                    
                    # Save UTF-8 text file to output directory
                    saved_path = save_extracted_text(extracted_text, file_name)
                    st.session_state["saved_path"] = saved_path

            # Display Extraction Results if present in session state
            if "extracted_text" in st.session_state and st.session_state.get("extracted_file_name") == file_name:
                extracted_text = st.session_state["extracted_text"]
                saved_path = st.session_state.get("saved_path")

                st.success(f"✅ Extraction completed! Saved to `{saved_path.name}`")

                # -------------------------------------------------------------
                # OCR Statistics Panel
                # -------------------------------------------------------------
                char_count = len(extracted_text)
                word_count = len(extracted_text.split())
                line_count = len([line for line in extracted_text.splitlines() if line.strip()])
                page_count = len(images)

                st.markdown("##### 📊 Document Extraction Statistics")
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                
                with stat_col1:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-val">{char_count:,}</div>
                        <div class="stat-lbl">Characters</div>
                    </div>
                    """, unsafe_allow_html=True)
                with stat_col2:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-val">{word_count:,}</div>
                        <div class="stat-lbl">Words</div>
                    </div>
                    """, unsafe_allow_html=True)
                with stat_col3:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-val">{line_count:,}</div>
                        <div class="stat-lbl">Lines</div>
                    </div>
                    """, unsafe_allow_html=True)
                with stat_col4:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-val">{page_count}</div>
                        <div class="stat-lbl">Pages</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # -------------------------------------------------------------
                # Editable Text Result Box
                # -------------------------------------------------------------
                edited_text = st.text_area(
                    "Extracted Bangla Text Editor",
                    value=extracted_text,
                    height=300,
                    help="You can review and edit extracted text directly in this text box."
                )

                # -------------------------------------------------------------
                # Action Buttons (Download & Copy Drawer)
                # -------------------------------------------------------------
                btn_col1, btn_col2 = st.columns([1, 1])
                with btn_col1:
                    st.download_button(
                        label="📥 Download Text File",
                        data=edited_text,
                        file_name=f"extracted_{file_name}.txt",
                        mime="text/plain",
                        width="stretch"
                    )
                with btn_col2:
                    with st.expander("📋 Copy Text to Clipboard"):
                        st.code(edited_text, language="text")

                st.caption(f"💾 **Auto-Saved File Path**: `{saved_path}`")

                # -------------------------------------------------------------
                # Lightweight Text Search Section
                # -------------------------------------------------------------
                st.markdown("---")
                st.markdown("### 🔍 Real-Time Text Search & Highlighting")
                
                search_query = st.text_input(
                    "Search word or phrase",
                    placeholder="Enter Bangla (e.g., বাংলা) or English word...",
                    key="search_query"
                )

                if search_query:
                    highlighted_html, count = search_and_highlight(edited_text, search_query)
                    
                    if count > 0:
                        st.success(f"Found **{count}** match{'es' if count > 1 else ''} for query: **'{search_query}'**")
                    else:
                        st.warning(f"No occurrences found for query: **'{search_query}'**")

                    st.markdown(
                        f'<div class="search-results-box">{highlighted_html}</div>',
                        unsafe_allow_html=True
                    )


if __name__ == "__main__":
    main()
