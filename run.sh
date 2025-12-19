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

check_port() {
    netstat -an 2>/dev/null | grep ":$1 " | grep -q "LISTEN"
}

kill_port() {
    local port=$1
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]] || uname -s | grep -qi "MINGW\|MSYS\|CYGWIN"; then
        for pid in $(netstat -ano | grep ":$port " | grep LISTENING | awk '{print $5}' | sort -u); do
            [ -n "$pid" ] && [ "$pid" != "0" ] && taskkill //PID $pid //F 2>/dev/null || true
        done
    else
        local pid=$(lsof -ti:$port 2>/dev/null)
        [ -n "$pid" ] && kill -9 $pid 2>/dev/null || true
    fi
}

start_celery() {
    echo "Starting Celery..."
    cd src/main
    celery -A price_app.main:app worker --loglevel=info >> ../../logs/celery.log 2>&1 &
    cd ../..
    echo "celery:$!" >> "$PID_FILE"
    echo "  Started (PID: $!)"
}

start_flower() {
    echo "Starting Flower..."
    cd src/main
    celery -A price_app.main:app flower --port=5555 >> ../../logs/flower.log 2>&1 &
    cd ../..
    echo "flower:$!" >> "$PID_FILE"
    echo "  Started on http://localhost:5555"
}

start_dagster() {
    echo "Starting Dagster..."
    cd src/main
    dagster dev -m price_app.main >> ../../logs/dagster.log 2>&1 &
    cd ../..
    echo "dagster:$!" >> "$PID_FILE"
    echo "  Started on http://localhost:3000"
}

stop_all() {
    echo "Stopping services..."
    [ -f "$PID_FILE" ] && while IFS=: read -r service pid; do
        [ -n "$pid" ] && kill "$pid" 2>/dev/null || true
    done < "$PID_FILE"
    rm -f "$PID_FILE"
    kill_port 5555
    kill_port 3000
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
        cd src/main
        dagster dev -m price_app.main
        ;;
    *)
        echo "Usage: ./run.sh {start|stop|celery|dagster}"
        exit 1
        ;;
esac
