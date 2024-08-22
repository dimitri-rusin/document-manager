from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import os
import re
import subprocess
import sys

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Load the path from environment variables
DOCUMENTS_PATH = os.getenv("DM__DOCUMENTS_PATH")
UPDATED_SCRIPT_PATH = os.getenv("DM__UPDATER_PATH")

if not DOCUMENTS_PATH:
    raise RuntimeError("DOCUMENTS_PATH environment variable is not set.")

if not UPDATED_SCRIPT_PATH:
    raise RuntimeError("DM__UPDATER_PATH environment variable is not set.")

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
    keyword: str = Query(..., min_length=1, description="The regular expression to search for")
):
    search_results = {}

    # Compile the regular expression from the keyword
    try:
        regex = re.compile(keyword, re.IGNORECASE)  # Compile with case-insensitive flag
    except re.error as e:
        raise HTTPException(status_code=400, detail=f"Invalid regular expression: {str(e)}")

    for root, dirs, files in os.walk(DOCUMENTS_PATH):
        for file in files:
            if not file.endswith('.txt'):  # Only process text files
                continue
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()  # Read the entire file content
                    matches = list(regex.finditer(content))  # Find all matches

                    if matches:
                        search_results[file_path] = []

                        for match in matches:
                            # Get the match start and end positions in the content
                            start, end = match.span()

                            # Convert the start and end positions to line numbers
                            start_line = content.count('\n', 0, start)
                            end_line = content.count('\n', 0, end)

                            # Extract context lines
                            lines = content.splitlines()
                            context_start = max(start_line - DEFAULT_LINES_BEFORE, 0)
                            context_end = min(end_line + DEFAULT_LINES_AFTER + 1, len(lines))
                            context_lines = lines[context_start:context_end]

                            search_results[file_path].append({
                                "line_number": start_line + 1,  # line_number as an integer
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

@app.post("/run-script/")
async def run_script():
    if not os.path.exists(UPDATED_SCRIPT_PATH):
        raise HTTPException(status_code=404, detail="Script file not found")

    try:
        # Run the script as a new process and stream its output to the console
        process = subprocess.Popen(
            ["python", os.path.abspath(UPDATED_SCRIPT_PATH)],
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True
        )

        # Wait for the process to complete
        process.communicate()

        if process.returncode != 0:
            raise HTTPException(status_code=500, detail="Script encountered an error during execution")

        return {"message": "Script executed successfully"}

    except Exception as e:
        print(f"Error running script: {str(e)}")  # Print the error for debugging
        raise HTTPException(status_code=500, detail=f"Failed to run script: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
