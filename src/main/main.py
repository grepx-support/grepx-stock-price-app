"""Main entry point - Initialize application and export functions.

All _main.py files should import from here.

For PyCharm debugging, use separate run configurations:
1. Celery: Run celery_main.py or use: celery -A celery_main:app worker
2. Flower: Use: celery -A celery_main:app flower --port=5555
3. Dagster: Run dagster_main.py or use: dagster dev -m dagster_main
"""

try:
    # Import apps FIRST to register connection types
    import database_app
    import celery_app
    import dagster_app

    from servers.config import ConfigLoader
    from grepx_connection_registry import ConnectionManager
    from servers.app.application import Application
    from servers.utils.logger import get_logger
    
    # Initialize application singleton (this will also initialize logging)
    app = Application()
    logger = app.logger
    
    logger.info("Main module initialized")
    logger.debug("Application singleton created successfully")
    logger.debug("Connection types registered: database, celery, dagster")
    
    # Convenient exports
    get_connection = app.get_connection
    get_database = app.get_database
    get_collection = app.get_collection
    get_app = lambda: app  # Return the application singleton
    config = app.config
    connections = app.connections
    
except Exception as e:
    print(f"ERROR: Failed to initialize application: {e}")
    import traceback
    traceback.print_exc()
    raise


if __name__ == "__main__":
    """
    Start all services (Celery, Flower, Dagster) for testing.
    
    NOTE: For debugging with breakpoints, use separate PyCharm run configurations:
    1. Celery: Script path=celery_main.py, Parameters: (leave empty, celery CLI handles it)
       Or use: Module=celery, Parameters: -A celery_main:app worker --loglevel=info
    2. Flower: Module=celery, Parameters: -A celery_main:app flower --port=5555
    3. Dagster: Module=dagster, Parameters: dev -m dagster_main
    """
    import subprocess
    import sys
    import time
    import os
    from pathlib import Path
    
    processes = []
    
    # Use logger from app (already initialized)
    logger = get_logger(__name__)
    
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
        hostname = socket.gethostname()
        import random
        node_suffix = random.randint(1000, 9999)
        node_name = f"celery@{hostname}.{node_suffix}"
        
        # Start Celery worker with Windows-compatible configuration
        logger.info("Starting Celery worker (pool=%s, node=%s)...", pool_type, node_name)
        celery_cmd = [
            sys.executable, "-m", "celery", "-A", "celery_main:app", "worker",
            "--loglevel=info",
            f"--pool={pool_type}",
            f"-n", node_name
        ]
        logger.debug("Celery command: %s", " ".join(celery_cmd))
        
        # Start Celery worker (let output go to console for debugging)
        celery_worker = subprocess.Popen(
            celery_cmd,
            cwd=str(main_dir),
            encoding='utf-8'
        )
        processes.append(celery_worker)
        logger.info("Celery worker started (PID: %s, pool=%s, node=%s)", 
                   celery_worker.pid, pool_type, node_name)
        
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
