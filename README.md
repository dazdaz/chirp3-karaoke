# 🎵 Chirp2 Demo Enhanced - Google Cloud Speech & TTS Interactive Demo

Original demo from https://github.com/rickygodoy/chirp-demo
Full kudos to Felipe and Ricky.

Made some improvements to enhance the user experience

- Changed the default user experience language to english 
- Added in some popular songs for the Karaoke
- Made the listen functionality more centered around language learning
- Call analyzer now translated into english
- added setup-iam.sh, cleanup-iam.sh and start.sh

# Overview

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
- **[quickstart.md](quickstart.txt)** - Ultra-quick command reference

## 🎮 Features

### Module 1: Singing Contest
Karaoke competition - Sing along to popular songs and get scored.

- Select the song which you'd like to sing the words to.
- You'll see 4 sentences to sing, which will be highlighted so that you get the rhythm correct.
- Upon completion, you'll be added into a leaderboard.

**How it works**:
Sing the lyrics accurately to earn points based on accuracy, confidence, and timing.

**Features**:
- Low-latency streaming transcription
- Word-level confidence scoring
- Timing and rhythm analysis
- High score leaderboard
- Uses Chirp 2 for Speech-to-Text (STT) - configured in the streaming recognition config with model="chirp_2"
- Chirp 3 is not GA yet, but when available update line 242 in main.py and check regional support

### Module 2: Language Learning
Test your listening comprehension

- Listen carefully and transcribe phrases to learn new languages
- Select the language to hear the phrase in.
- Write doen the phrase which you heard.
- Then you'll see the meaning in English.

**Features**:
- Random phrase generation
- Accuracy scoring with Levenshtein distance
- Time-based bonus points
- Competitive leaderboard
- Uses Chirp 3 for Text-to-Speech (TTS) - uses "en-US-Chirp3-HD-Charon" voice for English synthesis

### Module 3: Analyze a Call
Call Analysis is a demonstration that shows how Chirp could be used for call transcription with speaker identification from multiple voices.

This is a static demonstration using hardcoded content, not actual Chirp speech-to-text with speaker diarization. It serves as a proof-of-concept showing what a call analysis interface could look like, but the transcript, speaker identification, and translations are all pre-prepared to simulate the experience.

**Features**:
- Transcribes spoken words into text
- Translates into a selection of 8 target languages

## 🛠 Technical Highlights from all demos

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

## 🆘 Support

For issues or questions, refer to:
- [Troubleshooting Guide](INSTRUCTIONS.md#troubleshooting)
- [Google Cloud Speech-to-Text Docs](https://cloud.google.com/speech-to-text/docs)
- [Google Cloud Text-to-Speech Docs](https://cloud.google.com/text-to-speech/docs)
