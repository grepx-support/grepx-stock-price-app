#!/bin/bash
set -e

# ============================================================================
# Apache Airflow Setup & Run Script (Clean + Reproducible)
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AIRFLOW_HOME="$SCRIPT_DIR"
VENV_DIR="$PROJECT_ROOT/apache_airflow_app/venv_airflow"

AIRFLOW_VERSION="2.10.3"
PYTHON_CMD="python3.11"

echo "=========================================="
echo "Apache Airflow Setup & Run"
echo "=========================================="
echo "Project Root : $PROJECT_ROOT"
echo "Airflow Home : $AIRFLOW_HOME"
echo "Airflow Ver  : $AIRFLOW_VERSION"
echo ""

# ============================================================================
# 1. CHECK PYTHON VERSION
# ============================================================================
echo "▶ Step 1: Checking Python..."

if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ Python 3.11 not found"
    echo "Install with: brew install python@3.11"
    exit 1
fi

echo "✓ Using $($PYTHON_CMD --version)"

# ============================================================================
# 2. CREATE FRESH VENV
# ============================================================================
echo ""
echo "▶ Step 2: Creating virtual environment..."

rm -rf "$VENV_DIR"
$PYTHON_CMD -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "✓ Virtual environment ready"

# ============================================================================
# 3. UPGRADE PIP TOOLING
# ============================================================================
echo ""
echo "▶ Step 3: Upgrading pip..."

pip install --upgrade pip setuptools wheel 2>&1
echo "✓ pip upgraded"

# ============================================================================
# 4. INSTALL LOCAL LIBS FIRST
# ============================================================================
LOCAL_LIBS_DIR="$PROJECT_ROOT/../../.."  # go up 3 levels to reach grepx-orchestrator
LOCAL_LIBS_DIR="$LOCAL_LIBS_DIR/libs"    # then into libs

if [ -d "$LOCAL_LIBS_DIR" ]; then
    echo "▶ Installing all local libraries from $LOCAL_LIBS_DIR..."
    for lib in "$LOCAL_LIBS_DIR/"*; do
        [ -d "$lib" ] && pip install -e "$lib"  2>&1
    done
    echo "✓ Local libraries installed"
else
    echo "⚠️ $LOCAL_LIBS_DIR directory not found, skipping local libraries installation"
fi


# ============================================================================
# 4. INSTALL AIRFLOW (USING OFFICIAL CONSTRAINTS)
# ============================================================================
echo ""
echo "▶ Step 4: Installing Apache Airflow (constrained)..."

pip install \
  "apache-airflow==${AIRFLOW_VERSION}" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-3.11.txt" \
   2>&1

echo "✓ Apache Airflow installed"

# ============================================================================
# 5. INSTALL PROJECT REQUIREMENTS (ON TOP)
# ============================================================================
echo ""
echo "▶ Step 5: Installing project requirements..."

pip install -r "$PROJECT_ROOT/apache_airflow_app/requirements.txt" >/dev/null 2>&1

echo "✓ Project dependencies installed"


# ============================================================================
# 6. AIRFLOW CONFIG
# ============================================================================
echo ""
echo "▶ Step 6: Setting up airflow.cfg..."

mkdir -p "$AIRFLOW_HOME/dags" "$AIRFLOW_HOME/logs"

AIRFLOW_CFG="$AIRFLOW_HOME/airflow.cfg"

if [ ! -f "$AIRFLOW_CFG" ]; then
cat > "$AIRFLOW_CFG" << 'EOF'
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
    echo "✓ airflow.cfg created"
else
    echo "✓ airflow.cfg already exists"
fi

export AIRFLOW_HOME="$AIRFLOW_HOME"

# ============================================================================
# 7. INITIALIZE DB
# ============================================================================
echo ""
echo "▶ Step 7: Initializing Airflow DB..."

if [ ! -f "$AIRFLOW_HOME/airflow.db" ]; then
    airflow db migrate
    echo "✓ Database initialized"
else
    echo "✓ Database already exists"
fi

# ============================================================================
# 8. CREATE ADMIN USER
# ============================================================================
echo ""
echo "▶ Step 8: Creating admin user (if missing)..."

if ! airflow users list | grep -q "^admin"; then
    airflow users create \
        --username admin \
        --firstname Airflow \
        --lastname Admin \
        --role Admin \
        --email admin@example.com \
        --password admin123
    echo "✓ Admin user created"
else
    echo "✓ Admin user already exists"
fi

# ============================================================================
# 9. START AIRFLOW
# ============================================================================
echo ""
echo "=========================================="
echo "✓ Setup complete — starting Airflow"
echo "=========================================="
echo "Web UI  : http://localhost:8080"
echo "Login   : admin / admin123"
echo ""

cd "$PROJECT_ROOT"
exec "$VENV_DIR/bin/airflow" standalone
