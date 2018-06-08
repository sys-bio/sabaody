# Sabaody
# Copyright 2018 J Kyle Medley
from __future__ import print_function, division, absolute_import

from sabaody.migration_central import CentralMigrator

from toolz import partial
from numpy import array
from pygmo import population, rosenbrock

from uuid import uuid4

m = CentralMigrator('http://localhost:10100')

island1 = uuid4()
island2 = uuid4()

m.defineMigrantPool(island1, 3)
m.defineMigrantPool(island2, 3)

# migrants to island 1
m.pushMigrant(island1, array([1.,1.,1.]), 1.)
m.pushMigrant(island1, array([2.,2.,2.]), 2.)
# population for island 1
p1 = population(prob=rosenbrock(3), size=0, seed=0)
p1.push_back(array([9.,0.,1.]), array([3.]))
p1.push_back(array([9.,0.,2.]), array([4.]))

# migrants to island 2
m.pushMigrant(island2, array([3.,3.,3.]), 3.)
m.pushMigrant(island2, array([4.,4.,4.]), 4.)
# population for island 2
p2 = population(prob=rosenbrock(3), size=0, seed=0)
p2.push_back(array([9.,0.,1.]), array([3.]))
p2.push_back(array([9.,0.,2.]), array([4.]))

migrants = m.pullMigrants(island1)
print('Number of migrants: {}'.format(len(migrants)))
for m in migrants:
    print(m)

# re-push the migrants
m.pushMigrant(island1, array([1.,1.,1.]), 1.)
m.pushMigrant(island1, array([2.,2.,2.]), 2.)