# Bangla Document Intelligence System (Phase 2)

A lightweight, CPU-optimized Bangla Document Intelligence System. 
Phase 2 includes high-precision Bangla OCR extraction for uploaded PDF and Image files, alongside a lightweight, real-time in-memory text search and keyword highlighting feature.

---

## 🌟 Key Features

- **Bangla & English OCR**: Powered by EasyOCR with CPU optimization suitable for standard laptop hardware (12GB RAM).
- **PDF & Image Support**: Converts multi-page PDFs to images natively using PyMuPDF (`pymupdf`).
- **Interactive Web Interface**: Streamlit application with drag-and-drop file uploader and document page preview slider.
- **Lightweight Text Search**: Real-time keyword & phrase search across extracted Bangla and English text with match count statistics and visual highlighting.
- **Automatic Text Storage**: Extracted Bangla text is automatically saved to the `outputs/` folder with timestamps and UTF-8 encoding.
- **One-Click Download**: Download extracted text directly from the Web UI.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
Ensure you have **Python 3.9+** installed on your system.

### 2. Create Virtual Environment & Install Dependencies
Open PowerShell or Terminal in the project root:

```bash
# Create a virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 3. Launch the Application
Run the Streamlit web server:

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 🔍 Using the Text Search Feature

1. Upload a PDF or Image file containing Bangla/English text.
2. Click **Extract Bangla Text** to run the OCR engine.
3. Scroll to the **Search Extracted Text** section below the results box.
4. Enter any Bangla or English word or phrase in the search box.
5. Matches will be counted instantly and highlighted visually.

---

## 📁 Project Structure

```text
Bangla-Document-Intelligen/
├── .gitignore               # Git ignore rules for archives & test files
├── app.py                   # Streamlit Web Application interface
├── config.py                # System settings and CPU optimization flags
├── requirements.txt         # Lightweight Python dependencies
├── src/
│   ├── __init__.py
│   ├── ocr_engine.py        # EasyOCR wrapper with memory caching
│   ├── pdf_processor.py     # PDF to image rendering via PyMuPDF
│   └── utils.py             # UTF-8 text saving & text search/highlighting utilities
├── outputs/                 # Directory where extracted text files are stored
└── README.md                # Documentation & usage guide
```

---

## 💻 Hardware Compatibility
- **RAM**: 12 GB RAM minimum.
- **GPU**: Not required (Runs efficiently on CPU / Intel Iris Xe).
