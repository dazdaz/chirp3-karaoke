# Chirp3-Karaoke Project Structure

This document explains the purpose of the main folders in the Chirp3-Karaoke project and how they work together to create a complete karaoke system.

## Core Folders

### `songs-karaoke/` - Ready-to-Use Karaoke Tracks
**Purpose**: Storage for processed audio files that are ready for karaoke playback
- Contains instrumental versions of songs with vocals removed or reduced
- Audio files are organized and ready for the web karaoke interface
- Files are processed and optimized for karaoke use
- Populated by the `setup_music.py` script when importing music
- Supports MP3, OGG, and FLAC formats

**Usage**:
- Source material for the karaoke web application
- Users can select from these tracks in the web interface
- Files are automatically indexed in `songs.json` metadata database

### `songs-tobeprocessed/` - Raw Audio Input Directory
**Purpose**: Temporary storage for original audio files awaiting karaoke processing
- Raw audio files that users want to convert to karaoke tracks
- Contains original songs before vocal removal/processing
- Processed by `karaoke_maker.py` to create instrumental versions
- Files are moved or copied from here to `songs-karaoke/` after processing

**Usage**:
- Place your original audio files here before running karaoke processing
- Run `karaoke_maker.py` to convert files to instrumental versions
- Files in this directory are the source material for vocal separation

## How They Work Together

1. **Input**: Users place original audio files in `songs-tobeprocessed/`
2. **Processing**: Run `karaoke_maker.py` to create instrumental versions
3. **Output**: Processed files move to `songs-karaoke/` for use in the karaoke app
4. **Web Interface**: Users select from `songs-karaoke/` files in the web karaoke interface

## Audio Processing Workflow

```
Original Audio → songs-tobeprocessed/ → karaoke_maker.py → songs-karaoke/ → Web Interface
```

## Supported File Types

Both directories support:
- **MP3**: Most common format, good compression
- **FLAC**: Lossless quality, larger file size
- **WAV**: Uncompressed, high quality
- **OGG**: Open-source format

## Best Practices

### For `songs-tobeprocessed/`:
- Use high-quality source files for best karaoke results
- Organize files in subdirectories by artist or album
- Remove files after successful processing to save space
- Keep backup copies of original files elsewhere

### For `songs-karaoke/`:
- These files are optimized for karaoke use
- Don't edit these files directly - reprocess from source if needed
- The system automatically manages these files through the setup process

## Integration with Scripts

- **`setup_music.py`**: Populates `songs-karaoke/` with music from various sources
- **`karaoke_maker.py`**: Processes files from `songs-tobeprocessed/` to create karaoke versions
- **`karaoke_maker.sh`**: Shell wrapper for easy karaoke processing

## Example Usage

```bash
# 1. Place original files in to-be-processed directory
cp ~/Music/original_song.flac songs-tobeprocessed/

# 2. Process for karaoke
./karaoke_maker.sh -i songs-tobeprocessed/ -o songs-karaoke/ -t instrumental

# 3. Files are now ready for karaoke use
# 4. Optional: Update the web interface database
python3 setup_music.py
```