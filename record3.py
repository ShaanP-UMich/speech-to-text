import pyaudio
import wave
import keyboard

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

frames = []

print("Press and hold down the 'ctrl' key to start recording...")

while True:
    if keyboard.is_pressed('space'):
        print("Recording...")
        break

while True:
    data = stream.read(CHUNK)
    frames.append(data)
    if keyboard.is_pressed('space'):
        print("Recording...")
    else:
        print("Recording stopped.")
        break

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()
