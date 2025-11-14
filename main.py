import os
import logging
import json
import difflib
import re
from flask import Flask, render_template, request, jsonify
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import RecognitionConfig, RecognizeRequest, RecognitionFeatures

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- CONFIGURATION ---
LOCATION = "us" 
API_ENDPOINT = f"{LOCATION}-speech.googleapis.com"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_DB_PATH = os.path.join(BASE_DIR, 'songs.json')
LEADERBOARD_PATH = os.path.join(BASE_DIR, 'leaderboard.json')
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")

# --- HELPERS ---
def load_json(path, default=None):
    if not os.path.exists(path): return default if default is not None else {}
    try:
        with open(path, 'r', encoding='utf-8') as f: return json.load(f)
    except: return default if default is not None else {}

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# --- ROUTES ---

@app.route('/')
def index():
    songs_db = load_json(SONGS_DB_PATH)
    songs_list = []
    
    for key, data in songs_db.items():
        # CRITICAL FIX: We must ensure 'lyrics_map' exists, even if empty
        # This prevents the "Undefined" error in the template
        l_map = data.get('lyrics_map', [])
        
        songs_list.append({
            "id": key,
            "title": data.get('title', 'Unknown Title'),
            "filename": data.get('filename', ''),
            "lyrics": data.get('lyrics', ''),
            "lyrics_map": l_map  # <--- THIS WAS MISSING/CAUSING THE ERROR
        })
        
    return render_template('index.html', songs=songs_list)

@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
    data = load_json(LEADERBOARD_PATH, default=[])
    
    if request.method == 'POST':
        entry = request.json
        if not entry or 'name' not in entry or 'score' not in entry:
            return jsonify({'error': 'Invalid data'}), 400
            
        data.append(entry)
        data.sort(key=lambda x: x['score'], reverse=True)
        data = data[:10]
        save_json(LEADERBOARD_PATH, data)
        return jsonify({'status': 'saved', 'leaderboard': data})
        
    return jsonify(data)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        client = SpeechClient(client_options={"api_endpoint": API_ENDPOINT})
    except:
        return jsonify({'error': 'GCP Client Init Failed'}), 500

    audio_file = request.files.get('audio_data')
    song_id = request.form.get('song_id')
    
    if not audio_file: return jsonify({'error': 'No audio'}), 400
    content = audio_file.read()
    
    if len(content) < 100: return jsonify({'error': 'Audio too short'}), 400

    try:
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

        response = client.recognize(request=request_obj)
        
        transcript_parts = [r.alternatives[0].transcript for r in response.results if r.alternatives]
        full_transcript = " ".join(transcript_parts)

        # Scoring
        score = 0
        comparison_html = full_transcript
        
        songs_db = load_json(SONGS_DB_PATH)
        if song_id and song_id in songs_db:
            target_lyrics = songs_db[song_id].get('lyrics', '')
            score, comparison_html = calculate_score(full_transcript, target_lyrics)

        return jsonify({
            'transcript': full_transcript,
            'score': score,
            'comparison': comparison_html
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_score(user_text, official_text):
    def normalize(text):
        return re.sub(r'[^\w\s]', '', text).lower().split()

    user_words = normalize(user_text)
    target_words = normalize(official_text)
    
    if not target_words: return 0, user_text

    matcher = difflib.SequenceMatcher(None, user_words, target_words)
    score = int(matcher.ratio() * 100)

    html = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            html.append(f"<span class='text-green-400 font-bold'>{' '.join(user_words[i1:i2])}</span>")
        elif tag == 'replace':
            html.append(f"<span class='text-red-400'>{' '.join(user_words[i1:i2])}</span>")
        elif tag == 'insert':
             html.append(f"<span class='text-gray-500 opacity-50'>{' '.join(target_words[j1:j2])}</span>")
            
    return score, " ".join(html)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🎵 Server running on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)

