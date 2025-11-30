#!/bin/bash
set -e

cd "$(dirname "$0")"

LIBS_DIR="../../libs"

echo "Setting up price_app..."

if [ -d "venv" ]; then
    echo "Removing existing venv..."
    rm -rf venv
fi

echo "Creating virtual environment..."
python -m venv venv || python -m venv venv

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]] || uname -s | grep -qi "MINGW\|MSYS\|CYGWIN"; then
    PIP="venv/Scripts/pip"
else
    PIP="venv/bin/pip"
fi

echo "Installing requirements..."
$PIP install -r requirements.txt

echo "Installing dependencies from libs..."
for lib_dir in $LIBS_DIR/*; do
    if [ -d "$lib_dir" ]; then
        echo "Installing $(basename $lib_dir)..."
        $PIP install -e "$lib_dir"
    fi
done

echo ""
echo "Setup complete!"
echo "Run: ./run.sh"