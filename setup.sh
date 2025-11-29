#!/bin/bash
# Setup script for stock_data_app
# This script now delegates to orchestrator.sh

set -e

echo "Running orchestrator to setup frameworks..."
./orchestrator.sh

