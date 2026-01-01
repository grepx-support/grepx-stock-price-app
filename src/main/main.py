"""Main entry point - Initialize application and export functions.
All _main.py files should import from here.
"""

try:
    # Setup paths FIRST before importing apps
    import sys
    from pathlib import Path
    prefect_framework_path = Path(__file__).parent / "libs" / "prefect_framework" / "src"
    if prefect_framework_path.exists():
        sys.path.insert(0, str(prefect_framework_path))

    # Import apps to register connection types
    import database_app
    import celery_app
    import dagster_app
    import prefect_app  # Will gracefully handle missing prefect_framework

    from servers.config import ConfigLoader
    from grepx_connection_registry import ConnectionManager
    from servers.app.application import Application
    from servers.utils.logger import get_logger
    
    # Initialize application singleton (this will also initialize logging)
    app = Application()
    logger = app.logger
    
    logger.info("Main module initialized")
    logger.debug("Application singleton created successfully")
    logger.debug("Connection types registered: database, celery, dagster, prefect (if available)")
    
    # Convenient exports
    get_connection = app.get_connection
    get_database = app.get_database
    get_collection = app.get_collection
    get_app = lambda: app  # Return the application singleton
    config = app.config
    connections = app.connections

# Global lazy singleton
_app_instance = None

def _initialize_application():
    """Lazily initialize and return the Application singleton."""
    global _app_instance
    if _app_instance is not None:
        return _app_instance

    print("[MAIN] Starting lazy initialization of Application", file=sys.stderr)

    try:
        # Import heavy modules only when needed
        import database_app
        import celery_app
        import dagster_app
        import prefect_app

        from servers.app.application import Application
        from servers.utils.logger import get_logger

        print("[MAIN] Creating Application instance...", file=sys.stderr)
        _app_instance = Application()
        print("[MAIN] Application instance created successfully", file=sys.stderr)

        logger = _app_instance.logger
        logger.info("Main module lazily initialized")
        logger.debug("Application singleton created successfully")
        logger.debug("Connection types registered: database, celery, dagster, prefect")

        return _app_instance

    except Exception as e:
        print(f"[MAIN] FATAL ERROR during lazy initialization: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise


# Lazy exports
def get_connection(conn_id: str):
    app = _initialize_application()
    return app.get_connection(conn_id)


def get_database(db_name: str):
    app = _initialize_application()
    return app.get_database(db_name)


def get_collection(db_name: str, collection_name: str):
    app = _initialize_application()
    return app.get_collection(db_name, collection_name)


def get_config():
    app = _initialize_application()
    return app.config


def get_connections():
    app = _initialize_application()
    return app.connections


# Keep __main__ block for direct execution (unchanged)
if __name__ == "__main__":
    """
    Start all services (Celery, Flower, Dagster) for testing.
    """
    import subprocess
    import sys
    import time
    import os
    from pathlib import Path

    processes = []

    # Force initialization early for __main__
    app = _initialize_application()
    logger = app.logger

    def cleanup():
        """Stop all processes on exit."""
        logger.info("Shutting down services...")
        for p in processes:
            try:
                if p.poll() is None:  # Process still running
                    logger.debug("Terminating process PID: %s", p.pid)
                    p.terminate()
            except Exception as e:
                logger.warning("Error terminating process %s: %s", p.pid, e)
        time.sleep(1)
        for p in processes:
            try:
                if p.poll() is None:
                    logger.debug("Killing process PID: %s", p.pid)
                    p.kill()
            except Exception as e:
                logger.warning("Error killing process %s: %s", p.pid, e)
    
    # Set working directory to main.py's directory
    main_dir = Path(__file__).parent
    os.chdir(main_dir)

    logger.info("=" * 60)
    logger.info("Starting all services...")
    logger.warning("NOTE: Services run in subprocesses. For debugging, use separate PyCharm run configurations.")
    logger.info("Press Ctrl+C to stop all services")
    logger.info("=" * 60)

    try:
        # Detect Windows platform for pool configuration
        import platform
        is_windows = platform.system() == "Windows"
        
        # Use 'solo' pool on Windows to avoid PermissionError with billiard
        # On Linux/Unix, can use 'prefork' for better performance
        pool_type = "solo" if is_windows else "prefork"
        
        # Generate unique node name to avoid duplicate node warnings
        import socket
        import random
        hostname = socket.gethostname()
        node_suffix = random.randint(1000, 9999)
        node_name = f"celery@{hostname}.{node_suffix}"
        
        # Start Celery worker with Windows-compatible configuration
        logger.info("Starting Celery worker (pool=%s, node=%s)...", pool_type, node_name)
        celery_cmd = [
            sys.executable, "-m", "celery", "-A", "celery_main:app", "worker",
            "--loglevel=info",
            f"--pool={pool_type}",
            "-n", node_name
        ]
        logger.debug("Celery command: %s", " ".join(celery_cmd))
        
        # Start Celery worker (let output go to console for debugging)
        celery_worker = subprocess.Popen(
            celery_cmd,
            cwd=str(main_dir),
            encoding='utf-8'
        )
        processes.append(celery_worker)
        logger.info("Celery worker started (PID: %s)", celery_worker.pid)
        
        # Check if worker started successfully (give it a moment)
        time.sleep(2)
        if celery_worker.poll() is not None:
            logger.error("Celery worker exited immediately with code %s", celery_worker.returncode)
            raise RuntimeError(f"Celery worker failed to start (exit code: {celery_worker.returncode})")
        else:
            logger.debug("Celery worker is running successfully")
        
        # Start Flower
        logger.info("Starting Flower on port 5555...")
        flower = subprocess.Popen(
            [sys.executable, "-m", "celery", "-A", "celery_main:app", "flower", "--port=5555"],
            cwd=str(main_dir),
            encoding='utf-8'
        )
        processes.append(flower)
        logger.info("Flower started (PID: %s)", flower.pid)
        time.sleep(2)
        
        # Start Dagster (runs in foreground - this will block)
        logger.info("Starting Dagster dev server on port 3000...")
        dagster = subprocess.Popen(
            [sys.executable, "-m", "dagster", "dev", "-m", "dagster_main"],
            cwd=str(main_dir),
            encoding='utf-8'
        )
        processes.append(dagster)
        logger.info("Dagster started (PID: %s)", dagster.pid)
        
        logger.info("=" * 60)
        logger.info("All services started successfully!")
        logger.info("  Celery worker: Running (PID: %s)", celery_worker.pid)
        logger.info("  Flower: http://localhost:5555 (PID: %s)", flower.pid)
        logger.info("  Dagster: http://localhost:3000 (PID: %s)", dagster.pid)
        logger.info("=" * 60)
        
        # Wait for Dagster (it runs in foreground)
        dagster.wait()
        
    except KeyboardInterrupt:
        logger.warning("Received interrupt signal (Ctrl+C)...")
    except Exception as e:
        logger.error(f"Error starting services: {e}", exc_info=True)
        raise
    finally:
        cleanup()
        logger.info("All services stopped")