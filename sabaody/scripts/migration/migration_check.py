# Sabaody
# Copyright 2018 J Kyle Medley
from __future__ import print_function, division, absolute_import

from sabaody.migration_central import define_migrant_pool, push_migrant, pull_migrants

from toolz import partial
from numpy import array

from uuid import uuid4

define_migrant_pool = partial(define_migrant_pool, 'http://luna:10100')
push_migrant        = partial(push_migrant,        'http://luna:10100')
pull_migrants        = partial(pull_migrants,        'http://luna:10100')

island1 = uuid4()
island2 = uuid4()

define_migrant_pool(island1, 3)
define_migrant_pool(island2, 3)

# migrants to island 1
push_migrant(island1, array([1.,1.,1.]), 1.)
push_migrant(island1, array([2.,2.,2.]), 2.)
# population for island 1
p1 = population(prob=rosenbrock(3), size=0, seed=0)
p1.push_back(array([9.,0.,1.]), array([3.]))
p1.push_back(array([9.,0.,2.]), array([4.]))

# migrants to island 2
push_migrant(island2, array([3.,3.,3.]), 3.)
push_migrant(island1, array([4.,4.,4.]), 4.)
# population for island 2
p2 = population(prob=rosenbrock(3), size=0, seed=0)
p2.push_back(array([9.,0.,1.]), array([3.]))
p2.push_back(array([9.,0.,2.]), array([4.]))

migrants = pull_migrants(island1)
print('Number of migrants: {}'.format(len(migrants)))
for m in migrants:
    print(m)