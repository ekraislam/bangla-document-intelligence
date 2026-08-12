import pymupdf as fitz  # PyMuPDF
from PIL import Image
import io
from typing import List
import config

def load_image(image_bytes: bytes) -> Image.Image:
    """Load an image from raw bytes and convert to RGB format."""
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    return resize_image_if_needed(img)

def pdf_to_images(pdf_bytes: bytes, dpi: int = 150) -> List[Image.Image]:
    """
    Extract PDF pages as PIL Images using PyMuPDF (fitz).
    Optimized for memory efficiency on laptops with integrated GPU.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    
    # Calculate matrix scale factor from DPI (72 default DPI in fitz)
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert pixmap to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img = resize_image_if_needed(img)
        images.append(img)
        
    doc.close()
    return images

def resize_image_if_needed(img: Image.Image, max_side: int = config.MAX_IMAGE_SIDE) -> Image.Image:
    """
    Resize image if any dimension exceeds max_side to prevent RAM spikes during OCR.
    """
    w, h = img.size
    if max(w, h) > max_side:
        scale = max_side / float(max(w, h))
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    return img
