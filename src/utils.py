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

def search_and_highlight(text: str, query: str):
    """
    Searches for word/phrase in extracted text (case-insensitive).
    Returns (highlighted_html, match_count).
    """
    if not query or not query.strip():
        escaped_text = (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\n", "<br>")
        )
        return escaped_text, 0

    clean_query = query.strip()
    import re
    pattern = re.compile(re.escape(clean_query), re.IGNORECASE)
    matches = list(pattern.finditer(text))
    match_count = len(matches)

    if match_count == 0:
        escaped_text = (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\n", "<br>")
        )
        return escaped_text, 0

    last_idx = 0
    html_parts = []
    for match in matches:
        start, end = match.span()
        prefix = text[last_idx:start]
        escaped_prefix = prefix.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        html_parts.append(escaped_prefix)

        matched_val = text[start:end]
        escaped_val = matched_val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html_parts.append(f'<mark style="background-color: #ffd54f; color: #000; padding: 2px 4px; border-radius: 3px; font-weight: bold;">{escaped_val}</mark>')
        last_idx = end

    suffix = text[last_idx:]
    escaped_suffix = suffix.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
    html_parts.append(escaped_suffix)

    return "".join(html_parts), match_count

