# Karaoke Maker - UVR CLI Wrapper

Create perfect karaoke tracks with full instrumental, guide vocals, or reduced vocals using Ultimate Vocal Remover in CLI mode.

> **Important Note:** There is no separate `uvr-cli` package. The Ultimate Vocal Remover GUI application includes full CLI support via command-line arguments. This script uses the UVR executable in CLI mode with the `--no_gui` flag.

## Installation

### 1. Install Ultimate Vocal Remover

```bash
brew install --cask ultimate-vocal-remover
```

This installs the UVR executable at `/Applications/Ultimate Vocal Remover.app/Contents/MacOS/UVR` which supports both GUI and CLI modes.

### 2. Install ffmpeg (Required for reduced-vocals mode)

```bash
brew install ffmpeg
```

### 3. Make the script executable

```bash
chmod +x karaoke_maker.sh
```

## Features

- **Auto-detection**: Automatically detects file format (MP3/FLAC) from input
- **Smart model selection**: Auto-selects best model based on target
- **Batch processing**: Handles single files or entire directories
- **Simple presets**: Use friendly names instead of full model names
- **Color output**: Clear progress indicators
- **Three modes**: Full instrumental, vocals only, or reduced vocals
- **🆕 Reduced Vocals**: Mix instrumental with quiet guide vocals for easier singing!

## Usage Modes

### Mode 1: Full Instrumental (No Vocals)

Perfect for karaoke experts who don't need guide vocals:

```bash
./karaoke_maker.sh -i song.mp3 -o output/
```

### Mode 2: Reduced Vocals (Guide Vocals)

**NEW!** Keep quiet vocals in the background to help singers stay on track:

```bash
# 30% vocal volume (default, balanced)
./karaoke_maker.sh -i song.mp3 -o output/ -t reduced-vocals

# 20% vocal volume (soft guide)
./karaoke_maker.sh -i song.mp3 -o output/ -t reduced-vocals -v 0.2

# 40% vocal volume (more pronounced)
./karaoke_maker.sh -i song.mp3 -o output/ -t reduced-vocals -v 0.4
```

### Mode 3: Vocals Only

Extract vocals for practice or remixing:

```bash
./karaoke_maker.sh -i song.mp3 -o output/ -t vocals
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-i <path>` | Input file or directory (required) | - |
| `-o <path>` | Output directory (required) | - |
| `-t <target>` | Target: `instrumental`, `vocals`, or `reduced-vocals` | `instrumental` |
| `-v <volume>` | Vocal volume for reduced-vocals (0.0-1.0) | `0.3` |
| `-m <model>` | Model preset or full name | Auto-selected |
| `-f <format>` | Force format: `MP3` or `FLAC` | Auto-detected |
| `-h` | Show help message | - |

## Target Modes Explained

| Mode | Output | Best For |
|------|--------|----------|
| `instrumental` | Pure instrumental, no vocals | Experienced singers, practice tracks |
| `reduced-vocals` | Instrumental + quiet guide vocals | Learning new songs, staying on pitch |
| `vocals` | Vocals only | Acapella practice, vocal analysis |

## Vocal Volume Guide

For `reduced-vocals` mode, typical volumes:

| Volume | Description | Use Case |
|--------|-------------|----------|
| `0.1-0.2` | Very soft guide | Minimal assistance, almost instrumental |
| `0.3` | Balanced (default) | Good mix of guide and independence |
| `0.4-0.5` | Pronounced guide | Learning new songs, complex melodies |
| `0.6+` | Strong guide | Maximum vocal assistance |

## Model Presets

| Preset | Full Model Name | Best For |
|--------|----------------|----------|
| `vocal-hq` | Kim_Vocal_2 | High-quality vocal extraction |
| `vocal-fast` | MDX23C-InstVoc HQ | Faster processing |
| `instrumental` | Demucs_v4_hybrid | Instrumental extraction |
| `demucs` | Demucs_v4_hybrid | Same as instrumental |

## Examples

### Create Karaoke with Guide Vocals

```bash
# Process entire music library with 30% guide vocals
./karaoke_maker.sh \
  -i ~/Music/Collection/ \
  -o ~/Music/Karaoke/ \
  -t reduced-vocals
```

### Batch Process with Custom Vocal Level

```bash
# Process folder with 25% guide vocals
./karaoke_maker.sh \
  -i /Music/NewSongs/ \
  -o /Music/Karaoke-Guide/ \
  -t reduced-vocals \
  -v 0.25
```

### Create Pure Instrumental Tracks

```bash
# No vocals at all
./karaoke_maker.sh \
  -i ~/Music/Songs/ \
  -o ~/Music/Instrumentals/ \
  -t instrumental
```

### Extract Vocals for Practice

```bash
# Vocals only for acapella practice
./karaoke_maker.sh \
  -i song.flac \
  -o output/ \
  -t vocals \
  -m vocal-hq
```

## How It Works

### Reduced-Vocals Mode (3-Step Process)

When you use `-t reduced-vocals`:

1. **Extract Instrumental**: Uses UVR-CLI to separate the instrumental track
2. **Extract Vocals**: Extracts the vocal track separately  
3. **Mix with ffmpeg**: Combines instrumental (100%) + vocals (reduced volume)

The result is saved as `filename_(Reduced_Vocals).mp3`

### Standard Modes

For `instrumental` or `vocals` modes, it simply runs UVR-CLI with the appropriate model.

## Integration with Karaoke Setup

Perfect workflow for creating karaoke tracks:

```bash
# Step 1: Create guide vocal tracks
./karaoke_maker.sh \
  -i ~/Music/OriginalSongs/ \
  -o ~/Music/ForKaraoke/ \
  -t reduced-vocals \
  -v 0.3

# Step 2: Import to karaoke system
python3 setup_music.py \
  --files ~/Music/ForKaraoke/ \
  --artist "Various" \
  --album "Karaoke Collection"
```

## Troubleshooting

### UVR-CLI Not Found

```
Error: UVR-CLI not found
```

**Solution**: 
```bash
brew install --cask ultimate-vocal-remover
```

### ffmpeg Not Found

```
Error: ffmpeg is required for reduced-vocals mode
```

**Solution**:
```bash
brew install ffmpeg
```

### Permission Denied

```
Permission denied: ./karaoke_maker.sh
```

**Solution**:
```bash
chmod +x karaoke_maker.sh
```

### Mixing Failed

If ffmpeg mixing fails:
- Check that both vocal and instrumental files were created
- Ensure sufficient disk space
- Try with a different vocal volume

## Technical Details

### UVR Executable Location

The script uses the UVR executable in CLI mode, installed at:
```
/Applications/Ultimate Vocal Remover.app/Contents/MacOS/UVR
```

**Important:** This is NOT a separate CLI tool - it's the same UVR application that can run in both GUI and CLI modes.

### CLI Arguments Used

The script invokes UVR with the following arguments for CLI mode:
- `-i <input>`: Input file or directory
- `-o <output>`: Output directory  
- `-m <model>`: Model name for separation
- `-f <format>`: Output format (MP3 or FLAC)
- `--no_gui`: Run in CLI mode without opening the GUI

### Output File Naming

- **Instrumental**: `filename_(Instrumental).ext`
- **Vocals**: `filename_(Vocals).ext`
- **Reduced Vocals**: `filename_(Reduced_Vocals).ext`

### Supported Formats

- **Input**: MP3, FLAC
- **Output**: Same as input (or forced with `-f`)

### Dependencies

- **UVR (Ultimate Vocal Remover)**: Vocal/instrumental separation engine (supports CLI mode)
- **ffmpeg**: Audio mixing (required for reduced-vocals mode)

### About UVR CLI Mode

The Ultimate Vocal Remover application is primarily a GUI tool but fully supports CLI operation through command-line arguments. This script leverages that CLI capability to automate batch processing and create custom karaoke tracks. There is no separate `uvr-cli` package to install.

## Advanced Usage

### Custom Model Names

Use full UVR model names directly:

```bash
./karaoke_maker.sh \
  -i song.mp3 \
  -o output/ \
  -m "MDX-Net_Kim_Vocal_2" \
  -t reduced-vocals
```

### Process FLAC with High Quality

```bash
./karaoke_maker.sh \
  -i ~/Music/FLAC/ \
  -o ~/Music/Karaoke-FLAC/ \
  -t reduced-vocals \
  -v 0.35 \
  -f FLAC
```

## Tips for Best Results

### Vocal Volume Selection

- **Learning**: Start with 0.4-0.5 for new songs
- **Practice**: Use 0.2-0.3 as you improve
- **Performance**: Try 0.1-0.2 or pure instrumental

### Model Selection

- Use `vocal-hq` for best separation quality
- Use `vocal-fast` when processing large batches
- Use `demucs` for complex instrumentation

### Batch Processing

- Process similar songs together
- Keep original files as backup
- Use consistent vocal volume for albums

## Related Documentation

- [Ultimate Vocal Remover GitHub](https://github.com/Anjok07/ultimatevocalremovergui/releases)
- [Music Setup Tool](README_MUSIC_SETUP.md)
- [Karaoke System README](README.md)

## License

This script is part of the chirp3-karaoke project.

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

The recommended setup simply installs audio-separator system-wide via `pip3`. This gives instant access to audio-separator for any number of karaoke projects in any directory, regardless of the location of the karaoke-maker script. Additionally, it uses `--break-system-packages` to ensure Python 3.13 modules are installed, provided your system is using Python 3.13 or higher.

#### Using a Virtual Environment

For stricter environment management and isolation, activate a project-specific virtual environment:
```bash
# Create virtual environment and enter it
python3.13 -m venv venv_py313
source venv_py313/bin/activate

# Install dependencies
pip install audio-separator
```

You would then use
[ Karaoke Maker - Python Version

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

The recommended setup simply installs audio-separator system-wide via `pip3`. This gives instant access to audio-separator for any number of karaoke projects in any directory, regardless of the location of the karaoke-maker script. Additionally, it uses `--break-system-packages` to ensure Python 3.13 modules are installed, provided your system is using Python 3.13 or higher.

#### Using a Virtual Environment

For stricter environment management and isolation, activate a project-specific virtual environment:
```bash
# Create virtual environment and enter it
python3.13 -m venv venv_py313
source venv_py313/bin/activate

# Install dependencies
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
