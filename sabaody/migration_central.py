# Sabaody
# Copyright 2018 J Kyle Medley
from __future__ import print_function, division, absolute_import

from requests import post
from yarl import URL
import attr
from numpy import array
from tornado.web import Application, RequestHandler
from tornado.escape import json_decode
import arrow

from collections import deque
from abc import ABC, abstractmethod

# ** Client Logic **
def purge_all():
    # type: () -> None
    '''
    Wipe the island definitions and all migrants.
    Return to state at service startup.
    '''
    pass

def define_migrant_pool(root_url, id, param_vector_size, buffer_type='FIFO', expiration_time=arrow.utcnow().shift(days=+1)):
    # type: (str, array) -> None
    '''
    Sends an island definition to the server.

    :param root_url: The url of the server, e.g. http://localhost:10100.
    :param id: The id of the island/pool to be created (one pool per island).
    :param param_vector_size: The size of the parameter vector for the island/pool. Will be used to check pushed migrant vectors.
    :param buffer_type: Type of migration buffer to use. Can be 'FIFO'.
    :param expiration_time: The time when the pool should expire and be garbage collected. Should be longer than expected run time of fitting task.
    '''
    r = post(URL(root_url) / 'define-island' / str(id),
             json={
               'param_vector_size': param_vector_size,
               'buffer_type': buffer_type,
               'expiration_time': arrow.get(expiration_time).isoformat(),
               })
    r.raise_for_status()

def push_migrant(root_url, island_id, migrant_vector, expiration_time=arrow.utcnow().shift(days=+1)):
    # type: (str, array) -> None
    '''
    Sends an island definition to the server.

    :param expiration_time: If set, updates the expiration time of the pool.
    '''
    r = post(URL(root_url) / str(island_id) / 'push-migrant',
             json={
               'migrant_vector': migrant_vector.tolist(),
               'expiration_time': arrow.get(expiration_time).isoformat(),
               })
    r.raise_for_status()

# ** Server Logic **
class MigrationBuffer(ABC):
    @abstractmethod
    def push(self, param_vec):
        pass

    @abstractmethod
    def pop(self, n=1):
        pass

@attr.s(frozen=True)
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

    def push(self, param_vec):
        # type: (array) -> None
        '''
        Pushes a new migrant parameter vector
        to the buffer.
        '''
        if self.param_vector_size == 0:
            self.param_vector_size = param_vec.size
        elif param_vec.size != self.param_vector_size:
            raise RuntimeError('Wrong length for parameter vector: expected {} but got {}'.format(self.param_vector_size, param_vec.size))
        self._buf.append(param_vec)

    def pop(self, n=1):
        '''
        Remove n migrants from the buffer and return them
        as a sequence.
        '''
        return tuple(self._buf.pop() for x in range(n))

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

    def push(self, param_vec):
        return self._buffer.push(param_vec)

    def pop(self, n=1):
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

    def defineMigrantPool(self, id, param_vector_size, buffer_type, expiration_time):
        '''
        Defines a new island to be stored in the migration service.
        '''
        if self.param_vector_size == 0:
            self.param_vector_size = param_vector_size
        elif param_vector_size != self.param_vector_size:
            raise RuntimeError('Wrong length for parameter vector: expected {} but got {}'.format(self.param_vector_size, param_vector_size))
        print('buffer type: {}'.format(buffer_type))
        print('ctors: {}'.format(self._migrant_pool_ctors))
        if not buffer_type in self._migrant_pool_ctors:
            raise InvalidMigrantBufferType()
        self._migrant_pools[str(id)] = self._migrant_pool_ctors[buffer_type](param_vector_size=param_vector_size, expiration_time=arrow.get(expiration_time))

    def pushMigrant(self, id, migrant_vector, expiration_time):
        '''
        Pushes a migrant vector to a pool.
        '''
        migrant_vector = array(migrant_vector)
        if migrant_vector.size != self.param_vector_size:
            raise RuntimeError('Expected migrant vector of length {} but received length {}'.format(self.param_vector_size, migrant_vector.size))
        self._migrant_pools[str(id)].push(migrant_vector)

    def garbageCollect(self):
        '''
        Purges migrant pools that are past their expiration time.
        '''
        time_now = arrow.utcnow()
        self._migrant_pools = {(id,p) for id,p in self._migrant_pools.items() if time_now <= p.expiration_time}

# ** Service **
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

def create_central_migration_service():
    migration_host = MigrationServiceHost()
    return Application([
        (r"/define-island/([a-z0-9-]+)/?", DefineMigrantPoolHandler, {'migration_host': migration_host}),
        (r"/([a-z0-9-]+)/push-migrant/?", PushMigrantHandler, {'migration_host': migration_host}),
    ])