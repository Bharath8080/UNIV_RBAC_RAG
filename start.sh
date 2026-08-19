#!/bin/bash
set -e

echo "🚀 Starting FastAPI backend on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Wait briefly for FastAPI to be healthy
sleep 3

echo "🎨 Starting Streamlit UI frontend on port 8501..."
export BACKEND_URL="http://127.0.0.1:8000"
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
