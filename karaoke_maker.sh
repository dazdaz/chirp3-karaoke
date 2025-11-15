#!/bin/bash

# Karaoke Maker - Wrapper Script
# This script automatically activates the correct virtual environment and runs the Python karaoke maker

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the Python 3.13 virtual environment
source "$SCRIPT_DIR/venv_py313/bin/activate"

# Run the Python karaoke maker with Python 3.13 specifically
python3.13 "$SCRIPT_DIR/karaoke_maker.py" "$@"