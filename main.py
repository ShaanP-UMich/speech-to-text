import pyaudio
import wave
import keyboard
import uuid
import hashlib
import time
import threading
import os

OUTPUT_DIR = 'output'


def record_clip(record_flag):
    while record_flag[0]:
        audio_uuid = uuid.uuid4()
        sha256 = hashlib.sha256(str(audio_uuid).encode('utf-8')).hexdigest()
        short_uuid = sha256[:8]

        CHUNK = 4096  # 8182
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        WAVE_OUTPUT_FILENAME = f"output-{short_uuid}.wav"
        OUTPUT_FILE = os.path.join(OUTPUT_DIR, WAVE_OUTPUT_FILENAME)

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

        print("Hold 'space' to start recording. Release 'space' to stop recording. Press 'q' to stop the program.")

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
            elif not record_flag[0]:
                print("Recording manually stopped")
                stream.stop_stream()
                stream.close()
                p.terminate()
                return

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(OUTPUT_FILE, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()


def on_q(record_flag):
    print("'q' key was pressed")
    record_flag[0] = False
    exit(0)


def main():
    print("main function")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    record_flags = [True]

    keyboard.add_hotkey('q', on_q, args=[record_flags])

    recording_thread = threading.Thread(
        target=record_clip, args=(record_flags,))

    recording_thread.start()


if __name__ == "__main__":
    main()
