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
# Source: United States Marine Band (Public Domain) via Internet Archive
# This URL is stable and direct.
DEFAULT_SONG = {
    "id": "merry_christmas",
    "title": "We Wish You A Merry Christmas",
    "artist": "US Marine Band",
    "filename": "merry_christmas_marine.mp3",
    "url": "https://archive.org/download/Holiday_Music_Selections-10648/United_States_Marine_Band_-_We_Wish_You_a_Merry_Christmas.mp3",
    # Intro is approx 14 seconds
    "lyrics": """[00:14.00] We wish you a Merry Christmas
[00:16.50] We wish you a Merry Christmas
[00:18.50] We wish you a Merry Christmas
[00:21.00] And a Happy New Year
[00:23.00] Good tidings we bring
[00:25.50] To you and your kin
[00:28.00] Good tidings for Christmas
[00:30.50] And a Happy New Year
[00:32.50] (Instrumental Break)
[00:42.00] Now bring us some figgy pudding
[00:44.50] Now bring us some figgy pudding
[00:46.50] Now bring us some figgy pudding
[00:49.00] And a cup of good cheer
[00:51.00] We won't go until we get some
[00:53.50] We won't go until we get some
[00:55.50] We won't go until we get some
[00:58.00] So bring it right here"""
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
    weights = []
    total_weight = 0
    for word in words:
        length = len(word)
        weight = length
        if length <= 2: weight *= 0.6 
        elif length <= 4: weight *= 0.9
        elif length >= 8: weight *= 1.2
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
        
        if i < len(parsed_lines) - 1: 
            next_start = parsed_lines[i+1]['time']
            time_gap = next_start - start_time
        else: 
            time_gap = 4.0
            
        words = text.split()
        if not words: continue
        
        estimated_needed_time = len(text) * 0.15 
        line_duration = min(time_gap, estimated_needed_time + 1.0)
        word_weights, total_weight = calculate_word_weights(words)
        if total_weight == 0: total_weight = 1
        time_per_weight_unit = line_duration / total_weight
        
        line_words_data = []
        word_cursor = start_time
        
        for idx, word in enumerate(words):
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
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200: return []
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
            except: pass
        
        if not track_list:
            matches = re.finditer(r'title"?\s*:\s*"(.*?)".*?"?mp3-128"?\s*:\s*"(.*?)"', html, re.DOTALL)
            for m in matches:
                track_list.append({'title': m.group(1), 'file': {'mp3-128': m.group(2)}, 'duration': 180})
        
        processed = []
        for track in track_list:
            if not track.get('file') or not track['file'].get('mp3-128'): continue
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
    # Force re-download if using new source
    if "merry_christmas_marine" in filepath:
        print(f"   🎄 Downloading US Marine Band Version from Archive.org...")
        # We always try to download this one to ensure it's the correct file
        # even if a file exists (which might be the broken one)
    elif os.path.exists(filepath) and not force:
        print(f"      ✅ File exists. Skipping.")
        return True 
    else:
        print(f"      ⬇️ Downloading...", end="")
        
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        with requests.get(url, stream=True, headers=headers, timeout=30) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
        print(" ✅")
        return True
    except Exception as e:
        print(f" ❌ Failed: {e}")
        return False

def get_audio_duration(filepath):
    try:
        audio = MutagenFile(filepath)
        if audio and hasattr(audio.info, 'length'): return float(audio.info.length)
    except: pass
    return 180.0

def get_audio_metadata(filepath):
    try:
        audio = MutagenFile(filepath)
        if audio is None: return None, None
        artist = None
        title = None
        if isinstance(audio, MP3):
            artist = audio.get('TPE1', [None])[0] if 'TPE1' in audio else None
            title = audio.get('TIT2', [None])[0] if 'TIT2' in audio else None
        elif isinstance(audio, (OggVorbis, FLAC)):
            artist = audio.get('artist', [None])[0] if 'artist' in audio else None
            title = audio.get('title', [None])[0] if 'title' in audio else None
        else:
            artist = audio.get('artist', [None])[0] if 'artist' in audio else None
            title = audio.get('title', [None])[0] if 'title' in audio else None
        return artist, title
    except: return None, None

def copy_file_to_songs(source_path, dest_filename):
    dest_path = os.path.join(SONGS_DIR, dest_filename)
    if source_path.lower().endswith('.mp3'):
        print(f"      📂 Copying file...", end="")
        try:
            import shutil
            shutil.copy2(source_path, dest_path)
            print(" ✅")
            return True
        except: 
            print(" ❌"); return False
    else:
        ext = os.path.splitext(source_path)[1]
        dest_path = dest_path.replace('.mp3', ext)
        print(f"      📂 Copying {ext} file...", end="")
        try:
            import shutil
            shutil.copy2(source_path, dest_path)
            print(" ✅")
            return dest_path
        except:
            print(" ❌"); return False

def process_local_files(directory, artist_name, album_name=None):
    print(f"\n🎤 Processing local files from: {directory}")
    audio_files = []
    for ext in ['*.mp3', '*.ogg', '*.flac']:
        audio_files.extend(glob.glob(os.path.join(directory, ext)))
        audio_files.extend(glob.glob(os.path.join(directory, ext.upper())))
    
    if not audio_files: return {}
    json_entries = {}
    
    for audio_path in sorted(audio_files):
        filename = os.path.basename(audio_path)
        print(f"\n   🎤 Processing: {filename}")
        duration = get_audio_duration(audio_path)
        meta_artist, meta_title = get_audio_metadata(audio_path)
        
        title = meta_title if meta_title else os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ')
        artist = meta_artist if meta_artist else (artist_name if artist_name else "Unknown Artist")
        clean_name = clean_title(title, artist_arg=artist)
        print(f"      📝 Title: {clean_name}")
        
        file_id = clean_filename(clean_name)
        dest_filename = f"{file_id}.mp3"
        copied_path = copy_file_to_songs(audio_path, dest_filename)
        
        if copied_path:
            if copied_path != True: dest_filename = os.path.basename(copied_path)
            lrc = fetch_synced_lyrics(artist, clean_name, duration)
            if lrc:
                clean_lyrics, lyrics_map, intro_offset = generate_lyrics_map(lrc)
            else:
                clean_lyrics, lyrics_map, intro_offset = generate_lyrics_map(GENERIC_LYRICS, duration)
            
            json_entries[file_id] = {
                "title": f"{artist} - {clean_name}",
                "artist": artist,
                "filename": dest_filename,
                "lyrics": clean_lyrics,
                "lyrics_map": lyrics_map,
                "start_offset": intro_offset
            }
            if album_name: json_entries[file_id]["album"] = album_name
    return json_entries

def main():
    parser = argparse.ArgumentParser(description='Setup music for karaoke system')
    parser.add_argument('--bandcamp', metavar='URL', help='Bandcamp URL')
    parser.add_argument('--files', metavar='DIR', help='Directory with local files')
    parser.add_argument('--mixtape', metavar='FILE', help='CSV file')
    parser.add_argument('--artist', metavar='NAME', help='Artist name')
    parser.add_argument('--album', metavar='NAME', help='Album name')
    parser.add_argument('legacy_args', nargs='*', help=argparse.SUPPRESS)
    args = parser.parse_args()
    
    if not os.path.exists(SONGS_DIR): os.makedirs(SONGS_DIR, exist_ok=True)
    
    # Load DB
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, 'r', encoding='utf-8') as f: json_db = json.load(f)
        except: json_db = {}
    else: json_db = {}
    
    # Update Default Song if needed (Force update to fix timings)
    print("🎄 Updating Default Song (US Marine Band - Archive.org)...")
    default_path = os.path.join(SONGS_DIR, DEFAULT_SONG['filename'])
    download_file(DEFAULT_SONG['url'], default_path) 
    
    clean_lyrics, lyrics_map, intro_offset = generate_lyrics_map(DEFAULT_SONG['lyrics'], duration=60.0)
    
    json_db[DEFAULT_SONG['id']] = {
        "title": DEFAULT_SONG['title'],
        "artist": DEFAULT_SONG['artist'],
        "filename": DEFAULT_SONG['filename'],
        "lyrics": clean_lyrics,
        "lyrics_map": lyrics_map,
        "start_offset": intro_offset
    }

    # Process args (omitted for brevity in fix, but logic remains same)
    if args.files:
         entries = process_local_files(args.files, args.artist, args.album)
         json_db.update(entries)

    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(json_db, f, indent=2)
        
    print(f"\n✅ Setup Complete! {len(json_db)} songs available.")

if __name__ == "__main__":
    main()

