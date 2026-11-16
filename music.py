# THE SYNTHESIZER

# ALL THE IMPORTS
import numpy as np
import sounddevice as sd
import keyboard as kb
import time

from matplotlib import pyplot as plt #FOR LOGSHII



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

# calm and sustain phases dgaf about time or vector (consts)

adsr_phases_params = {
    'calm': {
        'aim': 0,
        'time': 1,
        'vector': 1,
            },
    'attack': {
        'aim': 1,
        'time': 0.07,
        'vector': 1,
            },
    'decay': {
        'aim': 0.3,
        'time': 0.1,
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

#ALL THE LOGIC AND FUNCS
class Note:
    def __init__(
        self, 
        freq, 
        ):
        
        # self.__dict__.update({p: m for p, m in locals().items() if p!= 'self'})
        self.phase = 0
        self.freq = freq
        self.aim_freq = freq
        self.Is_Pressed = 0
        self.adsr = 'calm'
        self.env = 0
        self.aim_env = 0
        self.last_env = 0
        self.last_signal = [0]
        self.curr_signal = [0]
        
        

note_track = {
    'a': 
        Note( 
              note_pad['a']),
    's': 
        Note(
              note_pad['s']),
    'd': 
        Note( 
              note_pad['d']),
    'f': 
        Note( 
              note_pad['f']),
    'g': 
        Note( 
              note_pad['g']),
    'h': 
        Note( 
              note_pad['h']),
    'j': 
        Note( 
              note_pad['j']),
    'w': 
        Note( 
              note_pad['w']),
    'e': 
        Note( 
              note_pad['e']),
    't': 
        Note( 
              note_pad['t']),
    'y': 
        Note( 
              note_pad['y']),
    'u': 
        Note( 
              note_pad['u']),
}

tracks = set(
                )


class Synthesizer():
    def __init__(
        self,
        amp,
        dB_step,
        sample_rate,
        # wave,
        adsr_phases,
        lpf,
        d_lfo,
        f_lfo,
        
        ):

        self.amp = amp
        self.aim_amp = amp
        self.dB_step = dB_step
        self.lpf = lpf
        self.aim_lpf = lpf
        self.sample_rate = sample_rate
        self.wave = 0
        self.adsr_phases = adsr_phases
        self.Play = 1
        
        self.d_lfo = d_lfo
        self.f_lfo = f_lfo
        self.k_lfo = 0
        
        self.dB_koef = 10**(self.dB_step/20)
                
                
        self.lfo_phase = 0
        
                
                
    def LFO(self):
        lfo_curr_d_phase = np.full(256, 2*np.pi*self.f_lfo/self.sample_rate)
        # print(lfo_curr_d_phase)
        # lfo_curr_phase = self.lfo_phase + lfo_curr_d_phase * (256-1) 
        lfo_curr_phase = self.lfo_phase + np.cumsum(lfo_curr_d_phase)

        # self.lfo_phase = (self.lfo_phase + lfo_curr_d_phase * (256))%(2*np.pi)
        
        self.lfo_phase = (self.lfo_phase + np.cumsum(lfo_curr_d_phase)[-1])%(2*np.pi)

                
        # return self.Wave_shaper(lfo_curr_phase)
        return np.sin(lfo_curr_phase)
        
        
        
    def change_play(self):
        self.Play = 1 - self.Play
                
    def Wave_change(self):
        self.wave += 1

    def Wave_shaper(self, curr_phase):
        shapes = [      
                (np.sin(curr_phase)),
                (np.sign(np.sin(curr_phase))),
                (np.mod(curr_phase/(2*np.pi), 1) - 1),
                (np.abs(2*np.mod(curr_phase/(2*np.pi), 1) - 1)),
                        ]
        return shapes[self.wave%4]

    def Up_lpf(self):
        if self.aim_lpf * self.dB_koef < 1:
            self.aim_lpf *= self.dB_koef
            
    def Down_lpf(self):
        if self.aim_lpf / self.dB_koef > 0.005:
            self.aim_lpf /= self.dB_koef

    def Up_amp(self):
        if self.aim_amp / self.dB_koef < 1:
            self.aim_amp *= self.dB_koef
        
    def Down_amp(self):
        if self.aim_amp / self.dB_koef > 0.001:
            self.aim_amp /= self.dB_koef
        
    def Change_play(self):
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
                
    #LPF formula - curr_exit = last_exit + k * (curr_enter - last_exit)
                
    def LPF(self, track):        
        track.curr_signal[0] = track.last_signal[-1] + self.lpf * (track.curr_signal[0] - track.last_signal[-1])
        for i in range(1, len(track.curr_signal)):
            track.curr_signal[i] = track.curr_signal[i-1] + self.lpf * (track.curr_signal[i] - track.curr_signal[i-1])
        return track.curr_signal
        
    def Sound(self, tracks):
        
        kb_router = {
            # 'right': module.up_freq,
            # 'left': module.down_freq,
            'right': self.Up_lpf,
            'left': self.Down_lpf,
            'up': self.Up_amp,
            'down': self.Down_amp,
            'alt': self.Wave_change,
            'space': self.Change_play,
        }
        
        def kb_handler(event):
            if event.event_type == 'down': 
                # print('down')
                if event.name not in note_pad:
                    kb_router.get(event.name)()
                    return
                
                tracks.add(note_track[event.name])
                if not note_track[event.name].Is_Pressed:
                    note_track[event.name].adsr = 'attack'
                note_track[event.name].Is_Pressed = 1
                
            elif event.event_type == 'up':
                # print('up')
                if event.name not in note_pad:
                    return

                note_track[event.name].Is_Pressed = 0
                note_track[event.name].last_env = note_track[event.name].env
                note_track[event.name].adsr = 'release'


        
        def buf_Phase_callback(outdata, frames, time, status):
            signals = np.zeros((frames, ))

            if self.Play:
                target_amp = self.aim_amp
                target_lpf = self.aim_lpf
                
                lfo_wave = self.LFO()

                for track in tracks:
                    target_freq = track.aim_freq
                    self.ADSR(track)
                    
                    block_count = self.adsr_phases[track.adsr]['time'] / ((frames/self.sample_rate))
                    delta_env = (track.aim_env - track.last_env)/ block_count
                    
                    curr_env = np.linspace(track.env, (track.env + delta_env), frames, endpoint = False)


                    def otladka():
                        print(f'\n')
                        # print(f'phase: {track.adsr}')
                        # print(f'env: {module.env}')
                        # print(f'block_count: {block_count}')
                        # print(f'last_env: {module.last_env}')
                        # print(f'aim_env: {track.aim_env}')
                        # print(f'amp: {self.amp}')
                        # print(f'delta_env: {delta_env}')
                        # print(f'length: {len(tracks)}')
                        # print(f'lfo: {self.lfo_phase}')
                        
                    # otladka()
                
                
                    curr_freq = np.geomspace(track.freq, target_freq, frames, endpoint = False) 
                    curr_d_phase = 2*np.pi*curr_freq/self.sample_rate
                    curr_phase = track.phase + np.cumsum(curr_d_phase) - curr_d_phase
                    
                    # #LFO ----------------
                    
                    # lfo_curr_d_phase = 2*np.pi*self.f_lfo/self.sample_rate
                    # lfo_curr_phase = self.lfo_phase + np.cumsum(lfo_curr_d_phase) - lfo_curr_d_phase
                    # lfo_wave = self.Wave_shaper(lfo_curr_phase)
                    
                    
                    
                    # -------------------
                    
                    # if module.env + delta_env <0:
                    #     delta_env = -1*module.env
                    if track.env + delta_env <= 2 and track.env + delta_env >= 0:
                    # if (self.adsr_phases[track.adsr]['vector'])*(track.env + delta_env) < (self.adsr_phases[track.adsr]['vector'])*(track.aim_env):
                        track.env += delta_env
                        
                    # else:
                    #     track.env += (track.aim_env - (track.env + delta_env))
    
                    track.phase = (track.phase + np.cumsum(curr_d_phase)[-1])%(2*np.pi)
                    self.lpf = target_lpf
                    
                    track.freq = target_freq
                    
                    track.curr_signal = self.Wave_shaper(curr_phase)
                    
                    track.curr_signal = self.LPF(track)
                    
                    signals += curr_env*track.curr_signal
                    track.last_signal = track.curr_signal                    
                
            else:
                delta_env = 0
                target_amp = 0
                
                self.lfo_phase = 0
                lfo_wave = 0

            
            
            curr_amp = np.linspace(self.amp, target_amp, frames, endpoint = False) * ( 1 + self.d_lfo * lfo_wave )
                    

            self.amp = target_amp

            
            outdata[:, 0] = curr_amp * signals

                

        # #PLAYIN AND SHII
        
        with sd.OutputStream(blocksize = 256,
                            samplerate = self.sample_rate,
                            channels = 1,
                            callback = buf_Phase_callback):
            kb.hook(kb_handler)
            kb.wait('esc')

Syn = Synthesizer(0.1,
                0.5,
                44100,
                # 0,
                adsr_phases_params,
                0.1,
                0.5,
                5,
                  )        
Syn.Sound(tracks)
