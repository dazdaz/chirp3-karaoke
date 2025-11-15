# Karaoke Maker - Python Version

Create high-quality karaoke tracks using AI-powered vocal separation with audio-separator.

## Features

- 🎵 **High-Quality Vocal Separation**: Uses advanced AI models for clean vocal removal
- 🎛️ **Adjustable Vocal Reduction**: Control how much of the vocals are reduced (0.0-1.0)
- 📁 **Batch Processing**: Process entire directories of audio files
- 🎧 **Multiple Formats**: Supports FLAC, MP3, WAV files
- 🚀 **Pure CLI**: No GUI components, completely command-line driven
- 🤖 **AI-Powered**: Uses state-of-the-art machine learning models
- 🍎 **Apple Silicon Optimized**: MPS/CoreML acceleration for Mac M1/M2/M3

## Installation

### Prerequisites

- Python 3.13 (required)
- ffmpeg (for audio processing)

### Quick Setup

```bash
# Install audio-separator system-wide (recommended)
pip3 install --break-system-packages audio-separator

# Or create virtual environment
python3.13 -m venv venv_py313
source venv_py313/bin/activate
pip install audio-separator
```

## Usage

### Basic Usage

```bash
# Create instrumental tracks (full vocal removal)
./karaoke_maker.sh -i "input_directory/" -o "output_directory/" -t instrumental

# Create reduced vocals (keep some vocals)
./karaoke_maker.sh -i "input_directory/" -o "output_directory/" -t reduced-vocals
```

### Advanced Usage

```bash
# Specify vocal reduction level (0.0 = no reduction, 1.0 = full removal)
./karaoke_maker.sh -i "input/" -o "output/" -t instrumental -r 0.8

# Process single file
./karaoke_maker.sh -i "song.flac" -o "output/" -t instrumental -r 0.9

# Light vocal reduction (keep more vocals)
./karaoke_maker.sh -i "album/" -o "karaoke/" -t instrumental -r 0.3

# Heavy vocal reduction (almost no vocals)
./karaoke_maker.sh -i "album/" -o "karaoke/" -t instrumental -r 0.95
```

### Manual Usage (Advanced)

If you prefer to activate the environment manually:

```bash
source venv_py313/bin/activate
python3.13 karaoke_maker.py -i "input/" -o "output/" -t instrumental -r 0.8
```

## Command Line Options

- `-i, --input`: Input file or directory (required)
- `-o, --output`: Output directory (required)
- `-t, --type`: Processing type (`instrumental` or `reduced-vocals`, default: `instrumental`)
- `-r, --reduction`: Vocal reduction level (0.0-1.0, default: 1.0)

## Vocal Reduction Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| 0.0 | No reduction | Original audio |
| 0.3 | Light reduction | Practice vocals |
| 0.5 | Moderate reduction | Background vocals |
| 0.7 | Heavy reduction | Karaoke with guide vocals |
| 1.0 | Full removal | Pure instrumental |

## Supported Audio Formats

- FLAC (recommended for highest quality)
- MP3
- WAV

## Output Files

The script creates output files with the following naming convention:

- **Instrumental**: `filename_instrumental.flac`
- **Reduced Vocals**: `filename_reduced_vocals.flac`

## AI Models Used

- **Demucs_v4_hybrid**: High-quality instrumental separation
- **Kim_Vocal_2**: Advanced vocal extraction
- **bs_roformer**: Alternative model for specific use cases

## Examples

### Process an entire album
```bash
./karaoke_maker.sh -i "Thriller [96kHz · 24bit]/" -o "thriller_karaoke/" -t instrumental -r 0.9
```

### Create practice tracks with light vocal reduction
```bash
./karaoke_maker.sh -i "practice_songs/" -o "practice_output/" -t instrumental -r 0.4
```

### Extract vocals for remixing
```bash
./karaoke_maker.sh -i "remix_source/" -o "vocals_output/" -t reduced-vocals -r 0.8
```

## Troubleshooting

### audio-separator not found
```bash
# Install audio-separator
pip3 install --break-system-packages audio-separator

# Or use virtual environment
python3.13 -m venv venv_py313
source venv_py313/bin/activate
pip install audio-separator
```

### Python version issues
```bash
# Ensure you're using Python 3.13
python3.13 --version

# Create virtual environment with correct version
python3.13 -m venv venv_py313
```

### Memory issues
Audio processing requires significant RAM. For large files:
- Ensure you have at least 8GB RAM available
- Process files individually rather than in large batches

## Performance Tips

- Use FLAC files for best quality
- Process files individually for better memory management
- Higher reduction levels may take longer to process
- Apple Silicon users get automatic acceleration

## Architecture

- **karaoke_maker.sh**: Wrapper script that handles environment activation
- **karaoke_maker.py**: Main Python script with audio-separator integration
- **venv_py313/**: Python 3.13 virtual environment (if used)

## License

This project uses audio-separator and associated AI models. Please check the respective licenses for usage terms.

## Contributing

Feel free to submit issues and enhancement requests!
