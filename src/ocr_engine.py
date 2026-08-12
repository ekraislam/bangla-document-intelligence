import easyocr
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Union
import config

class BanglaOCREngine:
    """
    Lightweight Bangla & English OCR engine using EasyOCR tuned for CPU usage.
    """
    def __init__(self, languages: List[str] = config.OCR_LANGUAGES, gpu: bool = config.USE_GPU):
        self.languages = languages
        self.gpu = gpu
        self.reader = None

    def _initialize_reader(self):
        """Lazy load EasyOCR reader model into memory."""
        if self.reader is None:
            self.reader = easyocr.Reader(self.languages, gpu=self.gpu)

    def extract_text_from_image(self, pil_image: Image.Image, detail: int = 0) -> str:
        """
        Extract text from a PIL Image object.
        
        :param pil_image: PIL Image object
        :param detail: 0 for simple text output, 1 for detailed output with bounding boxes
        :return: Extracted string in Bangla/English
        """
        self._initialize_reader()
        img_np = np.array(pil_image)
        
        # EasyOCR readtext returns list of strings when detail=0
        results = self.reader.readtext(img_np, detail=detail, paragraph=True)
        
        if detail == 0:
            extracted_text = "\n".join(results)
        else:
            # Reconstruct text lines from detailed output tuple (bbox, text, prob)
            lines = [res[1] for res in results]
            extracted_text = "\n".join(lines)
            
        return extracted_text.strip()

    def process_document_pages(self, images: List[Image.Image]) -> Dict[str, Any]:
        """
        Process a list of page images and return page-by-page extracted text as well as combined text.
        """
        self._initialize_reader()
        pages_text = []
        
        for idx, img in enumerate(images):
            text = self.extract_text_from_image(img, detail=0)
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
