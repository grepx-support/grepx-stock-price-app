#!/bin/bash
set -e

cd "$(dirname "$0")"
source common.sh

if [ ! -d "venv" ]; then
    PYTHON=$(find_python)
    log "Creating virtual environment..."
    $PYTHON -m venv venv
fi

log "Upgrading pip..."
$VENV_PYTHON -m pip install --upgrade pip

# Install libs from ../libs
LIBS_DIR="../libs"
if [ -d "$LIBS_DIR" ]; then
    log "Installing libraries from $LIBS_DIR..."
    for lib in "$LIBS_DIR"/*; do
        if [ -d "$lib" ]; then
            log "  Installing $(basename $lib)..."
            $VENV_PIP install -e "$lib"
        fi
    done
fi

# Install requirements
if [ -f "requirements.txt" ]; then
    log "Installing requirements..."
    $VENV_PIP install -r requirements.txt
fi

log "Setup complete!"
log "Run: ./run.sh start"
