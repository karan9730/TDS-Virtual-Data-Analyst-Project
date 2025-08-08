def read_text_file(file_name: str, directory: str) -> str:
    import os

    if directory not in ["uploads", "outputs"]:
        return f"Error: Unsupported directory '{directory}'. Must be 'uploads' or 'outputs'."

    file_path = os.path.join(directory, file_name)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Always return full content for questions.txt from uploads
        if directory == "uploads" and file_name == "questions.txt":
            return content

        # For other files, apply truncation limits
        max_words = 1500
        max_chars = 10000

        word_count = len(content.split())
        char_count = len(content)

        if word_count > max_words or char_count > max_chars:
            truncated = content[:max_chars]
            return (
                "⚠️ File too long for direct reading. Only partial content shown below.\n"
                "Please use a more specific extraction tool (e.g., dom_structure, get_relevant_data) "
                "or write code via `execute_code` to process large files.\n\n"
                + truncated
            )

        return content

    except FileNotFoundError:
        return f"Error: File '{file_name}' not found in '{directory}/'."
    except Exception as e:
        return f"Error: Could not read file '{file_name}': {e}"