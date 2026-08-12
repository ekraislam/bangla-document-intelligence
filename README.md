# Bangla Document Intelligence Dashboard (Modern AI UI Redesign)

A modern, production-grade Bangla Document Intelligence System featuring a high-precision Bangla & English OCR extraction pipeline and a real-time, in-memory text search engine.

---

## 🌟 Key Features

- **Modern AI Dashboard UI**: Glassmorphic dark card design, Google Fonts (`Plus Jakarta Sans` & `Noto Sans Bengali`), hero banner, and responsive layout.
- **Bangla & English OCR**: Powered by EasyOCR with CPU optimization suitable for standard laptop hardware (12GB RAM) and cloud servers.
- **PDF & Image Support**: Converts multi-page PDFs to images natively using PyMuPDF (`pymupdf`).
- **OCR Statistics Panel**: Real-time stats cards for character count, word count, line count, and page count.
- **Lightweight Text Search**: Real-time keyword & phrase search across extracted text with match count statistics and visual highlighting.
- **Copy-to-Clipboard & One-Click Download**: Integrated text drawer for easy copying and downloadable UTF-8 text files.
- **Deployment-Ready**: Pre-configured with `.streamlit/config.toml`, Linux `packages.txt`, and production `Dockerfile`.

---

## 🎨 UI Comparison (Before vs. After)

| Feature / UI Element | Old UI | Redesigned AI Dashboard |
| :--- | :--- | :--- |
| **Theme & Aesthetic** | Standard Streamlit plain theme | Custom Glassmorphism UI with Dark Indigo AI Hero banner |
| **Typography** | Default browser sans-serif | Google Fonts (`Plus Jakarta Sans` + `Noto Sans Bengali`) |
| **Document Stats** | None | Real-time Character, Word, Line, and Page metrics panel |
| **Streamlit Deprecations** | Used `use_container_width=True` | Fully updated to modern `width="stretch"` standard |
| **Action Bar** | Basic download button | Dual-action bar with Download Button and Copy-to-Clipboard drawer |
| **Sidebar Layout** | Static text markdown | Interactive status badges, hardware metrics, and workflow guide |
| **Search Viewport** | Standard white container | Styled dark glass search viewport with highlighted `<mark>` tags |

---

## 🚀 Quickstart Guide (Local Development)

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

## ☁️ Cloud Deployment Guide

### Option A: Streamlit Community Cloud (Recommended & 1-Click)

1. **Push Code to GitHub**: Push this repository to your GitHub account.
2. **Sign In**: Log into [share.streamlit.io](https://share.streamlit.io) using your GitHub account.
3. **Deploy App**:
   - Click **New app**.
   - Select your repository, branch (`main` or `master`), and set Main file path to `app.py`.
   - Click **Deploy!**.
4. *Note*: The included `packages.txt` (`libgl1`, `libglib2.0-0`) and `.streamlit/config.toml` will automatically configure system dependencies and server settings.

---

### Option B: Docker Container Deployment (Render / Railway / Hugging Face Spaces / GCP Cloud Run)

This repository includes a production-ready `Dockerfile`.

```bash
# Build the Docker image
docker build -t bangla-ocr-app .

# Run container on port 8501
docker run -d -p 8501:8501 --name bangla-ocr bangla-ocr-app
```

Access the deployed application in browser at `http://localhost:8501` (or your cloud server's domain).

---

## 📁 Project Structure

```text
Bangla-Document-Intelligen/
├── .gitignore               # Git ignore rules for archives & output text files
├── Dockerfile               # Production Docker container build file
├── packages.txt             # Linux system dependencies (libgl1, libglib2.0-0)
├── requirements.txt         # Python dependencies including opencv-python-headless
├── app.py                   # Redesigned Streamlit AI Dashboard UI interface
├── config.py                # System settings and CPU optimization flags
├── .streamlit/
│   └── config.toml          # Streamlit server and theme configuration
├── src/
│   ├── __init__.py
│   ├── ocr_engine.py        # EasyOCR wrapper with memory caching (Unchanged)
│   ├── pdf_processor.py     # PDF to image rendering via PyMuPDF (Unchanged)
│   └── utils.py             # UTF-8 text saving & text search/highlighting utilities
├── outputs/                 # Directory where extracted text files are stored
└── README.md                # Documentation & deployment guide
```

---

## 💻 Hardware Compatibility & Resource Requirements
- **RAM**: 2 GB RAM minimum for Cloud Server (12 GB recommended for heavy local batch processing).
- **GPU**: Not required (Runs 100% efficiently on CPU).
