# Sabaody
# Copyright 2018 J Kyle Medley
from __future__ import print_function, division, absolute_import

from .migration import Migrator

#from requests import post
from yarl import URL
import attr
from numpy import array, ndarray, argsort, transpose
from tornado.web import Application, RequestHandler
from tornado.escape import json_decode
import arrow

from collections import deque
from abc import ABC, abstractmethod
import typing

# ** Client Logic **
class CentralMigrator(Migrator):
    def __init__(self, root_url):
        self.root_url = URL(root_url)

    def purge_all(self):
        # type: () -> None
        '''
        Wipe the island definitions and all migrants.
        Return to state at service startup.
        '''
        pass # TODO

    def define_migrant_pool(self, id, param_vector_size, buffer_type='FIFO', expiration_time=arrow.utcnow().shift(days=+1)):
        # type: (str, array, str, arrow.Arrow) -> None
        '''
        Sends an island definition to the server.

        :param self.root_url: The url of the server, e.g. http://localhost:10100.
        :param id: The id of the island/pool to be created (one pool per island).
        :param param_vector_size: The size of the parameter vector for the island/pool. Will be used to check pushed migrant vectors.
        :param buffer_type: Type of migration buffer to use. Can be 'FIFO'.
        :param expiration_time: The time when the pool should expire and be garbage collected. Should be longer than expected run time of fitting task.
        '''
        from requests import post
        r = post(str(self.root_url / 'define-island' / str(id)),
                json={
                  'param_vector_size': param_vector_size,
                  'buffer_type': buffer_type,
                  'expiration_time': arrow.get(expiration_time).isoformat(),
                  })
        r.raise_for_status()

    def push_migrant(self, dest_island_id, migrant_vector, fitness, src_island_id = None, expiration_time=arrow.utcnow().shift(days=+1)):
        # type: (str, ndarray, float, str, arrow.Arrow) -> None
        '''
        Sends an island definition to the server.

        :param expiration_time: If set, updates the expiration time of the pool.
        '''
        extra_args = dict()
        if src_island_id is not None:
            extra_args[src_island_id] = src_island_id
        from requests import post
        r = post(str(self.root_url / str(dest_island_id) / 'push-migrant'),
                json={
                  'migrant_vector': migrant_vector.tolist(),
                  'fitness': float(fitness),
                  'expiration_time': arrow.get(expiration_time).isoformat(),
                  **extra_args
                  })
        r.raise_for_status()

    def pull_migrants(self, island_id, n=0):
        # type: (array, int) -> typing.List[ndarray]
        '''
        Gets n migrants from the pool and returns them.
        If n is zero, return all migrants.
        '''
        from requests import post
        r = post(str(self.root_url / str(island_id) / 'pop-migrants'),
                json={
                  'n': n,
                  })
        r.raise_for_status()
        return (array(r.json()['migrants']),
                array([[f] for f in r.json()['fitness']]),
                r.json()['src_island_id'])

    def replace(self, island_id, population, policy):
        '''
        Replace migrants in the specified population with candidates
        in the pool according to the specified policy.
        '''
        candidates,candidate_f,src_ids = self.pull_migrants(island_id)
        return (policy.replace(population,candidates,candidate_f),src_ids)

# ** Server Logic **
class MigrationBuffer(ABC):
    @abstractmethod
    def push(self, param_vec):
        pass

    @abstractmethod
    def pop(self, n=1):
        pass

@attr.s
class FIFOMigrationBuffer(MigrationBuffer):
    '''
    Per-island buffer that stores incoming migrants from
    other islands.
    '''
    buffer_size = attr.ib(default=10)
    # if zero, determined by first push
    param_vector_size = attr.ib(default=0)
    _buf = attr.ib()
    @_buf.default
    def init_buf(self):
        return deque(maxlen=self.buffer_size)

    def push(self, param_vec, fitness, src_island_id=None):
        # type: (ndarray, float, str) -> None
        '''
        Pushes a new migrant parameter vector
        to the buffer.
        '''
        if self.param_vector_size == 0:
            self.param_vector_size = param_vec.size
        elif param_vec.size != self.param_vector_size:
            raise RuntimeError('Wrong length for parameter vector: expected {} but got {}'.format(self.param_vector_size, param_vec.size))
        self._buf.append((param_vec,fitness,src_island_id))

    def pop(self, n=0):
        '''
        Remove n migrants from the buffer and return them
        as a sequence.
        '''
        if n > 0:
            return tuple(self._buf.pop() for x in range(n))
        else:
            return tuple(self._buf.pop() for x in range(len(self._buf)))

@attr.s(frozen=True)
class LocalMigrantPool:
    '''
    Keeps track of all incoming migrants for a specific island.
    Contains one migration buffer. There should be
    exactly one LocalMigrantPool per island.
    '''
    expiration_time = attr.ib(type=arrow.Arrow)
    _buffer = attr.ib()
    @_buffer.validator
    def check_buffer(self, attribute, value):
        if not isinstance(value, MigrationBuffer):
            raise RuntimeError('Expected migration buffer subclass')

    def push(self, param_vec, fitness):
        return self._buffer.push(param_vec, fitness)

    def pop(self, n=0):
        return self._buffer.pop(n)

    @classmethod
    def FIFO(cls, param_vector_size, expiration_time):
        '''
        Constructs a LocalMigrantPool from a FIFO buffer.
        '''
        return cls(buffer=FIFOMigrationBuffer(param_vector_size=param_vector_size), expiration_time=expiration_time)

class InvalidMigrantBufferType(KeyError):
    pass

@attr.s
class MigrationServiceHost:
    '''
    Contains all logic for the migration server.
    '''
    _migrant_pools = attr.ib(default=attr.Factory(dict))
    _migrant_pool_ctors = attr.ib(default={
      'FIFO': LocalMigrantPool.FIFO
      })
    param_vector_size = attr.ib(default=0)

    def purgeAll(self):
        self._migrant_pools = {}
        self.param_vector_size = 0

    def defineMigrantPool(self, id, param_vector_size, buffer_type, expiration_time):
        '''
        Defines a new island to be stored in the migration service.
        '''
        if self.param_vector_size == 0:
            self.param_vector_size = param_vector_size
        elif param_vector_size != self.param_vector_size:
            raise RuntimeError('Wrong length for parameter vector: expected {} but got {}'.format(self.param_vector_size, param_vector_size))
        if not buffer_type in self._migrant_pool_ctors:
            raise InvalidMigrantBufferType()
        self._migrant_pools[str(id)] = self._migrant_pool_ctors[buffer_type](param_vector_size=param_vector_size, expiration_time=arrow.get(expiration_time))

    def pushMigrant(self, id, migrant_vector, fitness, expiration_time):
        '''
        Pushes a migrant vector to a pool.
        '''
        migrant_vector = array(migrant_vector)
        if migrant_vector.size != self.param_vector_size:
            raise RuntimeError('Expected migrant vector of length {} but received length {}'.format(self.param_vector_size, migrant_vector.size))
        self._migrant_pools[str(id)].push(migrant_vector, fitness)

    def popMigrants(self, id, n):
        '''
        Pops n migrants from the pool.
        '''
        return self._migrant_pools[str(id)].pop(n)

    def garbageCollect(self):
        '''
        Purges migrant pools that are past their expiration time.
        '''
        time_now = arrow.utcnow()
        self._migrant_pools = {(id,p) for id,p in self._migrant_pools.items() if time_now <= p.expiration_time}

# ** Request Handlers **
class PurgeAllHandler(RequestHandler):
    def initialize(self, migration_host):
        self.migration_host = migration_host

    def post(self):
        try:
            self.migration_host.purgeAll()
        except Exception as e:
            print('Misc. error "{}"'.format(e))
            self.clear()
            self.set_status(400)
            self.write({
              'error': str(e),
              })

class DefineMigrantPoolHandler(RequestHandler):
    def initialize(self, migration_host):
        self.migration_host = migration_host

    def post(self, id):
        args = json_decode(self.request.body)
        try:
            self.migration_host.defineMigrantPool(id, **args)
        except InvalidMigrantBufferType:
            print('Invalid migrant buffer type "{}"'.format(args['buffer_type']))
            self.clear()
            self.set_status(400)
            self.finish('No such migrant buffer type "{}"'.format(args['buffer_type']))
        except Exception as e:
            print('Misc. error "{}"'.format(e))
            self.clear()
            self.set_status(400)
            self.write({
              'error': str(e),
              })

class PushMigrantHandler(RequestHandler):
    def initialize(self, migration_host):
        self.migration_host = migration_host

    def post(self, id):
        args = json_decode(self.request.body)
        try:
            self.migration_host.pushMigrant(id, **args)
        except Exception as e:
            print('Misc. error "{}"'.format(e))
            self.clear()
            self.set_status(400)
            self.write({
              'error': str(e),
              })

class PopMigrantsHandler(RequestHandler):
    def initialize(self, migration_host):
        self.migration_host = migration_host

    def post(self, id):
        args = json_decode(self.request.body)
        try:
            migrants = self.migration_host.popMigrants(id, **args)
            self.write({
              'migrants': [v.tolist() for v,fitness,src_id in migrants],
              'fitness': [float(fitness) for v,fitness,src_id in migrants],
              'src_island_id': [str(src_id) for v,fitness,src_id in migrants],
              })
        except Exception as e:
            print('Misc. error "{}"'.format(e))
            self.clear()
            self.set_status(400)
            self.write({
              'error': str(e),
              })

# TODO: test with https://github.com/eugeniy/pytest-tornado
def create_central_migration_service():
    migration_host = MigrationServiceHost()
    return Application([
        (r"/purge-all/?", PurgeAllHandler, {'migration_host': migration_host}),
        (r"/define-island/([a-z0-9-]+)/?", DefineMigrantPoolHandler, {'migration_host': migration_host}),
        (r"/([a-z0-9-]+)/push-migrant/?", PushMigrantHandler, {'migration_host': migration_host}),
        (r"/([a-z0-9-]+)/pop-migrants/?", PopMigrantsHandler, {'migration_host': migration_host}),
    ])

def start_migration_service():
    '''
    Starts the migration service in a separate process.
    '''
    from subprocess import Popen
    from os.path import join, dirname
    import sys
    return Popen((sys.executable, join(dirname(__file__),'scripts','migration','migration_service.py'),))