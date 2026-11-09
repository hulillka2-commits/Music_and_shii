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

Wave = 0

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
        
# MIDI: (Do: n= 60) f = 440 * 2 **((n - 69) / 12)

def MIDI_(n):
    return (440 * 2 **((n - 69) / 12))

white_notes = {
    'Do': MIDI_(60),
    'Re': MIDI_(62),
    'Me': MIDI_(64),
    'Fa': MIDI_(65),
    'So': MIDI_(67),
    'La': MIDI_(69),
    'Si': MIDI_(71),
}

black_notes = {
    'Do_dies': MIDI_(61),
    'Re_dies': MIDI_(63),
    'So_bimole': MIDI_(66),
    'La_bimole': MIDI_(68),
    'La_dies': MIDI_(70),
}

note_pad = {
    'A': white_notes['Do'],
    'S': white_notes['Re'],
    'D': white_notes['Me'],
    'F': white_notes['Fa'],
    'G': white_notes['So'],
    'H': white_notes['La'],
    'J': white_notes['Si'],
    'W': black_notes['Do_dies'],
    'E': black_notes['Re_dies'],
    'T': black_notes['So_bimole'],
    'Y': black_notes['La_bimole'],
    'U': black_notes,
}


class Modulator():
    
    def wave_change(self):
        global Wave
        Wave += 1

    def up_freq(self):
        global aim_freq
        if freq<10000:
            aim_freq*=2**(1/12)
        
    def down_freq(self):
        global aim_freq
        if freq>20:
            aim_freq/=2**(1/12)
            
    def up_amp(self):
        global aim_amp
        if amp<1:
            aim_amp*= 10**(dB_step/20)
        
    def down_amp(self):
        global aim_amp
        if amp>0.001:
            aim_amp/= 10**(dB_step/20)
        
    def change_play(self):
        global Play
        Play = 1 - Play
        
modulator = Modulator()

kb.add_hotkey('right', modulator.up_freq)
kb.add_hotkey('left', modulator.down_freq)
kb.add_hotkey('up', modulator.up_amp)
kb.add_hotkey('down', modulator.down_amp)
kb.add_hotkey('alt', modulator.wave_change)

kb.add_hotkey('space', modulator.change_play)


def buf_Phase_callback(outdata, frames, time, status):
    global phase
    global amp
    global freq
    
    target_amp = aim_amp if Play else 0
    
    curr_freq = np.geomspace(freq, aim_freq, frames, endpoint = False)
    curr_d_phase = 2*np.pi*curr_freq/sample_rate
    curr_amp = np.linspace(amp, target_amp, frames, endpoint = False)
    curr_phase = phase + np.cumsum(curr_d_phase) - curr_d_phase

    signals = [
        (np.sin(curr_phase)),
        (np.sign(np.sin(curr_phase))),
        (np.mod(curr_phase/(2*np.pi), 1) - 1),
        (np.abs(2*np.mod(curr_phase/(2*np.pi), 1) - 1))
        ]
    
    outdata[:, 0] = curr_amp * signals[Wave%4]
    
    phase = (phase + np.cumsum(curr_d_phase)[-1])%(2*np.pi)
    amp = target_amp
    freq = aim_freq



# #PLAYIN AND SHII

with sd.OutputStream(blocksize = 256,
                     samplerate = sample_rate,
                     channels = 1,
                     callback = buf_Phase_callback):
    kb.wait()
    input()

