import numpy as np
import sounddevice as sd
import soundfile as sf
fs=44100
def piano_note(freq,duration=0.5):
    t=np.linspace(0,duration,int(fs * duration),False)
    wave=(1.0 * np.sin(2 * np.pi * freq * t )+
          0.5 * np.sin(2 * np.pi *2 * freq * t)+
          0.25 * np.sin(2 * np.pi * 3 * freq * t))
    env=np.ones(len(t))
    fade=int(0.05 * fs)
    env[:fade]=np.linspace(0,1,fade)
    env[-fade:]=np.linspace(1,0,fade)
    return 0.3 *wave/ 1.75 *env
notes={
    "C4":261.63,"D4":293.66,"E4":329.63,"F4":349.23,
    "G4":392.00,"A4":440.00,"B4":493.88,"C5":523.25
}
melody=["C4","E4","G4","C5","G4","E4","C4","E4","F4","A4","C5","A4","F4","C4"]
song=np.concatenate([piano_note(notes[n],0.4) for n in melody])
sf.write("my_music.wav",song,fs) 
sd.play(song,fs)
sd.wait()       

