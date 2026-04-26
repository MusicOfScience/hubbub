#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "No .env found; using .env.example defaults"
    export $(grep -v '^#' .env.example | xargs)
fi

echo "Starting Margin of Error..."
streamlit run frontend/app.py \
    --server.port 8501 \
    --server.headless true \
    --browser.gatherUsageStats false
