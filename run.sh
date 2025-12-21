#!/bin/bash
set -e

cd "$(dirname "$0")"
source common.sh

# Initialize project
check_venv
activate_venv
setup_project_paths

# Verify PYTHONPATH is set
if [ -z "$PYTHONPATH" ]; then
    log_error "PYTHONPATH is not set!"
    exit 1
fi
log "PYTHONPATH: $PYTHONPATH"

# Service configuration
PID_FILE="logs/pids.txt"
LOG_DIR="logs"

# Start service
start_service() {
    local name=$1
    local cmd=$2
    local log_file="$LOG_DIR/${name}.log"
    
    if [ -f "$PID_FILE" ] && grep -q "^${name}:" "$PID_FILE" 2>/dev/null; then
        local old_pid=$(grep "^${name}:" "$PID_FILE" | cut -d: -f2)
        if is_running "$old_pid"; then
            log "$name is already running (PID: $old_pid)"
            return 0
        fi
    fi
    
    log "Starting $name..."
    # Ensure PYTHONPATH is set in the command for background processes
    eval "PYTHONPATH=\"$PYTHONPATH\" $cmd >> $log_file 2>&1 &"
    local pid=$!
    echo "${name}:${pid}" >> "$PID_FILE"
    log "$name started (PID: $pid)"
}

# Stop service
stop_service() {
    local name=$1
    if [ ! -f "$PID_FILE" ]; then
        return 0
    fi
    
    local pid=$(grep "^${name}:" "$PID_FILE" 2>/dev/null | cut -d: -f2)
    if [ -n "$pid" ] && is_running "$pid"; then
        log "Stopping $name (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        sleep 1
        kill -9 "$pid" 2>/dev/null || true
        remove_pid_from_file "$name" "$PID_FILE"
        log "$name stopped"
    fi
}

# Status check
check_status() {
    log "Checking service status..."
    echo ""
    
    local services=("celery" "flower" "dagster")
    local all_running=true
    
    for service in "${services[@]}"; do
        if [ -f "$PID_FILE" ]; then
            local pid=$(grep "^${service}:" "$PID_FILE" 2>/dev/null | cut -d: -f2)
            if [ -n "$pid" ] && is_running "$pid"; then
                echo "  ✓ $service: RUNNING (PID: $pid)"
            else
                echo "  ✗ $service: STOPPED"
                all_running=false
            fi
        else
            echo "  ✗ $service: STOPPED"
            all_running=false
        fi
    done
    
    echo ""
    if [ "$all_running" = true ]; then
        log "All services are running"
        echo "  Flower: http://localhost:5555"
        echo "  Dagster: http://localhost:3000"
    else
        log "Some services are not running"
    fi
}

# View logs
view_logs() {
    local service=$1
    local log_file="$LOG_DIR/${service}.log"
    
    if [ ! -f "$log_file" ]; then
        log_error "Log file not found: $log_file"
        return 1
    fi
    
    if [ "$2" = "tail" ] || [ "$2" = "follow" ]; then
        log "Following $service logs (Ctrl+C to stop)..."
        tail -f "$log_file"
    else
        cat "$log_file"
    fi
}

# Deploy Prefect flows
prefect_deploy() {
  # Run Prefect deployment for price_app
  cd "$PROJECT_ROOT" || exit 1
  python -m price_app.src.main.prefect_app.deployments.deploy_price_flows
}

# Stop all services by port (fallback when PID file is missing)
stop_by_ports() {
    log "Stopping all services by port..."
    
    # Kill processes by port
    log "Killing processes on port 3000 (Dagster)..."
    kill_port 3000
    
    log "Killing processes on port 5555 (Flower)..."
    kill_port 5555
    
    # Also try to kill by process name as fallback
    log "Killing processes by name..."
    pkill -f "celery.*worker" 2>/dev/null || true
    pkill -f "flower" 2>/dev/null || true
    pkill -f "dagster" 2>/dev/null || true
    
    # Clean up PID file if it exists
    [ -f "$PID_FILE" ] && rm -f "$PID_FILE" || true
    
    log "All services stopped by port"
}

# Main commands
case "$1" in
    start)
        log "Starting all services..."
        start_service "celery" "celery -A celery_app.celery_app:app worker --loglevel=info"
        sleep 2
        start_service "flower" "celery -A celery_app.celery_app:app flower --port=5555"
        sleep 2
        start_service "dagster" "dagster dev -m dagster_app.dagster_app"
        sleep 2
        echo ""
        check_status
        ;;
    
    stop)
        log "Stopping all services..."
        # Try to stop by PID first
        stop_service "celery"
        stop_service "flower"
        stop_service "dagster"
        # Fallback: kill by ports if PID file is missing or empty
        if [ ! -f "$PID_FILE" ] || [ ! -s "$PID_FILE" ]; then
            log "PID file missing or empty, using port-based kill..."
            stop_by_ports
        else
            # Clean up any remaining processes
            pkill -f "celery.*worker" 2>/dev/null || true
            pkill -f "flower" 2>/dev/null || true
            pkill -f "dagster" 2>/dev/null || true
            # Kill processes on ports as additional cleanup
            kill_port 3000
            kill_port 5555
        fi
        log "All services stopped"
        ;;
    
    kill-ports|stop-ports)
        stop_by_ports
        ;;
    
    restart)
        log "Restarting all services..."
        $0 stop
        sleep 2
        $0 start
        ;;
    
    status)
        check_status
        ;;
    
    logs)
        if [ -z "$2" ]; then
            log_error "Usage: ./run.sh logs {celery|flower|dagster} [tail|follow]"
            exit 1
        fi
        view_logs "$2" "$3"
        ;;
    
    celery)
        start_service "celery" "celery -A celery_app.celery_app:app worker --loglevel=info"
        start_service "flower" "celery -A celery_app.celery_app:app flower --port=5555"
        ;;
    
    dagster)
        cd src/main
        dagster dev -m dagster_app.dagster_app
        ;;
    
    prefect_deploy)
        prefect_deploy
        ;;
    
    *)
        echo "Usage: ./run.sh {start|stop|restart|status|logs|kill-ports|celery|dagster|prefect_deploy}"
        echo ""
        echo "Commands:"
        echo "  start         - Start all services"
        echo "  stop          - Stop all services (tries PID first, falls back to ports)"
        echo "  restart       - Restart all services"
        echo "  status        - Check service status"
        echo "  logs          - View logs: ./run.sh logs {celery|flower|dagster} [tail]"
        echo "  kill-ports    - Force stop all services by killing processes on ports 3000, 5555"
        echo "  celery        - Start celery and flower only"
        echo "  dagster       - Start dagster in foreground"
        echo "  prefect_deploy - Deploy Prefect flows"
        exit 1
        ;;
esac
