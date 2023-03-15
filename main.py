import pyaudio
import wave
import keyboard

CHUNK = 8182
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

# print(pyaudio.PyAudio().get_device_count())
# exit()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

frames = []
is_recording = False

while True:
    if keyboard.is_pressed('space'):
        if not is_recording:
            print("Recording started...")
            is_recording = True
        data = stream.read(CHUNK)
        frames.append(data)
    elif is_recording:
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
