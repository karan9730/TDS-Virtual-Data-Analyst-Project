# formulate_response.py
import os
import base64
import re

OUTPUT_FOLDER = "/tmp/outputs"

def prepare_response(conversation_result: str) -> dict:
    """
    Takes the final planner message from run_conversation and
    returns a structured JSON including base64-encoded files if any.
    """
    if not conversation_result:
        return {"final_answer": "", "files": [], "status": "complete"}

    # Clean escape characters
    cleaned_result = conversation_result.replace("\\", "").strip()

    # Extract filenames from 'Files to be returned' line
    files_to_return = []
    match = re.search(r"Files to be returned\s*:\s*\[([^\]]*)\]", cleaned_result, re.IGNORECASE)
    if match:
        files_list_str = match.group(1)
        # Split by comma and strip whitespace/quotes
        files_to_return = [f.strip().strip('"').strip("'") for f in files_list_str.split(",") if f.strip()]

        # Remove the 'Files to be returned' line from the final answer
        cleaned_result = re.sub(r"Files to be returned\s*:\s*\[[^\]]*\]", "", cleaned_result, flags=re.IGNORECASE).strip()

    # Encode files as base64
    encoded_files = []
    for filename in files_to_return:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                file_bytes = f.read()
                b64_content = base64.b64encode(file_bytes).decode("utf-8")
                encoded_files.append({"filename": filename, "content_base64": b64_content})
        else:
            # If file missing, just note it
            encoded_files.append({"filename": filename, "error": "File not found"})

    return {
        "final_answer": cleaned_result,
        "files": encoded_files,
        "status": "complete"
    }