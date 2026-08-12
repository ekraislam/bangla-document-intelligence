import streamlit as st
from PIL import Image
import config
from src.pdf_processor import pdf_to_images, load_image
from src.ocr_engine import BanglaOCREngine
from src.utils import save_extracted_text

# Set page layout & title
st.set_page_config(
    page_title="Bangla Document Intelligence - Phase 1 OCR",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_ocr_engine():
    """Cache EasyOCR engine initialization to minimize memory footprint."""
    return BanglaOCREngine(languages=config.OCR_LANGUAGES, gpu=config.USE_GPU)

def main():
    st.title("📄 Bangla Document Intelligence System")
    st.caption("Phase 1: Lightweight Bangla OCR for PDF & Image Files (CPU Optimized)")

    st.markdown("---")

    # Sidebar Information
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info("💡 **Hardware Mode**: CPU (Intel Iris Xe / 12GB RAM)")
        st.write(f"**Languages Supported**: {', '.join(config.OCR_LANGUAGES).upper()}")
        st.write(f"**Output Directory**: `{config.OUTPUT_DIR}`")
        
        st.markdown("---")
        st.markdown("### ℹ️ Instructions")
        st.markdown("""
        1. Upload a PDF or Image file containing Bangla text.
        2. Preview document pages on the left.
        3. Click **Extract Bangla Text**.
        4. View, edit, download, or inspect the auto-saved text file.
        """)

    # File Uploader
    uploaded_file = st.file_uploader(
        "Upload a PDF or Image Document",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Supports PDF files and standard image formats."
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.name
        file_ext = file_name.split(".")[-1].lower()

        # Load Document Images
        with st.spinner("Processing document layout..."):
            if file_ext == "pdf":
                images = pdf_to_images(file_bytes)
            else:
                img = load_image(file_bytes)
                images = [img]

        st.success(f"Loaded document `{file_name}` ({len(images)} page{'s' if len(images) > 1 else ''})")

        # Two-column interface: Left = Preview, Right = Extraction & Results
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("🖼️ Document Preview")
            if len(images) > 1:
                page_idx = st.slider("Select Page", 1, len(images), 1) - 1
            else:
                page_idx = 0
            
            st.image(images[page_idx], caption=f"Page {page_idx + 1} of {len(images)}", use_container_width=True)

        with col2:
            st.subheader("📝 Text Extraction (Bangla OCR)")

            if st.button("🚀 Extract Bangla Text", type="primary", use_container_width=True):
                ocr = get_ocr_engine()
                
                with st.spinner("Performing Bangla OCR extraction... (Please wait)"):
                    results = ocr.process_document_pages(images)
                    extracted_text = results["full_text"]
                    
                    # Store extracted text in session state
                    st.session_state["extracted_text"] = extracted_text
                    st.session_state["extracted_file_name"] = file_name
                    
                    # Save to disk
                    saved_path = save_extracted_text(extracted_text, file_name)
                    st.session_state["saved_path"] = saved_path

            # Display results if present in session state
            if "extracted_text" in st.session_state and st.session_state.get("extracted_file_name") == file_name:
                extracted_text = st.session_state["extracted_text"]
                saved_path = st.session_state.get("saved_path")

                st.success(f"✅ Extraction completed! Saved to `{saved_path.name}`")

                # Editable Text Box for extracted Bangla text
                edited_text = st.text_area(
                    "Extracted Bangla Text",
                    value=extracted_text,
                    height=350
                )

                # Action Buttons (Download & Path Info)
                c_down, c_info = st.columns([1, 1])
                with c_down:
                    st.download_button(
                        label="📥 Download Text File",
                        data=edited_text,
                        file_name=f"extracted_{file_name}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                with c_info:
                    st.caption(f"💾 **Auto-Saved File**: `{saved_path}`")

if __name__ == "__main__":
    main()
