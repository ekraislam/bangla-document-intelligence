# Bangla Document Intelligence System (Phase 1)

A lightweight, CPU-optimized Bangla Document Intelligence System. 
Phase 1 focuses on high-precision Bangla OCR extraction for uploaded PDF and Image files without heavy dependencies like LLMs, RAG, or vector databases.

---

## 🌟 Key Features

- **Bangla & English OCR**: Powered by EasyOCR with CPU optimization suitable for 12GB RAM laptops.
- **PDF & Image Support**: Converts multi-page PDFs to images natively using PyMuPDF (`fitz`).
- **Interactive Web Interface**: Streamlit application with drag-and-drop upload and document page preview.
- **Automatic Text Storage**: Extracted Bangla text is automatically saved to the `outputs/` folder with timestamps and UTF-8 encoding.
- **One-Click Download**: Download extracted text directly from the Web UI.

---

## 🚀 Quickstart Guide

### 1. Prerequisite
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

## 📁 Project Structure

```
Bangla-Document-Intelligen/
├── app.py                   # Streamlit Web Application interface
├── config.py                # System settings and CPU optimization flags
├── requirements.txt         # Lightweight Python dependencies
├── src/
│   ├── __init__.py
│   ├── ocr_engine.py        # EasyOCR wrapper with memory caching
│   ├── pdf_processor.py     # PDF to image rendering via PyMuPDF
│   └── utils.py             # UTF-8 text saving & utility functions
├── outputs/                 # Directory where extracted text files are stored
└── README.md                # Documentation & usage guide
```

---

## 💻 Hardware Compatibility
- **RAM**: 12 GB RAM minimum.
- **GPU**: Not required (Runs efficiently on Intel Iris Xe / CPU).
