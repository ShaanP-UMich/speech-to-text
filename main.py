import pyaudio
import wave
import keyboard
import uuid
import hashlib
import time

audio_uuid = uuid.uuid4()
sha256 = hashlib.sha256(str(audio_uuid).encode('utf-8')).hexdigest()
short_uuid = sha256[:8]

CHUNK = 4096  # 8182
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
WAVE_OUTPUT_FILENAME = f"output-{short_uuid}.wav"

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

print("Hold 'space' to start recording. Release 'space' to stop recording")

while True:
    if keyboard.is_pressed('space'):
        if not is_recording:
            print("Recording started...")
            is_recording = True
        data = stream.read(CHUNK)
        frames.append(data)
    elif is_recording:
        start_time = time.time()
        while time.time() - start_time < 1:
            data = stream.read(CHUNK)
            frames.append(data)
            
        print("Recording stopped.")
        print(f"Outputted to file {WAVE_OUTPUT_FILENAME}")
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
