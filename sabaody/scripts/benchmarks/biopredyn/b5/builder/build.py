from param_builder import param_id_to_default_value_map

from jinja2 import Environment, FileSystemLoader

from functools import reduce
from os.path import join, dirname, realpath, abspath
import re

with open(abspath(join(dirname(realpath(__file__)), 'b5.sb.fragment'))) as f:
    fragment_in = f.read()

pow_re = re.compile(r'pow\(([^,]+),([^,]+)\)')
assn_re = re.compile(r'^([^=]+)=(.*)$')

def stage1(l,r):
    r = r.lstrip().rstrip()
    r = pow_re.sub(r'\1^\2',r)
    # r = re.sub(r'pow\(([^,]+),([^,]+)\)', 'pow(1,2)', r)
    # r = re.sub('pow', 'xow', r)
    if r.startswith('//'):
        return l
    elif ';' in r:
        return l+r.replace(';','')+'\n'
    else:
        return l+r
fragment_stage1 = reduce(stage1, fragment_in.splitlines(), '')

def stage2(line):
    m = assn_re.match(line)
    if m is not None:
        return 'J_{q}: -> {q}; {rate}'.format(q=m.group(1), rate=m.group(2))
    else:
        return line
fragment_stage2 = '\n'.join((stage2(l) for l in fragment_stage1.splitlines()))

# print(fragment_stage2)

env = Environment(loader=FileSystemLoader(dirname(realpath(__file__))),
                  extensions=['jinja2.ext.autoescape'],
                  trim_blocks=True,
                  lstrip_blocks=True)

t = env.get_template('b5-antimony.template')

sb_src = t.render(
    reactions = fragment_stage2,
    param_id_to_default_value_map = param_id_to_default_value_map,
)

print(sb_src)
