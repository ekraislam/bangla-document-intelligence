from typing import List, Generator
import pymupdf as fitz  # PyMuPDF
from PIL import Image
import io
import config

def load_image(image_bytes: bytes) -> Image.Image:
    """Load an image from raw bytes and convert to RGB format."""
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    return resize_image_if_needed(img)

def pdf_to_images(pdf_bytes: bytes, dpi: int = 150) -> List[Image.Image]:
    """
    Extract all PDF pages as PIL Images using PyMuPDF (fitz).
    Returns list of PIL images.
    """
    return list(stream_pdf_to_images(pdf_bytes, dpi=dpi))

def stream_pdf_to_images(pdf_bytes: bytes, dpi: int = 150) -> Generator[Image.Image, None, None]:
    """
    Yield PDF pages as PIL Images one page at a time using PyMuPDF (fitz).
    Memory efficient generator stream for multi-page documents.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    
    try:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            pix = None  # Immediately free C-level pixmap buffer
            yield resize_image_if_needed(img)
    finally:
        doc.close()

def resize_image_if_needed(img: Image.Image, max_side: int = config.MAX_IMAGE_SIDE) -> Image.Image:
    """
    Resize image if any dimension exceeds max_side to prevent RAM spikes during OCR.
    """
    w, h = img.size
    if max(w, h) > max_side:
        scale = max_side / float(max(w, h))
        new_w = int(w * scale)
        new_h = int(h * scale)
        return img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    return img

