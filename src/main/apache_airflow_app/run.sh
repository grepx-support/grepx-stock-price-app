#!/bin/bash
set -e

# ============================================================================
# Apache Airflow Run Script
# ============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/apache_airflow_app/venv_airflow"
AIRFLOW_HOME="$SCRIPT_DIR"

# Activate venv
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

export AIRFLOW_HOME="$AIRFLOW_HOME"

echo "=========================================="
echo "Starting Apache Airflow"
echo "=========================================="

# ============================================================================
# 1. AIRFLOW CONFIG
# ============================================================================
mkdir -p "$AIRFLOW_HOME/dags" "$AIRFLOW_HOME/logs"

AIRFLOW_CFG="$AIRFLOW_HOME/airflow.cfg"

if [ ! -f "$AIRFLOW_CFG" ]; then
cat > "$AIRFLOW_CFG" << 'EOF'
[core]
dags_folder = /home/ubuntu/grepx-orchestrator/price_app/src/main/apache_airflow_app/dags
base_log_folder = /home/ubuntu/grepx-orchestrator/price_app/src/main/apache_airflow_app/logs
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

# ============================================================================
# 2. INITIALIZE DB
# ============================================================================
echo ""
echo "▶ Initializing Airflow DB..."

if [ ! -f "$AIRFLOW_HOME/airflow.db" ]; then
    airflow db migrate
    echo "✓ Database initialized"
else
    echo "✓ Database already exists"
fi

# ============================================================================
# 3. CREATE ADMIN USER
# ============================================================================
echo ""
echo "▶ Creating admin user (if missing)..."

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
# 4. START AIRFLOW
# ============================================================================
echo ""
echo "=========================================="
echo "✓ Airflow ready"
echo "Web UI  : http://localhost:8080"
echo "Login   : admin / admin123"
echo ""
cd "$PROJECT_ROOT"
exec "$VENV_DIR/bin/airflow" standalone
