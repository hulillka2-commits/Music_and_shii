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

aim_amp = amp

dB_step = 2

freq = 440

aim_freq = freq

duration = 1

sample_rate = 44100       # for .wav it's better to use either 44100 or 48000  

t = np.arange(sample_rate * duration) / sample_rate



#FLAGS and FUNCS

Play = 1

# class Signal_Modulations:
#     def __init__(self, 
#                  amp,
#                  freq,
#                  ):
#         self.amp = amp
#         self.freq = freq
    
#     def up_freq(self):
#         if self.freq<10000:
#             self.freq*=2**(1/12)
    
#     def down_freq(self):
#         if self.freq>20:
#             self.freq/=2**(1/12)
            
#     def up_amp(self):
#         if self.amp<1:
#             self.amp*= 10**(dB_step/20)
            
#     def down_amp(self):
#         if self.amp>0.001:
#             self.amp/= 10**(dB_step/20)
        

def up_freq():
    global aim_freq
    if freq<10000:
        aim_freq*=2**(1/12)
    
def down_freq():
    global aim_freq
    if freq>20:
        aim_freq/=2**(1/12)
        
def up_amp():
    global aim_amp
    if amp<1:
        aim_amp*= 10**(dB_step/20)
    
def down_amp():
    global aim_amp
    if amp>0.001:
        aim_amp/= 10**(dB_step/20)
    
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
    global amp
    global freq
    
    target_amp = aim_amp if Play else 0
    # target_phase = phase + d_phase*frames
    d_amp = (target_amp - amp)/frames
    d_freq = (aim_freq - freq)/frames
    
    curr_freq = np.geomspace(freq, aim_freq, frames, endpoint = False)
    curr_d_phase = 2*np.pi*curr_freq/sample_rate
    curr_amp = np.linspace(amp, target_amp, frames, endpoint = False)
    # curr_phase = np.linspace(phase, target_phase, frames, endpoint = False)
    curr_phase = phase + np.cumsum(curr_d_phase) - curr_d_phase

    # curr_phase = phase + d_phase*nums
    # curr_amp = amp + d_amp*nums
    
    outdata[:, 0] = (curr_amp*(np.sin(curr_phase)))
    
    phase = (phase + np.cumsum(curr_d_phase)[-1])%(2*np.pi)
    amp = aim_amp
    freq = aim_freq



# #PLAYIN AND SHII

with sd.OutputStream(blocksize=512,
                     samplerate = sample_rate,
                     channels = 1,
                     callback = buf_Phase_callback):
    kb.wait()
    input()

