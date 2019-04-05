# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from parameters import param_id_to_default_value_map
from species import species

from jinja2 import Environment, FileSystemLoader

from functools import reduce
from os.path import join, dirname, realpath, abspath
import re

with open(abspath(join(dirname(realpath(__file__)), 'b5.sb.fragment'))) as f:
    fragment_in = f.read()

pow_re = re.compile(r'pow\(([^,]+),([^,]+)\)')
rxn_re = re.compile(r'^d([^=]+)=(.*)$')
assn_re = re.compile(r'^([^d][^=]*)=(.*)$')

def stage1(l,r):
    r = r.lstrip().rstrip()
    r = pow_re.sub(r'\1^\2',r)
    if r.startswith('//'):
        return l
    elif ';' in r:
        return l+r.replace(';','')+'\n'
    else:
        return l+r
fragment_stage1 = reduce(stage1, fragment_in.splitlines(), '')

def filter_reactions(line):
    m = rxn_re.match(line)
    if m is not None:
        return 'J_{q}: -> {q}; {rate}'.format(q=m.group(1), rate=m.group(2))
    else:
        return ''
reactions = '\n'.join((filter_reactions(l).replace('OR', 'myor') for l in fragment_stage1.splitlines()))
reactions = '\n'.join((l for l in reactions.splitlines() if l != ''))

def filter_assignments(line):
    m = assn_re.match(line)
    if m is not None:
        return '{q} := {rhs}'.format(q=m.group(1), rhs=m.group(2))
    else:
        return ''
assignments = '\n'.join((filter_assignments(l).replace('OR', 'myor') for l in fragment_stage1.splitlines()))
assignments = '\n'.join((l for l in assignments.splitlines() if l != ''))

env = Environment(loader=FileSystemLoader(dirname(realpath(__file__))),
                  extensions=['jinja2.ext.autoescape'],
                  trim_blocks=True,
                  lstrip_blocks=True)

t = env.get_template('b5-antimony.template')

sb_src = t.render(
    species = species,
    reactions = reactions,
    assignments = assignments,
    param_id_to_default_value_map = param_id_to_default_value_map,
)
print(sb_src)

# import antimony
# antimony.loadAntimonyString(sb_src)
# sbml_str = antimony.getSBMLString('b5model')
# with open(abspath(join(dirname(realpath(__file__)), '..','..','..','..','..','sbml','b5.xml')), 'w') as f:
#     f.write(sbml_str)
