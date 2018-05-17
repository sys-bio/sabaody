# Sabaody
# Copyright 2018 J Kyle Medley
from __future__ import print_function, division, absolute_import

from requests import post
from yarl import URL
import attr
from numpy import array
from tornado.web import Application, RequestHandler

from collections import deque

# ** Client Logic **
def purge_all():
    # type: () -> None
    '''
    Wipe the island definitions and all migrants.
    Return to state at service startup.
    '''
    pass

def define_island(root_url, id, param_vector_size, buffer_type='FIFO'):
    # type: (str, array) -> None
    '''
    Sends an island definition to the server.
    '''
    r = post(URL(root_url) / 'define-island' / str(id),
             json={
               'param_vector_size': param_vector_size,
               'buffer_type': buffer_type,
               })
    r.raise_for_status()

# ** Server Logic **
@attr.s(frozen=True)
class FIFOMigrationBuffer:
    '''
    Per-island buffer that stores incoming migrants from
    other islands.
    '''
    buffer_size = attr.ib(default=10)
    # if zero, determined by first push
    vector_length = attr.ib(default=0)
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
        if self.vector_length == 0:
            self.vector_length = param_vec.size
        elif param_vec.size != self.vector_length:
            raise RuntimeError('Wrong length for parameter vector: expected {} but got {}'.format(self.vector_length, param_vec.size))
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
    _buffer = attr.ib()
    @_buffer.validator
    def check_buffer(self, attribute, value):
        if not isinstance(buffer, MigrationBuffer):
            raise RuntimeError('Expected migration buffer subclass')

    @classmethod
    def FIFO(cls):
        '''
        Constructs a LocalMigrantPool from a FIFO buffer.
        '''
        return cls(buffer=FIFOMigrationBuffer())

class InvalidMigrantBufferType(KeyError):
    pass

@attr.s
class MigrationServiceHost:
    '''
    Contains all logic for the migration server.
    '''
    _migrant_pools = attr.ib(default=attr.Factory(list))
    _migrant_pool_ctors = attr.ib(default={
      'FIFO': LocalMigrantPool.FIFO
      })
    param_vector_size = attr.ib(default=0)

    def defineIsland(self, id, param_vector_size, buffer_type):
        if self.param_vector_size == 0:
            self.param_vector_size = param_vector_size
        elif param_vector_size != self.param_vector_size:
            raise RuntimeError('Wrong length for parameter vector: expected {} but got {}'.format(self.param_vector_size, param_vector_size))
        if not buffer_type in self._migrant_pool_ctors:
            raise InvalidMigrantBufferType()
        self._migrant_pools.append(self._migrant_pool_ctors[buffer_type])

# ** Service **
class DefineIslandHandler(RequestHandler):
    def initialize(self, migration_host):
        self.migration_host = migration_host

    def post(self, id):
        args = json_decode(self.request.body)
        try:
            migration_host.defineIsland(id, *args)
        except InvalidMigrantBufferType:
            self.clear()
            self.set_status(400)
            self.finish('No such migrant buffer "{}"'.format(args['buffer_type']))
        except Exception as e:
            self.clear()
            self.set_status(400)
            self.write({
              'error': str(e),
              })

def create_central_migration_service():
    host = MigrationServiceHost()
    return Application([
        (r"/define-island/([a-z0-9-]+)/?", DefineIslandRequest, {'host': MigrationServiceHost}),
    ])