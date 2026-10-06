import numpy as np
import soundfile as sf
import sounddevice as sd

fs=44100
duration=2.0
t=np.linspace(0, duration, int(fs * duration), False)
f_start=200.0
f_end=1000.0
phase=2 * np.pi * (f_start * t + (f_end - f_start) * t**2 / (2 * duration))
audio_data=0.5* np.sin(phase)

sf.write('test_chirp.wav' , audio_data, fs)
sd.play(audio_data, fs)
sd.wait()

print("test_chirp.wav")
