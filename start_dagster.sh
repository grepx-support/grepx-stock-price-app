#!/bin/bash
# Start Dagster dev server only

set -e

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/Scripts/activate
fi

# Start Dagster dev server
echo "Starting Dagster dev server..."
dagster dev -m dagster_app

