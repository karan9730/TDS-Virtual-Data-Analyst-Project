# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "flask",
#    "flask-cors",
#    "werkzeug",
#    "httpx",
#    "google-generativeai",
#    "asyncio",
#    "typing",
#    "beautifulsoup4",
#    "pandas",
#    "playwright",
#    "PyMuPDF",
# ]
# ///

import os
import re
from flask import Flask, request, jsonify # type: ignore
from flask_cors import CORS # type: ignore
from werkzeug.utils import secure_filename # type: ignore

from llm_conversation import run_conversation  # New orchestration logic

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/health")
def health():
    return "OK", 200

@app.route("/api/", methods=["POST"])
def handle_query():
    if not request.files:
        return jsonify({"error": "No files uploaded"}), 400

    for filename, file in request.files.items():
        safe_name = secure_filename(filename)
        file_path = os.path.join(UPLOAD_FOLDER, safe_name)
        file.save(file_path)

    # Run the planner-worker interaction loop
    try:
        final_answer = run_conversation()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "status": "complete",
        "final_answer": final_answer
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port)