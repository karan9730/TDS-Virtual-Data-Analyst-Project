# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "google-generativeai",
# ]
# ///

import os
import base64
import tempfile
import google.generativeai as genai # type: ignore
  # type: ignore # Make sure GENAI_API_KEY is set in env

def get_image_description(image_bytes: bytes, suffix: str = ".png") -> str:
    client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(image_bytes)
        tmp_file_path = tmp_file.name

    try:
        uploaded_file = client.files.upload(file=tmp_file_path)
        result = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                uploaded_file,
                "Describe the content of this image in detail, focusing on any text, objects, or relevant features that could help answer questions about it."
            ]
        )
        return result.text
    finally:
        os.remove(tmp_file_path)


def read_image_file(file_name=None, b64_string=None, directory="uploads"):
    if not file_name and not b64_string:
        return "Error: Provide either 'file_name' or 'b64_string'."

    if directory not in ["uploads", "outputs"]:
        return f"Error: Unsupported directory '{directory}'. Must be 'uploads' or 'outputs'."

    try:
        if file_name:
            file_path = os.path.join(directory, file_name)
            suffix = os.path.splitext(file_name)[-1] or ".png"
            with open(file_path, "rb") as f:
                image_bytes = f.read()

        elif b64_string:
            if b64_string.startswith("data:image/"):
                header, b64_string = b64_string.split(",", 1)
                # Optional: extract file extension from MIME type
                suffix = "." + header.split("/")[1].split(";")[0]
            else:
                suffix = ".png"

            image_bytes = base64.b64decode(b64_string)

        return get_image_description(image_bytes, suffix)

    except Exception as e:
        return f"Error processing image: {e}"