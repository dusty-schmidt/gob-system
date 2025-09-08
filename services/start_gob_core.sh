#!/bin/bash
# /home/ds/sambashare/GOB/GOB-system/services/start_gob_core.sh
# Official startup script for the Grid Overwatch Bridge.

echo "============================================="
echo "Initializing Grid Overwatch Bridge"
echo "============================================="

# Get the directory where the script is located.
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Set the GOB-system directory path, which is one level above the script's directory.
export GOB_SYSTEM_DIR="$SCRIPT_DIR/.."

# Change to the grid-overwatch-bridge directory to ensure correct pathing for imports.
cd "$GOB_SYSTEM_DIR/grid-overwatch-bridge" || { echo "Error: Could not change to the grid-overwatch-bridge directory."; exit 1; }

# Use conda run to execute the python script in the correct environment.
# This handles all pathing and activation automatically.
conda run -n gob-core python3 service.py

echo "============================================="
echo "Grid Overwatch Bridge has terminated."
echo "============================================="
