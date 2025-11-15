#!/bin/bash
# Filename: artists.sh

# The album name is optional, this is for backing tracks where random songs, 
# perhaps not all from the same album are recorded.

python3 ./setup_music.py \
 --bandcamp https://palochebeatz.bandcamp.com/album/aerosmith-guitar-backing-tracks \
 --artist "Aerosmith"

python3 ./setup_music.py \
 --bandcamp https://palochebeatz.bandcamp.com/album/the-police-guitar-backing-tracks \
 --artist "The Police"

python3 ./setup_music.py \
 --bandcamp https://palochebeatz.bandcamp.com/album/red-hot-chili-peppers-guitar-backing-tracks \
 --artist "Red Hot Chili Peppers"
