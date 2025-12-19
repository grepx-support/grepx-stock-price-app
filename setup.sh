#!/bin/bash
set -e

cd "$(dirname "$0")"
source common.sh

if [ ! -d "venv" ]; then
    PYTHON=$(find_python)
    $PYTHON -m venv venv
fi

$VENV_PYTHON -m pip install --upgrade pip

# Install libs from ../libs
LIBS_DIR="../libs"
if [ -d "$LIBS_DIR" ]; then
    echo "Installing libraries from $LIBS_DIR..."
    for lib in "$LIBS_DIR"/*; do
        if [ -d "$lib" ]; then
            echo "  Installing $(basename $lib)..."
            $VENV_PIP install -e "$lib"
        fi
    done
fi

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    $VENV_PIP install -r requirements.txt
fi

# Add src/main to PYTHONPATH
export PYTHONPATH="$(pwd)/src/main:$PYTHONPATH"

echo "Setup complete!"
echo "Run: ./run.sh start"
