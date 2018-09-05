# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley
from __future__ import print_function, division, absolute_import

from .migration import Migrator, MigrantData, convert_to_2d_array, to_migrant_tuple

from typing import Any
from kafka import KafkaProducer
from kafka import KafkaConsumer
from interruptingcow import timeout
from numpy import array, ndarray, vstack
import arrow

from uuid import uuid4
import json
import typing

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


class KafkaMigrator(Migrator):
    '''
    A migrator which sends / receives migrants using Kafka.
    Kafka does not use pools - it is a distributed message
    processing system, so the order in which migrants are
    received will, in general, be unknown.
    '''


    def __init__(self, migration_policy, selection_policy, replacement_policy, builder, time_limit=10):
        '''
        Constructor for KafkaMigrator.

        :param timeout: Time limit (in seconds) to wait for incoming migrants.
        '''
        super().__init__(migration_policy, selection_policy, replacement_policy)
        self._builder = builder
        self._identifier = str(uuid4())
        self._time_limit = time_limit
        self._producer = self._builder.build_producer()


    def __getstate__(self):
        return {
          'builder': self._builder.__getstate__(),
          'identifier': self._identifier,
          'time_limit': self._time_limit,
          'selection_policy': self.selection_policy,
          'replacement_policy': self.replacement_policy,
          }


    def __setstate__(self, state):
        selection_policy = state['selection_policy']
        replacement_policy = state['replacement_policy']
        super().__init__(selection_policy, replacement_policy)

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


    def _migrate(self, dest_island_id, migrants, fitness, src_island_id=None, *args, **kwars):
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


    def _welcome(self, island_id, n=0):
        # type: (str, int) -> typing.Tuple[ndarray,ndarray,typing.List[str]]
        '''
        Gets ``n`` incoming migrants for the given island and returns them.
        If ``n`` is zero, return all migrants.
        '''
        consumer = self._builder.build_consumer(self.topic(island_id)) # consumer_timeout_ms=time_limit*1000
        result_migrants = []
        total_migrants = 0
        class TimeoutError(Exception):
            pass
        try:
            with timeout(self._time_limit, exception=TimeoutError):
                for migrant_msg in consumer:
                    # unpack the message
                    migrant = self.deserialize(migrant_msg)

                    result_migrants.append(migrant)
                    total_migrants += migrant.migrants.shape[0]
                    if n != 0 and total_migrants >= n:
                        # we have the requested number of migrants - return
                        break
        except TimeoutError:
            print('Timeout for request from Island : {0}'.format(island_id))
        # sort by most recent
        sorted_migrants = sorted(result_migrants, key=lambda migrant: migrant.timestamp, reverse=True)
        #sorted_migrants = result_migrants

        return to_migrant_tuple(sorted_migrants, n)

