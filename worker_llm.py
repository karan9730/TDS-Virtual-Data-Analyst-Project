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

from tools.scrape_website import scrape_website
from tools.get_relevant_data import get_relevant_data
from tools.read_csv_file import read_csv_file
from tools.save_to_csv import save_to_csv
from tools.read_image_file import read_image_file
from tools.convert_to_base64 import convert_to_base64
from tools.read_pdf_file import read_pdf_file
from tools.read_text_file import read_text_file
from tools.save_to_json import save_to_json

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

    with open("tools/gpt_response.json", "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)

    if "choices" not in parsed or "message" not in parsed["choices"][0]:
        print("Malformed response:", parsed)
        return {"content": "Error: 'choices' not in response"}

    message = parsed["choices"][0]["message"]

    if "tool_calls" in message:
        tool_call_results = []
        for tool_call in message["tool_calls"]:
            tool_result = execute_tool_call(tool_call)
            tool_call_results.append(tool_result)
        return tool_call_results[0]  # Return first result for now (you can change this)

    return message

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
    with open("tools/followup_response.json", "w", encoding="utf-8") as f:
        f.write(followup.text)

    try:
        return followup.json()["choices"][0]["message"].get("content")
    except KeyError:
        return followup.text

def execute_tool_call(tool_call: dict) -> dict:
    function_name = tool_call["function"]["name"]
    parameters = json.loads(tool_call["function"]["arguments"])

    if function_name == "scrape_website":
        asyncio.run(scrape_website(**parameters))
        return {"role": "tool", "tool_call_id": tool_call["id"], "content": f"Scraping completed and saved to {parameters['output_file']}"}

    elif function_name == "get_relevant_data":
        result = get_relevant_data(**parameters)
        return {"role": "tool", "tool_call_id": tool_call["id"], "content": json.dumps(result)}

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
            "content": (
                f"Here are the contents of the text file. Do not read, summarize, or plan based on this. Just return it to the Planner as-is:\n\n{result}"
            )
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

    else:
        return {"role": "tool", "tool_call_id": tool_call["id"], "content": f"Tool '{function_name}' not implemented."}