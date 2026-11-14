# THE SYNTHESIZER

# ALL THE IMPORTS
import numpy as np
import sounddevice as sd
import keyboard as kb
import time

from matplotlib import pyplot as plt #FOR LOGSHII



# THE PARAMETERS (amplitude, freq - Hz; duration - s; samples - times), POINT'S MASSIVE (s)

# MIDI: (Do: n= 60) f = 440 * 2 **((n - 69) / 12)

def MIDI_(n):
    return (440 * 2 **((n - 69) / 12))

notes = {
    'Do': MIDI_(60),
    'Do_dies': MIDI_(61),
    'Re': MIDI_(62),
    'Re_dies': MIDI_(63),
    'Me': MIDI_(64),
    'Fa': MIDI_(65),
    'So_bimole': MIDI_(66),
    'So': MIDI_(67),
    'La_bimole': MIDI_(68),
    'La': MIDI_(69),
    'La_dies': MIDI_(70),
    'Si': MIDI_(71),
}

note_pad = {
    'a': notes['Do'],
    's': notes['Re'],
    'd': notes['Me'],
    'f': notes['Fa'],
    'g': notes['So'],
    'h': notes['La'],
    'j': notes['Si'],
    'w': notes['Do_dies'],
    'e': notes['Re_dies'],
    't': notes['So_bimole'],
    'y': notes['La_bimole'],
    'u': notes['La_dies'],
}

#All the logic

adsr_phases_params = {
    'calm': {
        'aim': 0,
        'time': 1,
        'vector': 1,
            },
    'attack': {
        'aim': 1,
        'time': 0.1,
        'vector': 1,
            },
    'decay': {
        'aim': 0.3,
        'time': 0.5,
        'vector': -1,
            },
    'sustain': {
        'aim': 0.3,
        'time': 1,
        'vector': 1,
            },
    'release': {
        'aim': 0,
        'time': 1,
        'vector': -1,
            },
    }

# ОБЩЕЕ ИЗ Track: 
# - amp, dB_step, sample_rate, Wave, aim_amp, adsr_phases,
# У КАЖДОЙ НОТЫ РАЗНОЕ:
# - phase, freq, aim_freq, Is_Pressed, adsr, env, aim_env, last_env
# Play - 50/50

class Track:
    def __init__(
        self, 
        phase, 
        dB_step, 
        freq, 
        ):
        
        # self.__dict__.update({p: m for p, m in locals().items() if p!= 'self'})
        self.phase = phase
        self.dB_step = dB_step
        self.freq = freq
        self.aim_freq = freq
        self.Is_Pressed = 0
        self.adsr = 'calm'
        self.env = 0
        self.aim_env = 0
        self.last_env = 0
        
    def up_freq(self):
        if self.freq<10000:
            self.aim_freq*=2**(1/12)
        
    def down_freq(self):
        if self.freq>20:
            self.aim_freq/=2**(1/12)
            
    def set_freq(self, l):
        self.aim_freq = note_pad[l]
            
trackk = Track(0,
                2,
                1,
                )

note_track = {
    'a': Track(0, 2, note_pad['a']),
    's': Track(0, 2, note_pad['s']),
    'd': Track(0, 2, note_pad['d']),
    'f': Track(0, 2, note_pad['f']),
    'g': Track(0, 2, note_pad['g']),
    'h': Track(0, 2, note_pad['h']),
    'j': Track(0, 2, note_pad['j']),
    'w': Track(0, 2, note_pad['w']),
    'e': Track(0, 2, note_pad['e']),
    't': Track(0, 2, note_pad['t']),
    'y': Track(0, 2, note_pad['y']),
    'u': Track(0, 2, note_pad['u']),
}

tracks = set(
    
)


class Synthesizer():
    def __init__(
        self,
        amp,
        dB_step,
        sample_rate,
        Wave,
        adsr_phases,
        ):

        self.amp = amp
        self.dB_step = dB_step
        self.sample_rate = sample_rate
        self.Wave = Wave
        self.aim_amp = amp
        self.adsr_phases = adsr_phases
        self.Play = 1
                
    def change_play(self):
        self.Play = 1 - self.Play
                
    def wave_change(self):
        self.Wave += 1

    def up_amp(self):
        if self.amp<1:
            self.aim_amp*= 10**(self.dB_step/20)
        
    def down_amp(self):
        if self.amp>0.001:
            self.aim_amp/= 10**(self.dB_step/20)
        
    def change_play(self):
        self.Play = 1 - self.Play
        
    def ADSR(self, module):

        if module.adsr == 'calm':
            module.aim_env = 0
            module.env = 0
            module.last_env = 0
  
        elif module.adsr == 'attack':
            module.aim_env = self.adsr_phases[module.adsr]['aim']
            if module.env >= module.aim_env:
                module.adsr = 'decay'
                module.last_env = module.env

        elif module.adsr == 'decay':
            module.aim_env = self.adsr_phases[module.adsr]['aim']
            if module.env <= module.aim_env:
                module.adsr = 'sustain'
                module.last_env = module.env

        elif module.adsr == 'sustain':
            module.aim_env = self.adsr_phases[module.adsr]['aim']    
            module.last_env = module.env      
            
        elif module.adsr == 'release':
            module.aim_env = self.adsr_phases[module.adsr]['aim']
            if module.env <= self.adsr_phases[module.adsr]['aim']:
                module.adsr = 'calm'
                module.env = 0
                module.last_env = 0
                
    
        
    def Sound(self, module):
        
        kb_router = {
            'right': module.up_freq,
            'left': module.down_freq,
            'up': self.up_amp,
            'down': self.down_amp,
            'alt': self.wave_change,
            'space': self.change_play,
        }
        
        def kb_handler(event):
            if event.event_type == 'down': 
                print('down')
                if event.name not in note_pad:
                    kb_router.get(event.name)()
                    return
                
                tracks.add(note_track[event.name])
                if not note_track[event.name].Is_Pressed:
                    note_track[event.name].adsr = 'attack'
                note_track[event.name].Is_Pressed = 1
                
            elif event.event_type == 'up':
                print('up')
                if event.name not in note_pad:
                    return

                note_track[event.name].Is_Pressed = 0
                note_track[event.name].last_env = note_track[event.name].env
                note_track[event.name].adsr = 'release'

                print('\n')
        
        def buf_Phase_callback(outdata, frames, time, status):
            signals = np.zeros((frames, ))

            if self.Play:
                target_amp = self.aim_amp
                # curr_amp = np.linspace(self.amp, target_amp, frames, endpoint = False)

                for track in tracks:
                    target_freq = track.aim_freq
                    self.ADSR(track)
                    target_env = track.aim_env
                    block_count = self.adsr_phases[track.adsr]['time'] / ((frames/self.sample_rate))
                    #delta_env = 1(distance) / (module.adsr_phases[module.adsr]['time'] * module.sample_rate) - alternate formula
                    delta_env = (track.aim_env - track.last_env)/ block_count
                    
                    curr_env = np.linspace(track.env, (track.env + delta_env), frames, endpoint = False)
                    # curr_amp = curr_env*np.linspace(self.amp, target_amp, frames, endpoint = False)

                    def otladka():
                        # print(f'\n')
                        print(f'phase: {track.adsr}')
                        # print(f'env: {module.env}')
                        # print(f'target_env: {target_env}')
                        # print(f'block_count: {block_count}')
                        # print(f'last_env: {module.last_env}')
                        # print(f'aim_env: {module.aim_env}')
                        # print(f'delta_env: {delta_env}')
                        print(f'length: {len(tracks)}')
                        
                    # otladka()
                
                
                    curr_freq = np.geomspace(track.freq, target_freq, frames, endpoint = False)
                    curr_d_phase = 2*np.pi*curr_freq/self.sample_rate
                    curr_phase = track.phase + np.cumsum(curr_d_phase) - curr_d_phase
                    
                    # if module.env + delta_env <0:
                    #     delta_env = -1*module.env
                    if track.env <= 2 and track.env >= 0:
                        track.env += delta_env
                        
                    track.phase = (track.phase + np.cumsum(curr_d_phase)[-1])%(2*np.pi)
                    self.amp = target_amp
                    track.freq = target_freq
                    
                    
                    signal = [
                        (np.sin(curr_phase)),
                        (np.sign(np.sin(curr_phase))),
                        (np.mod(curr_phase/(2*np.pi), 1) - 1),
                        (np.abs(2*np.mod(curr_phase/(2*np.pi), 1) - 1))
                        ]
                    
                    signals += curr_env*signal[self.Wave%4]
                    # if track.adsr == 'calm':
                    #     # tracks.pop(tracks.index(track))
                    #     tracks.remove(track)
                    
                    
                
            else:
                delta_env = 0
                target_amp = 0
                curr_amp = np.linspace(self.amp, target_amp, frames, endpoint = False)



            curr_amp = np.linspace(self.amp, target_amp, frames, endpoint = False)

            outdata[:, 0] = curr_amp * signals

                

        # #PLAYIN AND SHII
        # try:
        with sd.OutputStream(blocksize = 256,
                            samplerate = self.sample_rate,
                            channels = 1,
                            callback = buf_Phase_callback):
            kb.hook(kb_handler)
            kb.wait('esc')

Syn = Synthesizer(0.1,
                  2,
                  44100,
                  0,
                adsr_phases_params,
                  )        
Syn.Sound(trackk)
