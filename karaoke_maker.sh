#!/bin/bash

# Karaoke Maker - Wrapper Script
# This script runs the Python karaoke maker using uv

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the Python karaoke maker using uv
uv run "$SCRIPT_DIR/karaoke_maker.py" "$@"
