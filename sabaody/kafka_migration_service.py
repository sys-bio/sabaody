# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley
from __future__ import print_function, division, absolute_import

from .migration import Migrator

from kafka import KafkaProducer
from kafka import KafkaConsumer
from interruptingcow import timeout
from numpy import array, ndarray, vstack
import arrow

from uuid import uuid4
import json
import typing

def make_migrant_array(migrants):
    # type: (typing.Union[ndarray,typing.List[ndarray]]) -> ndarray
    '''
    Convert ``migrants`` into a 2d array.
    ``migrants`` can be a list of decision vectors,
    a single decision vector, or a 2d (in which case
    it is returned as-is).
    '''
    if isinstance(migrants,list):
        for m in migrants:
            if not isinstance(m,ndarray):
                raise RuntimeError('`migrants` should be a list of ndarrays, instead found element of type {}'.format(type(m)))
            if not (m.ndim < 2 or (m.ndim == 2 and m.shape[-1] == 1)):
                raise RuntimeError('Received 2d array for migrant - migrants should be 1d arrays or row vectors')
        return vstack(tuple(m for m in migrants))
    elif isinstance(migrants,ndarray):
        if migrants.ndim == 1:
            return migrants.reshape((1,-1))
        elif migrants.ndim == 2:
            return migrants
        else:
            raise RuntimeError('Wrong n dims for migrants: {}'.format(migrants.ndim))
    else:
        raise RuntimeError('Wrong type for migrants - should be list or ndarray but received {}'.format(type(migrants)))

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


    def build_consumer(self, topic_name):
        url = ",".join(each_host + ":" + self._port for each_host in self._hosts)
        return KafkaConsumer(topic_name , bootstrap_servers=url , auto_offset_reset='earliest')



class KafkaMigrator(Migrator):
    '''
    A migrator which sends / receives migrants using Kafka.
    Kafka does not use pools - it is a distributed message
    processing system, so the order in which migrants are
    received will, in general, be unknown.
    '''

    def __init__(self, selection_policy, migration_policy, builder, timeout=10):
        '''
        Constructor for KafkaMigrator.

        :param timeout: Time limit (in seconds) to wait for incoming migrants.
        '''
        self._builder = builder
        self._identifier = str(uuid4())
        self._timeout = timeout
        self._producer = self._builder.build_producer()


    def serialize(self, migrant_array, fitness):
        '''
        Returns a JSON-serialized bytes object representing the 2d migrant array.
        Decision vectors should be row-encoded in the input array.
        '''
        serialized_data = {
            'migrants': migrant_array.tolist(),
            'fitness' : fitness.tolist(),
            }
        return json.dumps(serialized_data).encode('utf-8')


    def deserialize(self, migrant_data):
        data = json.loads(migrant_data)
        return (array(data['migrants']), array(data['fitness']))


    def migrate(self, dest_island_id, migrants, fitness, src_island_id = None, expiration_time=arrow.utcnow().shift(days=+1)):
        # type: (str, ndarray, float, str, arrow.Arrow) -> None
        '''
        Send migrants from one island to another.
        The ``mingrants`` parameter can be a single decision vector,
        a list of vectors, or a 2d matrix with the decision vectors
        encoded in rows.
        '''
        migrants = make_migrant_array(migrants)
        topic_name = '_'.join([dest_island_id, self._identifier])
        if isinstance(src_island_id,str):
            src_island_id = src_island_id.encode('utf-8')
        self._producer.send(topic_name, key = src_island_id, value = self.serialize(migrants, fitness))


    def welcome(self, island_id, n=0):
        # type: (str, int) -> typing.Tuple[ndarray,ndarray,typing.List[str]]
        '''
        Gets ``n`` incoming migrants for the given island and returns them.
        If ``n`` is zero, return all migrants.
        '''
        result_migrants = []
        result_fitness = []
        source_ids = []
        topic_name = "_".join([island_id, self._identifier])
        consumer = self._builder.build_consumer(topic_name)
        try:
            with timeout(self._timeout, exception=RuntimeError):
                for migrant_msg in consumer:
                    source_ids.append(migrant_msg.key.decode('utf-8'))

                    migrants,fitness = self.deserialize(migrant_msg.value)
                    result_migrants.append(migrants)
                    result_fitness.append(fitness)
                    if n != 0 and len(result_migrants) >= n:
                        # we have the requested number of migrants - return
                        break
        except RuntimeError:
            print('Timeout for request from Island : {0}'.format(island_id))
        return (vstack(result_migrants), vstack(result_fitness), source_ids)

