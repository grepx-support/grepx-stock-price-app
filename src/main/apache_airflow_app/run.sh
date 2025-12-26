#!/usr/bin/env bash
set -e

echo "========================================="
echo "     Apache Airflow Standalone Setup"
echo "========================================="

### -----------------------------
### 1. SET AIRFLOW_HOME TO THIS FOLDER
### -----------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export AIRFLOW_HOME="${SCRIPT_DIR}"

echo "✔ AIRFLOW_HOME = $AIRFLOW_HOME"
cd "$AIRFLOW_HOME"

### -----------------------------
### 2. USE PYTHON 3.11 (Best wheel support)
### -----------------------------
if ! command -v python3.11 &> /dev/null; then
  echo "❌ Python 3.11 is required but not found"
  echo "Install it with: brew install python@3.11"
  exit 1
fi

PYTHON_CMD="python3.11"
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')

echo "✔ Using Python ${PYTHON_VERSION}"

### -----------------------------
### 3. INSTALL uv IF NOT PRESENT
### -----------------------------
if ! command -v uv &> /dev/null; then
  echo "⚠ uv not found — installing..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
else
  echo "✔ uv already installed"
fi

### -----------------------------
### 4. CREATE & ACTIVATE VENV
### -----------------------------
if [ ! -d "${SCRIPT_DIR}/venv" ]; then
  echo "✔ Creating .venv using uv…"
  uv venv --python=$PYTHON_CMD "${SCRIPT_DIR}/venv"
else
  echo "✔ Using existing venv"
  rm -rf "${SCRIPT_DIR}/venv/lib/python*/site-packages/grpc*"
fi

source "${SCRIPT_DIR}/venv/bin/activate"
which python
echo "✔ Virtual environment activated"

### -----------------------------
### 5. REMOVE GRPCIO CACHE
### -----------------------------
echo "Cleaning up any cached grpcio builds..."
rm -rf ~/.cache/uv/builds-v0
rm -rf ~/.cache/uv/sdists-v9

### -----------------------------
### 6. UPGRADE PIP
### -----------------------------
echo "Upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip

### -----------------------------
### 7. USE AIRFLOW 2.10.3 WITH LEGACY EXECUTION MODE
### ---------------------
AIRFLOW_VERSION=2.10.3
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

echo "Installing Apache Airflow ${AIRFLOW_VERSION}..."
echo "Using constraints: ${CONSTRAINT_URL}"

# Install without any compiled dependencies
$PYTHON_CMD -m pip install --no-cache-dir \
  --constraint "${CONSTRAINT_URL}" \
  "apache-airflow[webserver,crypto]==${AIRFLOW_VERSION}"

echo "✔ Airflow installation complete"

### -----------------------------
### 8. CONFIGURE AIRFLOW FOR LOCAL EXECUTION
### -----------------------------
echo "Configuring Airflow for stable local execution..."

# Create airflow.cfg with settings that prevent timeout issues
cat > "${SCRIPT_DIR}/airflow.cfg" <<'EOF'
[core]
dags_folder = /Users/mahesh/Desktop/Projects/grepx-orchestrator/price_app/src/main/apache_airflow_app/dags
base_log_folder = /Users/mahesh/Desktop/Projects/grepx-orchestrator/price_app/src/main/apache_airflow_app/logs
executor = SequentialExecutor
parallelism = 4
max_active_tasks_per_dag = 2
load_examples = True

[database]
sqlalchemy_pool_size = 5
sqlalchemy_pool_recycle = 3600

[scheduler]
catchup_by_default = False
dag_dir_list_interval = 300

[api]
auth_backends = airflow.api.auth.backend.default

[logging]
remote_logging = False

EOF

echo "✔ Airflow configuration created"

### -----------------------------
### 9. INSTALL EXTRA PYTHON PACKAGES
### -----------------------------
echo "========================================="
echo "Installing additional Python packages..."
echo "========================================="

$PYTHON_CMD -m pip install --no-cache-dir pandas==2.2.3

echo "✔ pandas installed"
python -c "import pandas; print(pandas.__version__)"

### -----------------------------
### 10. INITIALIZE DATABASE
### -----------------------------
echo "Initializing Airflow database..."
"${SCRIPT_DIR}/venv/bin/airflow" db migrate

echo "✔ Database initialized"

### -----------------------------
### 11. START AIRFLOW STANDALONE
### -----------------------------
echo "========================================="
echo "Starting Airflow Standalone..."
echo "========================================="
echo "⚠️  If you see timeout errors, this is normal and will stabilize"
echo "========================================="

"${SCRIPT_DIR}/venv/bin/airflow" standalone