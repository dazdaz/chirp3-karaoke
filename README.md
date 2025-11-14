# Chirp3 - Audio Recognition Game 🎵

An interactive web-based audio game where players test their music knowledge by identifying songs from short audio clips. Built with Python Flask and modern web technologies.

## Features

- **Song Recognition Game**: Players listen to 3-second audio clips and guess the song
- **Multiple Difficulty Levels**: Choose from Easy, Medium, or Hard modes
- **Real-time Scoring**: Track your score and combo streaks
- **Leaderboard System**: Compete with other players for the top spot
- **Audio Processing**: Advanced audio manipulation including pitch shifting and speed changes
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Technologies Used

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Audio Processing**: Web Audio API
- **Data Storage**: JSON files for songs and leaderboard data
- **Deployment**: Docker support included

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/dazdaz/chirp3.git
cd chirp3
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the song database:
```bash
python setup_data.py
```

4. Run the application:
```bash
python main.py
```

The application will be available at `http://localhost:8080`

## Docker Deployment

Build and run with Docker:

```bash
docker build -t chirp3 .
docker run -p 8080:8080 chirp3
```

## Game Modes

### Easy Mode
- 10 seconds per round
- Basic song selection
- No audio effects

### Medium Mode  
- 7 seconds per round
- Wider song selection
- Minor pitch variations

### Hard Mode
- 5 seconds per round
- All songs available
- Advanced audio effects (pitch shift, speed changes)

## Project Structure

```
chirp3/
├── main.py              # Flask application server
├── setup_data.py        # Initialize song database
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── static/             # Frontend assets
│   ├── script.js       # Game logic
│   ├── audio-processor.js  # Audio manipulation
│   ├── style.css       # Styling
│   └── songs/          # Audio files
├── templates/          # HTML templates
│   └── index.html      # Main game interface
├── songs.json          # Song database
└── leaderboard.json    # Player scores
```

## Deployment Scripts

- `deploy.sh` - Deploy to cloud services
- `setup-iam.sh` - Configure IAM permissions
- `cleanup-iam.sh` - Clean up IAM resources
- `start.sh` - Start the application

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Audio clips are for educational purposes only
- Built as a demonstration of web audio capabilities
- Inspired by music quiz games and audio processing techniques

## Contact

For questions or feedback, please open an issue on the [GitHub repository](https://github.com/dazdaz/chirp3/issues).