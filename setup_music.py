#!/usr/bin/env python3
import sys
import os
import json
import requests
import re
import urllib.parse
import html as html_entity
from bs4 import BeautifulSoup
import time

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_DIR = os.path.join(BASE_DIR, 'static', 'songs')
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
    return re.sub(r'[^a-z0-9_]', '', s) + ".mp3"

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
        if resp.status_code != 200: return []
        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        track_list = []
        tags = soup.find_all(attrs={"data-tralbum": True})
        for tag in tags:
            try:
                d = json.loads(html_entity.unescape(tag['data-tralbum']))
                if 'trackinfo' in d: track_list = d['trackinfo']; break
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
        return processed
    except: return []

def download_file(url, filepath, force=False):
    if os.path.exists(filepath) and not force:
        if "merry_christmas" in filepath and os.path.getsize(filepath) > 10000:
            print(f"   🎁 Default Song ready.")
            return True
        if "merry_christmas" not in filepath:
            print(f"      ✅ File exists. Skipping.")
            return True 
    
    if "merry_christmas" in filepath:
        print(f"   🎁 Downloading Default Song...")
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

def main():
    args = sys.argv[1:]
    
    if not os.path.exists(SONGS_DIR): os.makedirs(SONGS_DIR, exist_ok=True)
    
    # --- 1. INITIALIZE DEFAULT SONG ---
    print("🎄 Initializing Default Song...")
    default_path = os.path.join(SONGS_DIR, DEFAULT_SONG['filename'])
    download_file(DEFAULT_SONG['url'], default_path) 
    
    clean_lyrics, lyrics_map, intro_offset = generate_lyrics_map(DEFAULT_SONG['lyrics'], duration=120.0)
    
    json_db = {
        DEFAULT_SONG['id']: {
            "title": DEFAULT_SONG['title'],
            "artist": DEFAULT_SONG['artist'],
            "filename": DEFAULT_SONG['filename'],
            "lyrics": clean_lyrics,
            "lyrics_map": lyrics_map,
            "start_offset": intro_offset
        }
    }

    # --- 2. PROCESS ARGS ---
    if len(args) > 0 and len(args) % 2 == 0:
        for i in range(0, len(args), 2):
            url = args[i]
            artist = args[i+1]
            print(f"\n🚀 Batch: {artist}")
            songs = scrape_bandcamp(url)
            
            for song in songs:
                clean_name = clean_title(song['title'], artist_arg=artist)
                print(f"\n   🎵 {artist} - {clean_name}")
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

    # --- 3. SAVE ---
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(json_db, f, indent=2)
        
    print(f"\n✅ Setup Complete! {len(json_db)} songs available.")

if __name__ == "__main__":
    main()

