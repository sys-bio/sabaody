# Sabaody
# Copyright 2018 J Kyle Medley
from __future__ import print_function, division, absolute_import

from sabaody.migration_central import define_migrant_pool, push_migrant, pop_migrants

from toolz import partial
from numpy import array

from uuid import uuid4

define_migrant_pool = partial(define_migrant_pool, 'http://luna:10100')
push_migrant        = partial(push_migrant,        'http://luna:10100')
pop_migrants        = partial(pop_migrants,        'http://luna:10100')

island_id = uuid4()

define_migrant_pool(island_id, 4)

push_migrant(island_id, array([1., 2., 3., 4.]))

migrants = pop_migrants(island_id)
print('Number of migrants: {}'.format(len(migrants)))
for m in migrants:
    print(m)