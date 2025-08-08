import base64
import os

def convert_to_base64(file_name: str, directory: str = "outputs") -> str:
    """
    Converts an image file from the specified directory to a base64-encoded string.
    """

    if directory not in ["uploads", "outputs"]:
        return f"Error: Unsupported directory '{directory}'. Must be 'uploads' or 'outputs'."

    file_path = os.path.join(directory, file_name)

    if not os.path.exists(file_path):
        return f"Error: File '{file_name}' not found in '{directory}/'."

    try:
        with open(file_path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/{file_name.split('.')[-1]};base64,{encoded_string}"
    except Exception as e:
        return f"Error: Could not convert file '{file_name}' to base64: {e}"