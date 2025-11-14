# 1. Ensure directory exists
mkdir -p static/songs

# 2. Download a test song (Beethoven - Moonlight Sonata)
# We use curl to fetch a sample mp3 so you can test immediately
curl -L -o static/songs/test_track.mp3 "https://upload.wikimedia.org/wikipedia/commons/e/eb/Beethoven_Moonlight_1st_movement.ogg"

echo "✅ Test track downloaded to static/songs/test_track.mp3"

