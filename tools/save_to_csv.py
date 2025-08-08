# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
# ]
# ///

import pandas as pd
import os
from typing import Union, List, Dict

def save_to_csv(result: Dict[str, Union[str, List[str]]], file_name: str = "output.csv") -> str:
    """
    Saves extracted data (from get_relevant_data) to a CSV file.
    
    Parameters:
        result (dict): Expected to contain a key 'data' with a list of strings.
        file_name (str): The name of the file to save to. Defaults to 'output.csv'.

    Returns:
        str: Message confirming the file save.
    """
    # Basic format validation
    if "data" not in result:
        return "Error: No 'data' key found in input. Nothing was saved."

    raw_rows = result["data"]
    if not isinstance(raw_rows, list) or not all(isinstance(row, str) for row in raw_rows):
        return "Error: 'data' must be a list of strings."

    # Convert rows into list of list (split using whitespace or multiple spaces)
    parsed_rows = [r.split() for r in raw_rows]

    # Determine the output path
    output_path = os.path.join("outputs", file_name)

    # Create DataFrame and save
    df = pd.DataFrame(parsed_rows)
    df.to_csv(output_path, index=False, header=False)

    return f"Data successfully saved to {output_path}"
