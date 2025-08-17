# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "beautifulsoup4",
# ]
# ///

from bs4 import BeautifulSoup, Comment # type: ignore

def extract_dom_structure_with_identifiers(html: str, max_depth: int = 12) -> str:
    """
    Returns a formatted DOM structure from the given HTML string, including tags with IDs/classes,
    up to a specified depth (default is 10).
    """
    soup = BeautifulSoup(html, "html.parser")

    if not soup.find():
        return "No HTML content found."

    
    def format_tag(tag):
        parts = [tag.name]
        if tag.get("id"):
            parts.append(f"#{tag['id']}")
        if tag.get("class"):
            class_str = "." + ".".join(tag.get("class"))
            parts.append(class_str)
        return "".join(parts)

    def traverse(node, depth=0):
        if depth > max_depth:
            return []
        lines = []
        for child in node.children:
            if isinstance(child, Comment) or child.name in ['script', 'style']:
                continue
            if hasattr(child, 'name') and child.name:
                lines.append("  " * depth + format_tag(child))
                lines.extend(traverse(child, depth + 1))
        return lines

    return "\n".join(traverse(soup))

# Optional debug usage
if __name__ == "__main__":
    with open("/tmp/outputs/scraped_content.html", encoding="utf-8") as f:
        html = f.read()
    print(extract_dom_structure_with_identifiers(html))