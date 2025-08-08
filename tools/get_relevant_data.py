# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "beautifulsoup4",
#   "typing",
# ]
# ///

import os
from bs4 import BeautifulSoup # type: ignore
from typing import Dict, Any
from tools.dom_structure import extract_dom_structure_with_identifiers

def get_relevant_data(file_name: str, js_selector: str = None) -> Dict[str, Any]:
    # Ensure path is relative to tools directory if not already
    if not os.path.isabs(file_name) and not file_name.startswith("outputs/"):
        file_name = os.path.join("outputs", file_name)

    with open(file_name, encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    if js_selector:
        elements = soup.select(js_selector)
        return {"data": [el.get_text(strip=True) for el in elements]}

    # JS selector was not provided — return DOM structure and a message
    dom_structure = extract_dom_structure_with_identifiers(html, max_depth=10)
    return {
        "message": "No js_selector provided. Here is the DOM structure. Please re-call the tool with a chosen js_selector.",
        "dom_structure": dom_structure
    }
