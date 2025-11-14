#!/bin/bash
# Filename: start.sh

# 1. Define a cleanup function
cleanup() {
    echo "" # Newline for readability after ^C
    echo "Cleaning up environment variables..."
    unset GOOGLE_APPLICATION_CREDENTIALS
    # unset GOOGLE_CLOUD_PROJECT 
}

# 2. Set the trap
# EXIT runs on normal completion or error
# SIGINT runs on Ctrl+C
trap cleanup EXIT SIGINT

# 3. Your main logic
# Ensure these point to your actual project and key location
export GOOGLE_CLOUD_PROJECT="daev-playground"
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/chirp-demo-credentials.json"

# Check if credentials file actually exists to prevent confusing errors later
if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "ERROR: Credentials file not found at: $GOOGLE_APPLICATION_CREDENTIALS"
    exit 1
fi

echo "🚀 Starting Chirp 3 Demo..."
echo "🔧 Enforcing Python 3.11 to ensure Google Cloud compatibility..."

# 4. Run the application
# We explicitly pass --python 3.11 to uv. 
# uv will automatically download and use Python 3.11, bypassing the system's Python 3.14.
uv run --python 3.11 python main.py ${1:-8080}

