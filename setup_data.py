import json
import os
import urllib.request
import ssl
import shutil

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_DIR = os.path.join(BASE_DIR, 'static', 'songs')
JSON_PATH = os.path.join(BASE_DIR, 'songs.json')

# --- ROYALTY-FREE GENRE TRACKS (Kevin MacLeod) ---
GENRE_TRACKS = {
    "rock": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Hard%20Boiled.mp3",
    "disco": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Disco%20con%20Tutti.mp3",
    "ballad": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Airport%20Lounge.mp3",
    "blues": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Backed%20Vibes%20Clean.mp3",
    "latin": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Cheery%20Monday.mp3",
    "country": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Protofunk.mp3"
}

# --- SONGS WITH LYRICS ---
songs_list = [
    { "id": "bohemian_rhapsody", "genre": "ballad", "title": "Bohemian Rhapsody", "lines": ["Is this the real life?", "Is this just fantasy?", "Caught in a landslide", "No escape from reality", "Open your eyes", "Look up to the skies and see"] },
    { "id": "livin_on_a_prayer", "genre": "rock", "title": "Livin' on a Prayer", "lines": ["Tommy used to work on the docks", "Union's been on strike", "He's down on his luck", "It's tough, so tough", "Gina works the diner all day", "Working for her man"] },
    { "id": "dont_stop_believin", "genre": "rock", "title": "Don't Stop Believin'", "lines": ["Just a small town girl", "Livin' in a lonely world", "She took the midnight train", "Goin' anywhere", "Just a city boy", "Born and raised in South Detroit"] },
    { "id": "dancing_queen", "genre": "disco", "title": "Dancing Queen", "lines": ["You can dance", "You can jive", "Having the time of your life", "Ooh, see that girl", "Watch that scene", "Digging the dancing queen"] },
    { "id": "i_will_survive", "genre": "disco", "title": "I Will Survive", "lines": ["At first I was afraid", "I was petrified", "Kept thinking I could never live", "Without you by my side", "But then I spent so many nights", "Thinking how you did me wrong"] },
    { "id": "sweet_caroline", "genre": "disco", "title": "Sweet Caroline", "lines": ["Sweet Caroline", "Good times never seemed so good", "I've been inclined", "To believe they never would", "But now I", "Look at the night"] },
    { "id": "imagine", "genre": "ballad", "title": "Imagine", "lines": ["Imagine there's no heaven", "It's easy if you try", "No hell below us", "Above us only sky", "Imagine all the people", "Living for today"] },
    { "id": "hey_jude", "genre": "ballad", "title": "Hey Jude", "lines": ["Hey Jude, don't make it bad", "Take a sad song and make it better", "Remember to let her into your heart", "Then you can start to make it better"] },
    { "id": "house_rising_sun", "genre": "blues", "title": "House of the Rising Sun", "lines": ["There is a house in New Orleans", "They call the Rising Sun", "And it's been the ruin", "Of many a poor boy", "And God, I know I'm one"] },
    { "id": "folsom_prison", "genre": "blues", "title": "Folsom Prison Blues", "lines": ["I hear the train a comin'", "It's rolling round the bend", "And I ain't seen the sunshine", "Since I don't know when", "I'm stuck in Folsom prison", "And time keeps draggin' on"] },
    { "id": "ring_of_fire", "genre": "country", "title": "Ring of Fire", "lyrics": ["I fell into a burning ring of fire", "I went down, down, down", "And the flames went higher", "And it burns, burns, burns", "The ring of fire"] },
    { "id": "la_bamba", "genre": "latin", "title": "La Bamba", "lines": ["Para bailar la bamba", "Para bailar la bamba", "Se necesita una poca de gracia", "Una poca de gracia pa' mi pa' ti", "Y arriba y arriba"] },
    { "id": "wonderwall", "genre": "ballad", "title": "Wonderwall", "lines": ["Today is gonna be the day", "That they're gonna throw it back to you", "By now you should've somehow", "Realized what you gotta do"] },
    { "id": "hotel_california", "genre": "rock", "title": "Hotel California", "lines": ["On a dark desert highway", "Cool wind in my hair", "Warm smell of colitas", "Rising up through the air"] },
    { "id": "yesterday", "genre": "ballad", "title": "Yesterday", "lines": ["Yesterday", "All my troubles seemed so far away", "Now it looks as though they're here to stay", "Oh, I believe in yesterday"] }
]

def download_file(url, filepath):
    headers = {'User-Agent': 'Mozilla/5.0'}
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx) as response:
            with open(filepath, 'wb') as out_file: out_file.write(response.read())
            return True
    except: return False

def main():
    if os.path.exists(SONGS_DIR): shutil.rmtree(SONGS_DIR)
    os.makedirs(SONGS_DIR, exist_ok=True)

    print("⬇️  Downloading Genre Tracks...")
    genre_cache = {}
    for genre, url in GENRE_TRACKS.items():
        cache_path = os.path.join(SONGS_DIR, f"_cache_{genre}.mp3")
        if download_file(url, cache_path): genre_cache[genre] = cache_path

    json_db = {}
    print("\n🎵 Generating Synchronized Lyrics Data...")

    for song in songs_list:
        genre = song['genre']
        filename = f"{song['id']}.mp3"
        target_path = os.path.join(SONGS_DIR, filename)
        
        if genre in genre_cache: shutil.copy(genre_cache[genre], target_path)

        # GENERATE FAKE TIMESTAMPS FOR DEMO
        # In a real app, you would hand-code these numbers to match the music.
        # Here we just space them 4 seconds apart.
        lyrics_map = []
        current_time = 2.0 # Start at 2 seconds
        raw_text = ""
        
        lines = song.get('lines', song.get('lyrics', [])) # Handle both keys
        if isinstance(lines, str): lines = lines.split('\n')

        for line in lines:
            lyrics_map.append({
                "time": current_time,
                "text": line
            })
            raw_text += line + "\n"
            current_time += 4.0 # Add 4 seconds per line

        json_db[song['id']] = {
            "title": song['title'],
            "filename": filename,
            "lyrics": raw_text.strip(),
            "lyrics_map": lyrics_map # <--- The Key New Data Structure
        }

    with open(JSON_PATH, 'w', encoding='utf-8') as f: json.dump(json_db, f, indent=2)
        
    print("\n✅ Setup Complete. Lyrics are now time-coded.")

if __name__ == "__main__": main()

