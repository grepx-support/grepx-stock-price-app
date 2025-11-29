#!/bin/bash
# Start both Celery and Dagster

set -e

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/Scripts/activate
fi

# Start Celery worker in background
echo "Starting Celery worker..."
./start_celery.sh &
CELERY_PID=$!

# Wait a moment for Celery to start
sleep 2

# Start Dagster dev server
echo "Starting Dagster dev server..."
./start_dagster.sh &
DAGSTER_PID=$!

echo ""
echo "Both services started!"
echo "Celery PID: $CELERY_PID"
echo "Dagster PID: $DAGSTER_PID"
echo ""
echo "To stop both services, press Ctrl+C or run:"
echo "  kill $CELERY_PID $DAGSTER_PID"

# Wait for both processes
wait

