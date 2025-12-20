#!/bin/bash
# Common utilities and configuration for all scripts

# ============================================================================
# OS Detection
# ============================================================================
is_windows() {
    [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]] || uname -s | grep -qi "MINGW\|MSYS\|CYGWIN"
}

# ============================================================================
# Python Configuration
# ============================================================================
PYTHON_CMD="python3.12"
PYTHON_FALLBACK="python3"

find_python() {
    if command -v $PYTHON_CMD &> /dev/null; then
        echo $PYTHON_CMD
    elif command -v $PYTHON_FALLBACK &> /dev/null; then
        echo $PYTHON_FALLBACK
    else
        echo "python"
    fi
}

# ============================================================================
# Virtual Environment Paths
# ============================================================================
if is_windows; then
    VENV_PYTHON="venv/Scripts/python.exe"
    VENV_PIP="venv/Scripts/pip.exe"
    VENV_ACTIVATE="venv/Scripts/activate"
else
    VENV_PYTHON="venv/bin/python"
    VENV_PIP="venv/bin/pip"
    VENV_ACTIVATE="venv/bin/activate"
fi

# Activate virtual environment
activate_venv() {
    if [ -f "$VENV_ACTIVATE" ]; then
        source "$VENV_ACTIVATE"
    fi
}

# Check if venv exists
check_venv() {
    if [ ! -d "venv" ]; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] Error: Virtual environment not found. Run setup.sh first" >&2
        exit 1
    fi
}

# ============================================================================
# Project Paths
# ============================================================================
setup_project_paths() {
    # Get project root - use current directory (should be set by calling script)
    if [ -z "$PROJECT_ROOT" ]; then
        PROJECT_ROOT="$(pwd)"
    fi
    cd "$PROJECT_ROOT"

    # Convert to absolute path
    PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd)"

    # Set Python path (absolute path)
    local python_path="$PROJECT_ROOT/src/main"
    if [ -d "$python_path" ]; then
        export PYTHONPATH="$python_path${PYTHONPATH:+:$PYTHONPATH}"
    else
        log_error "Python path not found: $python_path"
        exit 1
    fi

    # Add ORM library to PYTHONPATH
    local orm_lib_path="$PROJECT_ROOT/../libs/grepx-orm-libs/src"
    if [ -d "$orm_lib_path" ]; then
        export PYTHONPATH="$orm_lib_path:$PYTHONPATH"
    else
        log_error "ORM library path not found: $orm_lib_path"
        exit 1
    fi

    # Set Dagster home
    export DAGSTER_HOME="$PROJECT_ROOT/dagster_home"
    mkdir -p "$DAGSTER_HOME" logs

    # Export for use in other scripts
    export PROJECT_ROOT
}

# ============================================================================
# Logging
# ============================================================================
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*" >&2
}

# ============================================================================
# Process Management
# ============================================================================
# Check if process is running (cross-platform)
is_running() {
    local pid=$1
    if [ -z "$pid" ]; then
        return 1
    fi
    # Try kill -0 first (works on Unix)
    kill -0 "$pid" 2>/dev/null && return 0
    # On Windows, check if process exists
    if is_windows; then
        tasklist //FI "PID eq $pid" 2>/dev/null | grep -q "$pid" && return 0
    fi
    return 1
}

# Remove PID from file (cross-platform)
remove_pid_from_file() {
    local name=$1
    local pid_file=$2
    
    if is_windows; then
        # Windows/Git Bash - use temp file
        grep -v "^${name}:" "$pid_file" > "${pid_file}.tmp" 2>/dev/null && mv "${pid_file}.tmp" "$pid_file" 2>/dev/null || true
    else
        # Linux/Mac
        sed -i '' "/^${name}:/d" "$pid_file" 2>/dev/null || sed -i "/^${name}:/d" "$pid_file" 2>/dev/null || true
    fi
}

# Kill process on port (Windows)
kill_port_windows() {
    local port=$1
    for pid in $(netstat -ano 2>/dev/null | grep ":$port " | grep LISTENING | awk '{print $5}' | sort -u); do
        [ -n "$pid" ] && [ "$pid" != "0" ] && taskkill //PID $pid //F 2>/dev/null || true
    done
}

# Kill process on port (Unix)
kill_port_unix() {
    local port=$1
    local pid=$(lsof -ti:$port 2>/dev/null)
    [ -n "$pid" ] && kill -9 "$pid" 2>/dev/null || true
}

# Kill process on port (cross-platform)
kill_port() {
    local port=$1
    if is_windows; then
        kill_port_windows "$port"
    else
        kill_port_unix "$port"
    fi
}

# ============================================================================
# Export variables
# ============================================================================
export PYTHON_CMD
export VENV_PYTHON
export VENV_PIP
export VENV_ACTIVATE
