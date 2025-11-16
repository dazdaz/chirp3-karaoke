# Karaoke King - Python Version

Create high-quality karaoke tracks using AI-powered vocal separation with audio-separator.

## Features

- 🎵 **High-Quality Vocal Separation**: Advanced AI models for clean vocal removal
- 🎛️ **Adjustable Vocal Reduction**: Control vocal reduction (0.0-1.0)
- 📁 **Batch Processing**: Process directories of audio files
- 🎧 **Multiple Formats**: FLAC, MP3, WAV support
- 🚀 **Pure CLI**: Command-line driven
- 🤖 **AI-Powered**: State-of-the-art ML models
- 🍎 **Apple Silicon Optimized**: MPS/CoreML acceleration

## Installation

### Prerequisites
- Python 3.8+ (3.13 recommended)
- uv package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
- ffmpeg

### Setup
```bash
# Install uv (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-extras

# Alternative: Manual environment
uv venv venv && source venv/bin/activate && uv sync
```

## Usage

```bash
# Full vocal removal (instrumentals)
uv run karaoke_maker -i "songs-tobeprocessed/" -o "songs-karaoke/" -r 1.0

# Light reduction (practice vocals)
uv run karaoke_maker -i "songs-tobeprocessed/" -o "songs-karaoke/" -r 0.3

# Moderate reduction
uv run karaoke_maker -i "songs-tobeprocessed/" -o "songs-karaoke/" -r 0.5

# Single file processing
uv run karaoke_maker -i "songs-tobeprocessed/song.flac" -o "songs-karaoke/" -r 0.9

# No reduction (copy original)
uv run karaoke_maker -i "songs-tobeprocessed/" -o "songs-karaoke/" -r 0.0
```

## Options

- `-i, --input`: Input file/directory (required)
- `-o, --output`: Output directory (required)  
- `-r, --reduction`: Vocal reduction 0.0-1.0 (default: 1.0)

## Vocal Reduction Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| 0.0 | No reduction | Original audio |
| 0.3 | Light | Practice vocals |
| 0.5 | Moderate | Background vocals |
| 0.7 | Heavy | Guide vocals |
| 1.0 | Full removal | Pure instrumental |

## Supported Formats
FLAC (recommended), MP3, WAV

## Output
- **Instrumental**: `filename_instrumental.flac`
- **Reduced Vocals**: `filename_reduced_vocals.flac`

## AI Models
- **Demucs_v4_hybrid**: High-quality instrumental separation
- **Kim_Vocal_2**: Advanced vocal extraction  
- **bs_roformer**: Alternative model

## Examples

```bash
# Process album with full removal
uv run karaoke_maker -i "songs-tobeprocessed/thriller/" -o "songs-karaoke/thriller/" -r 1.0

# Practice tracks with light reduction
uv run karaoke_maker -i "songs-tobeprocessed/" -o "songs-karaoke/" -r 0.4

# Extract vocals for remixing
uv run karaoke_maker -i "songs-tobeprocessed/remix_source/" -o "songs-karaoke/vocals/" -r 0.8
```

## Troubleshooting

### uv not found
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# or: brew install uv | scoop install uv | pip install uv
```

### Dependencies
```bash
uv sync --all-extras
```

### Memory issues
- Ensure 8GB+ RAM available
- Process files individually for large batches

## Performance Tips
- Use FLAC for best quality
- Individual files better for memory management
- uv provides faster dependency resolution

## Architecture
- **uv**: Modern Python package manager
- **pyproject.toml**: Project configuration
- **karaoke_maker.py**: Main script with audio-separator

## License
This project uses audio-separator and AI models. Check respective licenses for usage terms.

## Contributing
Submit issues and enhancement requests!
