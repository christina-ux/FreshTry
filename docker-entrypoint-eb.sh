#!/bin/bash
set -e

# Print environment information
echo "Starting PolicyEdgeAI with environment: $APP_ENV"
echo "FastAPI port: $PORT"
echo "Streamlit port: $STREAMLIT_PORT"

# Create necessary directories if they don't exist
mkdir -p /app/data/uploads
mkdir -p /app/data/reports
mkdir -p /app/data/dashboard
mkdir -p /app/data/scoring
mkdir -p /app/logs

# Start Streamlit in the background
echo "Starting Streamlit dashboard..."
nohup streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=$STREAMLIT_PORT --server.enableCORS=false > /app/logs/streamlit.log 2>&1 &

# Start FastAPI in the foreground
echo "Starting FastAPI server..."
exec uvicorn app:app --host 0.0.0.0 --port $PORT