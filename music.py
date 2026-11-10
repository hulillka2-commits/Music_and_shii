# THE SYNTHESIZER

# ALL THE IMPORTS
import numpy as np
import sounddevice as sd
import keyboard as kb
import time

from matplotlib import pyplot as pt #FOR LOGSHII



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

adsr_phases = {
    'calm': {
        'aim': 0,
        'time': 1
        },
    'attack': {
        'aim': 1,
        'time': 0.5,
            },
    'decay': {
        'aim': 0.3,
        'time': 0.8,
            },
    'sustain': {
        'aim': 0.3,
        'time': 1,
            },
    'release': {
        'aim': 0,
        'time': 0.5,
            },
}
class Modulator:
    def __init__(
        self, 
        phase, 
        amp, 
        dB_step, 
        freq, 
        sample_rate, 
        Wave,
        adsr_phase,
        env,
        last_env,
        ):
        
        # self.__dict__.update({p: m for p, m in locals().items() if p!= 'self'})
        self.phase = phase
        self.amp = amp
        self.aim_amp = amp
        self.dB_step = dB_step
        self.freq = freq
        self.aim_freq = freq
        self.sample_rate = sample_rate
        self.Wave = Wave
        self.Play = 1
        self.Is_Pressed = 0
        self.adsr_phases = adsr_phase
        self.adsr = 'calm'
        self.env = env
        self.aim_env = env
        self.last_env = last_env
        
    
    def ADSR(self):
        # print("OMAGAD")
        # print(f'{self.adsr}')
        
        if self.adsr == 'calm':
            self.aim_env = 0
            self.env = 0
            self.last_env = 0
        
        if self.adsr == 'attack':
            print("ITS ATTACK")
            self.aim_env = self.adsr_phases[self.adsr]['aim']
            if self.env >= self.aim_env:
                print('OMG ITS BIGGER')
                self.adsr = 'decay'
                self.last_env = self.env
                
        elif self.adsr == 'decay':
            print("ITS DECAY")
            self.aim_env = self.adsr_phases[self.adsr]['aim']
            if self.env <= self.aim_env:
                self.adsr = 'sustain'
                self.last_env = self.env
            
        elif self.adsr == 'sustain':
            print('ITS SUSTAIN')
            self.aim_env = self.adsr_phases[self.adsr]['aim']    
            self.last_env = self.env            
            
        elif self.adsr == 'release':
            self.aim_env = self.adsr_phases[self.adsr]['aim']
            if self.env <= self.adsr_phases[self.adsr]['aim']:
                self.adsr = 'calm'
                self.env = 0
                self.last_env = 0
                
        
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
                      0.1,
                      2,
                      440,
                      44100,
                      0,
                      adsr_phases,
                      0.1,
                      0,
                      )



kb_router = {
    'right': modulator.up_freq,
    'left': modulator.down_freq,
    'up': modulator.up_amp,
    'down': modulator.down_amp,
    'alt': modulator.wave_change,
    'space': modulator.change_play,
}

def kb_handler(event):
    # print(event.event_type,event.name)
    
    # print(modulator.adsr)
    if event.event_type == 'down': 
        if event.name not in note_pad:
            kb_router[event.name]()
            return
        modulator.set_freq(event.name)
        if not modulator.Is_Pressed:
            modulator.adsr = 'attack'
        modulator.Is_Pressed = 1  
    elif event.event_type == 'up':
        modulator.Is_Pressed = 0
        modulator.last_env = modulator.env
        modulator.adsr = 'release'
        # modulator.aim_freq = 440

def Sound(module):
    def buf_Phase_callback(outdata, frames, time, status):
        target_freq = module.aim_freq
        if module.Play:
            # target_amp = module.aim_amp if (module.adsr != 'calm')*module.Play else 0
            target_amp = module.aim_amp
            # target_env = module.aim_env
        
        
        
        # if module.adsr == 'calm':
        #     curr_amp = np.linspace(module.amp, target_amp, frames, endpoint = False)
        #     delta_env = 0
        # else:
            module.ADSR()
            target_env = module.aim_env
            block_count = module.adsr_phases[module.adsr]['time'] / ((frames/module.sample_rate))
            #delta_env = 1(путь) / (module.adsr_phases[module.adsr]['time'] * module.sample_rate)
            delta_env = (module.aim_env - module.last_env)/ block_count

            def otladka():
                print(f'\n')
                print(f'phase: {module.adsr}')
                print(f'env: {module.env}')
                print(f'target_env: {target_env}')
                print(f'block_count: {block_count}')
                print(f'last_env: {module.last_env}')
                # print(f'frames: {frames}')
                print(f'aim_env: {module.aim_env}')
                print(f'delta_env: {delta_env}')
                
            otladka()
                
            curr_env = np.linspace(module.env, (module.env + delta_env), frames, endpoint = False)
                
                
        
            curr_amp = curr_env*np.linspace(module.amp, target_amp, frames, endpoint = False)
        
        else:
            delta_env = 0
            target_amp = 0
            curr_amp = np.linspace(module.amp, target_amp, frames, endpoint = False)
        
        curr_freq = np.geomspace(module.freq, target_freq, frames, endpoint = False)
        curr_d_phase = 2*np.pi*curr_freq/module.sample_rate
        # curr_amp = np.linspace(module.amp, target_amp, frames, endpoint = False)
        curr_phase = module.phase + np.cumsum(curr_d_phase) - curr_d_phase
        
        signals = [
            (np.sin(curr_phase)),
            (np.sign(np.sin(curr_phase))),
            (np.mod(curr_phase/(2*np.pi), 1) - 1),
            (np.abs(2*np.mod(curr_phase/(2*np.pi), 1) - 1))
            ]
        #module.ADSR()
        outdata[:, 0] = curr_amp * signals[module.Wave%4]
        module.env += delta_env
        module.phase = (module.phase + np.cumsum(curr_d_phase)[-1])%(2*np.pi)
        module.amp = target_amp
        module.freq = target_freq
        
            



    # #PLAYIN AND SHII

    with sd.OutputStream(blocksize = 2048,
                        samplerate = module.sample_rate,
                        channels = 1,
                        callback = buf_Phase_callback):
        kb.hook(kb_handler)
        kb.wait()
        input()
        
Sound(modulator)

