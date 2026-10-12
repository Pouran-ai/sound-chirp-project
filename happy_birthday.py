import numpy as np
import soundfile as sf
import sounddevice as sd
import os
fs=44100
def piano_note(freq,duration=0.5,volume=0.3):
    t=np.linspace(0,duration,int(fs * duration),False)
    wave=(1.0 * np.sin(2 * np.pi * freq * t )+
              0.6 * np.sin(2 * np.pi *2 * freq * t)+
              0.3 * np.sin(2 * np.pi * 3 * freq * t)+
              0.15 * np.sin(2 * np.pi * 4 * freq * t)
              )
    env=np.ones(len(t))
    fade_in=int(0.01 * fs) 
    fade_out=int(0.15 * fs)
    env[:fade_in]=np.linspace(0,1,fade_in)
    env[-fade_out:]=np.linspace(1,0,fade_out)
    return volume * wave/ 2.05 *env
def silence(duration):
    return np.zeros(int(fs*duration))
notes={
    "C4":261.63,"D4":293.66,"E4":329.63,"F4":349.23,
    "G4":392.00,"A4":440.00,"B4":493.88,"C5":523.25,
    "D5":587.33,"E5":659.25,"F5":698.46,"G5":783.99
}
melody=[("G4",0.3),("G4",0.15),("A4",0.5),("G4",0.5),("C5",0.5),("B4",0.8),
        ("G4",0.3),("G4",0.15),("A4",0.5),("G4",0.5),("D5",0.5),("C5",0.8),
        ("G4",0.3),("G4",0.15),("G5",0.5),("E5",0.5),("C5",0.5),("B4",0.5),("A4",0.8),
        ("F5",0.3),("F5",0.15),("E5",0.5),("C5",0.5),("D5",0.5),("C5",0.8),
    ]
song=np.concatenate([piano_note(notes[n],d) for n , d in melody])
song=np.concatenate([song,silence(0.3)])
save_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),"happybirthday.wav")
sf.write(save_path,song,fs) 
sd.play(song,fs)
sd.wait()  
    
    
    