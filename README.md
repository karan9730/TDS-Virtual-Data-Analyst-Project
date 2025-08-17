# TDS Virtual Data Analyst Project

## Overview
The **TDS Virtual Data Analyst Project** is a Flask-based application that processes user queries using a **Planner–Worker LLM architecture** and a collection of data-processing tools.  
It can:

- Read and process files  
- Scrape websites  
- Retrieve relevant course content  
- Execute multi-step reasoning and transformations via tool calls  

The app can run **locally** or be deployed to **Hugging Face Spaces** using a custom Dockerfile.

## Files & Structure
   .
   ├── app.py # Main Flask application
   ├── llm_conversation.py # Orchestrates Planner–Worker conversation
   ├── worker_llm.py # Worker LLM logic
   ├── utils/ # Planner and helper modules
   ├── tools/ # Individual tools + JSON definitions
   ├── uploads/ # Input files (auto-created)
   ├── outputs/ # Generated files (auto-created)
   ├── Dockerfile # Container definition for Hugging Face
   ├── space.yaml # Hugging Face Spaces configuration
   ├── LICENSE # MIT license
   └── README.md

## Setup Instructions (Optional: Local Development)

1. **Clone the repository**:
```bash
git clone https://github.com/<your-username>/tds-virtual-data-analyst
cd tds-virtual-data-analyst
```

2. **Create a virtual environment** (optional but recommended):
   ```
   python3 -m venv .venv
   source .venv/bin/activate   # On Windows: `.venv\Scripts\activate`
   ```

3. **Install dependencies**:
   We use uv to handle dependencies declared in /// script headers:

   ```
   pip install uv
   uv pip install --system flask flask-cors werkzeug httpx google-generativeai asyncio typing beautifulsoup4 pandas playwright PyMuPDF
   playwright install --with-deps chromium
   ```

4. **Run the application**:
   ```
   uv run app.py
   ```

## Docker Usage (Recommended)
   Build the image
   docker build -t tds-vda .
   
   Run the container
   ```
     docker run -p 7860:7860 \
     -e GENAI_API_KEY=your_google_api_key \
     -e AIPIPE_TOKEN=your_aipipe_token \
     tds-vda
   ```
   
   The application will be available at http://localhost:7860.

 # API Endpoints

   GET / → Returns a message indicating the API is running.
   
   POST /api/ → Accepts uploaded files and processes them.
   
   Supported form fields
   
   - questions.txt → Text file containing questions/instructions
   
   - image.png (optional) → Image file for analysis/conversion
   
   - data.csv (optional) → CSV file for processing/extraction
   
   - and other file types

  # Example Usage

     ```
     curl "http://localhost:7860/api/" \
     -F "questions.txt=@questions.txt" \
     -F "image.png=@image.png" \
     -F "data.csv=@data.csv"
     ```
   ## Response:

   A JSON object containing results, possibly including:
   
   File paths in outputs/
   
   Structured data from the processing pipeline

## License
This project is licensed under the MIT License.
