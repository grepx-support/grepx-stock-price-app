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

start_celery() {
    echo "Starting Celery worker..."
    celery -A app.main worker --loglevel=info >> logs/celery.log 2>&1 &
    CELERY_PID=$!
    echo "Celery started with PID: $CELERY_PID"
    echo "celery:$CELERY_PID" >> "$PID_FILE"
}

start_flower() {
    echo "Starting Flower..."
    celery -A app.main flower --port=5555 >> logs/flower.log 2>&1 &
    FLOWER_PID=$!
    echo "Flower started with PID: $FLOWER_PID on http://localhost:5555"
    echo "flower:$FLOWER_PID" >> "$PID_FILE"
}

start_dagster() {
    echo "Starting Dagster..."
    dagster dev -m app.main >> logs/dagster.log 2>&1 &
    DAGSTER_PID=$!
    echo "Dagster started with PID: $DAGSTER_PID"
    echo "dagster:$DAGSTER_PID" >> "$PID_FILE"
}

stop_all() {
    echo "Stopping all services..."

    if [ ! -f "$PID_FILE" ]; then
        echo "No PID file found. Services may not be running."
        return
    fi

    while IFS=: read -r service pid; do
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo "Stopping $service (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
        else
            echo "$service (PID: $pid) is not running"
        fi
    done < "$PID_FILE"

    rm -f "$PID_FILE"
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