# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "PyMuPDF",
# ]
# ///

def read_pdf_file(file_name: str, directory: str) -> str:
    import os
    import fitz  # type: ignore # PyMuPDF

    if directory not in ["uploads", "outputs"]:
        return f"Error: Unsupported directory '{directory}'. Must be 'uploads' or 'outputs'."

    file_path = os.path.join(directory, file_name)

    try:
        with fitz.open(file_path) as doc:
            text = ""
            for page in doc:
                text += page.get_text()

        # Cap output to avoid LLM overload (approx. 8000 characters)
        char_limit = 8000
        if len(text) > char_limit:
            truncated = text[:char_limit]
            return truncated + "\n\n[Output truncated — file too long for direct reading. Please use a more specific extraction tool or write custom code with `execute_code`.]"
        return text or "[No readable text found in the PDF.]"

    except FileNotFoundError:
        return f"Error: File '{file_name}' not found in '{directory}/'."
    except Exception as e:
        return f"Error: Could not read file '{file_name}': {e}"
