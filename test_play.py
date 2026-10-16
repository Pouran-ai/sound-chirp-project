import soundfile as sf
import sounddevice as sd
data,samplerate=sf.read('test_chirp.wav',dtype='float32')
print('data:' ,data.shape)
print('samplerate:',samplerate)
print("playing")
sd.play(data,samplerate)
sd.wait()
print('finish')