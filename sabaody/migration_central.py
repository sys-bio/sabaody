# Sabaody
# Copyright 2018 J Kyle Medley
from __future__ import print_function, division, absolute_import

from requests import post
from yarl import URL
import attr
from numpy import array

from collections import deque

# ** Communication **
def purge_all():
    # type: () -> None
    '''
    Wipe the island definitions and all migrants.
    Return to state at service startup.
    '''
    pass

def define_island(root_url, id, param_vector_size):
    # type: (str, array) -> None
    '''
    Sends an island definition to the server.
    '''
    r = post(URL(root_url) / 'define-island' / str(id), json={'param_vector_size': param_vector_size})
    r.raise_for_status()

# ** Logic **
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