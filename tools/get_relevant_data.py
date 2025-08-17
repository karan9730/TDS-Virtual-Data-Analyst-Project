# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "beautifulsoup4",
#   "typing",
# ]
# ///

import os
from bs4 import BeautifulSoup  # type: ignore
from typing import Dict, Any
from tools.dom_structure import extract_dom_structure_with_identifiers

MAX_WORDS = 1500
OUTPUT_DIR = "/tmp/outputs"
OUTPUT_FILE = "extracted_relevant_data.txt"


def get_relevant_data(file_name: str, js_selector: str = None, max_depth: int = 10) -> Dict[str, Any]:
    """
    Extract relevant data from a saved HTML file using an optional CSS/JS selector.
    
    - If js_selector is provided, returns matching text content.
    - If no selector or no matches, returns the DOM structure (max depth capped at 15).
    - If extracted text is too large (>MAX_WORDS), saves it to a file instead.
    """
    # Resolve file path
    if not os.path.isabs(file_name) and not file_name.startswith(OUTPUT_DIR):
        file_name = os.path.join(OUTPUT_DIR, file_name)

    if not os.path.exists(file_name):
        return {"error": f"File not found: {file_name}"}

    try:
        with open(file_name, encoding="utf-8") as f:
            html = f.read()
    except UnicodeDecodeError:
        return {"error": "Unable to decode HTML file with UTF-8 encoding."}

    soup = BeautifulSoup(html, "html.parser")

    if js_selector:
        try:
            elements = soup.select(js_selector)
        except Exception as e:
            return {"error": f"Invalid selector '{js_selector}': {e}"}

        if elements:
            text_data = [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]
            if text_data:
                combined_text = "\n".join(text_data)
                word_count = len(combined_text.split())

                if word_count > MAX_WORDS:
                    os.makedirs(OUTPUT_DIR, exist_ok=True)
                    save_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
                    with open(save_path, "w", encoding="utf-8") as out_f:
                        out_f.write(combined_text)
                    return {
                        "message": f"Extracted text too large (~{word_count} words). Saved to file instead.",
                        "file_path": save_path
                    }

                return {"data": text_data}
        # If no elements or no text found → fall through to DOM structure

    # Cap depth at 15
    max_depth = min(max_depth, 15)
    dom_structure = extract_dom_structure_with_identifiers(html, max_depth=max_depth)

    if dom_structure.strip() == "No HTML content found.":
        return {"message": "HTML file is empty or contains no parseable content."}

    return {
        "message": (
            "No matching content found for the provided selector. "
            "try to guess another js_selector based on the webpage type."
            if js_selector else
            "No js_selector provided."
            "Inspect the url and try to guess a suitable js_selector based on website/webpage type, then pass it along in your steps."
        )
    }


if __name__ == "__main__":
    result = get_relevant_data("scraped_content.html")
    print(result)