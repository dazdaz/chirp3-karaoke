# Karaoke King 🎵

Karaoke King - An advanced karaoke application with real-time transcription and scoring using Google Cloud's Chirp 3 speech recognition. Features professional-grade word-by-word lyric synchronization, fuzzy matching for accurate scoring, and a competitive leaderboard system. Built with Python Flask and modern web technologies.

## Features

- **Real-time Transcription**: Powered by Google Cloud Speech API with Chirp 3 model for accurate voice recognition
- **Karaoke Teleprompter**: Word-by-word lyric highlighting synchronized with the music
- **Advanced Scoring Engine**: Fuzzy matching with Jaro-Winkler similarity algorithm for intelligent scoring
- **Flexible Recording Options**: Choose from 10s to 60s durations or full song mode
- **Sync Adjustment**: Fine-tune lyric timing with ±0.5s adjustments
- **Leaderboard System**: Compete with other singers and track high scores
- **Audio Visualization**: Real-time frequency spectrum display during playback
- **Skip Intro Feature**: Automatically jump to vocals for faster practice
- **Visual Countdown**: 3-2-1 countdown before recording starts
- **Responsive Design**: Works seamlessly on desktops

<img width="1179" height="673" alt="Screenshot 2025-11-14 at 19 59 58" src="https://github.com/user-attachments/assets/4f86f6c1-5a13-4492-a7fd-7b84fadd36d1" />

## Technologies Used

- **Backend**: Python Flask
- **Speech Recognition**: Google Cloud Speech-to-Text V2 (Chirp 3 model)
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Audio Processing**: Web Audio API with real-time visualization
- **Fuzzy Matching**: Jellyfish library for Jaro-Winkler similarity scoring
- **Data Storage**: JSON files for songs and leaderboard data
- **Deployment**: Docker support included

## Installation

### Prerequisites

- Python 3.8 or higher
- uv package manager ([install here](https://docs.astral.sh/uv/getting-started/installation/))
- Google Cloud account with Speech-to-Text API enabled
- Google Cloud credentials configured

### Setup with uv

1. Clone the repository:
```bash
git clone https://github.com/dazdaz/chirp3-karaoke-king.git
cd chirp3-karaoke-king
```

2. Set up Google Cloud credentials:
```bash
# Set your Google Cloud project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Authenticate with Google Cloud
gcloud auth application-default login
```

3. Install dependencies using uv:
```bash
uv sync
```

4. Initialize the song database:
```bash
# Download songs from Bandcamp
uv run python setup_music.py <bandcamp_album_url> <name of artist or band>
# Or see README_MUSIC_SETUP.md for detailed music setup instructions
```

5. Run the application:
```bash
uv run python main.py
```

The application will be available at `http://localhost:8080`

### Legacy pip Installation (Optional)

If you prefer to use pip instead of uv:

```bash
pip install -r requirements.txt
```

## Docker Deployment

Build and run with Docker:

```bash
docker build -t karaoke-king .
docker run -p 8080:8080 karaoke-king
```

## Recording Durations

Choose your preferred recording duration:
- **Quick Test**: 10 seconds
- **Short**: 20 seconds (default)
- **Medium**: 30 seconds
- **Long**: 40 seconds
- **Extended**: 50 seconds
- **Minute**: 60 seconds
- **Full Song**: Complete track

## Scoring System

The application uses an advanced AI-powered scoring engine that:
- Normalizes text and handles contractions ("gonna" → "going to")
- Uses Jaro-Winkler similarity for fuzzy matching
- Awards full points for exact matches (green)
- Gives partial credit for close matches (yellow)
- Deducts points for wrong words (red)
- Identifies missing lyrics (gray)
- Applies a "vibe boost" for similar word counts

## Project Structure

```
karaoke-king/
├── main.py              # Flask application server
├── setup_music.py       # Download and setup music
=======
├── setup_music.py       # Download and setup music
├── karaoke_maker.py     # AI-powered vocal separation for karaoke tracks
├── pyproject.toml       # Project configuration and dependencies
├── requirements.txt     # Legacy requirements file (optional)
├── Dockerfile           # Docker configuration
├── artists.sh           # Example quickstart Artist data management script, wrapper to setup_music.py
├── static/              # Frontend assets
├── artists.sh           # Artist data management script, wrapper to setup_music.py
├── static/              # Frontend assets
│   ├── audio-processor.js  # Audio manipulation
│   ├── style.css        # Styling
│   └── songs/           # Audio files
├── templates/           # HTML templates
│   └── index.html       # Main game interface
├── songs.json           # Song database (gitignored)
├── songs-karaoke/       # Processed karaoke-ready audio files
├── songs-tobeprocessed/ # Raw audio files awaiting processing (gitignored)
├── leaderboard.json     # Player scores
├── README.md            # Main documentation
├── README_MUSIC_SETUP.md # Music setup guide
├── README_KARAOKE_MAKER.md # Karaoke maker guide
└── .uv/                 # uv project cache (gitignored)
...
```

## Disclaimer & Legal Notice

**⚠️ IMPORTANT: Copyright and Fair Use Notice**

This software is provided for **educational and personal use only**. Users are solely responsible for ensuring they have the legal right to use any audio content with this application.

**What you MUST do:**
- ✅ Purchase music from legitimate sources (Bandcamp, HDTracks, official artist websites, etc.)
- ✅ Use only music you own or have permission to use
- ✅ Ensure compliance with local copyright laws
- ✅ Respect artist rights and intellectual property

**What you MUST NOT do:**
- ❌ Use copyrighted music without proper licensing
- ❌ Distribute or share processed audio files
- ❌ Commercial use without appropriate permissions
- ❌ Violate any applicable copyright laws

**Recommended Legal Sources:**
- [Bandcamp](https://bandcamp.com/) - Direct artist support
- [HDTracks](https://hdtracks.com/) - High-quality downloads
- [7digital](https://www.7digital.com/) - Legal music platform
- [Amazon Music](https://music.amazon.com/) - Licensed content
- Apple Music, Spotify, etc. (check terms for offline use)

The developers assume no responsibility for misuse of this software. By using this application, you agree to comply with all applicable laws and terms of service.
