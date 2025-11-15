# Chirp3-Karaoke Music Setup Tool

This tool helps you populate the karaoke system with music from multiple sources: Bandcamp downloads, local audio files, or mixtape collections.

## Features

- **Download from Bandcamp**: Automatically downloads MP3 tracks from Bandcamp album URLs
- **Import local files**: Process mp3, ogg, or flac files from a directory
- **Mixtape support**: Import collections with songs from different artists
- **Automatic lyrics sync**: Fetches synchronized lyrics from lrclib.net
- **Smart metadata**: Reads artist/title from file tags or filenames
- **Album organization**: Optional album tagging for all import modes
- **File management**: Skips existing files, preserves database entries
- **Format support**: Handles MP3, OGG, and FLAC audio files

## Usage

### Option 1: Download from Bandcamp

Download all tracks from a Bandcamp album:

```bash
python3 setup_music.py --bandcamp <url> --artist "Artist Name" [--album "Album Name"]
```

**Example:**
```bash
python3 setup_music.py --bandcamp https://palochebeatz.bandcamp.com/album/aerosmith-guitar-backing-tracks --artist "Aerosmith"
```

### Option 2: Import Local Audio Files

Process all audio files from a directory:

```bash
python3 setup_music.py --files /path/to/music [--artist "Artist Name"] [--album "Album Name"]
```

**Example:**
```bash
python3 setup_music.py --files ~/Music/BackingTracks --artist "Various" --album "Guitar Classics"
```

**Notes:**
- Supports mp3, ogg, and flac formats
- Reads artist/title from file metadata (ID3 tags) when available
- Falls back to filename if metadata is missing
- Artist parameter is optional (uses file metadata or "Unknown Artist")

### Option 3: Import Mixtape Collection

Import a collection of songs from different artists using a text file:

```bash
python3 setup_music.py --mixtape mixtape.txt --album "My Mixtape 2024"
```

**Mixtape file format** (one file path per line):
```
# My Favorite Songs - Comments start with #
/absolute/path/to/Queen - Bohemian Rhapsody.mp3
~/Music/Led Zeppelin - Stairway to Heaven.mp3
relative/path/to/Beatles - Hey Jude.mp3
```

**Notes:**
- Paths can be absolute or relative to the mixtape file location
- Artist info is read from file metadata or "Artist - Title" filename format
- Falls back to "Various Artists" if no artist info found
- All songs are grouped under the specified album name
- See `mixtape_example.txt` for more details

### Legacy Mode (Deprecated)

The old positional argument format still works for backward compatibility:

```bash
python3 setup_music.py <bandcamp_url> "Artist Name"
```

## Command-Line Options

| Option | Description |
|--------|-------------|
| `--bandcamp URL` | Bandcamp album URL to download |
| `--files DIR` | Directory containing local audio files |
| `--mixtape FILE` | Text file listing audio files for mixtape |
| `--artist NAME` | Artist name (required for --bandcamp) |
| `--album NAME` | Album name (optional, required for --mixtape) |
| `-h, --help` | Show help message with examples |

## How It Works

### Bandcamp Mode
1. Connects to Bandcamp and extracts track information
2. Downloads MP3 files with progress tracking
3. Fetches synchronized lyrics from lrclib.net
4. Updates songs.json with track metadata

### Local Files Mode
1. Scans directory for mp3/ogg/flac files
2. Reads metadata using mutagen library
3. Copies files to static/songs directory
4. Fetches synchronized lyrics
5. Updates songs.json with track information

### Mixtape Mode
1. Reads file paths from text file
2. Extracts artist/title from metadata or filename
3. Generates unique file IDs (includes artist name)
4. Copies files and fetches lyrics
5. Groups all tracks under specified album

## Automatic Lyrics Synchronization

The tool automatically fetches synchronized lyrics from lrclib.net for each track:

- Searches by artist and title
- Matches by duration for accuracy
- Falls back to generic timing if not found
- Timing includes word-level synchronization for karaoke display

## File Structure

```
chirp3-karaoke/
├── setup_music.py              # Main import script  
├── mixtape_example.txt         # Example mixtape file
├── songs.json                  # Track metadata database
├── artists.sh                  # Batch processing script
└── static/
    └── songs/                  # Audio files
        ├── artist_track.mp3
        └── ...
```

## Songs Database Format

Each track in `songs.json` contains:

```json
{
  "track_id": {
    "title": "Artist - Title",
    "artist": "Artist Name",
    "filename": "track_file.mp3",
    "lyrics": "Line 1\nLine 2\n...",
    "lyrics_map": [...],
    "start_offset": 4.0,
    "album": "Album Name"
  }
}
```

## Requirements

- Python 3.8 or higher
- Required packages (install with `pip3 install -r requirements.txt`):
  - requests
  - beautifulsoup4
  - mutagen
  - jellyfish

## Best Practices

### File Organization
- Keep backing tracks organized in directories by artist or genre
- Use descriptive filenames like "Artist - Title.mp3"
- Add ID3 tags to your files for best results

### Mixtape Files
- Use relative paths for portability
- Add comments to organize sections
- Group similar songs together

### Album Naming
- Use album names for organization (optional for most modes)
- Required for mixtapes to group diverse artists
- Helps filter songs in the karaoke interface

## Troubleshooting

### Bandcamp Issues
- **403 Errors with `uv run`**: Use `python3` directly instead
- **No tracks found**: Verify the URL is a valid Bandcamp album page
- **Download failures**: Check internet connection and retry

### File Import Issues
- **No metadata found**: Ensure files have ID3 tags or use "Artist - Title" filename format
- **Unsupported format**: Only mp3, ogg, and flac are supported
- **Permission errors**: Ensure write permissions to `static/songs` directory

### Lyrics Issues
- **Generic timing used**: Lyrics not found in lrclib.net database
- **Mismatched sync**: Duration mismatch between file and lyrics database
- **No lyrics**: Some tracks may not have synchronized lyrics available

## Examples

### Download multiple Bandcamp albums
```bash
# Can be automated with artists.sh
python3 ./setup_music.py --bandcamp https://example.bandcamp.com/album/album1 --artist "Artist 1"
python3 ./setup_music.py --bandcamp https://example.bandcamp.com/album/album2 --artist "Artist 2"
```

### Import a music directory
```bash
python3 ./setup_music.py --files ~/Downloads/KaraokeTracks --artist "Various" --album "Party Mix"
```

### Create a mixtape
```bash
# Create mixtape.txt with your song paths
python3 ./setup_music.py --mixtape my_favorites.txt --album "Best of 2024"
```

## Notes

- Downloads are for personal use only
- Respect artists' rights and Bandcamp's terms of service  
- The tool preserves existing songs and adds new ones
- Files are copied/downloaded, not moved
- songs.json is gitignored to avoid committing metadata
