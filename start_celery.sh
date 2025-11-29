#!/bin/bash
# Start Celery worker only (cross-platform, docker-safe)

set -euo pipefail

# --------- Detect OS (Windows vs Linux/Mac) ----------
OS_TYPE=$(uname)
WINDOWS=false
if [[ "$OS_TYPE" == *"MINGW"* || "$OS_TYPE" == *"CYGWIN"* || "$OS_TYPE" == *"MSYS"* ]]; then
    WINDOWS=true
fi

# --------- Activate virtual environment ----------
if [ -d "venv" ]; then
    if $WINDOWS; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
else
    echo "Virtual environment not found! Run setup.sh first."
    exit 1
fi

# --------- Check if Redis is running (host or docker) ----------
echo "Checking Redis..."

if redis-cli ping > /dev/null 2>&1; then
    echo "Redis is running ✔"
else
    echo "WARNING: Redis not reachable via redis-cli."
    echo ""
    echo "Options:"
    echo "  - Start local Redis:      redis-server"
    echo "  - OR start Docker Redis:  docker run -p 6379:6379 redis"
    echo ""
#    exit 1
fi

# --------- Start Celery worker ----------
echo "Starting Celery worker..."

# Add current directory to PYTHONPATH to ensure tasks module can be found
celery -A celery_app worker --loglevel=info
