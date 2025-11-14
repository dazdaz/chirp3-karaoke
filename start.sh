#!/bin/bash
# Filename: start.sh

# Function to stop the server
stop_server() {
    echo "🛑 Stopping Chirp 3 Demo..."
    pkill -f "python.*main.py" 2>/dev/null
    exit 0
}

# Handle stop command
if [ "$1" == "stop" ]; then
    stop_server
fi

# 1. Cleanup on Exit
cleanup() {
    echo "" 
    echo "🧹 Cleaning up..."
    unset GOOGLE_APPLICATION_CREDENTIALS
}
trap cleanup EXIT SIGINT

# 2. Environment Config
export GOOGLE_CLOUD_PROJECT="daev-playground"
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/chirp-demo-credentials.json"
VENV_DIR=".venv"

# Check Credentials
if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "❌ ERROR: Credentials file missing: $GOOGLE_APPLICATION_CREDENTIALS"
    exit 1
fi

echo "🚀 Starting Chirp 3 Demo..."

# 3. AUTO-FIX: Ensure Python 3.11
# We check if the existing venv is bad (Python 3.14 or missing)
REBUILD_VENV=false

if [ ! -d "$VENV_DIR" ]; then
    REBUILD_VENV=true
else
    # Check version inside existing venv
    CURRENT_VER=$("$VENV_DIR/bin/python" --version 2>&1)
    if [[ "$CURRENT_VER" != *"3.11"* ]]; then
        echo "⚠️  Detected incompatible Python version: $CURRENT_VER"
        REBUILD_VENV=true
    fi
fi

if [ "$REBUILD_VENV" = true ]; then
    echo "🔧 Building fresh Python 3.11 environment..."
    rm -rf "$VENV_DIR"
    uv venv --python 3.11
fi

# 4. Install Dependencies
echo "📚 Syncing dependencies..."
uv pip install -r requirements.txt > /dev/null 2>&1

# 5. Check Port & Run
PORT=${1:-8080}
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port $PORT in use. Killing old process..."
    pkill -f "python.*main.py" 2>/dev/null
    sleep 1
fi

echo "🎵 Starting server on port $PORT..."
"$VENV_DIR/bin/python" main.py $PORT

