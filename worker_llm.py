# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "asyncio",
#    "httpx",
#    "typing",
#    "playwright",
#    "pandas"
#    "beautifulsoup4",
#    "PyMuPDF",
#    "google-generativeai",
# ]
# ///

import json
import asyncio
import os
import httpx # type: ignore
from typing import Dict, Any

from tools.scrape_webpage import scrape_webpage
from tools.get_relevant_data import get_relevant_data
from tools.read_csv_file import read_csv_file
from tools.save_to_csv import save_to_csv
from tools.read_image_file import read_image_file
from tools.convert_to_base64 import convert_to_base64
from tools.read_pdf_file import read_pdf_file
from tools.read_text_file import read_text_file
from tools.save_to_json import save_to_json
from tools.execute_code import execute_code

# Tool definitions with name and description extracted dynamically

def load_tool_schemas(directory="tools/tool_jsons"):
    tools = []
    for file in os.listdir(directory):
        if file.endswith(".json"):
            with open(os.path.join(directory, file), "r", encoding="utf-8") as f:
                tools.append(json.load(f))
    return tools

tools = load_tool_schemas()

def run_worker(messages: list[dict[str, str]]) -> dict[str, Any]:
    import httpx # type: ignore
    import os
    import json

    response = httpx.post(
        "https://aipipe.org/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('AIPIPE_TOKEN')}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
        },
        timeout=60.0,
    )

    try:
        parsed = response.json()
    except Exception as e:
        print("JSON decode error:", e)
        print("Raw response text:", response.text)
        return {"content": f"Error: Invalid JSON response\n\n{response.text}"}

    # --- Append tool calls to gpt_response.json ---
    gpt_file = "/tmp/gpt_response.json"
    existing_calls = []
    if os.path.exists(gpt_file):
        try:
            with open(gpt_file, "r", encoding="utf-8") as f:
                existing_calls = json.load(f)
        except Exception:
            existing_calls = []

    # Collect current tool calls
    current_tool_calls = []
    if "choices" in parsed and parsed["choices"]:
        message = parsed["choices"][0]["message"]
        if "tool_calls" in message:
            current_tool_calls = message["tool_calls"]

    # Append current calls
    all_tool_calls = existing_calls + current_tool_calls
    with open(gpt_file, "w", encoding="utf-8") as f:
        json.dump(all_tool_calls, f, indent=2, ensure_ascii=False)

    # --- Execute tool calls ---
    tool_call_results = []
    for tool_call in current_tool_calls:
        result = execute_tool_call(tool_call)
        tool_call_results.append(result)

    # Return both the message content and all tool results
    return {
        "content": parsed["choices"][0]["message"] if "choices" in parsed else None,
        "tool_calls": current_tool_calls,
        "tool_results": tool_call_results
    }

def run_worker_followup(original_tool_call_msg, tool_outputs, planner_msg):
    followup = httpx.post(
        "https://aipipe.org/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('AIPIPE_TOKEN')}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                planner_msg,
                original_tool_call_msg,
                *tool_outputs
            ],
        },
        timeout=60.0,
    )
    with open("/tmp/followup_response.json", "w", encoding="utf-8") as f:
        f.write(followup.text)

    try:
        return followup.json()["choices"][0]["message"].get("content")
    except KeyError:
        return followup.text

def execute_tool_call(tool_call: dict) -> dict:
    function_name = tool_call["function"]["name"]
    parameters = json.loads(tool_call["function"]["arguments"])

    if function_name == "scrape_webpage":
        result = asyncio.run(scrape_webpage(**parameters))
        if result.get("status") == "success":
            return {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result["message"]
            }
        else:
            return {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": f"Error scraping page: {result.get('message')}"
            }

    elif function_name == "get_relevant_data":
        result = get_relevant_data(**parameters)
        return {
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": json.dumps(result)
        }

    elif function_name == "read_csv_file":
        result = read_csv_file(**parameters)
        return {
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": (
                f"Here are the first few rows of the CSV file. Do not interpret, summarize, or modify this. Just return it to the Planner as-is:\n\n{result}"
            )
        }

    elif function_name == "save_to_csv":
        result = save_to_csv(**parameters)
        return {"role": "tool", "tool_call_id": tool_call["id"], "content": result}
    
    elif function_name == "read_image_file":
        result = read_image_file(**parameters)
        return {
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": (
                f"Here is the image description. Do not interpret this — return it as-is to the Planner:\n\n{result}"
            )
        }
    
    elif function_name == "convert_to_base64":
        result = convert_to_base64(**parameters)
        return {
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": (
                f"The image file has been successfully converted to a base64 string:\n\n{result}"
            )
        }

    elif function_name == "read_text_file":
        result = read_text_file(**parameters)
        return {
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": f"the file's contents are as follows:\n\n{result}"  # inject actual content, not "{result}"
        }

    elif function_name == "read_pdf_file":
        result = read_pdf_file(**parameters)
        return {
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": (
                f"Here is the extracted text from the PDF. Do not interpret, summarize, or modify it. Just return it to the Planner as-is:\n\n{result}"
            )
        }
    
    elif function_name == "save_to_json":
        result = save_to_json(**parameters)
        return {
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": result
        }
    
    elif function_name == "execute_code":
        result = execute_code(**parameters)
        return {
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": json.dumps(result)
        }

    else:
        return {"role": "tool", "tool_call_id": tool_call["id"], "content": f"Tool '{function_name}' not implemented."}