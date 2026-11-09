# GENERATOR OF THE TONES AND ACCORDS



# ALL THE IMPORTS
import numpy as np
import sounddevice as sd
import keyboard as kb
import time

from matplotlib import pyplot as pt #FOR LOGSHII



# THE PARAMETERS (amplitude, freq - Hz; duration - s; samples - times), POINT'S MASSIVE (s)

# t = np.arange(sample_rate * duration) / sample_rate
     
     
     
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
    'a': white_notes['Do'],
    's': white_notes['Re'],
    'd': white_notes['Me'],
    'f': white_notes['Fa'],
    'g': white_notes['So'],
    'h': white_notes['La'],
    'j': white_notes['Si'],
    'w': black_notes['Do_dies'],
    'e': black_notes['Re_dies'],
    't': black_notes['So_bimole'],
    'y': black_notes['La_bimole'],
    'u': black_notes['La_dies'],
}

#All the logic
class Modulator:
    def __init__(
        self, 
        phase, 
        amp, 
        # aim_amp, 
        dB_step, 
        freq, 
        # aim_freq, 
        duration, 
        sample_rate, 
        Wave,
        Play,
        ):
        
        # self.__dict__.update({p: m for p, m in locals().items() if p!= 'self'})
        self.phase = phase
        self.amp = amp
        self.aim_amp = amp
        self.dB_step = dB_step
        self.freq = freq
        self.aim_freq = freq
        self.duration = duration
        self.sample_rate = sample_rate
        self.Wave = Wave
        self.Play = Play
    
    def wave_change(self):
        self.Wave += 1

    def up_freq(self):
        if self.freq<10000:
            self.aim_freq*=2**(1/12)
        
    def down_freq(self):
        if self.freq>20:
            self.aim_freq/=2**(1/12)
            
    def set_freq(self, l):
        self.aim_freq = note_pad[l]
            
    def up_amp(self):
        if self.amp<1:
            self.aim_amp*= 10**(self.dB_step/20)
        
    def down_amp(self):
        if self.amp>0.001:
            self.aim_amp/= 10**(self.dB_step/20)
        
    def change_play(self):
        self.Play = 1 - self.Play
        
modulator = Modulator(0,
                    #   0.1,
                      0.1,
                      2,
                      440,
                    #   440,
                      1,
                      44100,
                    #   np.arange(44100 * 1) / 44100,
                      0,
                      1
                      )

Is_Pressed = 0

kb_router = {
    'right': modulator.up_freq,
    'left': modulator.down_freq,
    'up': modulator.up_amp,
    'down': modulator.down_amp,
    'alt': modulator.wave_change,
    'space': modulator.change_play,
}

# synth_kb_router = {
#     'a': modulator.set_freq,
#     's': mo
# }

def kb_handler(event):
    if event.name not in 'asdfghjwetyu':
        kb_router[event.name]()
        return
    # synth_kb_router[event.name](event.name)
    else:
        if event.event_type == 'down':
            Is_Pressed = 1   
            modulator.set_freq(event.name)
        elif event.event_type == 'up':
            Is_Pressed = 0
            modulator.aim_freq = 440

def Sound(module):
    def buf_Phase_callback(outdata, frames, time, status):
        
        target_amp = module.aim_amp if module.Play else 0
        
        curr_freq = np.geomspace(module.freq, module.aim_freq, frames, endpoint = False)
        curr_d_phase = 2*np.pi*curr_freq/module.sample_rate
        curr_amp = np.linspace(module.amp, target_amp, frames, endpoint = False)
        curr_phase = module.phase + np.cumsum(curr_d_phase) - curr_d_phase

        signals = [
            (np.sin(curr_phase)),
            (np.sign(np.sin(curr_phase))),
            (np.mod(curr_phase/(2*np.pi), 1) - 1),
            (np.abs(2*np.mod(curr_phase/(2*np.pi), 1) - 1))
            ]
        
        outdata[:, 0] = curr_amp * signals[module.Wave%4]
        
        module.phase = (module.phase + np.cumsum(curr_d_phase)[-1])%(2*np.pi)
        module.amp = target_amp
        module.freq = module.aim_freq



    # #PLAYIN AND SHII

    with sd.OutputStream(blocksize = 256,
                        samplerate = module.sample_rate,
                        channels = 1,
                        callback = buf_Phase_callback):
        # kb.on_press(kb_press_handler)
        # kb.on_release(kb_release_handler)
        kb.hook(kb_handler)
        kb.wait()
        input()
        
Sound(modulator)

