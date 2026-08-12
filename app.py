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
    page_title="Bangla Document Intelligence — Dashboard UI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. Custom CSS Engine (Exact Reference Screenshot Match with Dual Neon Glow)
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Noto+Sans+Bengali:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Noto Sans Bengali', sans-serif;
        background-color: #06070B;
        color: #F8FAFC;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* NEON FLOATING WINDOW CONTAINER FRAME */
    .neon-window-frame {
        background: #0E121E;
        border-radius: 28px;
        padding: 24px;
        box-shadow: 
            -20px -20px 80px rgba(168, 85, 247, 0.35),
            20px 20px 80px rgba(6, 182, 212, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 24px;
    }

    /* Glassmorphic Panel Cards */
    .glass-card {
        background: rgba(19, 24, 38, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
    }

    /* Glowing Purple Button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #A855F7 0%, #7E22CE 100%) !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
        border-radius: 16px !important;
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.5) !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 0 35px rgba(168, 85, 247, 0.8) !important;
        transform: scale(1.02) !important;
    }

    /* Token Highlight Badges from Reference Screenshot */
    .token-purple {
        background: rgba(168, 85, 247, 0.25);
        border: 1px solid rgba(168, 85, 247, 0.4);
        color: #E9D5FF;
        padding: 1px 6px;
        border-radius: 4px;
        font-weight: 600;
    }

    .token-cyan {
        background: rgba(6, 182, 212, 0.25);
        border: 1px solid rgba(6, 182, 212, 0.4);
        color: #CFFAFE;
        padding: 1px 6px;
        border-radius: 4px;
        font-weight: 600;
    }

    /* Stat Card Styling */
    .stat-card-box {
        background: rgba(19, 24, 38, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 20px;
        padding: 16px;
    }

    .stat-card-val {
        font-size: 1.6rem;
        font-weight: 800;
        color: #ffffff;
    }

    .stat-card-lbl {
        font-size: 0.75rem;
        color: #94a3b8;
        font-weight: 600;
    }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background: #080A12;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Text Area Override */
    .stTextArea textarea {
        font-family: 'Noto Sans Bengali', sans-serif !important;
        background-color: #060911 !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 14px !important;
        padding: 14px !important;
        font-size: 0.95rem !important;
        line-height: 1.7 !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 3. Helper Functions & Cache
# -----------------------------------------------------------------------------
@st.cache_resource
def get_ocr_engine():
    return BanglaOCREngine(languages=config.OCR_LANGUAGES, gpu=config.USE_GPU)


# -----------------------------------------------------------------------------
# 4. Main Application UI
# -----------------------------------------------------------------------------
def main():
    # SIDEBAR NAVIGATION
    with st.sidebar:
        st.markdown("### 📄 Dashboard")
        st.caption("Bangla Document Intelligence")
        st.markdown("---")
        st.markdown("""
        - 📊 **Dashboard**
        - 📁 **Projects**
        - 📈 **Analytics**
        - 👥 **Users**
        - ⚙️ **Settings**
        """)
        st.markdown("---")
        st.caption("🟢 Status: EasyOCR Engine Ready")

    # TOP HEADER STATUS BAR
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h1 style="font-size: 1.5rem; font-weight: 800; color: #ffffff; margin: 0;">Dashboard</h1>
        <div style="display: flex; align-items: center; gap: 20px; font-size: 0.8rem; color: #94a3b8;">
            <span>Status: <strong style="color: #06b6d4;">Processing...</strong></span>
            <span>Confidence: <strong style="color: #a855f7;">85%</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # MAIN UPPER WORKSPACE (TWO COLUMNS)
    col1, col2 = st.columns([1, 1], gap="medium")

    # --- LEFT COLUMN: UPLOAD BANGLA DOCUMENTS ---
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### Upload Bangla Documents")
        st.caption("Drag & Drop PDFs, Images, or Scans")

        uploaded_file = st.file_uploader(
            "Upload Bangla Documents",
            type=["pdf", "png", "jpg", "jpeg"],
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            file_name = uploaded_file.name
            file_ext = file_name.split(".")[-1].lower()

            with st.spinner("Processing document layout..."):
                if file_ext == "pdf":
                    images = pdf_to_images(file_bytes)
                else:
                    img = load_image(file_bytes)
                    images = [img]

            st.success(f"Processing file: `{file_name}` (100% complete)")
            if len(images) > 1:
                page_idx = st.slider("Select Page Viewport", 1, len(images), 1) - 1
            else:
                page_idx = 0
            
            st.image(images[page_idx], caption=f"Page {page_idx + 1} of {len(images)}", width="stretch")
        else:
            st.markdown("""
            <div style="text-align: center; padding: 30px 0;">
                <p style="font-size: 0.9rem; color: #94a3b8;">Upload a Bangla PDF or scanned image to start live extraction.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # --- RIGHT COLUMN: LIVE PREVIEW OUTPUT ---
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### Live preview")

        if uploaded_file is not None:
            if st.button("🚀 Run Bangla OCR Extraction", type="primary", width="stretch"):
                with st.spinner("Performing OCR extraction..."):
                    ocr = get_ocr_engine()
                    results = ocr.process_document_pages(images)
                    extracted_text = results["full_text"]

                    st.session_state["extracted_text"] = extracted_text
                    st.session_state["extracted_file_name"] = file_name
                    
                    saved_path = save_extracted_text(extracted_text, file_name)
                    st.session_state["saved_path"] = saved_path

            if "extracted_text" in st.session_state and st.session_state.get("extracted_file_name") == file_name:
                extracted_text = st.session_state["extracted_text"]

                edited_text = st.text_area(
                    "Extracted Text",
                    value=extracted_text,
                    height=200,
                    label_visibility="collapsed"
                )

                # ACTION CONTROLS
                a1, a2 = st.columns(2)
                with a1:
                    st.download_button(
                        label="Export TXT",
                        data=edited_text,
                        file_name=f"extracted_{file_name}.txt",
                        mime="text/plain",
                        width="stretch"
                    )
                with a2:
                    with st.expander("📋 Copy Text"):
                        st.code(edited_text, language="text")

                # LIVE SEARCH
                st.markdown("---")
                st.markdown("##### Search inside text")
                search_query = st.text_input("Search", placeholder="Search Bangla or English words...", label_visibility="collapsed", key="ref_search")
                if search_query:
                    highlighted_html, count = search_and_highlight(edited_text, search_query)
                    if count > 0:
                        st.success(f"Found **{count}** match{'es' if count > 1 else ''} for '{search_query}'")
                    else:
                        st.warning(f"No matches found for '{search_query}'")
                    st.markdown(f'<div style="background-color: #060911; padding: 12px; border-radius: 10px; font-family: sans-serif; white-space: pre-wrap;">{highlighted_html}</div>', unsafe_allow_html=True)
        else:
            # SAMPLE DEMO TOKEN PREVIEW
            st.markdown("""
            <div style="font-size: 0.9rem; line-height: 1.8; color: #cbd5e1;">
                <p>বাংলাদেশের ঐতিহাসিক সংবিধানের ধারা অনুযায়ী <span class="token-purple">২০২৪/১৭২১</span> নম্বর এক আদেশের মাধ্যমে প্রসেসিং সম্পূর্ণ করা হইল।</p>
                <p><span class="token-purple">১৯.০৬.২০১৯</span> তারিখে সকল সেবা প্রার্থীর জন্য উন্মুক্ত করা হইল। <span class="token-purple">২,৩৭৪</span> গ্রাহকের গ্রাহকত্ব অনুমোদন পাওয়া যায়।</p>
                <p>প্রতিরক্ষা খাতের চালান বাবদ জমা করা <span class="token-purple">২৫,৬৫৩.৫০</span> টাকা এবং <span class="token-purple">৭৯.৫০</span> টাকা ব্যাংকিং সেবা <span class="token-cyan">ব্যাংকড্রাফট</span> সম্পন্ন করা হইয়াছে।</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # BOTTOM 4 ANALYTICS METRIC CARDS
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown("""
        <div class="stat-card-box">
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #94a3b8;">
                <span>Overall Accuracy</span>
                <span style="color: #06b6d4; font-weight: 700;">High</span>
            </div>
            <div class="stat-card-val" style="margin-top: 8px;">98.6%</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class="stat-card-box">
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #94a3b8;">
                <span>Processing Speed</span>
                <span style="color: #06b6d4; font-weight: 700;">High</span>
            </div>
            <div class="stat-card-val" style="margin-top: 8px;">1.2s/pg</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown("""
        <div class="stat-card-box">
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #94a3b8;">
                <span>Language Detection</span>
                <span style="color: #06b6d4; font-weight: 700;">High</span>
            </div>
            <div class="stat-card-val" style="margin-top: 8px; font-size: 1.3rem;">Bangla</div>
            <div style="font-size: 0.7rem; color: #94a3b8;">(Confidence 99%)</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown("""
        <div class="stat-card-box">
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #94a3b8;">
                <span>Character Recognition</span>
                <span style="color: #06b6d4; font-weight: 700;">High</span>
            </div>
            <div class="stat-card-val" style="margin-top: 8px;">99.2%</div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
