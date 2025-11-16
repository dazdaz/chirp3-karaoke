import os
import logging
import json
import difflib
import re
import sys
import jellyfish  # Requires: uv pip install jellyfish
from flask import Flask, render_template, request, jsonify
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import RecognitionConfig, RecognizeRequest, RecognitionFeatures

# --- LOGGING SETUP ---
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

# --- PORT CONFIGURATION ---
def get_port():
    """Get port from command line argument or environment variable"""
    # Check command line arguments first
    if len(sys.argv) > 1:
        try:
            return int(sys.argv[1])
        except (ValueError, IndexError):
            pass
    
    # Fall back to environment variable
    return int(os.environ.get('PORT', 8080))

# --- DATA HELPERS ---
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
        l_map = data.get('lyrics_map', [])
        start_offset = 0 
        if l_map and len(l_map) > 0:
            first_lyric_time = l_map[0].get('time', 0)
            start_offset = max(0, first_lyric_time - 2)
            
        songs_list.append({
            "id": key,
            "title": data.get('title', 'Unknown Title'),
            "filename": data.get('filename', ''),
            "lyrics": data.get('lyrics', ''),
            "lyrics_map": l_map,
            "start_offset": start_offset
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
        data = data[:50]
        save_json(LEADERBOARD_PATH, data)
        return jsonify({'status': 'saved', 'leaderboard': data})
    return jsonify(data)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        client = SpeechClient(client_options={"api_endpoint": API_ENDPOINT})
    except Exception as e:
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

        score = 0
        comparison_html = full_transcript
        
        songs_db = load_json(SONGS_DB_PATH)
        if song_id and song_id in songs_db:
            target_lyrics = songs_db[song_id].get('lyrics', '')
            # CALL THE NEW AI SCORING ENGINE
            score, comparison_html = calculate_score_advanced(full_transcript, target_lyrics)

        return jsonify({
            'transcript': full_transcript,
            'score': score,
            'comparison': comparison_html
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- ADVANCED SCORING ENGINE ---
def normalize_text(text):
    """
    Cleans text and standardizes contractions to match Speech-to-Text output.
    """
    t = text.lower()
    # 1. Remove Punctuation
    t = re.sub(r'[^\w\s]', '', t)
    
    # 2. Standardize Slang (Karaoke Normalization)
    replacements = {
        "gonna": "going to",
        "wanna": "want to",
        "cause": "because",
        "cos": "because",
        "em": "them",
        "walkin": "walking",
        "talkin": "talking",
        "runnin": "running",
        "singin": "singing",
        "nothin": "nothing",
        "im": "i am",
        "youre": "you are",
        "cant": "cannot",
        "dont": "do not",
        "wont": "will not"
    }
    words = t.split()
    clean_words = [replacements.get(w, w) for w in words]
    return clean_words

def calculate_score_advanced(user_text, official_text):
    """
    Commercial-Grade Fuzzy Matching.
    Uses Jaro-Winkler similarity instead of binary equality.
    """
    user_words = normalize_text(user_text)
    target_words = normalize_text(official_text)
    
    if not target_words: return 0, user_text

    # SequenceMatcher finds the best alignment of words
    matcher = difflib.SequenceMatcher(None, user_words, target_words)
    
    html_output = []
    weighted_score = 0.0
    total_possible = len(target_words)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        
        # 1. EXACT MATCH (100% Points)
        if tag == 'equal':
            for w in user_words[i1:i2]:
                html_output.append(f"<span class='text-green-400 font-bold'>{w}</span>")
                weighted_score += 1.0
        
        # 2. REPLACEMENT (Check Similarity)
        elif tag == 'replace':
            user_segment = user_words[i1:i2]
            target_segment = target_words[j1:j2]
            
            # Compare segments word-by-word or best-fit
            # Simple approach: Zip them and compare
            for idx in range(max(len(user_segment), len(target_segment))):
                u_word = user_segment[idx] if idx < len(user_segment) else ""
                t_word = target_segment[idx] if idx < len(target_segment) else ""
                
                if u_word and t_word:
                    # Jaro-Winkler is better for short strings/typos
                    # 1.0 is perfect, 0.0 is distinct
                    similarity = jellyfish.jaro_winkler_similarity(u_word, t_word)
                    
                    if similarity > 0.85:
                        # Very close (Typos like "crazy" vs "krazy")
                        html_output.append(f"<span class='text-green-400 font-bold'>{u_word}</span>")
                        weighted_score += 1.0 # Count as full hit
                    elif similarity > 0.70:
                        # Close-ish (Phonetic match like "ya" vs "you")
                        html_output.append(f"<span class='text-yellow-400 font-bold' title='{int(similarity*100)}% Match'>{u_word}</span>")
                        weighted_score += 0.8
                    else:
                        # Wrong word
                        html_output.append(f"<span class='text-red-500 line-through opacity-50'>{u_word}</span>")
                elif u_word:
                    # Extra word user sang
                    html_output.append(f"<span class='text-red-500 text-xs opacity-50'>{u_word}</span>")
                # Missing words handled in next block
                
        # 3. MISSING (INSERTION)
        elif tag == 'insert':
             missing = " ".join(target_words[j1:j2])
             html_output.append(f"<span class='text-gray-600 opacity-30'>[{missing}]</span>")
             
        # 4. EXTRA WORDS (DELETION)
        elif tag == 'delete':
            for w in user_words[i1:i2]:
                html_output.append(f"<span class='text-red-500 text-xs opacity-50'>{w}</span>")

    # Final Score Calculation
    if total_possible > 0:
        final_score = int((weighted_score / total_possible) * 100)
    else:
        final_score = 0
        
    # Bonus Logic: If score is suspiciously low but word count is similar, 
    # apply a 'Vibe Boost' (assumes STT failed on slang)
    if final_score < 50 and len(user_words) > 0:
        length_ratio = len(user_words) / len(target_words)
        if 0.8 < length_ratio < 1.2:
            final_score += 10

    return min(100, final_score), " ".join(html_output)

if __name__ == '__main__':
    port = get_port()
    print(f"🎵 Server running on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)

