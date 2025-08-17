import os
import json
import re

from utils.planner import generate_planner_response
from worker_llm import tools, run_worker, execute_tool_call


def run_conversation():
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

    planner_messages = [
    {
        "role": "system",
        "content": f"""[Planner]
You are a **Virtual Data Analyst** trained using course materials from a data tools class.
You have access to the following tools:
{tool_summaries}

Special Tools:
📚 'reference_course_content' - Reference Tool:
- Use reference_course_content to retrieve tips or snippets from course material relevant to any text fed to the tool.
- This is for guidance or context — it is **not a replacement** for solving the question.

📝 Note:
- Be specific with your instruction steps, name any files you might be talking about explicitly, the worker would not remember them.
- Do not tell worker to read html files directly. use the `get_relevant_data` tool with guessed js_selector to extract data from HTML files.
- Do not dump multiple tasks/questions in a single step, keep them in mind, you have the entire conversation history, make the steps concise and short.
- Try to break down any preliminary tasks and the questions into smaller steps that the worker can carry, don't overload it with multiple tasks at once.
- execute_code doesn't carry over multiple steps, so if you have a complex task, try to do it in a single step.
- Do remember that if the entire question is code related and wouldn't work in tiny steps, you can send a single long code string at once to the worker.

🌟 Extremely important, when writing code, use print statements in order to get relevant outputs, otherwise no output will be given by worker.
🌟 do not put '/n' in your code, it can cause problems, using ''' <code> ''' should solve this issue.

🐍 'execute_code' - Custom Code Execution Tool:
- All code executed by the tool will be in **Python**.
- For code-related steps:
    1. Think over a singular long python script that would handle the task(s) at hand.
    2. Send the script to the worker in your step.
    3. enclose the python code in triple backticks (```) to ensure it is treated as code.
- Execution time is capped at 30 seconds; try to keep code concise.
- If the questions can be done in subsequent scripts, you can do that, but try to keep it simple.
- Example:
  Step 2:
  - Action: Execute this code '''print(2+3)'''.
  - Tool: execute_code
  - Expected Output: The sum as an integer.
  (Worker will write valid Python code to perform this calculation.)

🗂️ Directory Structure:
- `/tmp/uploads/` contains input files (e.g., `questions.txt`, `.csv`, `.db`, `.html`, etc.).
- `/tmp/outputs/` is where processed/generated files are saved.
- Do **not** include `/tmp/uploads/` or `/tmp/outputs/` in filenames; plain filenames like `"data.csv"` are sufficient.
- Reading tools require `"directory"` as `"/tmp/uploads"` or `"/tmp/outputs"` depending on location.
- Saving tools automatically save into `/tmp/outputs/`.

⚠️ Restrictions:
- Never read large files (like `.html`) directly; use a compact version (e.g., `dom_structure.txt`).
- If CSS-based extraction fails, try to guess an appropriate javascript selector after inspecting url.

📌 Handling Multiple Questions:
- If `questions.txt` has multiple questions, process them **one at a time**.
- If a question is problematic or takes too long, move on to the next.

🧠 Output & File Handling Rules:
- Prefer plain **text responses** unless structured formats are explicitly requested.
- Only save files if:
    1. The question explicitly asks for a file, or
    2. A file is needed for downstream tools.
- Do **not** invent filenames.

📋 Step-by-Step Planning:
- Begin by instructing Worker to read `/tmp/uploads/questions.txt` using `read_text_file`.
- Formulate steps **one at a time** based on the file content.
- Define filenames and instruct Worker to use exact names.
- Do **not** include multiple steps in a single message.
- Do **not** include final answers in any step text; leave that for the end.

✅ End your process with:
Final Answer: <final explanation or result>  
Files to be returned: [<filename1>, <filename2>, ...]

📌 Step Format:
Step X:
- **Action**: What should be done.
- **Tool**: Tool/library to use (e.g., `pandas`, `read_parquet_head`, etc.).
- **Expected Output**: What this step should produce.
"""
        },
        {
            "role": "user",
            "content": "[User] Please ask the Worker LLM to read `/tmp/uploads/questions.txt` for you and send the contents."
        }
    ]

    worker_messages = [
    {
        "role": "system",
        "content": f"""[Worker]
You are a **Worker LLM** that follows instructions from a Planner one step at a time.
You have access to the following tools:
{tool_summaries}

Special Tools:
📚 'reference_course_content' - Reference Tool:
- Accepts a short query and returns relevant course tips.
- Return tips exactly as provided, do not summarize or alter wording.

🐍 'execute_code' - Custom Code Execution Tool:
- Runs Python code in isolation and returns the raw output.
- Your job when told to execute code is to pass along as input the code string given by planner.
- Always execute the code and **return only the result**, not the code or reasoning.

🗂️ Directory Structure:
- Input files are in `/tmp/uploads/`.
- Output files go to `/tmp/outputs/`.
- Use **plain filenames only** — do not include the full path.
- Reading tools: specify `"directory": "/tmp/uploads"` or `"directory": "/tmp/outputs"`.
- Writing tools save automatically to `/tmp/outputs/`.

🔒 Rules:
✅ Always:
- Act on planner instructions using the appropriate tools.
- Return the raw output for every tool.
- Confirm filenames used, if any.

🚫 Never:
- Rephrase or summarize file content.
- Invent extra logic unrelated to the Planner.
- Include `/tmp/uploads/` or `/tmp/outputs/` in filenames unnecessarily.
- Include explanations or commentary in the output.

🔁 Stateless:
- Forget everything after each step.

📤 For each step:
- Planner instructions are in plain words.
- Understand them in order to carry out your tasks.
- Use the appropriate tool for the Planner's instructions.
- Return tool outputs exactly as they appear — do not summarize.
"""
    }
]


    final_answer = None
    MAX_ITERATIONS = 5

    def detect_quota_or_malformed(resp_str):
        try:
            resp_json = json.loads(resp_str)
            msg = resp_json.get("message", "").lower()
            if "usage" in msg or "quota" in msg or "exceeded" in msg:
                return f"Quota exceeded: {resp_json.get('message')}"
        except Exception:
            # Not JSON or no quota message found
            pass
        return None

    iteration = 0
    while iteration < MAX_ITERATIONS:
        iteration += 1

        # --- PLANNER THINKS ---
        planner_response = generate_planner_response(planner_messages)
        planner_messages.append({"role": "assistant", "content": planner_response})
        print("Planner:", planner_response)

        quota_error = detect_quota_or_malformed(planner_response)
        if quota_error:
            print(f"Planner quota error detected: {quota_error}")
            return f"Error: {quota_error}"
        
        # --- CHECK FOR FINAL ANSWER BEFORE WORKER EXECUTION ---
        if isinstance(planner_response, str) and re.search(r"final answer\s*[:\-]", planner_response, re.IGNORECASE):
            final_answer = planner_response.replace("\\", "")
            planner_messages.append({"role": "assistant", "content": planner_response})
            break  # terminate loop immediately, Worker is NOT called

        # --- WORKER EXECUTES (stateless per step) ---
        worker_step_messages = [
            {"role": "system", "content": worker_messages[0]["content"]},
            {"role": "user", "content": planner_response}
        ]
        worker_response = run_worker(worker_step_messages)

        quota_error = detect_quota_or_malformed(
            worker_response if isinstance(worker_response, str) else worker_response.get("content", "")
        )
        if quota_error:
            print(f"Worker quota error detected: {quota_error}")
            return f"Error: {quota_error}"

        tool_outputs = []

        if isinstance(worker_response, dict) and "tool_calls" in worker_response:
            for tool_result in worker_response.get("tool_results", []):
                content = tool_result["content"]
                tool_outputs.append(content)
                worker_messages.append({"role": "assistant", "content": f"[Worker] {content}"})
                planner_messages.append({"role": "user", "content": f"[Worker] {content}"})
                print("Worker:", content)
        else:
            content = worker_response.get("content", worker_response) if isinstance(worker_response, dict) else worker_response
            worker_messages.append({"role": "assistant", "content": f"[Worker] {content}"})
            planner_messages.append({"role": "user", "content": f"[Worker] {content}"})
            print("Worker:", content)

        # --- Check for final answer after appending everything ---
        if isinstance(planner_response, str) and re.search(r"final answer\s*[:\-]", planner_response, re.IGNORECASE):
            final_answer = planner_response
            # Optionally append the worker output one last time if any
            for output in tool_outputs:
                planner_messages.append({"role": "user", "content": f"[Worker] {output}"})
            break

    else:
        # Loop exhausted without final answer
        return "Error: Maximum iteration limit reached without final answer."

    final_answer = final_answer.replace("\\", "")
    return final_answer


if __name__ == "__main__":
    print(run_conversation())