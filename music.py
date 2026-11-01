# GENERATOR OF THE TONES AND ACCORDS



# ALL THE IMPORTS
import numpy as np
import sounddevice as sd
import keyboard as kb
import time

from matplotlib import pyplot as pt #для отладки



# THE PARAMETERS (amplitude, freq - Hz; duration - s; samples - times), POINT'S MASSIVE (s)

amp = 3

freq = 440

duration = 1

sample_rate = 44100       # for .wav it's better to use either 44100 or 48000  

t = np.arange(sample_rate * duration) / sample_rate

#GENERATE THE SIGNAL (sin(t))

#samples = np.sin(2*np.pi*amp*freq*t)

#FLAGS and FUNCS

Play = 1

def double_freq():
    global freq
    if freq<10000:
        freq*=2
        sd.stop()
    
def not_double_freq():
    global freq
    if freq>20:
        freq/=2
        sd.stop()
    
def change_play():
    global Play
    Play = 1 - Play
    sd.stop()
    
kb.add_hotkey('up', double_freq)
kb.add_hotkey('down', not_double_freq)

kb.add_hotkey('space', change_play)

#PLAYIN AND SHII

try:
    while True:
        if Play:
            n = round(freq*duration)
            buf_freq = n/duration
            samples = amp*np.sin(2*np.pi*buf_freq*t)
            sd.play(samples, sample_rate, blocking = True, loop = True)
        # pt.plot(t[-100:], samples[-100:])
        # pt.show()
        time.sleep(0.05)
except KeyboardInterrupt:
    sd.stop()

