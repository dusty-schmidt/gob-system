#!/bin/bash
# /home/ds/sambashare/GOB/GOB-V1.0/start_gob_core.sh
# Official startup script for the Grid Overwatch Bridge.

echo "============================================="
echo "Initializing Grid Overwatch Bridge"
echo "============================================="

# Set the project root directory
export GOB_DIR="/home/ds/sambashare/GOB"

# Change to the script's directory to ensure correct pathing for imports
cd "$GOB_DIR/grid-overwatch-bridge" || exit

# Use conda run to execute the python script in the correct environment
# This handles all pathing and activation automatically.
conda run -n gob-core python3 service.py

echo "============================================="
echo "Grid Overwatch Bridge has terminated."
echo "============================================="
