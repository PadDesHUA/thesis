#!/bin/bash

# Get the absolute path of the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define script paths relative to the script location
SCRIPTS=(
    "$SCRIPT_DIR/DATA/traffic.py"
    "$SCRIPT_DIR/ATH/weather_ath_pred.py"
    "$SCRIPT_DIR/THES/weather_thess_pred.py"
    "$SCRIPT_DIR/ARIMA/ARIMA.py"
)

# Execute each script sequentially
for script in "${SCRIPTS[@]}"; do
    if [[ -f "$script" ]]; then
        echo "Executing: $script"
        python3 "$script"
        echo "Finished: $script"
    else
        echo "Error: Script not found -> $script"
    fi
done
