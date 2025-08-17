import base64
import os
import mimetypes

def convert_to_base64(file_name: str, directory: str = "/tmp/outputs") -> str:
    """
    Converts any file from the specified directory to a base64-encoded string.
    Automatically detects MIME type.
    """

    if directory not in ["/tmp/uploads", "/tmp/outputs"]:
        return f"Error: Unsupported directory '{directory}'. Must be '/tmp/uploads' or '/tmp/outputs'."

    file_path = os.path.join(directory, file_name)

    if not os.path.exists(file_path):
        return f"Error: File '{file_name}' not found in '{directory}/'."
    
    if os.path.getsize(file_path) == 0:
        return f"Error: File '{file_name}' is empty."

    try:
        with open(file_path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode("utf-8")
        
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = "application/octet-stream"  # generic binary type
        
        return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        return f"Error: Could not convert file '{file_name}' to base64: {e}"