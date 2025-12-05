#!/bin/bash
set -e

cd "$(dirname "$0")"

# =============================================================================
#  ENVIRONMENT CONFIGURATION
# =============================================================================
# Environment: dev or staging (default: dev)
APP_ENV=${APP_ENV:-dev}
echo "Environment: $APP_ENV"

# Read ports from dagster_config.yaml based on APP_ENV using Python
CONFIG_FILE="./config/dagster_config.yaml"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: $CONFIG_FILE not found"
    exit 1
fi

# Use Python to reliably parse YAML and extract ports
read -r DAGSTER_PORT FLOWER_PORT < <(python3 << PYTHON_EOF
import re
import sys
import os

# Change to script directory to ensure relative paths work
os.chdir('.')

with open('$CONFIG_FILE', 'r') as f:
    content = f.read()

# Build regex pattern with the environment name
app_env = '$APP_ENV'
env_pattern = r'  ' + app_env + r':\s*\n((?:\s{4}\w+:.*\n?)*)'
env_match = re.search(env_pattern, content)

if not env_match:
    print("ERROR: Environment '" + app_env + "' not found in config", file=sys.stderr)
    sys.exit(1)

env_block = env_match.group(1)

# Extract dagster_port and flower_port
dagster_match = re.search(r'dagster_port:\s*(\d+)', env_block)
flower_match = re.search(r'flower_port:\s*(\d+)', env_block)

if not dagster_match:
    print("ERROR: dagster_port not found for environment '" + app_env + "'", file=sys.stderr)
    sys.exit(1)

dagster_port = dagster_match.group(1)
flower_port = flower_match.group(1) if flower_match else '5555'

print(dagster_port + ' ' + flower_port)
PYTHON_EOF
)

if [ -z "$DAGSTER_PORT" ]; then
    echo "ERROR: Could not find dagster_port for environment '$APP_ENV' in $CONFIG_FILE"
    exit 1
fi

echo "Dagster port: $DAGSTER_PORT"
echo "Flower port: $FLOWER_PORT"

export APP_ENV DAGSTER_PORT FLOWER_PORT

# =============================================================================
#  Validate virtual environment
# =============================================================================
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Run: ./app_setup.sh"
    exit 1
fi

PYTHON="venv/Scripts/python"
CELERY="venv/Scripts/celery"

# macOS / Linux detection for venv path
if [ ! -f "$PYTHON" ]; then
    PYTHON="venv/bin/python3"
    CELERY="venv/bin/python3 -m celery"
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
    brew services start redis
    echo "Redis Running"
fi

###############################################
#          CHECK / START MONGODB
###############################################
echo "Checking MongoDB status..."

# Load MongoDB config from YAML (use venv Python)
read -r MONGO_PORT MONGO_USER MONGO_PASS MONGO_AUTH < <($PYTHON -c "
import os
from omegaconf import OmegaConf

config_file = './config/database_config.yaml'
cfg = OmegaConf.load(config_file)
connection_type = cfg.mongodb.connection_type

if connection_type == 'local':
    port = str(cfg.mongodb.local.port).strip()
    user = str(cfg.mongodb.local.username).strip()
    pwd = str(cfg.mongodb.local.password).strip()
    auth = str(cfg.mongodb.local.auth_source).strip()
    print(f\"{port} {user} {pwd} {auth}\")
else:
    print('0 0 0 0')
")

# Only check/start MongoDB for local connection type
if [ "$MONGO_PORT" != "0" ]; then
    # 1. Check if MongoDB is running
    if lsof -i :$MONGO_PORT >/dev/null 2>&1; then
        echo "✔ MongoDB already running on localhost:$MONGO_PORT"
    else
        # 2. Check if a Docker MongoDB container already exists
        if docker ps -a --format "{{.Names}}" | grep -q "^mongodb$"; then
            echo "✔ MongoDB container exists"

            # Start it if stopped
            if ! docker ps --format "{{.Names}}" | grep -q "^mongodb$"; then
                echo "Starting existing mongodb container..."
                docker start mongodb >/dev/null
                sleep 3
            fi
        else
            # 3. Create new MongoDB container
            echo "No MongoDB found — creating new Docker MongoDB container..."

            docker run -d \
              --name mongodb \
              -p $MONGO_PORT:27017 \
              -e MONGO_INITDB_ROOT_USERNAME=$MONGO_USER \
              -e MONGO_INITDB_ROOT_PASSWORD=$MONGO_PASS \
              mongo:6

            echo "✔ MongoDB container created"
            sleep 10
        fi

        # 4. Verify MongoDB is responsive and authenticate with credentials
        echo "Waiting for MongoDB to be fully initialized..."
        MONGO_READY=false
        for i in {1..30}; do
            if docker exec mongodb mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
                echo "✔ MongoDB is running"
                MONGO_READY=true
                break
            fi
            sleep 2
        done

        if [ "$MONGO_READY" = true ]; then
            echo "Validating MongoDB authentication with credentials..."
            sleep 2
            docker exec mongodb mongosh --authenticationDatabase "$MONGO_AUTH" -u "$MONGO_USER" -p "$MONGO_PASS" --eval "db.adminCommand('ping')" >/dev/null 2>&1 && echo "✔ MongoDB authentication successful" || echo "⚠ Note: Authentication will be available after full initialization"
        fi
    fi
else
    echo "ℹ Using MongoDB Atlas - skipping local MongoDB checks"
fi

# -----------------------------
#  Start services
# -----------------------------
echo "Starting services..."

export PYTHONPATH="$(pwd)"


echo "Killing any existing processes on ports $DAGSTER_PORT, $FLOWER_PORT..."
lsof -ti:$DAGSTER_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:$FLOWER_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 5

echo "Cleaning up Dagster home..."
rm -rf dagster_home/.dagster/runs 2>/dev/null || true

# PROJECT_ROOT=$(pwd)
# export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

echo "Starting Celery worker..."
# Worker configuration from celery_config.yaml (pool: solo for Windows)
$CELERY -A app.celery_framework_app worker --loglevel=info &
CELERY_PID=$!

echo "Starting Flower on port $FLOWER_PORT..."
# Flower for task monitoring
$CELERY -A app.celery_framework_app flower --port=$FLOWER_PORT --persistent=false 2>&1 &
FLOWER_PID=$!

echo "Starting Dagster on port $DAGSTER_PORT..."
$PYTHON -m dagster dev -m app.dagster_framework_app --port $DAGSTER_PORT > dagster.log 2>&1 &
DAGSTER_PID=$!

# Sleep to allow services to start
sleep 3

# =============================================================================
#  Summary
# =============================================================================
echo ""
echo "=========================================="
echo "Services started:"
echo "=========================================="
echo "Environment:        $APP_ENV"
echo "Celery Worker PID:  $CELERY_PID"
echo "Flower PID:         $FLOWER_PID     (http://localhost:$FLOWER_PORT)"
echo "Dagster PID:        $DAGSTER_PID    (http://localhost:$DAGSTER_PORT)"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop..."

trap "kill $CELERY_PID $FLOWER_PID $DAGSTER_PID 2>/dev/null" EXIT

wait
