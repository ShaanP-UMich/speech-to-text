import pyaudio
import wave
from pynput import keyboard

# set up the audio parameters
chunk = 100000  # number of audio samples per frame
sample_format = pyaudio.paInt16  # 16-bit resolution
channels = 1  # mono
fs = 44100  # sampling rate
seconds_per_file = 5  # number of seconds to record per file

# set up the PyAudio stream
p = pyaudio.PyAudio()
# print(p.get_default_input_device_info())

stream = p.open(format=sample_format,
                channels=channels,
                rate=fs,
                frames_per_buffer=chunk,
                input=True)

# set up a counter for the files
file_counter = 1

# start recording when the 'r' key is pressed


def on_press(key):
    print("pressed key")
    print(key)
    try:
        # print('alphanumeric key {0} pressed'.format(
        #     key.char))
        if key.char == 'r':
            print("'R' key was pressed")
            # listener.stop()  # stop listening for 'r' key
            record()
            return False
    except AttributeError:
        print('special key {0} pressed'.format(
            key))


def on_release(key):
    print('released key')
    if key.char == 'q':
        # listener.stop_flag = True
        return False


def record():
    global file_counter
    frames = []  # buffer to hold the audio frames
    while True:
        data = stream.read(chunk)
        frames.append(data)
        if listener.stop_flag:  # stop recording when 'q' key is pressed
            listener.stop_flag = False  # reset the flag for next time
            break

    # save the audio file
    wf = wave.open(f"recording{file_counter}.wav", 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    # increment the file counter
    file_counter += 1

    # start listening for 'r' key again
    # listener.start()


# create a keyboard listener to detect the 'r' key press
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

print("Press 'R' to start recording and 'Q' to stop recording")

# wait for the listener to finish
listener.join()

# clean up the PyAudio stream
stream.stop_stream()
stream.close()
p.terminate()
