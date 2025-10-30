export GOOGLE_CLOUD_PROJECT=me-playground
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/chirp-demo-credentials.json"
uv run python main.py ${1:-8080}
