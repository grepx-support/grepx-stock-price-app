"""Composition Root - Thin entry point that delegates to main package."""

import subprocess
import sys
import time
import socket
from pathlib import Path

# Import from main package to trigger setup and expose exports
from main import (
    app,
    defs,
    orm_app,
    get_fetch_prices_use_case,
    get_compute_indicators_use_case,
    get_store_data_use_case,
)

__all__ = [
    "app",
    "defs",
    "orm_app",
    "get_fetch_prices_use_case",
    "get_compute_indicators_use_case",
    "get_store_data_use_case",
]


def check_port(port):
    """Check if a port is in use."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0


def start_mongodb():
    """Start MongoDB if not running."""
    if check_port(27017):
        print("✓ MongoDB is already running on port 27017")
        return None
    
    print("Starting MongoDB...")
    try:
        # Try to start MongoDB (adjust path as needed)
        process = subprocess.Popen(
            ["mongod", "--dbpath", str(Path(__file__).parent / "data" / "db")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)  # Wait for MongoDB to start
        if check_port(27017):
            print("✓ MongoDB started successfully")
            return process
        else:
            print("✗ Failed to start MongoDB")
            return None
    except FileNotFoundError:
        print("✗ MongoDB not found. Please install MongoDB or start it manually.")
        return None
    except Exception as e:
        print(f"✗ Error starting MongoDB: {e}")
        return None


def start_redis():
    """Start Redis if not running."""
    if check_port(6379):
        print("✓ Redis is already running on port 6379")
        return None
    
    print("Starting Redis...")
    try:
        process = subprocess.Popen(
            ["redis-server"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(1)  # Wait for Redis to start
        if check_port(6379):
            print("✓ Redis started successfully")
            return process
        else:
            print("✗ Failed to start Redis")
            return None
    except FileNotFoundError:
        print("✗ Redis not found. Please install Redis or start it manually.")
        return None
    except Exception as e:
        print(f"✗ Error starting Redis: {e}")
        return None


def start_celery():
    """Start Celery worker."""
    if check_port(5555):
        print("✓ Celery/Flower may already be running on port 5555")
    
    print("Starting Celery worker...")
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "celery", "-A", "app.main", "worker", "--loglevel=info"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✓ Celery worker started")
        return process
    except Exception as e:
        print(f"✗ Error starting Celery: {e}")
        return None


if __name__ == "__main__":
    print("Starting application services...")
    
    # Start datastore (MongoDB)
    mongodb_process = start_mongodb()
    
    # Start Redis (required for Celery)
    redis_process = start_redis()
    
    # Start Celery
    celery_process = start_celery()
    
    print("\nApplication services started!")
    print("Dagster UI: http://localhost:3000")
    print("Flower UI: http://localhost:5555")
    print("\nPress Ctrl+C to stop all services...")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        if celery_process:
            celery_process.terminate()
        if redis_process:
            redis_process.terminate()
        if mongodb_process:
            mongodb_process.terminate()
        print("All services stopped.")
