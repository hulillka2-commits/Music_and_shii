# GENERATOR OF THE TONES AND ACCORDS



# ALL THE IMPORTS
import numpy as np
import sounddevice as sd
import keyboard as kb
import time

from matplotlib import pyplot as pt #FOR LOGSHII



# THE PARAMETERS (amplitude, freq - Hz; duration - s; samples - times), POINT'S MASSIVE (s)

phase = 0

amp = 0.1

dB_step = 2

freq = 440

duration = 1

sample_rate = 44100       # for .wav it's better to use either 44100 or 48000  

t = np.arange(sample_rate * duration) / sample_rate



#FLAGS and FUNCS

Play = 1

def up_freq():
    global freq
    if freq<10000:
        freq*=2**(1/12)
    
def down_freq():
    global freq
    if freq>20:
        freq/=2**(1/12)
        
def up_amp():
    global amp
    if amp<1:
        amp*= 10**(dB_step/20)
    
def down_amp():
    global amp
    if amp>0.001:
        amp/= 10**(dB_step/20)
    
def change_play():
    global Play
    Play = 1 - Play
    
kb.add_hotkey('right', up_freq)
kb.add_hotkey('left', down_freq)
kb.add_hotkey('up', up_amp)
kb.add_hotkey('down', down_amp)

kb.add_hotkey('space', change_play)


def buf_Phase_callback(outdata, frames, time, status):
    global phase
    #COUNTIN A STEP
    d_phase = 2*np.pi*freq/sample_rate
    
    #CREATIN A FRAMES AND A BUF
    if Play:
        for i in range(frames):
            outdata[i,0] = (amp*np.sin(phase))
            phase+=d_phase
    else:
        for i in range(frames):
            outdata[i,0] = 0



# #PLAYIN AND SHII

with sd.OutputStream(blocksize=512,
                     samplerate = sample_rate,
                     channels = 1,
                     callback = buf_Phase_callback):
    kb.wait()
    input()





