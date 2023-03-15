import pyaudio
import wave
import keyboard
import uuid
import hashlib
import time
import threading
import os
import whisper

OUTPUT_DIR = 'output'


def record_clip(record_flag, files: list):
    print("record_clip thread started")

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

        print("Hold 'space' to start recording. Release 'space' to stop recording. Press 'CTRL + q' to stop the program.")

        while True:
            if keyboard.is_pressed('space'):
                if not is_recording:
                    print("Recording started...")
                    is_recording = True
                data = stream.read(CHUNK)
                frames.append(data)
            elif is_recording:
                start_time = time.time()
                while time.time() - start_time < 0.5:
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


        file = OUTPUT_FILE
        while not os.path.exists(file):
            print("Waiting for audio file to save...")
            time.sleep(0.1)

        print(file)

        model = whisper.load_model("base")
        result = model.transcribe(file)
        print(result["text"])


def on_q(record_flags):
    print("'q' key was pressed")
    record_flags[0] = False


def main():
    print("main function")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    record_flags = [True]
    files = []  # Queue

    keyboard.add_hotkey('ctrl+q', on_q, args=[record_flags])

    recording_thread = threading.Thread(
        target=record_clip, args=(record_flags, files,))

    recording_thread.start()

    recording_thread.join()


if __name__ == "__main__":
    main()
