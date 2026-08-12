import os
from datetime import datetime
from pathlib import Path
import config

def save_extracted_text(text: str, source_filename: str) -> Path:
    """
    Saves extracted Bangla text to a UTF-8 encoded text file in the outputs directory.
    
    :param text: Extracted text content
    :param source_filename: Name of original uploaded file
    :return: Path to saved file
    """
    clean_stem = Path(source_filename).stem.replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"extracted_{clean_stem}_{timestamp}.txt"
    output_path = config.OUTPUT_DIR / output_filename
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Source Document: {source_filename}\n")
        f.write(f"Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        f.write(text)
        
    return output_path
