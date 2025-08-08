import os
import pandas as pd # type: ignore

def read_csv_file(file_name: str, directory: str = "uploads") -> str:
    file_path = os.path.join(directory, file_name)
    
    if not os.path.isfile(file_path):
        return f"[Error] File not found: {file_path}"
    
    try:
        df = pd.read_csv(file_path)
        preview = df.head(10).to_string(index=False)
        return f"First 10 rows of {file_name}:\n\n{preview}"
    except Exception as e:
        return f"[Error] Failed to read CSV file: {e}"
