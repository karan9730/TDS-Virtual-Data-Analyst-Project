# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
# ]
# ///

import pandas as pd  # type: ignore
import os
from typing import Any, Union, List, Dict

def save_to_csv(data, file_name):
    import csv, os

    # Normalize input: if it's an object with a 'data' key, extract it
    if isinstance(data, dict) and "data" in data:
        data = data["data"]

    # Ensure outputs directory exists
    os.makedirs("outputs", exist_ok=True)
    file_path = os.path.join("outputs", file_name)

    # Write to CSV
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in data:
            # Wrap row in list if it's a single string
            if isinstance(row, str):
                writer.writerow([row])
            else:
                writer.writerow(row)