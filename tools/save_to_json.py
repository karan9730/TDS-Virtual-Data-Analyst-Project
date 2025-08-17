import os
import json
import traceback

def save_to_json(json_input, file_name: str) -> str:
    # Case-insensitive check for .json extension
    if not file_name.lower().endswith(".json"):
        return "Error: File name must end with '.json' (case-insensitive)."

    output_dir = "/tmp/outputs"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, file_name)

    try:
        # Accept dict/list directly, or parse JSON string
        if isinstance(json_input, (dict, list)):
            parsed = json_input
        elif isinstance(json_input, str):
            parsed = json.loads(json_input)
        else:
            return "Error: Input must be a JSON string, dict, or list."

        # Save as pretty-printed UTF-8 JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)

        return f"File saved successfully as {file_name} in /tmp/outputs"
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON string — {type(e).__name__}: {e}"
    except Exception as e:
        return f"Error saving JSON file — {type(e).__name__}: {e}\n{traceback.format_exc()}"