#!/usr/bin/env -S uv run
# /// script
# requires-python = "==3.13"
# dependencies = [
#     "flask==3.0.0",
#     "google-cloud-speech==2.26.0",
#     "requests",
#     "beautifulsoup4",
#     "jellyfish",
#     "mutagen",
#     "audio-separator>=0.39.0",
#     "torch>=2.3.0",
#     "torchaudio>=2.3.0",
#     "onnxruntime>=1.23.0",
# ]
# ///

import sys
import os
import json
import requests
import re
import urllib.parse
import html as html_entity
from bs4 import BeautifulSoup
import time
import argparse
import glob
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.flac import FLAC
from mutagen import File as MutagenFile

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_DIR = os.path.join(BASE_DIR, 'songs-karaoke')
JSON_PATH = os.path.join(BASE_DIR, 'songs.json')

# --- DEFAULT SONG DATA ---
DEFAULT_SONG = {
    "id": "merry_christmas",
    "title": "We Wish You A Merry Christmas",
    "artist": "Traditional",
    "filename": "merry_christmas.mp3",
    "url": "https://upload.wikimedia.org/wikipedia/commons/b/b7/We_Wish_you_a_Merry_Christmas_%28Kevin_MacLeod_%29_%28ISRC_USUAN1100369%29.oga",
    # Precise LRC Timings for Kevin MacLeod Version
    "lyrics": """[00:04.10] We wish you a Merry Christmas
[00:06.90] We wish you a Merry Christmas
[00:09.60] We wish you a Merry Christmas
[00:12.10] And a Happy New Year
[00:14.60] Good tidings we bring
[00:17.10] To you and your kin
[00:19.90] Good tidings for Christmas
[00:22.60] And a Happy New Year
[00:25.00] (Instrumental Break)
[00:35.60] Now bring us some figgy pudding
[00:38.10] Now bring us some figgy pudding
[00:40.90] Now bring us some figgy pudding
[00:43.60] And a cup of good cheer
[00:46.00] We won't go until we get some
[00:48.60] We won't go until we get some
[00:51.30] We won't go until we get some
[00:53.90] So bring it right here"""
}

GENERIC_LYRICS = """[00:10.00] (Instrumental Intro)
[00:15.00] Get ready to sing...
[00:20.00] (Waiting for lyrics...)
[00:25.00] Feel the rhythm!
[00:30.00] Sing your heart out!"""

def clean_filename(title):
    s = title.lower().replace(' ', '_')
    return re.sub(r'[^a-z0-9_]', '', s)

def clean_title(title, artist_arg=""):
    t = title.lower()
    if " - " in t: t = t.split(" - ")[0]
    
    remove_list = ["backing track", "guitar", "bass", "drum", "vocal", "karaoke", "version", 
                   "instrumental", "cover", "tribute", "hq", "demo", "remastered", "with click", 
                   "lyrics", "(", ")", "[", "]"]
    for word in remove_list: t = t.replace(word, "")
        
    if artist_arg:
        t = t.replace(artist_arg.lower(), "")
        for part in artist_arg.split():
            if len(part) > 3: t = t.replace(part.lower(), "")
    return " ".join(t.split()).title()

def fetch_synced_lyrics(artist, song_title, duration):
    print(f"      🔎 Lyrics: {artist} - {song_title} ...", end="")
    search_url = "https://lrclib.net/api/search"
    params = {'artist_name': artist, 'track_name': song_title}
    
    try:
        resp = requests.get(search_url, params=params, timeout=10)
        if resp.status_code != 200: return None
        data = resp.json()
        if not data: return None
        best_match = None
        best_diff = 9999
        for track in data:
            if not track.get('syncedLyrics'): continue
            diff = abs(track.get('duration', 0) - duration)
            if diff < best_diff:
                best_diff = diff
                best_match = track
        if best_match:
            print(f" ✅ Found!")
            return best_match['syncedLyrics']
        return None
    except: return None

def parse_lrc(lrc_text):
    lines = []
    regex = re.compile(r'\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)')
    for line in lrc_text.split('\n'):
        match = regex.match(line)
        if match:
            ts = (int(match.group(1)) * 60) + int(match.group(2)) + float(f"0.{match.group(3)}")
            text = match.group(4).strip()
            if text: lines.append({"time": ts, "text": text})
    return lines

def calculate_word_weights(words):
    """
    Calculates a 'weight' for each word to simulate natural singing rhythm.
    Short words are faster (lower weight). Long words are slower (higher weight).
    """
    weights = []
    total_weight = 0
    
    for word in words:
        length = len(word)
        weight = length
        
        # Rhythm heuristics
        if length <= 2: weight *= 0.6  # Fast small words (a, to, of)
        elif length <= 4: weight *= 0.9 # Normal short words
        elif length >= 8: weight *= 1.2 # Held long words
        
        weights.append(weight)
        total_weight += weight
        
    return weights, total_weight

def generate_lyrics_map(lrc_text, duration=None):
    parsed_lines = parse_lrc(lrc_text)
    if not parsed_lines and duration:
        return generate_heuristic_map(lrc_text, duration)
        
    if not parsed_lines: 
        parsed_lines = parse_lrc(GENERIC_LYRICS)

    lyrics_map = []
    for i, line in enumerate(parsed_lines):
        start_time = line['time']
        text = line['text']
        
        # Determine time available until next line
        if i < len(parsed_lines) - 1: 
            next_start = parsed_lines[i+1]['time']
            time_gap = next_start - start_time
        else: 
            time_gap = 4.0
            
        # VOCAL ACTIVITY DETECTION (VAD) SIMULATION
        # If the gap is huge (instrumental break), don't stretch lyrics across it.
        # Cap line duration at 4 seconds or reasonable reading speed
        words = text.split()
        if not words: continue
        
        estimated_needed_time = len(text) * 0.15 # approx 0.15s per char avg
        
        # Use the smaller of: Time until next line OR Estimated reading time + buffer
        # This creates pauses between lines instead of slow dragging
        line_duration = min(time_gap, estimated_needed_time + 1.0)
        
        # Apply Weighted Rhythm
        word_weights, total_weight = calculate_word_weights(words)
        if total_weight == 0: total_weight = 1
        
        time_per_weight_unit = line_duration / total_weight
        
        line_words_data = []
        word_cursor = start_time
        
        for idx, word in enumerate(words):
            # Duration based on linguistic weight
            w_dur = word_weights[idx] * time_per_weight_unit
            
            line_words_data.append({
                "text": word,
                "start": round(word_cursor, 2),
                "end": round(word_cursor + w_dur, 2)
            })
            word_cursor += w_dur

        lyrics_map.append({
            "time": round(start_time, 2),
            "text": text,
            "words": line_words_data
        })

    first_time = lyrics_map[0]['time'] if lyrics_map else 0
    return "\n".join(l['text'] for l in parsed_lines), lyrics_map, max(0, first_time - 4.0)

def generate_heuristic_map(text_block, duration):
    lines = [l.strip() for l in text_block.split('\n') if l.strip()]
    
    INTRO_OFFSET = 8.0 
    VOCAL_END = duration * 0.95
    
    available_time = max(0, VOCAL_END - INTRO_OFFSET)
    # Heuristic: Average line duration
    avg_line_dur = available_time / max(1, len(lines))
    
    lyrics_map = []
    current_time = INTRO_OFFSET
    LINE_GAP = 1.0 
    
    for line in lines:
        words = line.split()
        line_words_data = []
        word_cursor = current_time
        
        word_weights, total_weight = calculate_word_weights(words)
        if total_weight == 0: total_weight = 1
        
        time_per_unit = (avg_line_dur - LINE_GAP) / total_weight
        
        for idx, word in enumerate(words):
            w_dur = word_weights[idx] * time_per_unit
            line_words_data.append({
                "text": word,
                "start": round(word_cursor, 2),
                "end": round(word_cursor + w_dur, 2)
            })
            word_cursor += w_dur
            
        lyrics_map.append({
            "time": round(current_time, 2),
            "text": line,
            "words": line_words_data
        })
        current_time = word_cursor + LINE_GAP
        
    return "\n".join(lines), lyrics_map, INTRO_OFFSET

def scrape_bandcamp(url):
    print(f"   🔎 Connecting to Bandcamp...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200: 
            print(f"   ❌ HTTP {resp.status_code}")
            return []
        
        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        
        track_list = []
        tags = soup.find_all(attrs={"data-tralbum": True})
        for tag in tags:
            try:
                d = json.loads(html_entity.unescape(tag['data-tralbum']))
                if 'trackinfo' in d: 
                    track_list = d['trackinfo']
                    break
            except Exception as e:
                print(f"   ⚠️  JSON parse error: {e}")
        
        if not track_list:
            print(f"   ⚠️  No trackinfo found, trying regex fallback...")
            matches = re.finditer(r'title"?\s*:\s*"(.*?)".*?"?mp3-128"?\s*:\s*"(.*?)"', html, re.DOTALL)
            for m in matches:
                track_list.append({'title': m.group(1), 'file': {'mp3-128': m.group(2)}, 'duration': 180})
        
        processed = []
        for track in track_list:
            if not track.get('file') or not track['file'].get('mp3-128'): 
                print(f"   ⚠️  Skipping track (no file): {track.get('title', 'Unknown')}")
                continue
                
            processed.append({
                "title": track.get('title', 'Unknown'),
                "stream_url": track['file']['mp3-128'],
                "duration": float(track.get('duration', 180.0))
            })
        
        print(f"   ✅ Found {len(processed)} tracks")
        return processed
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []

def download_file(url, filepath, force=False):
    if os.path.exists(filepath) and not force:
        if "merry_christmas" in filepath and os.path.getsize(filepath) > 10000:
            print(f"   🎄 Default Song ready.")
            return True
        if "merry_christmas" not in filepath:
            print(f"      ✅ File exists. Skipping.")
            return True 
    
    if "merry_christmas" in filepath:
        print(f"   🎄 Downloading Default Song...")
    else:
        print(f"      ⬇️ Downloading...", end="")
        
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        with requests.get(url, stream=True, headers=headers, timeout=30) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
        if "merry_christmas" not in filepath: print(" ✅")
        return True
    except Exception as e:
        print(f" ❌ Failed: {e}")
        return False

def get_audio_duration(filepath):
    """Get duration of audio file in seconds using mutagen"""
    try:
        audio = MutagenFile(filepath)
        if audio is not None and hasattr(audio.info, 'length'):
            return float(audio.info.length)
    except Exception as e:
        print(f"      ⚠️  Could not read duration: {e}")
    return 180.0  # Default fallback

def get_audio_metadata(filepath):
    """Extract artist and title from audio file metadata"""
    try:
        audio = MutagenFile(filepath)
        if audio is None:
            return None, None
            
        artist = None
        title = None
        
        # Try different tag formats
        if isinstance(audio, MP3):
            artist = audio.get('TPE1', [None])[0] if 'TPE1' in audio else None
            title = audio.get('TIT2', [None])[0] if 'TIT2' in audio else None
        elif isinstance(audio, (OggVorbis, FLAC)):
            artist = audio.get('artist', [None])[0] if 'artist' in audio else None
            title = audio.get('title', [None])[0] if 'title' in audio else None
        else:
            # Generic tag reading
            artist = audio.get('artist', [None])[0] if 'artist' in audio else None
            title = audio.get('title', [None])[0] if 'title' in audio else None
            
        return artist, title
    except Exception as e:
        print(f"      ⚠️  Could not read metadata: {e}")
        return None, None

def copy_file_to_songs(source_path, dest_filename):
    """Copy audio file to songs directory, converting to mp3 if needed"""
    dest_path = os.path.join(SONGS_DIR, dest_filename)
    
    # If it's already an mp3, just copy it
    if source_path.lower().endswith('.mp3'):
        print(f"      📂 Copying file...", end="")
        try:
            import shutil
            shutil.copy2(source_path, dest_path)
            print(" ✅")
            return True
        except Exception as e:
            print(f" ❌ Failed: {e}")
            return False
    else:
        # For ogg/flac, we need to copy with the original extension
        # The karaoke app should handle different formats
        ext = os.path.splitext(source_path)[1]
        dest_path = dest_path.replace('.mp3', ext)
        print(f"      📂 Copying {ext} file...", end="")
        try:
            import shutil
            shutil.copy2(source_path, dest_path)
            print(" ✅")
            return dest_path
        except Exception as e:
            print(f" ❌ Failed: {e}")
            return False

def process_mixtape(mixtape_file, album_name=None):
    """Process mixtape from a CSV file with format: filename, songname, album, singer"""
    print(f"\n🎵 Processing mixtape from: {mixtape_file}")
    
    if not os.path.exists(mixtape_file):
        print(f"   ❌ Mixtape file not found: {mixtape_file}")
        return {}
    
    # Read CSV entries from mixtape file
    entries = []
    with open(mixtape_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse CSV: filename, songname, album, singer
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 4:
                print(f"   ⚠️  Line {line_num} invalid format (need: filename, songname, album, singer): {line}")
                continue
            
            file_path = parts[0]
            song_name = parts[1]
            album = parts[2]
            singer = parts[3]
            
            # Expand ~ and resolve relative paths
            file_path = os.path.expanduser(file_path)
            if not os.path.isabs(file_path):
                # Resolve relative to mixtape file location
                base_dir = os.path.dirname(os.path.abspath(mixtape_file))
                file_path = os.path.join(base_dir, file_path)
            
            if os.path.exists(file_path):
                entries.append({
                    'path': file_path,
                    'song_name': song_name,
                    'album': album,
                    'singer': singer
                })
            else:
                print(f"   ⚠️  File not found (skipping): {parts[0]}")
    
    if not entries:
        print(f"   ⚠️  No valid entries found in mixtape")
        return {}
    
    print(f"   📑 Found {len(entries)} songs in mixtape")
    
    json_entries = {}
    
    for entry in entries:
        audio_path = entry['path']
        song_name = entry['song_name']
        album = entry['album']
        singer = entry['singer']
        
        filename = os.path.basename(audio_path)
        print(f"\n   🎤 Processing: {filename}")
        print(f"      📝 Title: {song_name}")
        print(f"      🎙 Artist: {singer}")
        print(f"      💿 Album: {album}")
        
        # Get audio duration
        duration = get_audio_duration(audio_path)
        print(f"      ⏱️  Duration: {duration:.1f}s")
        
        # Generate file ID (include artist to avoid conflicts in mixtapes)
        file_id = clean_filename(f"{singer}_{song_name}")
        dest_filename = f"{file_id}.mp3"
        
        copied_path = copy_file_to_songs(audio_path, dest_filename)
        if copied_path:
            # Update filename to actual extension used
            if copied_path != True:
                dest_filename = os.path.basename(copied_path)
            
            # Try to fetch synced lyrics
            lrc = fetch_synced_lyrics(singer, song_name, duration)
            if lrc:
                clean_lyrics, lyrics_map, intro_offset = generate_lyrics_map(lrc)
            else:
                print("      ⚠️  Generic timing.")
                clean_lyrics, lyrics_map, intro_offset = generate_lyrics_map(GENERIC_LYRICS, duration)
            
            json_entries[file_id] = {
                "title": f"{singer} - {song_name}",
                "artist": singer,
                "filename": dest_filename,
                "lyrics": clean_lyrics,
                "lyrics_map": lyrics_map,
                "start_offset": intro_offset,
                "album": album
            }
    
    return json_entries

def process_local_files(directory, artist_name, album_name=None):
    """Process local audio files from a directory"""
    print(f"\n🎤 Processing local files from: {directory}")
    if artist_name:
        print(f"   🎙 Artist: {artist_name}")
    if album_name:
        print(f"   💿 Album: {album_name}")
    
    # Find all supported audio files
    audio_files = []
    for ext in ['*.mp3', '*.ogg', '*.flac']:
        audio_files.extend(glob.glob(os.path.join(directory, ext)))
        audio_files.extend(glob.glob(os.path.join(directory, ext.upper())))
    
    if not audio_files:
        print(f"   ⚠️  No audio files found in {directory}")
        return {}
    
    print(f"   📑 Found {len(audio_files)} audio files")
    
    json_entries = {}
    
    for audio_path in sorted(audio_files):
        filename = os.path.basename(audio_path)
        print(f"\n   🎤 Processing: {filename}")
        
        # Get metadata from file
        duration = get_audio_duration(audio_path)
        meta_artist, meta_title = get_audio_metadata(audio_path)
        
        # Use metadata or fallback to filename
        if meta_title:
            title = meta_title
        else:
            # Use filename without extension as title
            title = os.path.splitext(filename)[0]
            title = title.replace('_', ' ').replace('-', ' ')
        
        if meta_artist:
            artist = meta_artist
        elif artist_name:
            artist = artist_name
        else:
            artist = "Unknown Artist"
        
        # Clean title
        clean_name = clean_title(title, artist_arg=artist)
        print(f"      📝 Title: {clean_name}")
        print(f"      🎙 Artist: {artist}")
        print(f"      ⏱️  Duration: {duration:.1f}s")
        
        # Generate file ID and copy file
        file_id = clean_filename(clean_name)
        dest_filename = f"{file_id}.mp3"
        
        copied_path = copy_file_to_songs(audio_path, dest_filename)
        if copied_path:
            # Update filename to actual extension used
            if copied_path != True:
                dest_filename = os.path.basename(copied_path)
            
            # Try to fetch synced lyrics
            lrc = fetch_synced_lyrics(artist, clean_name, duration)
            if lrc:
                clean_lyrics, lyrics_map, intro_offset = generate_lyrics_map(lrc)
            else:
                print("      ⚠️  Generic timing.")
                clean_lyrics, lyrics_map, intro_offset = generate_lyrics_map(GENERIC_LYRICS, duration)
            
            json_entries[file_id] = {
                "title": f"{artist} - {clean_name}",
                "artist": artist,
                "filename": dest_filename,
                "lyrics": clean_lyrics,
                "lyrics_map": lyrics_map,
                "start_offset": intro_offset
            }
            
            if album_name:
                json_entries[file_id]["album"] = album_name
    
    return json_entries

def main():
    parser = argparse.ArgumentParser(
        description='Setup music for karaoke system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download from Bandcamp
  %(prog)s --bandcamp <url> --artist "Artist Name" --album "Album Name"
  
  # Process local files from directory
  %(prog)s --files /path/to/music --artist "Artist Name" --album "Album Name"
  
  # Process mixtape (CSV format with album/artist per song)
  %(prog)s --mixtape mixtape.txt
  
  # Legacy mode (deprecated)
  %(prog)s <bandcamp_url> "Artist Name"

Mixtape CSV format (filename, songname, album, singer):
  /path/to/song.mp3, Bohemian Rhapsody, Greatest Hits, Queen
  ~/Music/track.mp3, Stairway to Heaven, Rock Classics, Led Zeppelin
  
  Lines starting with # are comments. See mixtape_example.txt for details.
        """
    )
    
    parser.add_argument('--bandcamp', metavar='URL', 
                       help='Bandcamp URL to download mp3 files from')
    parser.add_argument('--files', metavar='DIR',
                       help='Directory containing local mp3/ogg/flac files')
    parser.add_argument('--mixtape', metavar='FILE',
                       help='CSV file with format: filename, songname, album, singer')
    parser.add_argument('--artist', metavar='NAME',
                       help='Artist name for the album')
    parser.add_argument('--album', metavar='NAME',
                       help='Album name (optional for --bandcamp/--files)')
    
    # Support legacy positional arguments for backward compatibility
    parser.add_argument('legacy_args', nargs='*',
                       help=argparse.SUPPRESS)
    
    args = parser.parse_args()
    
    if not os.path.exists(SONGS_DIR): 
        os.makedirs(SONGS_DIR, exist_ok=True)
    
    # --- 1. LOAD EXISTING DATABASE OR INITIALIZE ---
    if os.path.exists(JSON_PATH):
        print("📂 Loading existing songs database...")
        try:
            with open(JSON_PATH, 'r', encoding='utf-8') as f:
                json_db = json.load(f)
            print(f"   ✅ Loaded {len(json_db)} existing songs")
        except Exception as e:
            print(f"   ⚠️  Could not load existing database: {e}")
            json_db = {}
    else:
        json_db = {}
    
    # --- 2. ENSURE DEFAULT SONG EXISTS ---
    if DEFAULT_SONG['id'] not in json_db:
        print("🎄 Initializing Default Song...")
        default_path = os.path.join(SONGS_DIR, DEFAULT_SONG['filename'])
        download_file(DEFAULT_SONG['url'], default_path) 
        
        clean_lyrics, lyrics_map, intro_offset = generate_lyrics_map(DEFAULT_SONG['lyrics'], duration=120.0)
        
        json_db[DEFAULT_SONG['id']] = {
            "title": DEFAULT_SONG['title'],
            "artist": DEFAULT_SONG['artist'],
            "filename": DEFAULT_SONG['filename'],
            "lyrics": clean_lyrics,
            "lyrics_map": lyrics_map,
            "start_offset": intro_offset
        }
    else:
        print("🎄 Default song already in database")

    # --- 2. PROCESS NEW ARGUMENT STYLE ---
    if args.bandcamp or args.files or args.mixtape:
        if args.mixtape:
            # Process mixtape file (album is in the CSV, not from command line)
            entries = process_mixtape(args.mixtape)
            json_db.update(entries)
        
        elif args.bandcamp:
            # Download from Bandcamp
            if not args.artist:
                print("❌ Error: --artist is required when using --bandcamp")
                sys.exit(1)
            
            print(f"\n🚀 Bandcamp Download: {args.artist}")
            if args.album:
                print(f"   💿 Album: {args.album}")
            
            songs = scrape_bandcamp(args.bandcamp)
            
            for song in songs:
                clean_name = clean_title(song['title'], artist_arg=args.artist)
                print(f"\n   🎤 {args.artist} - {clean_name}")
                file_id = clean_filename(clean_name)
                local_path = os.path.join(SONGS_DIR, f"{file_id}.mp3")
                
                if download_file(song['stream_url'], local_path):
                    lrc = fetch_synced_lyrics(args.artist, clean_name, song['duration'])
                    if lrc:
                        clean_lyrics, lyrics_map, intro_offset = generate_lyrics_map(lrc)
                    else: 
                        print("      ⚠️  Generic timing.")
                        clean_lyrics, lyrics_map, intro_offset = generate_lyrics_map(GENERIC_LYRICS, song['duration'])
                    
                    json_db[file_id] = {
                        "title": f"{args.artist} - {clean_name}", 
                        "artist": args.artist,
                        "filename": f"{file_id}.mp3",
                        "lyrics": clean_lyrics,
                        "lyrics_map": lyrics_map,
                        "start_offset": intro_offset
                    }
                    
                    if args.album:
                        json_db[file_id]["album"] = args.album
                    
                    time.sleep(0.5)
        
        elif args.files:
            # Process local files
            if not os.path.exists(args.files):
                print(f"❌ Error: Directory not found: {args.files}")
                sys.exit(1)
            
            entries = process_local_files(args.files, args.artist, args.album)
            json_db.update(entries)
    
    # --- 3. LEGACY MODE SUPPORT (for backward compatibility) ---
    elif len(args.legacy_args) > 0:
        print("\n⚠️  Warning: Using legacy argument format. Consider using --bandcamp option.")
        if len(args.legacy_args) % 2 == 0:
            for i in range(0, len(args.legacy_args), 2):
                url = args.legacy_args[i]
                artist = args.legacy_args[i+1]
                print(f"\n🚀 Batch: {artist}")
                songs = scrape_bandcamp(url)
                
                for song in songs:
                    clean_name = clean_title(song['title'], artist_arg=artist)
                    print(f"\n   🎤 {artist} - {clean_name}")
                    file_id = clean_filename(clean_name)
                    local_path = os.path.join(SONGS_DIR, f"{file_id}.mp3")
                    
                    if download_file(song['stream_url'], local_path):
                        lrc = fetch_synced_lyrics(artist, clean_name, song['duration'])
                        if lrc:
                            clean_lyrics, lyrics_map, intro_offset = generate_lyrics_map(lrc)
                        else: 
                            print("      ⚠️  Generic timing.")
                            clean_lyrics, lyrics_map, intro_offset = generate_lyrics_map(GENERIC_LYRICS, song['duration'])
                        
                        json_db[file_id] = {
                            "title": f"{artist} - {clean_name}", 
                            "artist": artist,
                            "filename": f"{file_id}.mp3",
                            "lyrics": clean_lyrics,
                            "lyrics_map": lyrics_map,
                            "start_offset": intro_offset
                        }
                        time.sleep(0.5)

    # --- 4. SAVE ---
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(json_db, f, indent=2)
        
    print(f"\n✅ Setup Complete! {len(json_db)} songs available.")

if __name__ == "__main__":
    main()

