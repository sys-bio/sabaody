# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley
from __future__ import print_function, division, absolute_import

from .migration import Migrator

import attr
from typing import Any
from kafka import KafkaProducer
from kafka import KafkaConsumer
from interruptingcow import timeout
from numpy import array, ndarray, vstack
import arrow
from functools import reduce

from uuid import uuid4
import json
import typing

def convert_to_2d_array(array_or_list):
    # type: (typing.Union[ndarray,typing.List[ndarray]]) -> ndarray
    '''
    Convert ``array_or_list`` into a 2d array.
    ``array_or_list`` can be a list of decision vectors,
    a single decision vector, or a 2d (in which case
    it is returned as-is).
    '''
    if isinstance(array_or_list,list):
        for m in array_or_list:
            if not isinstance(m,ndarray):
                raise RuntimeError('`array_or_list` should be a list of ndarrays, instead found element of type {}'.format(type(m)))
            if not (m.ndim < 2 or (m.ndim == 2 and m.shape[0] == 1)):
                raise RuntimeError('Received 2d array for migrant - array_or_list should be 1d arrays or row vectors')
        return vstack(tuple(m for m in array_or_list))
    elif isinstance(array_or_list,ndarray):
        if array_or_list.ndim == 1:
            return array_or_list.reshape((1,-1))
        elif array_or_list.ndim == 2:
            return array_or_list
        else:
            raise RuntimeError('Wrong n dims for array_or_list: {}'.format(array_or_list.ndim))
    else:
        raise RuntimeError('Wrong type for array_or_list - should be list or ndarray but received {}'.format(type(array_or_list)))

class KafkaBuilder:
    '''
    A class for constructing Kafka producers and consumers.
    '''

    def __init__(self, hosts, port):
        '''
        Construct a new Kafka builder for a list of hosts and a port number (as a string).

        :param hosts: A list of host names / ips to use. If just one, can pass as string.
        :type hosts:  list or str
        :param port:  The port to listen on
        :type port:   int or str
        '''
        self._hosts = [hosts] if isinstance(hosts,str) else list(hosts)
        self._port = str(port)


    def build_producer(self):
        url = ",".join(each_host + ":" + self._port for each_host in self._hosts)
        return KafkaProducer(bootstrap_servers=url)


    def build_consumer(self, topic_name, *args, **kwargs):
        url = ",".join(each_host + ":" + self._port for each_host in self._hosts)
        return KafkaConsumer(topic_name, *args, bootstrap_servers=url, auto_offset_reset='earliest', **kwargs)


    def __getstate__(self):
        return {
          'hosts': self._hosts,
          'port': self._port,
          }


    def __setstate__(self, state):
        self._hosts = state['hosts']
        self._port  = state['port']

@attr.s
class MigrantData:
    migrants = attr.ib(type=array)
    fitness = attr.ib(type=array)
    timestamp = attr.ib(type=arrow.Arrow)
    src_id = attr.ib(type=str)

class KafkaMigrator(Migrator):
    '''
    A migrator which sends / receives migrants using Kafka.
    Kafka does not use pools - it is a distributed message
    processing system, so the order in which migrants are
    received will, in general, be unknown.
    '''


    def __init__(self, selection_policy, migration_policy, builder, time_limit=10):
        '''
        Constructor for KafkaMigrator.

        :param timeout: Time limit (in seconds) to wait for incoming migrants.
        '''
        super().__init__(selection_policy, migration_policy)
        self._builder = builder
        self._identifier = str(uuid4())
        self._time_limit = time_limit
        self._producer = self._builder.build_producer()


    def __getstate__(self):
        return {
          'builder': self._builder.__getstate__(),
          'identifier': self._identifier,
          'time_limit': self._time_limit,
          **super().__getstate()
          }


    def __setstate__(self, state):
        self._builder = KafkaBuilder(**state['builder'])
        self._identifier = state['identifier']
        self._time_limit = state['time_limit']
        self._producer = self._builder.build_producer()


    def topic(self, dest_island_id):
        return '_'.join([dest_island_id, self._identifier])


    def serialize(self, migrant_array, fitness):
        '''
        Returns a JSON-serialized bytes object representing the 2d migrant array.
        Decision vectors should be row-encoded in the input array.
        '''
        serialized_data = {
            'migrants' : migrant_array.tolist(),
            'fitness'  : fitness.tolist(),
            'timestamp': arrow.utcnow().isoformat(),
            }
        return json.dumps(serialized_data).encode('utf-8')


    def deserialize(self, migrant_msg):
        # type: (Any) -> MigrantData
        data = json.loads(migrant_msg.value.decode('utf-8'))
        src_id = migrant_msg.key.decode('utf-8')
        return MigrantData(
          migrants  = array(data['migrants']),
          fitness   = array(data['fitness']),
          timestamp = arrow.get(data['timestamp']),
          src_id    = src_id)


    def migrate(self, dest_island_id, migrants, fitness, src_island_id=None, *args, **kwars):
        # type: (str, ndarray, ndarray, str, *Any, **Any) -> None
        '''
        Send migrants from one island to another.
        The ``mingrants`` parameter can be a single decision vector,
        a list of vectors, or a 2d matrix with the decision vectors
        encoded in rows.
        '''
        migrants = convert_to_2d_array(migrants)
        fitness = convert_to_2d_array(fitness)
        assert migrants.shape[0] == fitness.shape[0]
        self._producer.send(self.topic(dest_island_id),
                            key = src_island_id.encode('utf-8') if isinstance(src_island_id,str) else None,
                            value = self.serialize(migrants, fitness))


    def welcome(self, island_id, n=0):
        # type: (str, int) -> typing.Tuple[ndarray,ndarray,typing.List[str]]
        '''
        Gets ``n`` incoming migrants for the given island and returns them.
        If ``n`` is zero, return all migrants.
        '''
        consumer = self._builder.build_consumer(self.topic(island_id)) # consumer_timeout_ms=time_limit*1000
        result_migrants = []
        try:
            with timeout(self._time_limit, exception=RuntimeError):
                for migrant_msg in consumer:
                    # unpack the message
                    migrant = self.deserialize(migrant_msg)

                    result_migrants.append(migrant)
                    if n != 0 and len(result_migrants) >= n:
                        # we have the requested number of migrants - return
                        break
        except RuntimeError:
            print('Timeout for request from Island : {0}'.format(island_id))
        # sort by most recent
        sorted_migrants = sorted(result_migrants, key=lambda migrant: migrant.timestamp)

        # vstack with empties
        def myvstack(u,v):
            if u.shape == (0,):
                return v
            elif v.shape == (0,):
                return u
            else:
                return vstack([u,v])

        def reducer(a,m):
            marray, farray, sid = a
            if marray.shape[0] < n or n == 0:
                return (myvstack(marray,m.migrants),
                        myvstack(farray,m.fitness),
                        sid + [m.src_id])
            else:
                return (marray, farray, sid)

        def truncate(a,n):
            if a.shape[0] > n:
                return array(a[:n,:])
            else:
                return a

        def truncate_list(l,n):
            if len(l) > n:
                return list(l[:n])
            else:
                return l

        migrant_array, fitness_array, source_ids = reduce(reducer, sorted_migrants, (array([]),array([]),[])) # type: ignore
        # truncate at n
        return (truncate(migrant_array,n), truncate(fitness_array,n), truncate_list(source_ids,n))

