import itertools
import pdb
import pyo
from random import shuffle

from pymuex.utils.pyoutils import PyoServer
import pymuex.instruments.simplepyo as pin
import pymuex.tuning.core as ptc
from pymuex.core import Note

reload(pin)
reload(ptc)

text = """
       C = 440
       D = 9/8 C
       E = 5/4 C
       F = 4/3 C
       G = 3/2 C
       A = 5/3 C
       B = 15/8 C
       C+ = 2/1 C
       """

text = """
       X = 440
       Y = 2 ^ 1/3 * X
       Q = 2 ^ 1/5 * X
       z = 2 ^ 1/3 * Y
       X+ = 2 X
       """

scale = ptc.create_scale(text)
keys = ptc.keyboard(scale, -2, +2)

s = PyoServer()

m = pin.SimpleBeep()

s.start()

n = Note(550, 0.9, 0.4)
m.play(n)


class TT(object):

    def __init__(self, scale, instr):
        x0 = list(scale.notes)
        x1 = list(scale.notes)
        shuffle(x0)
        shuffle(x1)
        notes = [scale.notes[i] for j in zip(x0, x1) for i in j]
        self.notes = itertools.cycle(notes)
        self.instr = instr

    def __call__(self):
        freq = self.notes.next()
        self.instr.play(Note(freq, 0, 0))


tt = TT(scale, m)


p = pyo.Pattern(tt, 0.2)
p.play()


