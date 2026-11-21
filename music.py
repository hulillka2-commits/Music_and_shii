# THE SYNTHESIZER

# ALL THE IMPORTS
import numpy as np
import sounddevice as sd
import keyboard as kb
import time as t

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
        'time': 0.05,
        'vector': 1,
            },
    'decay': {
        'aim': 0.3,
        'time': 0.05,
        'vector': -1,
            },
    'sustain': {
        'aim': 0.3,
        'time': 1,
        'vector': 1,
            },
    'release': {
        'aim': 0,
        'time': 0.7,
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
        adsr_phases,
        lpf,
        d_lfo,
        f_lfo,
        drive,
        delay_echo,
        delay_volume,
        delay_feedback,
        delay_max,
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
        self.mode = 0
        
        self.ef_mode = 0
        
        self.drive = drive

        self.d_lfo = d_lfo
        self.f_lfo = f_lfo
        self.k_lfo = 0
        self.lfo_phase = 0

        self.delay_echo = delay_echo
        self.delay_volume = delay_volume
        self.delay_samples = int(delay_echo * sample_rate)
        self.delayed = np.full(delay_max * sample_rate * 2, 0, dtype = float)
        self.last_delayed = np.full(delay_max * sample_rate * 2, 0, dtype = float)
        self.delay_feedback = delay_feedback
        self.delay_max = delay_max
        self.delay_read = self.delay_samples
        self.delay_write = 0


                
        self.dB_koef = 10**(self.dB_step/20)
                        
                
        
    def Change_effect(self):
        self.ef_mode += 1    
        
    def Change_play(self):
        self.Play = 1 - self.Play
                
    def Wave_change(self):
        self.wave += 1

    def Mode_change(self):
        self.mode += 1

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
                
    def LPF(self, track, curr_lpf):        
        
        track.curr_signal[0] = track.last_signal[-1] + curr_lpf[0] * (track.curr_signal[0] - track.last_signal[-1])
        for i in range(1, len(track.curr_signal)):
            track.curr_signal[i] = track.curr_signal[i-1] + curr_lpf[i-1] * (track.curr_signal[i] - track.curr_signal[i-1])
        return track.curr_signal
        
    def LFO(self, frames):
        lfo_curr_d_phase = np.full(frames, 2*np.pi*self.f_lfo/self.sample_rate)
        lfo_curr_phase = self.lfo_phase + np.cumsum(lfo_curr_d_phase)
        
        self.lfo_phase = (self.lfo_phase + np.cumsum(lfo_curr_d_phase)[-1])%(2*np.pi)

        return np.sin(lfo_curr_phase)
        
   
   
    def Up_drive(self):
        if self.drive * self.dB_koef < 20:
            self.drive *= self.dB_koef 
    
    def Down_drive(self):
        if self.drive / self.dB_koef > 1:
            self.drive /= self.dB_koef
   
    def Distortion(self, signals,):
        
        return np.tanh(self.drive * signals) / np.tanh(self.drive)
   


    def Delay(self, signals, frames):
        self.delay_read = (self.delay_write + self.delay_samples) % self.delay_samples
        # print(self.delay_write, self.delay_read, self.delay_read - self.delay_write, self.delay_samples)
        for i in range(frames):
            self.delay_read = (self.delay_read % self.delay_samples)
            self.delay_write = (self.delay_write % self.delay_samples)
            signals[i] += self.delayed[self.delay_read] 
            self.delayed[self.delay_write] = signals[i] * self.delay_feedback
            self.delay_read  += 1
            self.delay_write += 1
            
        return signals * self.delay_volume

    
    
    def Up_delay(self):
        if self.delay_echo + 0.2 <= 2:
            self.delay_echo  += 0.2
            self.delay_samples = int(self.delay_echo * self.sample_rate)

    def Down_delay(self):
        if self.delay_echo - 0.2 > 0 :
            self.delay_echo  -= 0.2
            self.delay_samples = int(self.delay_echo * self.sample_rate)
        
      
        
    def Effect_Handler(self, signals, frames):
        if self.ef_mode % 3 == 0:
            return signals
        
        if self.ef_mode % 3 == 1:
            return self.Distortion(signals)
        
        if self.ef_mode % 3 == 2:
            print(self.delay_echo)
            return self.Delay(signals, frames)

        
        
    def Sound(self, tracks):
        
        kb_router = {
            # 'right': module.up_freq,
            # 'left': module.down_freq,
            'right': self.Up_lpf,
            'left': self.Down_lpf,
            'up': self.Up_amp,
            'down': self.Down_amp,
            'alt': self.Wave_change,
            'shift': self.Mode_change,
            'space': self.Change_play,
            'v': self.Up_drive,
            'c': self.Down_drive,
            'b': self.Change_effect,
            'm': self.Up_delay,
            'n': self.Down_delay,
        }
        
        def kb_handler(event):
            if event.event_type == 'down': 
                if event.name not in note_pad:
                    kb_router.get(event.name)()
                    return
                
                tracks.add(note_track[event.name])
                if not note_track[event.name].Is_Pressed:
                    note_track[event.name].adsr = 'attack'
                note_track[event.name].Is_Pressed = 1
                
            elif event.event_type == 'up':
                if event.name not in note_pad:
                    return

                note_track[event.name].Is_Pressed = 0
                note_track[event.name].last_env = note_track[event.name].env
                note_track[event.name].adsr = 'release'


        
        def buf_Phase_callback(outdata, frames, time, status):
            
            # start = t.perf_counter()
            
            signals = np.zeros((frames, ))

        #CHECKIN IF ITS ON

            if self.Play:
                target_amp = self.aim_amp
                target_lpf = self.aim_lpf
                
                lfo_wave = self.LFO(frames)

                for track in tracks:
                    
                    if track.adsr != 'calm':
                    
                        target_freq = track.aim_freq
                        
                    #DEALIN WITH ADSR(COUNTIN ENV)
                    
                        self.ADSR(track)
                        block_count = self.adsr_phases[track.adsr]['time'] / ((frames/self.sample_rate))
                        delta_env = (track.aim_env - track.last_env) / block_count
                        curr_env = np.linspace(track.env, (track.env + delta_env), frames, endpoint = False)

                    #LOGS
                    
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
                    
                    
                    #COUNTIN FREQ, PHASE AND LPF
                    
                        curr_freq = np.geomspace(track.freq, target_freq, frames, endpoint = False) * (1 + self.d_lfo * lfo_wave * (self.mode % 4 == 3))
                        curr_d_phase = 2*np.pi*curr_freq/self.sample_rate
                        curr_phase = track.phase + np.cumsum(curr_d_phase) - curr_d_phase
                        
                        curr_lpf = np.linspace(self.lpf, target_lpf, frames, endpoint = False) * (1 + self.d_lfo * lfo_wave * (self.mode % 4 == 2))

                    #CHECKIN ENV LIMITS
                    
                        if track.env + delta_env <= 2 and track.env + delta_env >= -1:
                        # if (self.adsr_phases[track.adsr]['vector'])*(track.env + delta_env) < (self.adsr_phases[track.adsr]['vector'])*(track.aim_env):
                            track.env += delta_env
                            
                        # else:
                        #     track.env += (track.aim_env - (track.env + delta_env))
                    
                    #UPDATE PHASE, FREQ AND LPF
                    
                        track.phase = (track.phase + np.cumsum(curr_d_phase)[-1])%(2*np.pi)
                        track.freq = target_freq

                        self.lpf = target_lpf       
                        
                    #FINALLY CREATIN ONE AND SUMMIN IT(POLYPHONY)
                    
                        track.curr_signal = self.Wave_shaper(curr_phase)
                        track.curr_signal = self.LPF(track, curr_lpf)
                        
                        signals += curr_env*track.curr_signal
                        track.last_signal = track.curr_signal                    
                    
        #IF PAUSE OR SOME
            
            else:
                delta_env = 0
                target_amp = 0
                
                self.lfo_phase = 0
                lfo_wave = 0

        #COUNTIN THEN UPDATIN AMP AND FINNALY PACKIN IT
            
            curr_amp = np.linspace(self.amp, target_amp, frames, endpoint = False) * (1 + self.d_lfo * lfo_wave * (self.mode % 4 == 1))
            self.amp = target_amp

            outdata[:, 0] = curr_amp * self.Effect_Handler(signals, frames)


            # end = t.perf_counter()
            # print((end-start)*1000)



    #PLAYIN AND SHII

        with sd.OutputStream(blocksize = 256,
                            samplerate = self.sample_rate,
                            channels = 1,
                            callback = buf_Phase_callback):
            kb.hook(kb_handler)
            kb.wait('esc')



Syn = Synthesizer(0.1,
                1,
                44100,
                adsr_phases_params,
                0.1,
                0.5,
                5,
                0.6,
                0.7,
                1,
                0.5,
                2,
                  )        

Syn.Sound(tracks)

