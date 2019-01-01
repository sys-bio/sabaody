# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from os.path import join, dirname, realpath, abspath

import scipy.io

mat      = scipy.io.loadmat(abspath(join(dirname(realpath(__file__)), 'b5_data.mat')))
inputs   = mat['inputs']
exp_data = inputs[0][0][1][0][0][11][0]
exp_y0   = inputs[0][0][1][0][0][13][0]
u        = inputs[0][0][1][0][0][20][0]

from json import dump
with open(join(dirname(realpath(__file__)), 'exp_y0.json'), 'w') as f:
    dump([a.tolist() for a in exp_y0], f)

with open(join(dirname(realpath(__file__)), 'exp_data.json'), 'w') as f:
    dump([a.tolist() for a in exp_data], f)

with open(join(dirname(realpath(__file__)), 'stimuli.json'), 'w') as f:
    dump([{
        'egf':      int(a[0]) != 0,
        'tnfa':     int(a[1]) != 0,
        'pi3k_inh': int(a[2]) != 0,
        'raf1_inh': int(a[3]) != 0,
    } for a in u], f)
