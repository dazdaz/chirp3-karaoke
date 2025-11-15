# Karaoke Maker - Enhanced UVR-CLI Wrapper

Create perfect karaoke tracks with full instrumental, guide vocals, or reduced vocals using Ultimate Vocal Remover.

## Installation

### 1. Install Ultimate Vocal Remover

```bash
brew install --cask ultimate-vocal-remover
```

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

### Script Location

Assumes UVR-CLI is installed at:
```
/Applications/Ultimate Vocal Remover.app/Contents/MacOS/UVR-CLI-macOS
```

### Output File Naming

- **Instrumental**: `filename_(Instrumental).ext`
- **Vocals**: `filename_(Vocals).ext`
- **Reduced Vocals**: `filename_(Reduced_Vocals).ext`

### Supported Formats

- **Input**: MP3, FLAC
- **Output**: Same as input (or forced with `-f`)

### Dependencies

- **UVR-CLI**: Vocal/instrumental separation
- **ffmpeg**: Audio mixing (required for reduced-vocals mode)

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
