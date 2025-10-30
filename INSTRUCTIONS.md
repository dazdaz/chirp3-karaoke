# Chirp Demo - Quick Start Guide

A Google Cloud Speech-to-Text and Text-to-Speech demo application with singing and learning games.

## Prerequisites (Both Methods)

1. **Google Cloud Project** with billing enabled
2. **Enable APIs**:
   ```bash
   gcloud services enable speech.googleapis.com texttospeech.googleapis.com
   ```
3. **Set up credentials** (choose one):
   - **Automated** (recommended):
     ```bash
     chmod +x setup-iam.sh
     ./setup-iam.sh
     ```
   - **Manual**: Use existing service account with `roles/speech.client` role

---

## Method A: Using Docker Container 🐳

### Prerequisites
- Docker Desktop installed
- Google Cloud credentials ready

### Steps

1. **Clone and navigate to project**:
   ```bash
   cd /Users/user/src/chirp-demo
   ```

2. **Build Docker image**:
   ```bash
   docker build -t chirp-demo .
   ```

3. **Run container**:
   ```bash
   docker run -p 8080:8080 \
     -e GOOGLE_CLOUD_PROJECT="your-project-id" \
     -v ~/chirp-demo-credentials.json:/app/credentials.json \
     -e GOOGLE_APPLICATION_CREDENTIALS="/app/credentials.json" \
     chirp-demo
   ```

4. **Open browser**: http://localhost:8080

### Stop Container
```bash
# Find container ID
docker ps

# Stop container
docker stop <container-id>
```

---

## Method B: Running Locally on macOS 💻

### Prerequisites
- Python 3.9+ installed
- Google Cloud SDK installed

### Option 1: Using uv (Fast & Modern) ⚡

1. **Install uv**:
   ```bash
   # Using official installer
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # OR using Homebrew
   brew install uv
   ```

2. **Set up and run**:
   ```bash
   cd /Users/user/src/chirp-demo
   
   # Create virtual environment
   uv venv
   source .venv/bin/activate
   
   # Install dependencies
   uv pip install -r requirements.txt
   
   # Set environment variables
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export GOOGLE_APPLICATION_CREDENTIALS="~/chirp-demo-credentials.json"
   
   # Run application
   uv run python main.py
   ```

3. **Open browser**: http://localhost:8080

### Option 2: Using Traditional pip/venv 📦

1. **Set up Python environment**:
   ```bash
   cd /Users/user/src/chirp-demo
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Set environment and run**:
   ```bash
   # Set environment variables
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export GOOGLE_APPLICATION_CREDENTIALS="~/chirp-demo-credentials.json"
   
   # Run application
   python main.py
   
   # OR with uvicorn directly
   uvicorn main:app --host 0.0.0.0 --port 8080 --reload
   ```

3. **Open browser**: http://localhost:8080

### Stop Application
Press `Ctrl+C` in terminal, then:
```bash
deactivate  # Exit virtual environment
```

---

## Using the Application

### 🎤 Singing Contest Tab
1. Select a song from the dropdown
2. Click "Start Singing"
3. Sing along with the lyrics shown
4. Get scored on accuracy, confidence, and timing

### 🎧 Learning Game Tab
1. Click "Play Phrase"
2. Listen carefully to the audio
3. Type what you heard
4. Check your answer for scoring

### 📊 Call Analysis Tab
Analyze sentiment and patterns from recorded conversations

---

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| **Port 8080 in use** | `lsof -i :8080` then `kill -9 <PID>` |
| **Authentication error** | Check `GOOGLE_APPLICATION_CREDENTIALS` path |
| **Module not found** | Ensure virtual environment is activated |
| **Docker build fails** | Run `docker system prune -a` to clean up |
| **API not enabled** | Run the enable commands in Prerequisites |

---

## One-Line Quick Start

### With uv (Fastest):
```bash
cd /Users/user/src/chirp-demo && ./setup-iam.sh && uv venv && source .venv/bin/activate && uv pip install -r requirements.txt && export GOOGLE_CLOUD_PROJECT="your-project-id" && export GOOGLE_APPLICATION_CREDENTIALS="~/chirp-demo-credentials.json" && uv run python main.py
```

### With Docker:
```bash
cd /Users/user/src/chirp-demo && docker build -t chirp-demo . && docker run -p 8080:8080 -e GOOGLE_CLOUD_PROJECT="your-project-id" -v ~/chirp-demo-credentials.json:/app/credentials.json -e GOOGLE_APPLICATION_CREDENTIALS="/app/credentials.json" chirp-demo
```

---

## Clean Up

When done with the demo:
```bash
# Remove Google Cloud resources
./cleanup-iam.sh

# Remove Docker image (if used)
docker rmi chirp-demo

# Remove Python virtual environment (if used)
rm -rf .venv venv
```

---

💡 **Tip**: For development with auto-reload, add `--reload` flag when running with uvicorn.
