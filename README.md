# Sound Chirp & Music Project
This project generates sounds and music using Python.

## Installation

First, install the required libraries:

pip install -r requirements.txt

## Project Files
- "make_wav.py" - Chirp sound generator(frequency from 200 to 1000 Hz)
- "makemusic_wav.py" - Piano melody generator
- "happy_birthday.py" - Happy Birthday song player
- "sound_player.py" - Long audio file player (streaming)
- "sound_player_lite.py" - Long audio file player (streaming, without NumPy)
-  "play_web_stream.py" - Stream audio from a URL using FFmpeg

## How to Run

You can run each file independently:

python happy_birthday.py

or

python makemusic_wav.py

To play a long audio file with NumPy:

python sound_player.py FILENAME.wav

To play a long audio file without NumPy:

python sound_player_lite.py FILENAME.wav



## Technologies

- Python 3.12
- NumPy
- SoundFile
- SoundDevice
*Last updated: Today*
