import os
import re
from datetime import datetime
from pathlib import Path
from typing import Tuple
import config

def validate_file_upload(file_name: str, file_size: int, max_size_mb: int = 50) -> Tuple[bool, str]:
    """
    Validates uploaded file size and extension.
    Returns (is_valid, error_message).
    """
    allowed_extensions = {".pdf", ".png", ".jpg", ".jpeg"}
    ext = Path(file_name).suffix.lower()
    
    if ext not in allowed_extensions:
        return False, f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(allowed_extensions)}"
    
    max_bytes = max_size_mb * 1024 * 1024
    if file_size > max_bytes:
        return False, f"File size ({file_size / (1024*1024):.1f} MB) exceeds maximum allowed limit of {max_size_mb} MB."
    
    return True, ""

def save_extracted_text(text: str, source_filename: str) -> Path:
    """
    Saves extracted Bangla text to a UTF-8 encoded text file in the outputs directory.
    Sanitizes filename against path traversal attacks.
    
    :param text: Extracted text content
    :param source_filename: Name of original uploaded file
    :return: Path to saved file
    """
    # Sanitize file stem to alphanumeric and underscore/dash only
    raw_stem = Path(source_filename).stem
    clean_stem = re.sub(r'[^a-zA-Z0-9_\-]', '_', raw_stem)
    if not clean_stem:
        clean_stem = "document"
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"extracted_{clean_stem}_{timestamp}.txt"
    
    # Ensure resolved path remains strictly within OUTPUT_DIR
    target_dir = config.OUTPUT_DIR.resolve()
    output_path = (target_dir / output_filename).resolve()
    
    if not str(output_path).startswith(str(target_dir)):
        raise ValueError("Invalid file output path (path traversal attempt detected).")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Source Document: {source_filename}\n")
        f.write(f"Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        f.write(text)
        
    return output_path

def search_and_highlight(text: str, query: str) -> Tuple[str, int]:
    """
    Searches for word/phrase in extracted text (case-insensitive & Unicode-aware).
    Returns (highlighted_html, match_count).
    
    :param text: Extracted text content
    :param query: Word or phrase to search for
    :return: Tuple of (highlighted HTML string, count of matches found)
    """
    if not text:
        return "", 0

    # Normalize Windows CRLF to LF for consistent indexing and formatting
    normalized_text = text.replace("\r\n", "\n")

    def _escape_html(s: str) -> str:
        return (
            s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace("\n", "<br>")
        )

    if not query or not query.strip():
        return _escape_html(normalized_text), 0

    clean_query = query.strip()
    # Case-insensitive, regex-escaped pattern search
    pattern = re.compile(re.escape(clean_query), re.IGNORECASE)
    matches = list(pattern.finditer(normalized_text))
    match_count = len(matches)

    if match_count == 0:
        return _escape_html(normalized_text), 0

    last_idx = 0
    html_parts = []
    for match in matches:
        start, end = match.span()
        prefix = normalized_text[last_idx:start]
        html_parts.append(_escape_html(prefix))

        matched_val = normalized_text[start:end]
        escaped_val = _escape_html(matched_val)
        html_parts.append(
            f'<mark style="background-color: #ffd54f; color: #000000; padding: 2px 4px; border-radius: 3px; font-weight: bold;">{escaped_val}</mark>'
        )
        last_idx = end

    suffix = normalized_text[last_idx:]
    html_parts.append(_escape_html(suffix))

    return "".join(html_parts), match_count



