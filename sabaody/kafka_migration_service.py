# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley
from __future__ import print_function, division, absolute_import

from kafka import KafkaProducer
from kafka import KafkaConsumer
from uuid import uuid4
from interruptingcow import timeout
import json

class KafkaBuilder(object):
    def __init__(self, hosts, port):
        '''
        Construct a new Kafka builder for a list of hosts and a port number (as a string).

        :param hosts: A list of host names / ips to use.
        :type hosts:  list or str
        :param port:  The port to listen on
        :type port:   int or str
        '''
        self._hosts = list(hosts)
        self._port = str(port)


    def build_producer(self):
        url = ",".join(each_host + ":" + self._port for each_host in self._hosts)
        return KafkaProducer(bootstrap_servers=url)


    def build_consumer(self, topic_name):
        url = ",".join(each_host + ":" + self._port for each_host in self._hosts.split(","))
        return KafkaConsumer(topic_name , bootstrap_servers=url , auto_offset_reset='earliest')



class KafkaMigrator(object):
    def __init__(self, builder):
        self._builder = builder
        self._buffer_size = 10
        self._identifier = str(uuid4())
        self._timeout = 10
        self._producer = self._builder.build_producer()


    def set_migrants_buffer_size(self, buffer_size):
        self._buffer_size = buffer_size


    def set_timeout(self, timeout):
        self._timeout = timeout


    def migrate(self, migrants, from_island, to_island, num_generation):
        for each_migrant in migrants:
            topic_name = "_".join([to_island , self._identifier , str(num_generation)])
            self._producer.send(topic_name , key = from_island, value =self.serialize(each_migrant))


    def serialize(self, migrants):
        serialized_data = {"data":migrants}
        return json.dumps(serialized_data)


    def deserialize(self, migrant):
        return json.loads(migrant)["data"]


    def welcome(self, island, indegree, num_generation=1):
        replacement_policy_migrants = []
        source_ids = []
        topic_name = "_".join([island, self._identifier, str(num_generation-1)])
        consumer = self._builder.build_consumer(topic_name)
        try:
            with timeout(self._timeout, exception=RuntimeError):
                for each_migrant in consumer:
                    source_ids.append((each_migrant.key))
                    replacement_policy_migrants.append(self.deserialize(each_migrant.value))
                    if len(replacement_policy_migrants) >= self._buffer_size:
                        break
                    elif len(replacement_policy_migrants) >= indegree:
                        break
        except RuntimeError:
            print("Timeout for request from Island : {0} for generation : {1}".format(island,num_generation))
        replacement_policy_migrants = zip(*replacement_policy_migrants) # FIXME: needs to be a list?
        replacement_policy_migrants.append(source_ids)
        return replacement_policy_migrants
