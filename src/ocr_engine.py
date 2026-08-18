import easyocr
import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Optional, Union
import config

def enhance_image_for_bangla_ocr(pil_image: Image.Image) -> Image.Image:
    """
    OpenCV preprocessing pipeline for Bangla OCR.
    Applies CLAHE (Contrast Limited Adaptive Histogram Equalization) and noise reduction.
    """
    # Convert PIL Image to OpenCV BGR numpy array
    img_np = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    # 1. Grayscale Conversion
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    
    # 2. CLAHE (Adaptive Histogram Equalization for Bangla text contrast enhancement)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # 3. Fast Denoising
    denoised = cv2.fastNlMeansDenoising(enhanced, h=8)
    
    # Convert back to 3-channel RGB PIL Image for EasyOCR compatibility
    rgb_img = cv2.cvtColor(denoised, cv2.COLOR_GRAY2RGB)
    return Image.fromarray(rgb_img)

class BanglaOCREngine:
    """
    Lightweight Bangla & English OCR engine using EasyOCR tuned for CPU usage.
    """
    def __init__(self, languages: Optional[List[str]] = None, gpu: Optional[bool] = None):
        self.languages = languages if languages is not None else config.OCR_LANGUAGES
        self.gpu = gpu if gpu is not None else config.USE_GPU
        self.reader = None

    def _initialize_reader(self) -> None:
        """Lazy load EasyOCR reader model into memory."""
        if self.reader is None:
            self.reader = easyocr.Reader(self.languages, gpu=self.gpu)

    def extract_text_from_image(self, pil_image: Image.Image, detail: int = 0, preprocess: bool = False) -> str:
        """
        Extract text from a PIL Image object.
        
        :param pil_image: PIL Image object
        :param detail: 0 for simple text output, 1 for detailed output with bounding boxes
        :param preprocess: If True, applies OpenCV CLAHE + Denoise pipeline before OCR
        :return: Extracted string in Bangla/English
        """
        self._initialize_reader()
        
        if preprocess:
            processed_img = enhance_image_for_bangla_ocr(pil_image)
        else:
            processed_img = pil_image
            
        img_np = np.array(processed_img)
        
        try:
            results = self.reader.readtext(img_np, detail=0)
        except Exception as e:
            return f"[Error processing OCR: {str(e)}]"
        
        if detail == 0:
            extracted_text = "\n".join(results)
        else:
            lines = [res[1] for res in results]
            extracted_text = "\n".join(lines)
            
        cleaned = extracted_text.strip()
        if not cleaned:
            return "[No readable text detected on this page]"
        return cleaned

    def process_document_pages(self, images: List[Image.Image], preprocess: bool = False) -> Dict[str, Any]:
        """
        Process a list of page images and return page-by-page extracted text as well as combined text.
        """
        self._initialize_reader()
        pages_text = []
        
        for idx, img in enumerate(images):
            text = self.extract_text_from_image(img, detail=0, preprocess=preprocess)
            pages_text.append({
                "page": idx + 1,
                "text": text
            })
            
        full_text = "\n\n--- Page Break ---\n\n".join(
            [f"--- Page {p['page']} ---\n{p['text']}" for p in pages_text]
        )
        
        return {
            "full_text": full_text,
            "pages": pages_text,
            "total_pages": len(images)
        }

