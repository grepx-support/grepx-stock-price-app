#!/bin/bash
# Orchestrator script to download and install celery_framework and dagster_framework
# For now: installs from parent directory
# Later: will download from Git and install

set -e

# ============================================
# Configuration Variables
# ============================================
# Set installation method: "local" or "git"
INSTALL_METHOD="local"

# Local paths (for local installation)
CELERY_FRAMEWORK_LOCAL_PATH="../celery_framework"
DAGSTER_FRAMEWORK_LOCAL_PATH="../dagster_framework"

# Git URLs (for Git installation - uncomment and set when ready)
# CELERY_FRAMEWORK_GIT_URL="https://github.com/yourorg/celery_framework.git"
# DAGSTER_FRAMEWORK_GIT_URL="https://github.com/yourorg/dagster_framework.git"

# ============================================

echo "=========================================="
echo "Stock Data App - Orchestrator"
echo "=========================================="
echo "Installation method: ${INSTALL_METHOD}"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/Scripts/activate
else
    echo "Creating virtual environment..."
    python -m venv venv
    source venv/Scripts/activate
    echo "Upgrading pip..."
    pip install --upgrade pip
fi

# Function to install framework from local directory
install_local_framework() {
    local framework_name=$1
    local framework_path=$2
    
    if [ -d "$framework_path" ]; then
        echo ""
        echo "Installing ${framework_name} from local directory: ${framework_path}"
        cd "$framework_path"
        if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
            pip install -e .
            echo "✓ ${framework_name} installed successfully"
            cd - > /dev/null
            return 0
        else
            echo "⚠ Warning: ${framework_name} directory exists but no setup.py or pyproject.toml found"
            cd - > /dev/null
            return 1
        fi
    else
        return 1
    fi
}

# Function to install framework from Git (for future use)
install_git_framework() {
    local framework_name=$1
    local git_url=$2
    
    echo ""
    echo "Installing ${framework_name} from Git..."
    
    # Create temp directory for cloning
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # Clone repository
    git clone "$git_url" "$framework_name"
    cd "$framework_name"
    
    # Install
    if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
        pip install -e .
        echo "✓ ${framework_name} installed successfully from Git"
    else
        echo "✗ Error: ${framework_name} repository doesn't contain setup.py or pyproject.toml"
        cd - > /dev/null
        rm -rf "$TEMP_DIR"
        return 1
    fi
    
    cd - > /dev/null
    rm -rf "$TEMP_DIR"
    return 0
}

# Install celery_framework
echo "Checking for celery_framework..."
CELERY_INSTALLED=false

if [ "$INSTALL_METHOD" = "local" ]; then
    if [ -d "$CELERY_FRAMEWORK_LOCAL_PATH" ]; then
        if install_local_framework "celery_framework" "$CELERY_FRAMEWORK_LOCAL_PATH"; then
            CELERY_INSTALLED=true
        fi
    else
        echo "✗ celery_framework not found at: $CELERY_FRAMEWORK_LOCAL_PATH"
    fi
elif [ "$INSTALL_METHOD" = "git" ]; then
    if [ -z "$CELERY_FRAMEWORK_GIT_URL" ]; then
        echo "✗ CELERY_FRAMEWORK_GIT_URL not set"
    else
        if install_git_framework "celery_framework" "$CELERY_FRAMEWORK_GIT_URL"; then
            CELERY_INSTALLED=true
        fi
    fi
else
    echo "✗ Unknown INSTALL_METHOD: $INSTALL_METHOD (use 'local' or 'git')"
fi

# Install dagster_framework
echo ""
echo "Checking for dagster_framework..."
DAGSTER_INSTALLED=false

if [ "$INSTALL_METHOD" = "local" ]; then
    if [ -d "$DAGSTER_FRAMEWORK_LOCAL_PATH" ]; then
        if install_local_framework "dagster_framework" "$DAGSTER_FRAMEWORK_LOCAL_PATH"; then
            DAGSTER_INSTALLED=true
        fi
    else
        echo "✗ dagster_framework not found at: $DAGSTER_FRAMEWORK_LOCAL_PATH"
    fi
elif [ "$INSTALL_METHOD" = "git" ]; then
    if [ -z "$DAGSTER_FRAMEWORK_GIT_URL" ]; then
        echo "✗ DAGSTER_FRAMEWORK_GIT_URL not set"
    else
        if install_git_framework "dagster_framework" "$DAGSTER_FRAMEWORK_GIT_URL"; then
            DAGSTER_INSTALLED=true
        fi
    fi
else
    echo "✗ Unknown INSTALL_METHOD: $INSTALL_METHOD (use 'local' or 'git')"
fi

# Install main app dependencies
echo ""
echo "Installing main app dependencies..."
pip install -r requirements.txt

# Summary
echo ""
echo "=========================================="
echo "Installation Summary"
echo "=========================================="
if [ "$CELERY_INSTALLED" = true ]; then
    echo "✓ celery_framework: Installed"
else
    echo "✗ celery_framework: Not installed"
fi

if [ "$DAGSTER_INSTALLED" = true ]; then
    echo "✓ dagster_framework: Installed"
else
    echo "✗ dagster_framework: Not installed"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To start the app:"
echo "  ./start_all.sh    # Starts both Celery and Dagster"
echo ""

