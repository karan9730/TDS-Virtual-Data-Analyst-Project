def read_text_file(file_name: str, directory: str) -> str:
    import os

    allowed_extensions = ['.txt', '.csv', '.log', '.md']
    max_words = 1200
    max_chars = 8000
    max_file_size_bytes = 5 * 1024 * 1024  # 5 MB max file size

    if directory not in ["/tmp/uploads", "/tmp/outputs"]:
        return f"Error: Unsupported directory '{directory}'. Must be '/tmp/uploads' or '/tmp/outputs'."

    ext = os.path.splitext(file_name)[1].lower()
    # Block common large structured formats to prevent token overload
    blocked_extensions = ['.html', '.htm', '.xml', '.json', '.js', '.css']
    if ext in blocked_extensions:
        return f"Error: Reading files with '{ext}' extension is not supported due to potential token overload. Please use more specific extraction tools."

    if ext not in allowed_extensions:
        return f"Error: Unsupported file type '{ext}'. Allowed types: {', '.join(allowed_extensions)}"

    file_path = os.path.join(directory, file_name)

    try:
        if os.path.getsize(file_path) > max_file_size_bytes:
            return f"Error: File '{file_name}' exceeds maximum allowed size of {max_file_size_bytes // (1024*1024)} MB."

        with open(file_path, "r", encoding="utf-8", errors='replace') as f:
            content = f.read(max_chars + 1)

        if directory == "/tmp/uploads" and file_name == "questions.txt":
            # Return full content for questions.txt without truncation
            return content

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