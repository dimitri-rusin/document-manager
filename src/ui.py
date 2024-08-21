from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Any
import os
import subprocess
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Load the path from environment variable
DOCUMENTS_PATH = os.getenv("DM__DOCUMENTS_PATH")
if not DOCUMENTS_PATH:
    raise RuntimeError("DOCUMENTS_PATH environment variable is not set.")

# Load default configuration for context lines from environment variables
try:
    DEFAULT_LINES_BEFORE = int(os.getenv("DM__LINES_BEFORE"))
    DEFAULT_LINES_AFTER = int(os.getenv("DM__LINES_AFTER"))
except (TypeError, ValueError) as e:
    raise RuntimeError("Invalid configuration for context lines: " + str(e))

# Ensure the DOCUMENTS_PATH exists and is a directory
if not os.path.exists(DOCUMENTS_PATH):
    raise RuntimeError("DOCUMENTS_PATH does not exist.")
if not os.path.isdir(DOCUMENTS_PATH):
    raise RuntimeError("DOCUMENTS_PATH is not a directory.")

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/search/", response_model=Dict[str, List[Dict[str, Any]]])
async def search(
    keyword: str = Query(..., min_length=1, description="The keyword to search for")
):
    search_results = {}

    for root, dirs, files in os.walk(DOCUMENTS_PATH):
        for file in files:
            if not file.endswith('.txt'):  # Only process text files
                continue
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if keyword.lower() in line.lower():
                            if file_path not in search_results:
                                search_results[file_path] = []

                            # Calculate the start and end line indices
                            start_line = max(i - DEFAULT_LINES_BEFORE, 0)
                            end_line = min(i + DEFAULT_LINES_AFTER + 1, len(lines))

                            # Collect the relevant lines
                            context_lines = lines[start_line:end_line]

                            search_results[file_path].append({
                                "line_number": i + 1,  # line_number as an integer
                                "context": [ln.strip() for ln in context_lines]  # Strip to remove extra whitespace
                            })
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error reading file {file_path}: {str(e)}")

    return search_results

@app.post("/open-in-sublime/")
async def open_in_sublime(filepath: str = Query(..., description="The path of the file to open"), line: int = Query(..., description="The line number to open at")):
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    command = ["subl", f"{os.path.abspath(filepath)}:{line}"]  # Ensure full absolute path

    try:
        subprocess.Popen(command)
        return {"message": f"Opened {filepath} at line {line} in Sublime Text"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to open file in Sublime Text: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
