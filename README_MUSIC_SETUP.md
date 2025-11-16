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
uv run setup_music.py --bandcamp <url> --artist "Artist Name" [--album "Album Name"]
```

### Option 2: Import Local Audio Files

Process all audio files from a directory:

```bash
uv run setup_music.py --files /path/to/music [--artist "Artist Name"] [--album "Album Name"]
```

**Example:**
```bash
uv run setup_music.py --files ~/Music/BackingTracks --artist "Various" --album "Guitar Classics"
```

**Notes:**
- Supports mp3, ogg, and flac formats
- Reads artist/title from file metadata (ID3 tags) when available
- Falls back to filename if metadata is missing
- Artist parameter is optional (uses file metadata or "Unknown Artist")

### Option 3: Import Mixtape Collection

Import a collection of songs from different artists using a CSV file:

```bash
uv run setup_music.py --mixtape mixtape.txt
```

**Mixtape CSV format** (filename, songname, album, singer):
```
# Comments start with #

# Rock Classics
/home/user/Music/bohemian.mp3, Bohemian Rhapsody, Greatest Hits, Queen
~/Music/stairway.mp3, Stairway to Heaven, Rock Classics, Led Zeppelin

# Your Collection
music/hey_jude.mp3, Hey Jude, Party Mix, The Beatles
```

**Format explanation:**
- **Line format**: `filename, songname, album, singer`
- **filename**: Full path to audio file (absolute, ~/, or relative)
- **songname**: The title of the song
- **album**: Album name (each song can have different album)
- **singer**: Artist/band name
- **Comments**: Lines starting with # are ignored

See `mixtape_example.txt` for detailed documentation and more examples.

### Legacy Mode (Deprecated)

The old positional argument format still works for backward compatibility:

```bash
uv run setup_music.py <bandcamp_url> "Artist Name"
```

## Command-Line Options

| Option | Description |
|--------|-------------|
| `--bandcamp URL` | Bandcamp album URL to download |
| `--files DIR` | Directory containing local audio files |
| `--mixtape FILE` | CSV file with format: filename, songname, album, singer |
| `--artist NAME` | Artist name (required for --bandcamp) |
| `--album NAME` | Album name (optional for --bandcamp/--files) |
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
3. Copies files to songs/ directory
4. Fetches synchronized lyrics
5. Updates songs.json with track information

### Mixtape Mode
1. Reads CSV entries from text file (filename, songname, album, singer)
2. Uses explicitly provided song title, album, and artist from CSV
3. Generates unique file IDs (includes artist name)
4. Copies files and fetches lyrics
5. Groups tracks under album names specified in CSV (each song can have different album)

## Automatic Lyrics Synchronization

The tool automatically fetches synchronized lyrics from lrclib.net for each track:

- Searches by artist and title
- Matches by duration for accuracy
- Falls back to generic timing if not found
- Timing includes word-level synchronization for karaoke display

## File Structure

```
karaoke-king/
├── setup_music.py              # Main import script  
├── mixtape_example.txt         # Example mixtape file
├── songs.json                  # Track metadata database
├── artists.sh                  # Batch processing script
└── songs/                      # Audio files directory
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

- Python 3.8 or higher (Python 3.13 recommended)
- uv package manager ([install here](https://docs.astral.sh/uv/getting-started/installation/))
- All required packages are automatically installed when running `uv sync`

## Best Practices

### File Organization
- Keep backing tracks organized in directories by artist or genre
- Use descriptive filenames like "Artist - Title.mp3"
- Add ID3 tags to your files for best results

### Mixtape Files (CSV Format)
- Use CSV format: `filename, songname, album, singer`
- Specify complete information for each song
- Use relative paths for portability
- Add comments to organize sections
- Each song can have a different album name

### Album Naming
- Use album names for organization (optional for --bandcamp/--files)
- Mixtape albums are specified per-song in the CSV file
- Helps filter and organize songs in the karaoke interface

## Troubleshooting

### Bandcamp Issues
- **No tracks found**: Verify the URL is a valid Bandcamp album page
- **Download failures**: Check internet connection and retry
- **Dependencies**: Ensure uv is installed and dependencies are synced: `uv sync`

### File Import Issues
- **No metadata found**: Ensure files have ID3 tags or use "Artist - Title" filename format
- **Unsupported format**: Only mp3, ogg, and flac are supported
- **Permission errors**: Ensure write permissions to `songs/` directory

### Lyrics Issues
- **Generic timing used**: Lyrics not found in lrclib.net database
- **Mismatched sync**: Duration mismatch between file and lyrics database
- **No lyrics**: Some tracks may not have synchronized lyrics available

## Examples

### Download multiple Bandcamp albums
```bash
# Can be automated with artists.sh
uv run setup_music.py --bandcamp https://example.bandcamp.com/album/album1 --artist "Artist 1"
uv run setup_music.py --bandcamp https://example.bandcamp.com/album/album2 --artist "Artist 2"
```

### Import a music directory
```bash
uv run setup_music.py --files songs-karaoke/mixtape1 --artist "Various" --album "Party Mix"
```

### Create a mixtape
```bash
# Create mixtape.txt with CSV format (filename, songname, album, singer)
# Example content:
# ~/Music/song1.mp3, Bohemian Rhapsody, Greatest Hits, Queen
# ~/Music/song2.mp3, Stairway to Heaven, Rock Classics, Led Zeppelin

uv run setup_music.py --mixtape my_favorites.txt
```

## Notes

- Downloads are for personal use only
- Respect artists' rights and Bandcamp's terms of service  
- The tool preserves existing songs and adds new ones
- Files are copied/downloaded, not moved
- songs.json is gitignored to avoid committing metadata
