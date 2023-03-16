import pyaudio
import wave
import keyboard
import uuid
import hashlib
import time
import threading
import os
import whisper
from dotenv import load_dotenv
from voicevox import Client
from voicevox import AudioQuery
from voicevox.types import audio_query
from voicevox.http import HttpClient
import asyncio
import deepl
import requests
import json
import httpx

load_dotenv()

OUTPUT_DIR = 'output'
DEEPL_API_KEY = os.environ.get("DEEPL_API_KEY")

CHUNK = 4096  # 8182
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

translator = deepl.Translator(DEEPL_API_KEY)


def record_clip(record_flag, files: list):
    print("record_clip thread started")

    while record_flag[0]:
        audio_uuid = uuid.uuid4()
        sha256 = hashlib.sha256(str(audio_uuid).encode('utf-8')).hexdigest()
        short_uuid = sha256[:8]

        WAVE_OUTPUT_FILENAME = f"output-{short_uuid}.wav"
        OUTPUT_FILE = os.path.join(OUTPUT_DIR, WAVE_OUTPUT_FILENAME)

        # print(pyaudio.PyAudio().get_device_count())
        # exit()

        p = pyaudio.PyAudio()

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
                print("STOPPING PROGRAM")
                stream.stop_stream()
                stream.close()
                p.terminate()
                exit()

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
        result = model.transcribe(file, fp16=False, language='English')
        print(result["text"])

        transcribed_text = result['text']
        jp_translation = translator.translate_text(
            transcribed_text, target_lang='JA')

        jp_text = jp_translation.text
        # jp_text = '丘の上にいるのです。'
        print(jp_text)

        # query_app(jp_text, 3)
        asyncio.run(async_query_app(jp_text, 14, short_uuid))

        # asyncio.run(tts(jp_text, short_uuid))
        # asyncio.run(get_speakers())


async def async_query_app(text, speaker: int, uuid: str):
    async with httpx.AsyncClient() as client:
        # First POST request
        query_params = {'speaker': speaker, 'text': text}
        response = await client.post('http://localhost:50021/audio_query', params=query_params)
        query_json = response.json()

        # print(query_json)
        # print("================")
        query_json['outputSamplingRate'] = int(48000)
        query_json['outputStereo'] = True
        query_json['prePhonemeLength'] = 0.1
        query_json['postPhonemeLength'] = 0.1
        # query_json['pitchScale'] = 1
        # print(query_json)

        # Second POST request
        headers = {'Content-Type': 'application/json'}
        synth_params = {'speaker': speaker}
        response = await client.post('http://localhost:50021/synthesis', headers=headers, params=synth_params, json=query_json)
        audio_data = response.content
        # print(audio_data)

        new_file_name = f"output-{uuid}_{speaker}_JP.wav"
        OUTPUT_FILE = os.path.join(OUTPUT_DIR, new_file_name)

        with open(OUTPUT_FILE, "wb") as f:
            f.write(audio_data)
            print(f"Exported {new_file_name} to {OUTPUT_FILE}")

        p = pyaudio.PyAudio()

        device_index = None
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            print(dev['name'])
            if dev['name'] == 'CABLE Input (VB-Audio Virtual C':
                print(dev)
                device_index = dev['index']
                break

        if device_index is None:
            print('Desired output device not found!')
            exit()

        # open audio file
        with wave.open(OUTPUT_FILE, 'rb') as f:
            stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                            channels=f.getnchannels(),
                            rate=f.getframerate(),
                            output=True,
                            output_device_index=device_index)

            # read data
            print("opening file to play it")
            data = f.readframes(CHUNK)

            # play audio
            while data:
                stream.write(data)
                data = f.readframes(CHUNK)

        stream.stop_stream()
        stream.close()
        p.terminate()


async def tts(text: str, uuid):
    new_file_name = f"output-{uuid}_JP.wav"
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, new_file_name)
    async with Client() as client:
        audio_query = await client.create_audio_query(
            text, speaker=3
        )
        # audio_query['output_sampling_rate'] = 44100
        # print(audio_query.to_dict())
        with open(OUTPUT_FILE, "wb") as f:
            f.write(await audio_query.synthesis())
            print(f"Exported {new_file_name} to {OUTPUT_FILE}")


async def get_speakers():
    async with Client() as client:
        for speaker in await client.fetch_speakers():
            # print(speaker.uuid)
            print(speaker.name)
            # print(speaker.supported_features)


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
