# 🎵 Chirp Demo - Google Cloud Speech & TTS Interactive Demo

Original demo from https://github.com/rickygodoy/chirp-demo
Full kudos to Felipe and Ricky.

Made some improvements to enhance the user experience
- changed the default user experience language to english 
- added in some popular songs for the Karaoke
- made the listen functionality more centered around language learning
- call analyzer now translated into english

An interactive web application showcasing Google Cloud's advanced Speech-to-Text and Text-to-Speech capabilities through fun singing and learning games.

## 🚀 Quick Start

**Choose your preferred method:**

### Option A: Docker Container (Isolated Environment)
```bash
docker build -t chirp-demo .
docker run -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT="your-project-id" \
  -v ~/chirp-demo-credentials.json:/app/credentials.json \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/credentials.json" \
  chirp-demo
```

### Option B: Run Locally on macOS
```bash
# Using uv (recommended - fast & modern)
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="~/chirp-demo-credentials.json"
uv run python main.py
```

**Access the app at:** http://localhost:8080

## 📖 Documentation

- This guide which your reading now
- **[quickstart.md](quickstart.md)** - Ultra-quick command reference

## 🎮 Features

### Module 1: Creative Storyteller (TTS Demo)
- **Voice Quality & Variety**: Experience human-like TTS voices with distinct personalities
- **How it works**:
  1. Click "Talk" and dictate a story beginning
  2. See real-time transcription with automatic punctuation
  3. Choose from various voice profiles (Old Storyteller, Energetic Youth, etc.)
  4. Listen to your story read back with impressive clarity and personality

### Module 2: Singing Contest (STT Demo)
- **Real-time Transcription**: Sing along to popular songs and get scored
- **Features**:
  - Low-latency streaming transcription
  - Word-level confidence scoring
  - Timing and rhythm analysis
  - High score leaderboard

### Module 3: Learning Game
- **Listen & Type**: Test your listening comprehension
- **Features**:
  - Random phrase generation
  - Accuracy scoring with Levenshtein distance
  - Time-based bonus points
  - Competitive leaderboard

## 🛠 Technical Highlights

### Chirp STT Features Showcased
- ✅ Automatic punctuation
- ✅ Low-latency streaming
- ✅ High accuracy with rapid speech
- ✅ Word-level timestamps and confidence scores
- ✅ Speaker diarization capabilities

### Chirp TTS Features Showcased
- ✅ Superior naturalness and expressiveness
- ✅ Multiple voice personalities
- ✅ Wide variety of accents and styles
- ✅ Real-time synthesis

## 📋 Prerequisites

1. **Google Cloud Project** with billing enabled
2. **Enable APIs**:
   ```bash
   gcloud services enable speech.googleapis.com texttospeech.googleapis.com
   ```
3. **Service Account** with `roles/speech.client` role (use `./setup-iam.sh` for automated setup)

## 🧹 Cleanup

When done with the demo:
```bash
# Remove Google Cloud resources
./cleanup-iam.sh

# Remove Docker image (if used)
docker rmi chirp-demo

# Remove Python environment (if used)
rm -rf .venv venv
```

## 🔧 Development

For development with auto-reload:
```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

## 📄 License

This is a demonstration project for Google Cloud's Chirp Speech APIs.

## 🆘 Support

For issues or questions, refer to:
- [Troubleshooting Guide](INSTRUCTIONS.md#troubleshooting)
- [Google Cloud Speech-to-Text Docs](https://cloud.google.com/speech-to-text/docs)
- [Google Cloud Text-to-Speech Docs](https://cloud.google.com/text-to-speech/docs)
