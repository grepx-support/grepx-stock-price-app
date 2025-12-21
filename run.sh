#!/bin/bash
set -e

cd "$(dirname "$0")"
source common.sh

[ ! -d "venv" ] && echo "Run setup.sh first" && exit 1

activate_venv

export DAGSTER_HOME="$(pwd)/dagster_home"
export PYTHONPATH="$(pwd)/src/main:$PYTHONPATH"
mkdir -p "$DAGSTER_HOME" logs

PID_FILE="logs/pids.txt"

start_celery() {
    echo "Starting Celery..."
    PYTHONPATH="$(pwd)/src/main:$PYTHONPATH" celery -A main:app worker --loglevel=info >> logs/celery.log 2>&1 &
    echo "celery:$!" >> "$PID_FILE"
    echo "  Started (PID: $!)"
}

start_flower() {
    echo "Starting Flower..."
    PYTHONPATH="$(pwd)/src/main:$PYTHONPATH" celery -A main:app flower --port=5555 >> logs/flower.log 2>&1 &
    echo "flower:$!" >> "$PID_FILE"
    echo "  Started on http://localhost:5555"
}

start_dagster() {
    echo "Starting Dagster..."
    PYTHONPATH="$(pwd)/src/main:$PYTHONPATH" dagster dev -m main >> logs/dagster.log 2>&1 &
    echo "dagster:$!" >> "$PID_FILE"
    echo "  Started on http://localhost:3000"
}

stop_all() {
    echo "Stopping services..."
    [ -f "$PID_FILE" ] && while IFS=: read -r service pid; do
        [ -n "$pid" ] && kill "$pid" 2>/dev/null || true
    done < "$PID_FILE"
    rm -f "$PID_FILE"
    pkill -f "celery.*worker" 2>/dev/null || true
    echo "Stopped"
}

case "$1" in
    start)
        rm -f "$PID_FILE"
        start_celery
        sleep 1
        start_flower
        sleep 1
        start_dagster
        echo ""
        echo "Started!"
        echo "  Flower: http://localhost:5555"
        echo "  Dagster: http://localhost:3000"
        ;;
    stop)
        stop_all
        ;;
    celery)
        start_celery
        start_flower
        ;;
    dagster)
        PYTHONPATH="$(pwd)/src/main:$PYTHONPATH" dagster dev -m main
        ;;
    *)
        echo "Usage: ./run.sh {start|stop|celery|dagster}"
        exit 1
        ;;
esac
