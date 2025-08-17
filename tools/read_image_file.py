# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "google-generativeai",
# ]
# ///

import os
import base64
import tempfile
import google.generativeai as genai  # type: ignore
import binascii

def get_image_description(image_bytes: bytes, suffix: str = ".png") -> str:
    genai.configure(api_key=os.getenv("GENAI_API_KEY"))

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="/tmp") as tmp_file:
        tmp_file.write(image_bytes)
        tmp_file_path = tmp_file.name

    try:
        uploaded_file = genai.upload_file(tmp_file_path)
        model = genai.GenerativeModel("gemini-2.0-flash")
        result = model.generate_content(
            [
                uploaded_file,
                "Describe the content of this image in detail, focusing on any text, objects, or relevant features that could help answer questions about it."
            ]
        )
        return result.text
    finally:
        try:
            os.remove(tmp_file_path)
        except Exception:
            pass

def read_image_file(file_name=None, b64_string=None, directory="uploads"):
    # Normalize directory input to full absolute path
    dir_map = {
        "uploads": "/tmp/uploads",
        "/tmp/uploads": "/tmp/uploads",
        "outputs": "/tmp/outputs",
        "/tmp/outputs": "/tmp/outputs",
    }

    directory = dir_map.get(directory)
    if not directory:
        return "Error: Unsupported directory. Must be '/tmp/uploads', '/tmp/outputs', 'uploads', or 'outputs'."

    if (file_name and b64_string) or (not file_name and not b64_string):
        return "Error: Provide exactly one of 'file_name' or 'b64_string'."

    try:
        if file_name:
            file_path = os.path.join(directory, file_name)
            if not os.path.isfile(file_path):
                return f"Error: File not found: {file_path}"

            suffix = os.path.splitext(file_name)[-1] or ".png"
            with open(file_path, "rb") as f:
                image_bytes = f.read()

        else:  # b64_string provided
            if b64_string.startswith("data:image/"):
                try:
                    header, b64_data = b64_string.split(",", 1)
                    suffix = "." + header.split("/")[1].split(";")[0]
                    # Simple whitelist for suffixes, fallback to .png
                    if suffix.lower() not in [".png", ".jpeg", ".jpg", ".gif", ".bmp", ".webp"]:
                        suffix = ".png"
                    b64_string = b64_data
                except Exception:
                    suffix = ".png"
            else:
                suffix = ".png"

            try:
                image_bytes = base64.b64decode(b64_string, validate=True)
            except binascii.Error:
                return "Error: Provided base64 string is invalid."

        return get_image_description(image_bytes, suffix)

    except Exception as e:
        return f"Error processing image: {e}"