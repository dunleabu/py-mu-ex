import pdb

from collections import namedtuple, OrderedDict
import itertools
import numpy as np
import pyo
import re
import time

from pymuex.core import Scale


_X = '(?P<X>[A-Z][A-Z,0-9]*)(?P<OCTAVE>\+)?'
_NUM = '(?P<OP{x}>[+,-])?(?P<NUM{x}>[0-9]+)(/(?P<DENOM{x}>[0-9]+))?'
_Num = lambda x: _NUM.format(x=x)
_TERM = ' *({})? *({})? *(\^ *{})?'.format(_Num(1), _X, _Num(2))
_TERM = re.compile(_TERM)


_Term = namedtuple('_Term', 'constant root exponent')

def term(_string):
    # check string against regexp
    res = _TERM.search(_string)
    assert res is not None, 'incorrect format for number: {}'.format(_string)
    res = res.groupdict()
    # extract values
    op1 = res['OP1'] or '+'
    denom1 = res['DENOM1'] or 1
    numer1 = res['NUM1'] or 1
    op2 = res['OP2'] or '+'
    denom2 = res['DENOM2'] or 1
    numer2 = res['NUM2'] or 1
    position = res['X']
    # create output
    fac = 1 if op2 == '+' else -1
    constant = int(numer1), int(denom1)
    exponent = fac * int(numer2), int(denom2)
    #position = None if position is None else int(position)
    return _Term(constant, position, exponent)
    
def line(_string):
    _lhs, _rhs = _string.upper().split('=')
    position = _lhs.replace(' ','')
    terms = [term(_str) for _str in _rhs.split('*')]
    return position, terms

def create_matrices(lines):
    lines = [line(_line) for _line in lines]
    positions = set()
    for _line in lines:
        positions.add(_line[0])
        positions.update(term.root for term in _line[1]
                         if term.root is not None)
    keys = sorted(positions)
    positions = {v:k for k,v in enumerate(keys)}
    n = len(positions)
    matrix = np.zeros((n, n))
    vector = np.zeros(n)
    for pos, _line in enumerate(lines):
        matrix[pos, positions[_line[0]]] = -1.0
        const = 0.0
        for _term in _line[1]:
            exp = _term.exponent[0] / float(_term.exponent[1])
            if _term.root is None:
                const += exp * np.log(_term.constant[0])
                const -= exp * np.log(_term.constant[1])
            else:
                const += np.log(_term.constant[0])
                const -= np.log(_term.constant[1])
                matrix[pos, positions[_term.root]] = exp
        vector[pos] = -const
    return matrix, vector, keys

def create_scale(text):
    lines = [x for x in text.split('\n') if len(x.replace(' ','')) > 0]
    a, b, keys = create_matrices(lines)
    res = np.linalg.solve(a, b)
    _notes = dict(zip(keys, np.exp(res)))
    _octave = [key for key in keys if '+' in key]
    assert len(_octave) == 1
    _octave = _octave[0]
    _root = _octave.replace('+', '')
    assert _root in keys
    notes = [(k, v) for k,v in _notes.iteritems() if k != _octave]
    notes = OrderedDict(sorted(notes, key = lambda x: x[1]))
    octave = _notes[_octave] / _notes[_root]
    return Scale(notes, octave)

def even_tempered(n, root = 440, octave = 2):
    _root = ["x0 = {}".format(root)]
    fac = "{} ^ 1/{}".format(octave, n)
    other = ["x{} = {} * x{}".format(i+1, fac, i) for i in range(0, n-1)]
    _octave = ["x0+ = {} x0".format(octave)]
    output = _root + other + _octave
    print('\n'.join(output))
    return output

def keyboard(scale, low_octave, top_octave):
    output = OrderedDict()
    octs = range(low_octave, top_octave)
    for _oct in range(low_octave, top_octave+1):
        fac = scale.octave ** _oct
        for note, freq in scale.notes.iteritems():
            output['{}{}'.format(note, _oct)] = fac * freq 
    return output

