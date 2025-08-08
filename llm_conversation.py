import os
import json
import re

from utils.planner import generate_planner_response
from worker_llm import tools, run_worker, execute_tool_call, run_worker_followup


def run_conversation():
    # Extract tool summaries from the tools list
    tool_definitions = [
        {
            "name": tool["function"]["name"],
            "description": tool["function"]["description"]
        }
        for tool in tools if tool["type"] == "function"
    ]

    tool_summaries = "\n".join([
        f"{i+1}. `{tool['name']}`: {tool['description']}" for i, tool in enumerate(tool_definitions)
    ])

    # --- PLANNER CONVERSATION ---
    planner_messages = [
    {
        "role": "system",
        "content": f"""[Planner]
You are a **Virtual Data Analyst** trained using course materials from a data tools class.

You have access to the following tools:
{tool_summaries}

Most tools perform input → output transformations and can be chained into workflows.

🗂️ **Directory Structure**:
- `uploads/` contains input files (e.g., `questions.txt`, `.csv`, `.db`, `.html`, etc.).
- `outputs/` is where processed/generated files are saved.
- You do **not** need to include `uploads/` or `outputs/` in any filenames — filenames like `"data.csv"` are sufficient.
- Reading tools (e.g., `read_text_file`) require `"directory"` as `"uploads"` or `"outputs"` depending on file location.
- Saving tools (e.g., `save_to_csv`) **automatically save** into the `outputs/` folder.

⚠️ **Important Restrictions**:
- Never instruct reading large files (like `.html`) using `read_text_file`. Use `dom_structure.txt` or other tools instead.
- If CSS-based extraction fails, instruct the Worker to read `outputs/dom_structure.txt` instead — a compact version of the HTML structure.

📌 **Handling Multiple Questions**:
- If `questions.txt` has multiple questions, process them **one at a time**.
- If a question becomes problematic or takes too long, **move on to the next** to save time.

🧠 **Output & File Handling Rules**:
- Prefer plain **text responses** unless the question requests structured formats (e.g., JSON).
- Only use file-saving tools if:
  1. The question **explicitly** asks for file output (e.g., "save as CSV"), or
  2. A file is needed for downstream tools.
- Do **not** invent filenames or save results unless it’s justified by the question or plan.

📋 **Step-by-Step Planning**:
- Begin by instructing the Worker to read `uploads/questions.txt` using the `read_text_file` tool.
- Formulate steps **one at a time** based on the exact content of the file.
- Define all filenames yourself. Instruct the Worker to use your exact filenames and confirm them.
- Do **not** include multiple steps in a single message.
- Do **not** include planning steps in your final response.

✅ **End your process with**:
**Final Answer:** <final explanation or result>  
**Files to be returned:** [<filename1>, <filename2>, ...]

📌 **Each step must follow this format**:

Step X:
- **Action**: What should be done.
- **Tool**: Tool/library to use (e.g., `pandas`, `read_parquet_head`, etc.).
- **Expected Output**: What this step should produce.
"""
    },
    {
        "role": "user",
        "content": "[User] Please ask the Worker LLM to read `uploads/questions.txt` for you and send the contents."
    }
]

    worker_messages = [
    {
        "role": "system",
        "content": f"""[Worker]
You are a **Worker LLM** that follows instructions from a Planner one step at a time.

You have access to the following tools:
{tool_summaries}

🗂️ **Directory Structure**:
- Input files (e.g., `questions.txt`) are in the `uploads/` directory.
- Processed/generated files are saved to the `outputs/` directory.
- You must never include `uploads/` or `outputs/` in filenames — just use plain names like `"data.csv"`.
- When using reading tools, always specify `"directory": "uploads"` or `"directory": "outputs"`.
- Writing tools (e.g., `save_to_csv`) automatically save files into `outputs/`.

🔒 **Rules You Must Follow**:

✅ Always:
- Execute the step exactly as written — do not plan or interpret.
- Use **only the filename(s)** provided by the Planner.
- Mention the file used whenever reading from or writing to disk.
- Return tool outputs **exactly as they appear** — no rewriting, summarizing, or interpretation.

🚫 Never:
- Alter or rephrase file content.
- Add your own reasoning or responses.
- Save, rename, or read files unless told to.
- Add `outputs/` or `uploads/` into filenames.

🔁 You are stateless — forget everything after each step.

📤 After each step:
- Run the tool as directed.
- Return the raw tool output.
- Confirm filenames used, if any.
- Say nothing else.
"""
    }
]

    final_answer = None

    while True:
        # --- PLANNER THINKS ---
        planner_response = generate_planner_response(planner_messages)
        planner_messages.append({"role": "assistant", "content": f"[Planner] {planner_response}"})
        print("Planner:", planner_response)

        if re.search(r"\*\*Final Answer\*\* *:", planner_response, re.IGNORECASE):
            final_answer = planner_response
            break

        # --- WORKER EXECUTES ---
        worker_messages.append({"role": "user", "content": f"[Planner] {planner_response}"})
        worker_response = run_worker(worker_messages)

        tool_outputs = []
        original_tool_call_msg = None

        if "tool_calls" in worker_response:
            original_tool_call_msg = {
                "role": "assistant",
                "tool_calls": worker_response["tool_calls"]
            }

            for tool_call in worker_response["tool_calls"]:
                tool_output = execute_tool_call(tool_call)
                tool_outputs.append(tool_output)

        if worker_response.get("content") is None and tool_outputs and original_tool_call_msg:
            result = run_worker_followup(
                original_tool_call_msg, tool_outputs, worker_messages[-1]
            )
            worker_messages.append({"role": "assistant", "content": f"[Worker] {result}"})
            planner_messages.append({"role": "user", "content": f"[Worker] {result}"})
            print("Worker:", result)
        else:
            content = worker_response.get("content", "No content returned.")
            worker_messages.append({"role": "assistant", "content": f"[Worker] {content}"})
            planner_messages.append({"role": "user", "content": f"[Worker] {content}"})
            print("Worker:", content)

    return final_answer


if __name__ == "__main__":
    print(run_conversation())