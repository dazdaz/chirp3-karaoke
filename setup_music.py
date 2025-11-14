#!/usr/bin/env python3
"""
Bandcamp Music Downloader for Chirp3
Downloads MP3 files from Bandcamp URLs and populates static/songs directory
"""

import json
import os
import re
import shutil
import sys
import ssl
import urllib.request
import time
import html
from urllib.parse import urlparse, urljoin
import argparse

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_DIR = os.path.join(BASE_DIR, 'static', 'songs')
JSON_PATH = os.path.join(BASE_DIR, 'songs.json')

def sanitize_filename(filename):
    """Sanitize filename for safe file system usage"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.replace(' ', '_').lower()
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    # Limit length
    if len(filename) > 50:
        filename = filename[:50]
    return filename

def extract_bandcamp_data(url):
    """Extract track information from Bandcamp page"""
    print(f"🔍 Extracting track data from: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            if response.getcode() != 200:
                print(f"❌ Failed to fetch page: HTTP {response.getcode()}")
                return None, None, None
            
            html_content = response.read().decode('utf-8')
            
            # Extract album title from title tag
            title_match = re.search(r'<title>([^|]+)</title>', html_content)
            album_title = title_match.group(1).strip() if title_match else "Unknown Album"
            
            # Extract artist from meta tags or title
            artist_match = re.search(r'<meta property="og:title" content="([^"]+)"', html_content)
            if artist_match:
                artist_title = artist_match.group(1)
                if ' - ' in artist_title:
                    artist = artist_title.split(' - ')[0].strip()
                else:
                    artist = "Unknown Artist"
            else:
                artist = "Unknown Artist"
            
            # Extract the data-tralbum attribute which contains JSON with track info
            tralbum_match = re.search(r'data-tralbum="([^"]+)"', html_content)
            if not tralbum_match:
                print("❌ Could not find track data on page")
                return None, None, None
            
            # Decode HTML entities and parse JSON
            tralbum_data = html.unescape(tralbum_match.group(1))
            
            try:
                data = json.loads(tralbum_data)
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse track data JSON: {e}")
                return None, None, None
            
            # Extract track information
            tracks = []
            if 'trackinfo' in data:
                for track in data['trackinfo']:
                    if 'file' in track and 'mp3-128' in track['file']:
                        track_info = {
                            'id': track.get('id'),
                            'title': track.get('title', 'Unknown Track'),
                            'duration': track.get('duration', 0),
                            'mp3_url': track['file']['mp3-128'],
                            'track_num': track.get('track_num', 0)
                        }
                        tracks.append(track_info)
            
            print(f"✅ Found {len(tracks)} tracks in album: {album_title}")
            return tracks, album_title, artist
            
    except Exception as e:
        print(f"❌ Error extracting Bandcamp data: {e}")
        return None, None, None

def download_file(url, filepath, max_retries=3):
    """Download file with retry logic and better error handling"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    for attempt in range(max_retries):
        try:
            print(f"  📥 Attempt {attempt + 1}/{max_retries}...")
            req = urllib.request.Request(url, headers=headers)
            
            # Add timeout to prevent hanging
            with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
                # Check if response is successful
                if response.getcode() == 200:
                    content_type = response.headers.get('Content-Type', '')
                    
                    # Check if we're getting audio content
                    if 'audio' in content_type.lower() or 'application/octet-stream' in content_type.lower():
                        content_length = response.headers.get('Content-Length')
                        if content_length:
                            print(f"  📊 Downloading {int(content_length) / (1024*1024):.1f} MB...")
                        
                        with open(filepath, 'wb') as out_file:
                            # Download in chunks to handle large files
                            chunk_size = 8192
                            total_downloaded = 0
                            while True:
                                chunk = response.read(chunk_size)
                                if not chunk:
                                    break
                                out_file.write(chunk)
                                total_downloaded += len(chunk)
                                if content_length and total_downloaded % (1024*1024) == 0:
                                    progress = (total_downloaded / int(content_length)) * 100
                                    print(f"  📈 Progress: {progress:.1f}%")
                        
                        return True
                    else:
                        print(f"  ⚠️  Unexpected content type: {content_type}")
                        if attempt == max_retries - 1:
                            print(f"  This might be a webpage rather than an audio file")
                        return False
                else:
                    print(f"  ❌ HTTP Error: {response.getcode()}")
                    return False
                    
        except urllib.error.HTTPError as e:
            print(f"  ❌ HTTP Error {e.code}: {e.reason}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
        except urllib.error.URLError as e:
            print(f"  ❌ URL Error: {e.reason}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    
    return False

def download_bandcamp_album(url):
    """Download all tracks from a Bandcamp album"""
    tracks, album_title, artist = extract_bandcamp_data(url)
    
    if not tracks:
        print("❌ No tracks found or failed to extract data")
        return False
    
    # Ensure songs directory exists
    os.makedirs(SONGS_DIR, exist_ok=True)
    
    # Load existing songs database
    json_db = {}
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, 'r', encoding='utf-8') as f:
                json_db = json.load(f)
        except Exception as e:
            print(f"⚠️  Warning: Could not load existing songs.json: {e}")
    
    successful_downloads = 0
    failed_downloads = 0
    
    print(f"\n🎵 Downloading tracks from '{album_title}' by {artist}")
    print("=" * 60)
    
    for track in tracks:
        # Create a safe filename
        safe_title = sanitize_filename(track['title'])
        filename = f"{safe_title}.mp3"
        filepath = os.path.join(SONGS_DIR, filename)
        
        print(f"\n🎶 Track {track['track_num']}: {track['title']}")
        print(f"   URL: {track['mp3_url'][:80]}...")
        
        # Check if file already exists
        if os.path.exists(filepath):
            print(f"   ⚠️  File already exists, skipping...")
            successful_downloads += 1
        else:
            # Download the file
            if download_file(track['mp3_url'], filepath):
                print(f"   ✅ Downloaded: {filename}")
                successful_downloads += 1
            else:
                print(f"   ❌ Failed to download: {filename}")
                failed_downloads += 1
                continue
        
        # Add to songs database
        track_id = safe_title
        json_db[track_id] = {
            "title": track['title'],
            "filename": filename,
            "lyrics": "",
            "lyrics_map": [],
            "duration": track.get('duration', 0),
            "artist": artist,
            "album": album_title,
            "source_url": url
        }
    
    # Save updated songs database
    try:
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(json_db, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Updated songs.json with {len(tracks)} tracks")
    except Exception as e:
        print(f"❌ Failed to save songs.json: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 DOWNLOAD SUMMARY")
    print(f"   Album: {album_title}")
    print(f"   Artist: {artist}")
    print(f"   Total tracks: {len(tracks)}")
    print(f"   ✅ Successfully downloaded: {successful_downloads}")
    print(f"   ❌ Failed downloads: {failed_downloads}")
    print(f"   📁 Files saved to: {SONGS_DIR}")
    print(f"   📄 Database updated: {JSON_PATH}")
    
    return successful_downloads > 0

def list_current_songs():
    """List currently available songs"""
    if not os.path.exists(JSON_PATH):
        print("❌ No songs.json file found")
        return
    
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            songs = json.load(f)
        
        print(f"\n🎵 CURRENTLY AVAILABLE SONGS ({len(songs)} total)")
        print("=" * 60)
        
        for song_id, song_info in songs.items():
            filename = song_info.get('filename', 'Unknown')
            title = song_info.get('title', 'Unknown')
            artist = song_info.get('artist', 'Unknown')
            duration = song_info.get('duration', 0)
            
            # Format duration
            if duration > 0:
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                duration_str = f"{minutes}:{seconds:02d}"
            else:
                duration_str = "Unknown"
            
            # Check if file exists
            filepath = os.path.join(SONGS_DIR, filename)
            exists = "✅" if os.path.exists(filepath) else "❌"
            
            print(f"   {exists} {title}")
            print(f"      📁 {filename}")
            print(f"      🎤 {artist}")
            print(f"      ⏱️  {duration_str}")
            print()
            
    except Exception as e:
        print(f"❌ Error reading songs.json: {e}")

def clear_songs():
    """Clear all songs and reset database"""
    print("🗑️  Clearing all songs...")
    
    # Remove songs directory
    if os.path.exists(SONGS_DIR):
        try:
            shutil.rmtree(SONGS_DIR)
            print(f"   ✅ Removed directory: {SONGS_DIR}")
        except Exception as e:
            print(f"   ❌ Failed to remove directory: {e}")
    
    # Create empty songs directory
    os.makedirs(SONGS_DIR, exist_ok=True)
    
    # Create empty songs.json
    try:
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        print(f"   ✅ Reset database: {JSON_PATH}")
    except Exception as e:
        print(f"   ❌ Failed to reset database: {e}")
    
    print("✅ All songs cleared successfully")

def main():
    parser = argparse.ArgumentParser(description='Bandcamp Music Downloader for Chirp3')
    parser.add_argument('url', nargs='?', help='Bandcamp album URL to download')
    parser.add_argument('--list', action='store_true', help='List current songs')
    parser.add_argument('--clear', action='store_true', help='Clear all songs')
    parser.add_argument('--demo', action='store_true', help='Download demo tracks (original functionality)')
    
    args = parser.parse_args()
    
    print("🎵 Chirp3 Music Setup Tool")
    print("=" * 60)
    
    if args.clear:
        clear_songs()
        return
    
    if args.list:
        list_current_songs()
        return
    
    if args.demo:
        print("🎸 Demo mode not implemented in this version")
        print("   Use the original setup_music.py for demo tracks")
        return
    
    if not args.url:
        print("Usage:")
        print("   python setup_music.py <bandcamp_album_url>")
        print("   python setup_music.py --list")
        print("   python setup_music.py --clear")
        print("\nExample:")
        print("   python setup_music.py https://palochebeatz.bandcamp.com/album/ozzy-osbourne-guitar-backing-tracks")
        return
    
    # Validate URL
    parsed_url = urlparse(args.url)
    if not parsed_url.netloc.endswith('bandcamp.com'):
        print("❌ Error: URL must be from bandcamp.com")
        return
    
    # Download the album
    success = download_bandcamp_album(args.url)
    
    if success:
        print("\n🎉 Download completed successfully!")
        print("   You can now run the application and enjoy the new tracks!")
    else:
        print("\n❌ Download failed. Please check the URL and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
