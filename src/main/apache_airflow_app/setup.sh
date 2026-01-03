#!/bin/bash
set -e

# ============================================================================
# Apache Airflow Setup Script
# ============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/apache_airflow_app/venv_airflow"
PYTHON_CMD="python3.11"
AIRFLOW_VERSION="2.10.3"

echo "=========================================="
echo "Apache Airflow Setup"
echo "=========================================="
echo "Project Root : $PROJECT_ROOT"
echo "Airflow Ver  : $AIRFLOW_VERSION"
echo ""

# ============================================================================
# 1. CHECK PYTHON VERSION
# ============================================================================
echo "▶ Step 1: Checking Python..."

if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ Python 3.11 not found"
    echo "Install with: brew install python@3.11"
    exit 1
fi

echo "✓ Using $($PYTHON_CMD --version)"

# ============================================================================
# 2. CREATE FRESH VENV
# ============================================================================
echo ""
echo "▶ Step 2: Creating virtual environment..."

rm -rf "$VENV_DIR"
$PYTHON_CMD -m venv "$VENV_DIR"

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

echo "✓ Virtual environment ready"

# ============================================================================
# 3. UPGRADE PIP TOOLING
# ============================================================================
echo ""
echo "▶ Step 3: Upgrading pip..."

pip install --upgrade pip setuptools wheel 2>&1
echo "✓ pip upgraded"

# ============================================================================
# 4. INSTALL LOCAL LIBS FIRST
# ============================================================================
LOCAL_LIBS_DIR="$PROJECT_ROOT/../../.."
LOCAL_LIBS_DIR="$LOCAL_LIBS_DIR/libs"

if [ -d "$LOCAL_LIBS_DIR" ]; then
    echo "▶ Installing all local libraries from $LOCAL_LIBS_DIR..."
    for lib in "$LOCAL_LIBS_DIR/"*; do
        [ -d "$lib" ] && pip install -e "$lib" 2>&1
    done
    echo "✓ Local libraries installed"
else
    echo "⚠️ $LOCAL_LIBS_DIR directory not found, skipping local libraries installation"
fi

# ============================================================================
# 5. INSTALL AIRFLOW (USING OFFICIAL CONSTRAINTS)
# ============================================================================
echo ""
echo "▶ Step 5: Installing Apache Airflow (constrained)..."

pip install \
  "apache-airflow==${AIRFLOW_VERSION}" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-3.11.txt" \
  2>&1

echo "✓ Apache Airflow installed"

# ============================================================================
# 6. INSTALL PROJECT REQUIREMENTS
# ============================================================================
echo ""
echo "▶ Step 6: Installing project requirements..."

pip install -r "$PROJECT_ROOT/apache_airflow_app/requirements.txt" 2>&1
echo "✓ Project dependencies installed"

echo ""
echo "Setup complete! You can now run 'run.sh' to start Airflow."
