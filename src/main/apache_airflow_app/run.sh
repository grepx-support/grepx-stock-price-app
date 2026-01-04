#!/bin/bash
set -e

# ============================================================================
# Apache Airflow Run Script
# ============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/apache_airflow_app/venv_airflow"
AIRFLOW_HOME="$SCRIPT_DIR"

# Logging & PID management
PID_FILE="$AIRFLOW_HOME/airflow.pid"
LOG_DIR="$AIRFLOW_HOME/logs"
LOG_FILE="$LOG_DIR/airflow.log"

# Helper functions
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*" >&2
}

is_running() {
    local pid=$1
    [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

kill_port() {
    local port=$1
    local pids=$(lsof -ti :$port 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill -9 2>/dev/null || true
        log "Killed processes on port $port"
    fi
}

# ============================================================================
# AIRFLOW INITIALIZATION
# ============================================================================
initialize_airflow() {
    log "Initializing Apache Airflow..."
    
    # Activate venv
    if [ ! -d "$VENV_DIR" ]; then
        log_error "Virtual environment not found at: $VENV_DIR"
        exit 1
    fi
    
    # shellcheck disable=SC1090
    source "$VENV_DIR/bin/activate"
    export AIRFLOW_HOME="$AIRFLOW_HOME"
    
    # Create directories
    mkdir -p "$AIRFLOW_HOME/dags" "$LOG_DIR"
    
    # ============================================================================
    # 1. AIRFLOW CONFIG
    # ============================================================================
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
        log "✓ airflow.cfg created"
    else
        log "✓ airflow.cfg already exists"
    fi
    
    # ============================================================================
    # 2. INITIALIZE DB
    # ============================================================================
    log "▶ Initializing Airflow DB..."
    
    if [ ! -f "$AIRFLOW_HOME/airflow.db" ]; then
        airflow db migrate >> "$LOG_FILE" 2>&1
        log "✓ Database initialized"
    else
        log "✓ Database already exists"
    fi
    
    # ============================================================================
    # 3. CREATE ADMIN USER
    # ============================================================================
    log "▶ Creating admin user (if missing)..."
    
    if ! airflow users list 2>/dev/null | grep -q "^admin"; then
        airflow users create \
            --username admin \
            --firstname Airflow \
            --lastname Admin \
            --role Admin \
            --email admin@example.com \
            --password admin123 >> "$LOG_FILE" 2>&1
        log "✓ Admin user created"
    else
        log "✓ Admin user already exists"
    fi
}

# ============================================================================
# START AIRFLOW
# ============================================================================
start_airflow() {
    # Check if already running
    if [ -f "$PID_FILE" ]; then
        local old_pid=$(cat "$PID_FILE" 2>/dev/null)
        if is_running "$old_pid"; then
            log "Airflow is already running (PID: $old_pid)"
            return 0
        fi
        rm -f "$PID_FILE"
    fi
    
    # Initialize if needed
    initialize_airflow
    
    log "Starting Apache Airflow standalone..."
    
    # Activate venv
    # shellcheck disable=SC1090
    source "$VENV_DIR/bin/activate"
    export AIRFLOW_HOME="$AIRFLOW_HOME"
    
    # Start in background
    cd "$PROJECT_ROOT"
    nohup "$VENV_DIR/bin/airflow" standalone >> "$LOG_FILE" 2>&1 &
    local pid=$!
    
    sleep 3
    
    if ! is_running "$pid"; then
        log_error "Airflow failed to start. Check $LOG_FILE"
        return 1
    fi
    
    echo "$pid" > "$PID_FILE"
    
    log "✓ Airflow started (PID: $pid)"
    log "Web UI  : http://localhost:8080"
    log "Login   : admin / admin123"
}

# ============================================================================
# STOP AIRFLOW
# ============================================================================
stop_airflow() {
    log "Stopping Apache Airflow..."
    
    # Stop by PID file
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$pid" ] && is_running "$pid"; then
            log "Stopping Airflow (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
            sleep 2
            
            # Force kill if still running
            if is_running "$pid"; then
                kill -9 "$pid" 2>/dev/null || true
            fi
            
            rm -f "$PID_FILE"
            log "✓ Airflow stopped"
        else
            log "Airflow is not running (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        log "No PID file found"
    fi
    
    # Fallback: kill by port
    kill_port 8080
    
    # Kill any remaining airflow processes
    pkill -f "airflow.*standalone" 2>/dev/null || true
    pkill -f "airflow.*webserver" 2>/dev/null || true
    pkill -f "airflow.*scheduler" 2>/dev/null || true
    
    log "All Airflow processes stopped"
}

# ============================================================================
# CHECK STATUS
# ============================================================================
check_status() {
    log "Checking Airflow status..."
    echo ""
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$pid" ] && is_running "$pid"; then
            echo "  ✓ Airflow: RUNNING (PID: $pid)"
            echo ""
            echo "  Web UI: http://localhost:8080"
            echo "  Login : admin / admin123"
            return 0
        fi
    fi
    
    # Check by port if PID file doesn't exist
    if lsof -i :8080 >/dev/null 2>&1; then
        echo "  ⚠ Airflow: RUNNING (no PID file, check manually)"
        echo ""
        echo "  Web UI: http://localhost:8080"
        return 0
    fi
    
    echo "  ✗ Airflow: STOPPED"
    echo ""
    return 1
}

# ============================================================================
# VIEW LOGS
# ============================================================================
view_logs() {
    if [ ! -f "$LOG_FILE" ]; then
        log_error "Log file not found: $LOG_FILE"
        return 1
    fi
    
    if [ "$1" = "tail" ] || [ "$1" = "follow" ]; then
        log "Following Airflow logs (Ctrl+C to stop)..."
        tail -f "$LOG_FILE"
    else
        cat "$LOG_FILE"
    fi
}

# ============================================================================
# MAIN COMMAND HANDLER
# ============================================================================
case "$1" in
    start)
        start_airflow
        echo ""
        check_status
        ;;
    
    stop)
        stop_airflow
        ;;
    
    restart)
        log "Restarting Apache Airflow..."
        stop_airflow
        sleep 2
        start_airflow
        echo ""
        check_status
        ;;
    
    status)
        check_status
        ;;
    
    logs)
        view_logs "$2"
        ;;
    
    init)
        initialize_airflow
        ;;
    
    *)
        echo "Usage: ./run.sh {start|stop|restart|status|logs|init}"
        echo ""
        echo "Commands:"
        echo "  start    - Start Apache Airflow"
        echo "  stop     - Stop Apache Airflow"
        echo "  restart  - Restart Apache Airflow"
        echo "  status   - Check Airflow status"
        echo "  logs     - View logs: ./run.sh logs [tail|follow]"
        echo "  init     - Initialize Airflow (DB, config, user)"
        echo ""
        echo "After starting, access:"
        echo "  Web UI: http://localhost:8080"
        echo "  Login : admin / admin123"
        exit 1
        ;;
esac
