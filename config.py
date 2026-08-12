import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Output Directory for extracted text files
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Supported OCR Languages (Bangla & English)
OCR_LANGUAGES = ["bn", "en"]

# Hardware optimization (CPU mode for 12GB RAM + Intel Iris Xe)
USE_GPU = False

# Maximum image dimension for OCR to save memory
MAX_IMAGE_SIDE = 2000
