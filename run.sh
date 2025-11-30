#!/bin/bash
set -e

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Run: ./app_setup.sh"
    exit 1
fi

PYTHON="venv/Scripts/python"
CELERY="venv/Scripts/celery"
if [ ! -f "$PYTHON" ]; then
    PYTHON="venv/bin/python"
    CELERY="venv/bin/celery"
fi

echo "Starting services..."

echo "Starting Celery worker..."
$CELERY -A app.celery_app worker --loglevel=info &
CELERY_PID=$!

echo "Starting Flower..."
$CELERY -A app.celery_app flower --port=5555 &
FLOWER_PID=$!

echo "Starting Dagster..."
$PYTHON app/dagster_app.py &
DAGSTER_PID=$!

echo ""
echo "Services started:"
echo "  Celery Worker PID: $CELERY_PID"
echo "  Flower PID: $FLOWER_PID (http://localhost:5555)"
echo "  Dagster PID: $DAGSTER_PID"
echo ""
echo "Press Ctrl+C to stop..."

trap "kill $CELERY_PID $FLOWER_PID $DAGSTER_PID 2>/dev/null" EXIT

wait