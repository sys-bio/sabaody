experiment_num = 1

import tempfile
from os.path import join, dirname, realpath
from json import load
# from numpy import array
from subprocess import run

from parameters import param_ids, param_id_to_default_value_map, base_param_id_to_index_map

with open(join(dirname(realpath(__file__)), 'exp_y0.json')) as f:
    exp_y0_collection = [a for a in load(f)]
with open(join(dirname(realpath(__file__)), 'stimuli.json')) as f:
    stimuli_collection = [d for d in load(f)]
with open(join(dirname(realpath(__file__)), 'eval.c')) as f:
    eval_code = f.read()

lines = ''

y0 = '{'+', '.join((str(x) for x in exp_y0_collection[experiment_num]))+'}'
stimuli = stimuli_collection[experiment_num]

lines += 'static double y[26] = '+y0+';\n'

lines += '\n'

lines += 'double egf = {};\n'.format(1.*stimuli['egf'])
lines += 'double tnfa = {};\n'.format(1.*stimuli['tnfa'])
lines += 'double pi3k_inh = {};\n'.format(1.*stimuli['pi3k_inh'])
lines += 'double raf1_inh = {};\n'.format(1.*stimuli['raf1_inh'])

lines += '\n'

par_vals = [param_id_to_default_value_map[id] for id in param_ids]
for k,v in enumerate(par_vals):
    assert k == base_param_id_to_index_map[param_ids[k]]
    assert v == param_id_to_default_value_map[param_ids[k]]
pars = '{' + ',\n'.join((str(x) for x in par_vals))+'}'
lines += 'double pars[120] = {};\n'.format(pars)

lines += '\n'

out_c = lines + eval_code
# print(out_c)

with tempfile.NamedTemporaryFile(mode='w',suffix='.c') as f:
    # print(f.name)
    f.write(out_c)
    run(['clang', '-o', '/tmp/b5', f.name, '-lm'])
    run(['/tmp/b5'])
