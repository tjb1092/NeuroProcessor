#!usr/bin/env python
#coding=utf-8

import pyaudio
import wave

#define stream chunk
chunk = 1024

#open a wav format music
f = wave.open("Hello_10x.wav","rb")
#instantiate PyAudio
p = pyaudio.PyAudio()
#open stream
stream = p.open(format = p.get_format_from_width(f.getsampwidth()),
                channels = f.getnchannels(),
                rate = f.getframerate(),
                output = True)
#read data
data = f.readframes(chunk)

# It works, but it does have a glitchy thing at the beginning.
#play stream
while len(data) > 0:
    stream.write(data)
    data = f.readframes(chunk)

#stop stream
stream.stop_stream()
stream.close()

#close PyAudio
p.terminate()
