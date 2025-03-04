#!/bin/bash

# Get the absolute path of the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Log file for debugging
LOG_FILE="$SCRIPT_DIR/logs.txt"

# Define script paths relative to their respective directories
SCRIPTS=(
    "$SCRIPT_DIR/DATA/traffic.py"
    "$SCRIPT_DIR/ATH/weather_ath_pred.py"
    "$SCRIPT_DIR/THES/weather_thess_pred.py"
    "$SCRIPT_DIR/ARIMA/ARIMA.py"
)

# Run each script inside its respective directory
for script in "${SCRIPTS[@]}"; do
    if [[ -f "$script" ]]; then
        SCRIPT_DIR_PATH="$(dirname "$script")"  # Get script's directory

        echo "Executing: $script in $SCRIPT_DIR_PATH" | tee -a "$LOG_FILE"

        # Change to the script's directory before executing
        (cd "$SCRIPT_DIR_PATH" && /usr/bin/python3 "$(basename "$script")") >> "$LOG_FILE" 2>&1

        echo "Finished: $script" | tee -a "$LOG_FILE"
    else
        echo "Error: Script not found -> $script" | tee -a "$LOG_FILE"
    fi
done
