# UVR-CLI Wrapper for macOS

A simplified wrapper script for Ultimate Vocal Remover CLI that makes it easier to extract instrumental tracks or vocals from audio files.

## Installation

### 1. Install Ultimate Vocal Remover

```bash
brew install --cask ultimate-vocal-remover
```

### 2. Make the wrapper executable

```bash
chmod +x uvr_wrapper.sh
```

## Features

- **Auto-detection**: Automatically detects file format (MP3/FLAC) from input
- **Smart model selection**: Auto-selects best model based on target (vocals/instrumental)
- **Batch processing**: Automatically handles single files or entire directories
- **Simple presets**: Use friendly names like `vocal-hq` instead of full model names
- **Color output**: Clear, colorful progress indicators
- **Error handling**: Checks for installation and validates inputs

## Usage

### Basic Usage

```bash
# Process single file (auto-detect everything)
./uvr_wrapper.sh -i "/path/to/song.mp3" -o "/path/to/output/"

# Process entire directory
./uvr_wrapper.sh -i "/Music/Songs/" -o "/Music/Instrumentals/"
```

### Advanced Usage

```bash
# Extract vocals with high-quality model
./uvr_wrapper.sh -i "/Music/Songs/" -o "/Music/Vocals/" -t vocals -m vocal-hq

# Process FLAC files with specific model
./uvr_wrapper.sh -i "/Music/album/" -o "/Music/karaoke/" -m demucs -f FLAC

# Process single file with custom model
./uvr_wrapper.sh -i "song.mp3" -o "output/" -m "Kim_Vocal_2"
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-i <path>` | Input file or directory (required) | - |
| `-o <path>` | Output directory (required) | - |
| `-m <model>` | Model preset or full name | Auto-selected |
| `-t <target>` | Target: `vocals` or `instrumental` | `instrumental` |
| `-f <format>` | Force format: `MP3` or `FLAC` | Auto-detected |
| `-h` | Show help message | - |

## Model Presets

| Preset | Full Model Name | Best For |
|--------|----------------|----------|
| `vocal-hq` | Kim_Vocal_2 | High-quality vocal extraction |
| `vocal-fast` | MDX23C-InstVoc HQ | Faster vocal separation |
| `instrumental` | Demucs_v4_hybrid | Instrumental extraction |
| `demucs` | Demucs_v4_hybrid | Same as instrumental |

You can also specify any UVR model name directly with the `-m` option.

## How It Works

### Auto-Detection Flow

1. **Format Detection**:
   - For single files: Checks file extension (.mp3 or .flac)
   - For directories: Finds first audio file and uses its format
   - Defaults to MP3 if unable to determine

2. **Model Selection**:
   - If `-t vocals` specified: Uses Kim_Vocal_2
   - If `-t instrumental` (default): Uses Demucs_v4_hybrid
   - Override with `-m` option for custom model

3. **Batch Mode**:
   - Automatically enabled for directory inputs
   - Uses `--batch` and `--recursive` flags
   - Processes all audio files in subdirectories

## Examples

### Create Karaoke Tracks

```bash
# Convert entire music library to instrumental tracks
./uvr_wrapper.sh \
  -i ~/Music/Collection/ \
  -o ~/Music/Karaoke/ \
  -m instrumental
```

### Extract Vocals for Acapella

```bash
# Extract vocals only with high quality
./uvr_wrapper.sh \
  -i ~/Music/Songs/ \
  -o ~/Music/Acapella/ \
  -t vocals \
  -m vocal-hq
```

### Process Single FLAC File

```bash
# High-quality FLAC processing
./uvr_wrapper.sh \
  -i "~/Music/song.flac" \
  -o "~/Music/output/" \
  -f FLAC
```

### Batch Process with Custom Model

```bash
# Use specific model for batch processing
./uvr_wrapper.sh \
  -i /Music/Archive/ \
  -o /Music/Instrumentals/ \
  -m "MDX-Net_Kim_Vocal_2"
```

## Integration with Karaoke Setup

You can use this script to prepare instrumental tracks before importing them into the karaoke system:

```bash
# Step 1: Extract instrumentals
./uvr_wrapper.sh \
  -i ~/Music/OriginalSongs/ \
  -o ~/Music/Instrumentals/

# Step 2: Import to karaoke system
python3 setup_music.py \
  --files ~/Music/Instrumentals/ \
  --artist "Various" \
  --album "Karaoke Collection"
```

## Troubleshooting

### UVR-CLI Not Found

```
Error: UVR-CLI not found at: /Applications/Ultimate Vocal Remover.app/...
Install with: brew install --cask ultimate-vocal-remover
```

**Solution**: Install Ultimate Vocal Remover using Homebrew

### Permission Denied

```
Permission denied: ./uvr_wrapper.sh
```

**Solution**: Make the script executable
```bash
chmod +x uvr_wrapper.sh
```

### No Audio Files Found

The script will detect the format based on files in the input directory. If no MP3 or FLAC files are found, it defaults to MP3.

### Processing Failed

Check the UVR-CLI output for specific error messages. Common issues:
- Invalid model name
- Insufficient disk space
- Corrupted input files

## Technical Details

### Script Location

The wrapper assumes UVR-CLI is installed at:
```
/Applications/Ultimate Vocal Remover.app/Contents/MacOS/UVR-CLI-macOS
```

### Supported Formats

- **Input**: MP3, FLAC
- **Output**: Same as input (or forced with `-f` option)

### Flags Passed to UVR-CLI

- `--no_gui`: Always runs in CLI mode
- `--batch`: Enabled for directory processing
- `--recursive`: Enabled for directory processing

## Notes

- The script always uses `--no_gui` mode for non-interactive processing
- Output files are saved with `_(Instrumental)` or `_(Vocals)` suffix
- Processing time depends on file size, format, and selected model
- Demucs models are generally slower but more accurate
- MDX models are faster but may have lower quality

## Related Documentation

- [Ultimate Vocal Remover GitHub](https://github.com/Anjok07/ultimatevocalremovergui/releases)
- [Music Setup Tool](README_MUSIC_SETUP.md)
- [Karaoke System README](README.md)

## License

This wrapper script is part of the chirp3-karaoke project.
