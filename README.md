# Chirp3-Karaoke Pro 🎵

An advanced karaoke application with real-time transcription and scoring using Google Cloud's Chirp 3 speech recognition. Features professional-grade word-by-word lyric synchronization, fuzzy matching for accurate scoring, and a competitive leaderboard system. Built with Python Flask and modern web technologies.

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
- pip (Python package manager)
- Google Cloud account with Speech-to-Text API enabled
- Google Cloud credentials configured

### Setup

1. Clone the repository:
```bash
git clone https://github.com/dazdaz/chirp3-karaoke.git
cd chirp3-karaoke
```

2. Set up Google Cloud credentials:
```bash
# Set your Google Cloud project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Authenticate with Google Cloud
gcloud auth application-default login
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the song database:
```bash
# Download songs from Bandcamp
python setup_music.py <bandcamp_album_url> <name of artist or band>
# Or see README_MUSIC_SETUP.md for detailed music setup instructions
```

5. Run the application:
```bash
python main.py
```

The application will be available at `http://localhost:8080`

## Docker Deployment

Build and run with Docker:

```bash
docker build -t chirp3-karaoke .
docker run -p 8080:8080 chirp3-karaoke
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
chirp3-karaoke/
├── main.py              # Flask application server
├── setup_music.py       # Download and setup music from Bandcamp
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── artists.sh           # Artist data management script, wraper to setup_music.py
├── static/              # Frontend assets
│   ├── script.js        # Game logic
│   ├── audio-processor.js  # Audio manipulation
│   ├── style.css        # Styling
│   └── songs/           # Audio files
├── templates/           # HTML templates
│   └── index.html       # Main game interface
├── songs.json           # Song database (gitignored)
├── leaderboard.json     # Player scores
├── README.md            # Main documentation
└── README_MUSIC_SETUP.md # Music setup guide
```

## Scripts & Tools

- `setup_music.py` - Download and manage songs from Bandcamp
- `artists.sh` - Artist data management
- `deploy.sh` - Deploy to cloud services
- `setup-iam.sh` - Configure IAM permissions
- `cleanup-iam.sh` - Clean up IAM resources
- `start.sh` - Start the application

## Environment Variables

```bash
# Required
GOOGLE_CLOUD_PROJECT=your-project-id

# Optional
PORT=8080  # Server port (default: 8080)
```

## API Requirements

This application requires:
- Google Cloud Speech-to-Text API enabled
- Appropriate IAM permissions for Speech API access
- Valid Google Cloud credentials

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Audio clips are for educational purposes only
- Built as a demonstration of web audio capabilities
- Inspired by music quiz games and audio processing techniques

## Contact

For questions or feedback, please open an issue on the [GitHub repository](https://github.com/dazdaz/chirp3-karaoke/issues).

## Additional Documentation

- [Music Setup Guide](README_MUSIC_SETUP.md) - Detailed instructions for downloading and managing music files
