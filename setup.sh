# price_app/setup.sh

#!/bin/bash
set -e

cd "$(dirname "$0")"
source common.sh

if [ ! -d "venv" ]; then
    PYTHON=$(find_python)
    $PYTHON -m venv venv
fi

$VENV_PYTHON -m pip install --upgrade pip

# Install all libs from ../libs
LIBS_DIR="../libs"
if [ -d "$LIBS_DIR" ]; then
    echo "Installing all libraries from $LIBS_DIR..."
    for lib in "$LIBS_DIR"/*; do
        if [ -d "$lib" ]; then
            echo "Installing $(basename $lib)..."
            $VENV_PIP install -e "$lib"
        fi
    done
fi

# Install app requirements
if [ -f "requirements.txt" ]; then
    echo "Installing app requirements..."
    $VENV_PIP install -r requirements.txt
fi

echo "price_app setup complete!"