import os
import json

def save_to_json(json_string: str, file_name: str) -> str:
    if not file_name.endswith(".json"):
        return "Error: File name must end with '.json'."

    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, file_name)

    try:
        # Validate and pretty-print the JSON before saving
        parsed = json.loads(json_string)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)
        return f"File saved successfully as {file_name} in outputs/"
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON string — {e}"
    except Exception as e:
        return f"Error saving JSON file: {e}"