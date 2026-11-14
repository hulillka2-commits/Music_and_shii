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


# class Vocie:
#     def __init__(
#         self,
#         phase,
#         freq,
#         aim_freq,
#         Is_Pressed,
#         adsr,
#         env,
#         aim_env,
#         last_env,
#         ):
#         self.phase = phase
#         self.freq = freq
#         self.aim_freq = freq
#         self.Is_Pressed = 0
#         self.adsr = 'calm'
#         self.env = 0
#         self.last_env = 0
#         self.aim_env = 0
        
class Track:
    def __init__(
        self, 
        phase, 
        # amp, 
        dB_step, 
        freq, 
        # sample_rate, 
        # Wave,
        # adsr_phases,
        # env,
        # last_env,
        # adsr_pos,
        ):
        
        # self.__dict__.update({p: m for p, m in locals().items() if p!= 'self'})
        self.phase = phase
        # self.amp = amp
        # self.aim_amp = amp
        self.dB_step = dB_step
        self.freq = freq
        self.aim_freq = freq
        # self.sample_rate = sample_rate
        # self.Wave = Wave
        # self.Play = 1
        self.Is_Pressed = 0
        # self.adsr_phases = adsr_phases
        self.adsr = 'calm'
        self.env = 0
        self.aim_env = 0
        self.last_env = 0
        # self.adsr_poses = list(adsr_phases.keys())
        # self.adsr_pos = 5
        
    
    # def ADSR(self):
    #     # phase = self.adsr_phases[self.adsr_poses[self.adsr_pos%5]]
    #     # self.aim_env = phase['aim']
    #     # if phase['vector']*self.env >= phase['vector']*self.aim_env:
    #     #     self.adsr_pos += 1 
    #     #     self.last_env = self.env
        
    #     # if self.Is_Pressed:
    #     #     self.adsr = 'attack'
    #     #     print("CHANGE 1.1")
    #     # else:
    #     #     self.adsr = 'release'
    #     #     print("CHANGE 1.4")

        
    #     if self.adsr == 'calm':
    #         self.aim_env = 0
    #         self.env = 0
    #         self.last_env = 0
    #         # print("CHANGE 2.5")
  
    #     elif self.adsr == 'attack':
    #         self.aim_env = self.adsr_phases[self.adsr]['aim']
    #         if self.env >= self.aim_env:
    #             self.adsr = 'decay'
    #             self.last_env = self.env
    #             # print("CHANGE 2.1")

    #     elif self.adsr == 'decay':
    #         self.aim_env = self.adsr_phases[self.adsr]['aim']
    #         if self.env <= self.aim_env:
    #             self.adsr = 'sustain'
    #             self.last_env = self.env
    #             # print("CHANGE 2.2")

    #     elif self.adsr == 'sustain':
    #         self.aim_env = self.adsr_phases[self.adsr]['aim']    
    #         self.last_env = self.env   
    #         # print("CHANGE 2.3")        
            
    #     elif self.adsr == 'release':
    #         self.aim_env = self.adsr_phases[self.adsr]['aim']
    #         if self.env <= self.adsr_phases[self.adsr]['aim']:
    #             self.adsr = 'calm'
    #             # print("CHANGE 2.4")
    #             self.env = 0
    #             self.last_env = 0
                
    # def wave_change(self):
    #     self.Wave += 1

    def up_freq(self):
        if self.freq<10000:
            self.aim_freq*=2**(1/12)
        
    def down_freq(self):
        if self.freq>20:
            self.aim_freq/=2**(1/12)
            
    def set_freq(self, l):
        self.aim_freq = note_pad[l]
            
    # def up_amp(self):
    #     if self.amp<1:
    #         self.aim_amp*= 10**(self.dB_step/20)
        
    # def down_amp(self):
    #     if self.amp>0.001:
    #         self.aim_amp/= 10**(self.dB_step/20)
        
    # def change_play(self):
    #     self.Play = 1 - self.Play
        
trackk = Track(0,
                # 0.1,
                2,
                1,
                # 44100,
                # 0,
                # adsr_phases_params,
            #   0.1,
            #   0,
            #   0,
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

tracks = [
    
]


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
            # start,end=0,0
            if event.event_type == 'down': 
                # start = time.perf_counter()
                print('down')
                if event.name not in note_pad:
                    kb_router.get(event.name)()
                    return
                module.set_freq(event.name)
                
                tracks.append(note_track[event.name])
                
                if not module.Is_Pressed:
                    module.adsr = 'attack'
                    # print("CHANGE 1.1")
                module.Is_Pressed = 1  
            elif event.event_type == 'up':
                end = time.perf_counter()
                print('up')
                if event.name not in note_pad:
                    return
                module.Is_Pressed = 0
                # print("CHANGE 1.4")
                module.last_env = module.env
                module.adsr = 'release'
                # print(start-end)
                print('\n')
        
        shii = []
        
        def buf_Phase_callback(outdata, frames, time, status):
            
            target_freq = module.aim_freq
            if self.Play:
                target_amp = self.aim_amp

                self.ADSR(module)
                target_env = module.aim_env
                block_count = self.adsr_phases[module.adsr]['time'] / ((frames/self.sample_rate))
                #delta_env = 1(distance) / (module.adsr_phases[module.adsr]['time'] * module.sample_rate) - alternate formula
                delta_env = (module.aim_env - module.last_env)/ block_count
                
                curr_env = np.linspace(module.env, (module.env + delta_env), frames, endpoint = False)
                curr_amp = curr_env*np.linspace(self.amp, target_amp, frames, endpoint = False)
                
                shii.append(curr_env)

                def otladka():
                    print(f'\n')
                    print(f'phase: {module.adsr}')
                    print(f'env: {module.env}')
                    print(f'target_env: {target_env}')
                    print(f'block_count: {block_count}')
                    print(f'last_env: {module.last_env}')
                    print(f'aim_env: {module.aim_env}')
                    print(f'delta_env: {delta_env}')
                    
                # otladka()
            
            else:
                delta_env = 0
                target_amp = 0
                curr_amp = np.linspace(self.amp, target_amp, frames, endpoint = False)
            
            curr_freq = np.geomspace(module.freq, target_freq, frames, endpoint = False)
            curr_d_phase = 2*np.pi*curr_freq/self.sample_rate
            curr_phase = module.phase + np.cumsum(curr_d_phase) - curr_d_phase
            
            signals = [
                (np.sin(curr_phase)),
                (np.sign(np.sin(curr_phase))),
                (np.mod(curr_phase/(2*np.pi), 1) - 1),
                (np.abs(2*np.mod(curr_phase/(2*np.pi), 1) - 1))
                ]
            
            outdata[:, 0] = curr_amp * signals[self.Wave%4]
            # if module.env + delta_env <0:
            #     delta_env = -1*module.env
            if module.env <= 2 and module.env >= 0:
                module.env += delta_env
                # print(module.env, module.amp)
                
            module.phase = (module.phase + np.cumsum(curr_d_phase)[-1])%(2*np.pi)
            self.amp = target_amp
            module.freq = target_freq
            
                

        # #PLAYIN AND SHII
        # try:
        with sd.OutputStream(blocksize = 256,
                            samplerate = self.sample_rate,
                            channels = 1,
                            callback = buf_Phase_callback):
            kb.hook(kb_handler)
            kb.wait('esc')
            # input()
        # except KeyboardInterrupt:
            # pass
            
        plt.plot(shii)
        plt.show()

Syn = Synthesizer(0.1,
                  2,
                  44100,
                  0,
                adsr_phases_params,
                  )        
Syn.Sound(trackk)
