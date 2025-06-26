#!/bin/bash

# Start FastAPI backend on port 8000
uvicorn patients_api:app --host 0.0.0.0 --port 8000 &

# Give FastAPI time to start
sleep 3

# Start Flask frontend on port 7860 (required by HF Spaces)
export FLASK_RUN_PORT=7860
export FLASK_RUN_HOST=0.0.0.0
python app.py