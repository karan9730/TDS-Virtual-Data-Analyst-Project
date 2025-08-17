import os
import pandas as pd  # type: ignore

ALLOWED_DIRS = {
    "uploads": "/tmp/uploads",
    "outputs": "/tmp/outputs"
}

def read_csv_file(file_name: str, directory_name: str = "uploads") -> str:
    if directory_name not in ALLOWED_DIRS:
        return f"[Error] Invalid directory name: {directory_name}. Allowed: {list(ALLOWED_DIRS.keys())}"
    
    directory = ALLOWED_DIRS[directory_name]
    file_path = os.path.join(directory, file_name)
    
    if not os.path.isfile(file_path):
        return f"[Error] File not found: {file_path}"
    
    try:
        df = pd.read_csv(file_path)
        preview = df.head(10).to_string(index=False)
        return f"First 10 rows of {file_name} in {directory_name}:\n\n{preview}"
    except Exception as e:
        return f"[Error] Failed to read CSV file: {e}"