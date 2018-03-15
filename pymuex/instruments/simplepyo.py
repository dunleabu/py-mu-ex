import pyo

class SimpleBeep(object):

    def __init__(self):
        self.env =  pyo.Adsr(attack=.01, decay=.6, sustain=.0,
                             release=.6, dur=1, mul=.5)
        sq = pyo.SawTable()
        self.osc = pyo.Osc(table=sq, mul=self.env, freq = 440)
        self.lowpass = pyo.MoogLP(self.osc, 1000, self.env)
        self.lowpass.out()

    def play(self, note):
        f = float(note.freq)
        self.osc.freq = f
        self.lowpass.freq = f * 2.5
        self.env.play()
