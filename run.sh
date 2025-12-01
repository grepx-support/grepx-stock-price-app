#!/bin/bash
set -e

cd "$(dirname "$0")"

# -----------------------------
#  Validate virtual environment
# -----------------------------
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Run: ./app_setup.sh"
    exit 1
fi

PYTHON="venv/Scripts/python"
CELERY="venv/Scripts/celery"

# macOS / Linux detection for venv path
if [ ! -f "$PYTHON" ]; then
    PYTHON="venv/bin/python3.12"
    CELERY="venv/bin/celery"
fi

# -----------------------------
#  DAGSTER_HOME SETUP
# -----------------------------
export DAGSTER_HOME="$(pwd)/dagster_home"

if [ ! -d "$DAGSTER_HOME" ]; then
    echo "Creating DAGSTER_HOME at $DAGSTER_HOME"
    mkdir -p "$DAGSTER_HOME"
fi

# Create dagster.yaml only if missing
if [ ! -f "$DAGSTER_HOME/dagster.yaml" ]; then
    echo "Creating dagster.yaml"
    cat > "$DAGSTER_HOME/dagster.yaml" <<EOF
local_artifact_storage:
  module: dagster.core.storage.root
  class: LocalArtifactStorage
  config:
    base_dir: \${DAGSTER_HOME}/artifacts

compute_logs:
  module: dagster.core.storage.local_compute_log_manager
  class: LocalComputeLogManager
  config:
    base_dir: \${DAGSTER_HOME}/compute_logs

run_launcher:
  module: dagster._core.launcher.in_process_launcher
  class: InProcessRunLauncher

telemetry:
  enabled: false
EOF
fi

# Check Redis status
echo "Checking Redis status..."
if lsof -i :6379 >/dev/null 2>&1 || docker ps 2>/dev/null | grep -q ':6379'; then
    echo "Redis is running"
else
    echo "ERROR: Redis not running on port 6379"
    exit 1
fi

# Check MongoDB status
echo "Checking MongoDB status..."
if docker ps 2>/dev/null | grep -q 'mongo'; then
    if docker exec mongodb mongosh --authenticationDatabase admin -u admin -p password123 --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
        echo "MongoDB is running and authenticated"
    else
        echo "ERROR: MongoDB authentication failed"
        exit 1
    fi
else
    echo "ERROR: MongoDB container not found"
    exit 1
fi

# -----------------------------
#  Start services
# -----------------------------
echo "Starting services..."

export PYTHONPATH="$(pwd)/.."

echo "Killing any existing processes on ports 3000, 5555..."
lsof -ti:3000 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:5555 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 3

echo "Cleaning up Dagster home..."
rm -rf dagster_home/.dagster/runs 2>/dev/null || true

echo "Starting Celery worker..."
$CELERY -A price_app.app.celery_framework_app worker --loglevel=info &
CELERY_PID=$!

echo "Starting Flower..."
$CELERY -A price_app.app.celery_framework_app flower --port=5555 &
FLOWER_PID=$!

echo "Starting Dagster..."
$PYTHON -m dagster dev -m price_app.app.dagster_framework_app --port 3000 > dagster.log 2>&1 &
DAGSTER_PID=$!

# -----------------------------
#  Summary
# -----------------------------
echo ""
echo "Services started:"
echo "  Celery Worker PID: $CELERY_PID"
echo "  Flower PID:       $FLOWER_PID     (http://localhost:5555)"
echo "  Dagster PID:      $DAGSTER_PID    (http://localhost:3000)"
echo ""
echo "Press Ctrl+C to stop..."

trap "kill $CELERY_PID $FLOWER_PID $DAGSTER_PID 2>/dev/null" EXIT

wait
