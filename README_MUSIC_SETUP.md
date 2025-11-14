# Chirp3 Music Setup Tool

This tool allows you to download MP3 files from Bandcamp URLs and populate the `static/songs` directory for use with Chirp3.

## Features

- **Download entire Bandcamp albums**: Automatically extracts and downloads all MP3 tracks from any Bandcamp album URL
- **Smart file management**: Skips existing files to avoid re-downloading
- **Rich metadata**: Automatically captures track titles, artist, album, duration, and source URL
- **Progress tracking**: Shows download progress with file sizes and completion percentages
- **Error handling**: Robust retry logic for network issues
- **Database integration**: Automatically updates `songs.json` with new track information

## Usage

### Download a Bandcamp Album

```bash
python3 setup_music.py <bandcamp_album_url>
```

**Example:**
```bash
python3 setup_music.py https://palochebeatz.bandcamp.com/album/ozzy-osbourne-guitar-backing-tracks
```

### List Current Songs

```bash
python3 setup_music.py --list
```

This shows all songs in the database with their file status (✅ = file exists, ❌ = file missing).

### Clear All Songs

```bash
python3 setup_music.py --clear
```

This removes all downloaded files and resets the songs database.

## How It Works

1. **URL Validation**: Ensures the URL is from bandcamp.com
2. **Page Scraping**: Extracts track information from the Bandcamp page's embedded JSON data
3. **MP3 Download**: Downloads each track with progress tracking and retry logic
4. **File Management**: Creates safe filenames and handles duplicates
5. **Database Update**: Updates `songs.json` with track metadata

## File Structure

```
chirp3/
├── setup_music.py          # Main script
├── songs.json              # Track metadata database
└── static/
    └── songs/              # Downloaded MP3 files
        ├── track_1.mp3
        ├── track_2.mp3
        └── ...
```

## Songs Database Format

Each track in `songs.json` contains:

```json
{
  "track_id": {
    "title": "Track Title",
    "filename": "track_filename.mp3",
    "lyrics": "",
    "lyrics_map": [],
    "duration": 258.926,
    "artist": "Artist Name",
    "album": "Album Name",
    "source_url": "https://bandcamp.com/album/..."
  }
}
```

## Supported URLs

The tool works with any Bandcamp album URL in the format:
- `https://artist.bandcamp.com/album/album-name`
- `https://bandcamp.com/artist/album/album-name`

## Error Handling

- **Network issues**: Automatic retries with exponential backoff
- **Invalid URLs**: Validation to ensure only Bandcamp URLs are processed
- **Missing tracks**: Continues downloading other tracks if one fails
- **File permissions**: Handles filesystem permission issues gracefully

## Requirements

- Python 3.x
- Standard library modules only (no external dependencies)
- Internet connection for downloading

## Notes

- Downloads are for personal use only
- Respect artists' rights and Bandcamp's terms of service
- Some tracks may not be downloadable due to artist restrictions
- The tool preserves existing songs and adds new ones to the database

## Troubleshooting

### "No tracks found" error
- Verify the URL is a valid Bandcamp album page
- Check if the album has downloadable tracks
- Ensure you're not trying to download from a private/restricted album

### Download failures
- Check your internet connection
- Some tracks may have download restrictions
- Try running the command again (it will skip existing files)

### File permission errors
- Ensure the script has write permissions to the `static/songs` directory
- On some systems, you may need to run with appropriate permissions
