# price_app/run.sh
#!/bin/bash
set -e

cd "$(dirname "$0")"
source common.sh

[ ! -d "venv" ] && echo "Error: venv not found. Run ./setup.sh first" && exit 1

activate_venv
# Your app commands