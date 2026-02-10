#!/bin/bash
echo "🚀 STARTING APP..."
echo "📂 Current Directory: $(pwd)"
echo "📂 Listing output directory:"
ls -la output/ || echo "❌ output/ directory missing"
echo "📂 Listing web/dist directory:"
ls -la web/dist/ || echo "❌ web/dist/ directory missing"
echo "🔧 ENV: PORT=$PORT"

# Ensure output directory exists to prevent crash if missing
mkdir -p output

# Start uvicorn
echo "🔥 Running uvicorn..."
exec python -m uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
