#!/bin/bash
set -e

cd "$(dirname "$0")"
source common.sh

[ ! -d "venv" ] && echo "Error: Run setup.sh first" && exit 1

activate_venv

export DAGSTER_HOME="$(pwd)/dagster_home"
mkdir -p "$DAGSTER_HOME"

PID_FILE="logs/pids.txt"
mkdir -p logs

# Check if port is in use (works on Windows Git Bash and Linux)
check_port() {
    local port=$1
    netstat -an 2>/dev/null | grep ":$port " | grep -q "LISTEN" && return 0 || return 1
}

# Kill process on port (works on Windows Git Bash and Linux)
kill_port() {
    local port=$1
    echo "Checking port $port..."

    # Check OS
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]] || uname -s | grep -qi "MINGW\|MSYS\|CYGWIN"; then
        # Windows Git Bash
        for pid in $(netstat -ano | grep ":$port " | grep LISTENING | awk '{print $5}' | sort -u); do
            if [ -n "$pid" ] && [ "$pid" != "0" ]; then
                echo "  Killing PID $pid on port $port"
                taskkill //PID $pid //F 2>/dev/null || true
            fi
        done
    else
        # Linux/Mac
        local pid=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$pid" ]; then
            echo "  Killing PID $pid on port $port"
            kill -9 $pid 2>/dev/null || true
        fi
    fi
}

start_celery() {
    if check_port 5555; then
        echo "✗ Port 5555 already in use. Stop services first: ./run.sh stop"
        return 1
    fi

    echo "Starting Celery worker..."
    celery -A app.main worker --loglevel=info >> logs/celery.log 2>&1 &
    CELERY_PID=$!
    echo "Celery started with PID: $CELERY_PID"
    echo "celery:$CELERY_PID" >> "$PID_FILE"
}

start_flower() {
    if check_port 5555; then
        echo "✗ Port 5555 already in use. Stop services first: ./run.sh stop"
        return 1
    fi

    echo "Starting Flower..."
    celery -A app.main flower --port=5555 >> logs/flower.log 2>&1 &
    FLOWER_PID=$!
    echo "Flower started with PID: $FLOWER_PID on http://localhost:5555"
    echo "flower:$FLOWER_PID" >> "$PID_FILE"
}

start_dagster() {
    if check_port 3000; then
        echo "✗ Port 3000 already in use. Stop services first: ./run.sh stop"
        return 1
    fi

    echo "Starting Dagster..."
    dagster dev -m app.main >> logs/dagster.log 2>&1 &
    DAGSTER_PID=$!
    echo "Dagster started with PID: $DAGSTER_PID"
    echo "dagster:$DAGSTER_PID" >> "$PID_FILE"
}

stop_all() {
    echo "Stopping all services..."

    # Stop by PID file
    if [ -f "$PID_FILE" ]; then
        while IFS=: read -r service pid; do
            if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
                echo "Stopping $service (PID: $pid)..."
                kill "$pid" 2>/dev/null || true
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi

    # Also kill by port (cleanup any orphaned processes)
    kill_port 5555  # Flower/Celery
    kill_port 3000  # Dagster

    # Kill celery workers by name
    pkill -f "celery.*worker" 2>/dev/null || true

    echo "All services stopped."
}

case "$1" in
    celery)
        echo "Starting Celery + Flower..."
        start_celery
        start_flower
        ;;
    dagster)
        echo "Starting Dagster..."
        dagster dev -m app.main
        ;;
    start)
        echo "Starting all services..."
        rm -f "$PID_FILE"
        start_celery
        sleep 1
        start_flower
        sleep 1
        start_dagster
        echo ""
        echo "All services started!"
        echo "Flower UI: http://localhost:5555"
        echo "Dagster UI: http://localhost:3000"
        echo "Logs: tail -f logs/*.log"
        echo "Stop with: ./run.sh stop"
        ;;
    stop)
        stop_all
        ;;
    status)
        $VENV_PYTHON -m app.main
        ;;
    *)
        echo "Usage: ./run.sh {celery|dagster|start|stop|status}"
        echo "  celery  - Start Celery worker + Flower"
        echo "  dagster - Start Dagster only"
        echo "  start   - Start all services (Celery, Flower, Dagster)"
        echo "  stop    - Stop all services"
        echo "  status  - Show app status"
        exit 1
        ;;
esac