# Filename: main.py
import os
import logging
import json
import difflib
import re
import sys
import time
import random
import traceback

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- LIBRARY CHECKS ---
print("\n🔍 --- SYSTEM CHECK ---")
try:
    import jellyfish
    JELLYFISH_AVAILABLE = True
    print("✅ 'jellyfish' library loaded (Enhanced Fuzzy Matching enabled)")
except ImportError:
    JELLYFISH_AVAILABLE = False
    print("⚠️  'jellyfish' NOT found. Using basic matching. (pip install jellyfish)")

try:
    import google.auth
    from google.cloud.speech_v2 import SpeechClient
    from google.cloud.speech_v2.types import RecognitionConfig, RecognizeRequest, RecognitionFeatures
    GCP_AVAILABLE = True
    print("✅ Google Cloud libraries loaded")
except ImportError:
    GCP_AVAILABLE = False
    print("❌ Google Cloud libraries NOT found. (pip install google-cloud-speech)")

from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

# --- CONFIGURATION ---
LOCATION = "us" 
API_ENDPOINT = f"{LOCATION}-speech.googleapis.com"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_DIR = os.path.join(BASE_DIR, 'songs-karaoke')
SONGS_DB_PATH = os.path.join(BASE_DIR, 'songs.json')
LEADERBOARD_PATH = os.path.join(BASE_DIR, 'leaderboard.json')

# Auto-detect Project ID
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID and GCP_AVAILABLE:
    try:
        _, PROJECT_ID = google.auth.default()
    except Exception as e:
        print(f"⚠️  Auth Error: {e}")

print(f"ℹ️  Project ID: {PROJECT_ID if PROJECT_ID else 'NOT SET (Check GOOGLE_CLOUD_PROJECT)'}")
print("----------------------\n")

# Ensure templates directory exists
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
if not os.path.exists(TEMPLATE_DIR):
    os.makedirs(TEMPLATE_DIR)

# --- DATA HELPERS ---
def load_json(path, default=None):
    if not os.path.exists(path): return default if default is not None else {}
    try:
        with open(path, 'r', encoding='utf-8') as f: return json.load(f)
    except: return default if default is not None else {}

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# --- SCORING ENGINE ---
def normalize_text(text):
    t = text.lower()
    t = re.sub(r'[^\w\s]', '', t)
    replacements = {
        "gonna": "going to", "wanna": "want to", "cause": "because",
        "cos": "because", "em": "them", "im": "i am", "youre": "you are",
        "cant": "cannot", "dont": "do not", "wont": "will not"
    }
    return [replacements.get(w, w) for w in t.split()]

def calculate_score_advanced(user_text, official_text):
    print("\n📊 --- SCORING CALCULATION ---")
    user_words = normalize_text(user_text)
    target_words = normalize_text(official_text)
    
    print(f"🗣️  User Words ({len(user_words)}): {user_words}")
    print(f"📄 Target Words ({len(target_words)}): {target_words[:10]}...") # Truncate for log

    if not target_words: return 0, user_text
    
    matcher = difflib.SequenceMatcher(None, user_words, target_words)
    html_output = []
    weighted_score = 0.0
    total_possible = len(target_words)
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for w in user_words[i1:i2]:
                html_output.append(f"<span class='text-green-400 font-bold'>{w}</span>")
                weighted_score += 1.0
        elif tag == 'replace':
            user_segment = user_words[i1:i2]
            target_segment = target_words[j1:j2]
            for idx in range(max(len(user_segment), len(target_segment))):
                u_word = user_segment[idx] if idx < len(user_segment) else ""
                t_word = target_segment[idx] if idx < len(target_segment) else ""
                
                match_found = False
                if u_word and t_word and JELLYFISH_AVAILABLE:
                    sim = jellyfish.jaro_winkler_similarity(u_word, t_word)
                    if sim > 0.85:
                        html_output.append(f"<span class='text-green-400 font-bold'>{u_word}</span>")
                        weighted_score += 1.0
                        match_found = True
                    elif sim > 0.70:
                        html_output.append(f"<span class='text-yellow-400 font-bold'>{u_word}</span>")
                        weighted_score += 0.8
                        match_found = True
                
                if not match_found and u_word:
                    html_output.append(f"<span class='text-red-500 line-through opacity-50'>{u_word}</span>")
        elif tag == 'insert':
             pass 
        elif tag == 'delete':
            for w in user_words[i1:i2]:
                html_output.append(f"<span class='text-red-500 text-xs opacity-50'>{w}</span>")

    final_score = int((weighted_score / total_possible) * 100) if total_possible > 0 else 0
    print(f"📈 Final Score: {final_score}%")
    return min(100, final_score), " ".join(html_output)

# --- ROUTES ---
@app.route('/songs/<path:filename>')
def serve_audio(filename):
    return send_from_directory(SONGS_DIR, filename)

@app.route('/')
def index():
    songs_db = load_json(SONGS_DB_PATH)
    songs_list = []
    for key, data in songs_db.items():
        songs_list.append({
            "id": key,
            "title": data.get('title', 'Unknown'),
            "filename": data.get('filename', ''),
            "lyrics_map": data.get('lyrics_map', []),
            "start_offset": data.get('start_offset', 0)
        })
    return render_template('index.html', songs=songs_list)

@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
    data = load_json(LEADERBOARD_PATH, default=[])
    if request.method == 'POST':
        entry = request.json
        if not entry or 'name' not in entry: return jsonify({'error': 'Invalid'}), 400
        data.append(entry)
        data.sort(key=lambda x: x['score'], reverse=True)
        data = data[:50]
        save_json(LEADERBOARD_PATH, data)
        return jsonify({'status': 'saved'})
    return jsonify(data)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    print("\n🎤 --- STARTING TRANSCRIPTION ---")
    
    if not GCP_AVAILABLE:
        print("❌ FAILURE: Google Cloud Libraries missing.")
        return jsonify({'transcript': "Server Config Error", 'score': 0})

    if not PROJECT_ID:
        print("❌ FAILURE: No Project ID found.")
        return jsonify({'error': 'Server Config Error: No Project ID'}), 500

    audio_file = request.files.get('audio_data')
    song_id = request.form.get('song_id')
    
    if not audio_file: 
        print("❌ FAILURE: No audio file received.")
        return jsonify({'error': 'No audio'}), 400
    
    content = audio_file.read()
    print(f"📦 Received Audio Size: {len(content)} bytes")
    print(f"🎵 Song ID: {song_id}")

    try:
        print(f"📡 Connecting to Speech-to-Text (Project: {PROJECT_ID})...")
        client = SpeechClient(client_options={"api_endpoint": API_ENDPOINT})
        
        parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
        config = RecognitionConfig(
            auto_decoding_config={},
            language_codes=["en-US"],
            model="chirp_3", 
            features=RecognitionFeatures(enable_automatic_punctuation=True),
        )
        request_obj = RecognizeRequest(
            recognizer=f"{parent}/recognizers/_", 
            config=config,
            content=content,
        )

        print("⏳ Waiting for GCP response...")
        response = client.recognize(request=request_obj)
        
        # --- DEBUG RAW RESPONSE ---
        if not response.results:
            print("⚠️  GCP Response contained NO results (Empty Transcript)")
            full_transcript = ""
        else:
            transcript_parts = [r.alternatives[0].transcript for r in response.results if r.alternatives]
            full_transcript = " ".join(transcript_parts)
            print(f"📝 FULL TRANSCRIPT: '{full_transcript}'")
        
        score = 0
        comparison = ""
        
        # --- LYRICS LOOKUP ---
        songs_db = load_json(SONGS_DB_PATH)
        if song_id and song_id in songs_db:
            target_lyrics = songs_db[song_id].get('lyrics', '')
            if not target_lyrics:
                print("⚠️  WARNING: No lyrics found in database for this song!")
            else:
                score, comparison = calculate_score_advanced(full_transcript, target_lyrics)
        else:
            print(f"❌ ERROR: Song ID {song_id} not found in database.")

        return jsonify({
            'transcript': full_transcript,
            'score': score,
            'comparison': comparison
        })
    except Exception as e:
        print("❌ FATAL ERROR during transcription:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Server running on http://localhost:{port}")
    app.run(debug=True, host='0.0.0.0', port=port)

