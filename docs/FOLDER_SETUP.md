# Folder Setup Guide

This guide explains how to properly set up and organize the music folders for the Chirp3-Karaoke system.

## Quick Setup

If these folders don't exist yet, create them:

```bash
# Create the main directories
mkdir -p songs-karaoke
mkdir -p songs-tobeprocessed

# Ensure proper permissions
chmod 755 songs-karaoke songs-tobeprocessed
```

## Folder Purposes Explained

### `songs-karaoke/` - Your Karaoke Music Library
**Purpose**: Final destination for all karaoke-ready audio files
- Contains processed instrumental tracks with vocals removed/reduced
- Files in this folder are directly accessible by the web karaoke interface
- Automatically indexed by `songs.json` metadata database
- Supports MP3, OGG, FLAC formats

**What goes here**:
- ✅ Instrumental versions of songs
- ✅ Processed karaoke tracks
- ✅ Files ready for immediate use in karaoke sessions

### `songs-tobeprocessed/` - Raw Audio Staging Area
**Purpose**: Temporary storage for original audio files awaiting karaoke processing
- Contains raw, original audio files before vocal separation
- Files here will be processed by `karaoke_maker.py` to create instrumental versions
- gitignored to prevent committing large audio files
- Should be cleaned up after processing

**What goes here**:
- ✅ Original song files (MP3, FLAC, WAV)
- ✅ Files awaiting vocal removal processing
- ✅ Temporary staging area

**What doesn't go here**:
- ❌ Already processed instrumental files
- ❌ Final karaoke tracks
- ❌ Files that should be permanently stored

## Workflow Examples

### Example 1: Process a New Album
```bash
# 1. Copy original album to processing folder
cp -r "/path/to/original/album/"* songs-tobeprocessed/

# 2. Process for karaoke (remove vocals)
./karaoke_maker.sh -i songs-tobeprocessed/ -o songs-karaoke/ -t instrumental

# 3. Clean up original files (optional)
rm songs-tobeprocessed/*

# 4. Update karaoke database
python3 setup_music.py
```

### Example 2: Import Bandcamp Album Directly
```bash
# Downloads directly to songs-karaoke (no processing folder needed)
python3 setup_music.py --bandcamp <album_url> --artist "Artist Name"
```

### Example 3: Import Local Music Collection
```bash
# Processes directory and puts results in songs-karaoke
python3 setup_music.py --files /path/to/music --artist "Various"
```

## Best Practices

### Organization Tips
- **Subdirectories**: You can create subdirectories within each folder for better organization
- **Naming**: Use descriptive filenames like "Artist - Title.flac"
- **Quality**: Use highest quality source files for best karaoke results

### Storage Management
- **songs-karaoke/**: These files are your permanent karaoke library
- **songs-tobeprocessed/**: Treat as temporary storage - clean up after processing
- **Backup**: Keep backups of original files elsewhere before placing in processing folder

### File Management
```bash
# Check folder sizes
du -sh songs-karaoke/ songs-tobeprocessed/

# List files in each folder
ls -la songs-karaoke/
ls -la songs-tobeprocessed/

# Clean up processing folder after use
find songs-tobeprocessed/ -type f -delete
```

## Integration with Scripts

The folders work seamlessly with the project's scripts:

- **`karaoke_maker.py`**: Reads from `songs-tobeprocessed/` → writes to `songs-karaoke/`
- **`setup_music.py`**: Reads from various sources → writes to `songs-karaoke/`
- **Web Interface**: Reads from `songs-karaoke/` for playback

## Troubleshooting

### Folder Not Found
```bash
# Create missing folders
mkdir -p songs-karaoke songs-tobeprocessed

# Verify creation
ls -ld songs-*/
```

### Permission Issues
```bash
# Fix permissions
chmod 755 songs-karaoke songs-tobeprocessed
chmod 644 songs-karaoke/* 2>/dev/null || true
```

### Disk Space
```bash
# Check usage
du -sh songs-*/

# Clean old files from processing folder
find songs-tobeprocessed/ -mtime +7 -delete
```

## Summary

- **`songs-karaoke/`** = Your permanent karaoke music library
- **`songs-tobeprocessed/`** = Temporary staging area for raw files
- Process raw files → move to karaoke folder → enjoy karaoke!
- Both folders are essential for the complete karaoke workflow