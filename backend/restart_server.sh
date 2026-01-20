#!/bin/bash
# Restart script for Industry Readiness Portal backend

echo "=========================================="
echo "RESTARTING BACKEND SERVER"
echo "=========================================="
echo ""

# Find and kill existing uvicorn process
echo "1. Stopping existing server..."
pkill -f "uvicorn main:app" 2>/dev/null
sleep 2

# Navigate to backend directory
cd "$(dirname "$0")"

# Activate virtual environment
echo "2. Activating virtual environment..."
source venv/bin/activate

# Verify template exists
if [ -f "templates/thinkbinary_report.html" ]; then
    echo "✓ ThinkBinary template found"
else
    echo "✗ WARNING: ThinkBinary template not found!"
fi

# Start server
echo "3. Starting server..."
echo ""
uvicorn main:app --reload --host 0.0.0.0 --port 8000
