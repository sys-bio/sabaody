# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley
from __future__ import print_function, division, absolute_import

from .migration import Migrator, MigrantData, convert_to_2d_array, to_migrant_tuple

from elasticsearch import Elasticsearch, helpers
from numpy import array, ndarray
import arrow

from uuid import uuid4
import json
import datetime
from typing import Tuple, List, Any

from .kafka_migration_service import convert_to_2d_array


class ESBuilder:
    '''
    A class for connecting to ES instances.
    '''

    def __init__(self, host, port):
        '''
        Connect to an ES instance at the specified host & port.

        :param hosts: The ES host
        :type hosts:  str
        :param port:  The port ES is running on
        :type port:   int
        '''
        self._host = host
        self._port = port


    def build(self):
        return Elasticsearch([{'host': self._host , 'port': self._port}])


class ESMigratorBase(Migrator):
    '''
    A migrator which sends / receives migrants using Elastic Search.
    '''

    def __init__(self, migration_policy, selection_policy, replacement_policy, es_builder, archipelago_id):
        '''
        Constructor for ES migrator.
        '''
        super().__init__(migration_policy, selection_policy, replacement_policy)
        self.es_instance = es_builder.build()
        self.archipelago_id = archipelago_id

        self.es_instance.indices.create(index=self.archipelago_id, body={
                                        "mappings" : {
                                            "_doc" : {
                                                "properties" : {
                                                    #"migrants" : {
                                                        #"type" : "keyword",
                                                    #},
                                                    #"fitness" : {
                                                        #"type" : "keyword",
                                                    #},
                                                    "from" : {
                                                        "type" : "keyword",
                                                    },
                                                    "to" : {
                                                        "type" : "keyword",
                                                    },
                                                    #"timestamp" : {
                                                        #"type" : "keyword",
                                                    #},
                                                }
                                            }
                                        }})


    def deserialize(self, data):
        # type: (Any) -> MigrantData
        return MigrantData(
          migrants  = array(data['migrants']),
          fitness   = array(data['fitness']),
          timestamp = arrow.get(data['timestamp']),
          src_id    = array(data['from']),
          )


    def _migrate(self, dest_island_id, migrants, fitness, src_island_id=None, expiration_time=arrow.utcnow().shift(days=+1)):
        migrants = convert_to_2d_array(migrants)
        fitness = convert_to_2d_array(fitness)
        assert migrants.shape[0] == fitness.shape[0]

        #helpers.bulk(self.es_instance, [
            #{
                #"_index": self.archipelago_id,
                #"_type": "document",
                #"_id": str(uuid4()),
                #"_source": {
                    ##"gen": generation ,
                    #"to": dest_island_id,
                    #"from": src_island_id,
                    #"migrants": m.tolist(),
                    #"fitness": f.tolist(),
                    #"timestamp": arrow.utcnow().isoformat(),
                #}
            #}
            #for m,f in zip(migrants,fitness)
        #])
        #print('index {}'.format(self.archipelago_id))
        self.es_instance.index(index=self.archipelago_id,
                               doc_type="_doc",
                               id=str(uuid4()),
                               body={
                                   #"gen": generation ,
                                   "to": dest_island_id,
                                   "from": src_island_id,
                                   "migrants": migrants.tolist(),
                                   "fitness": fitness.tolist(),
                                   "timestamp": arrow.utcnow().isoformat(),
                               })


class ESMigratorPostSort(ESMigratorBase):
    '''
    ES migrator class that performs sorting in Python.
    '''

    def _welcome(self, island_id, n=0):
        # type: (str, int) -> Tuple[ndarray,ndarray,List[str]]
        '''
        Gets ``n`` incoming migrants for the given island and returns
        migrants sorted by timestamp descending.
        If ``n`` is zero, return all migrants.
        '''
        self.es_instance.indices.refresh(index=self.archipelago_id)
        search_results = self.es_instance.search(index=self.archipelago_id,
                                                 body={
                                                     "query": {
                                                         "term": {"to": island_id}
                                                         #"match_all": {}
                                                     }
                                                 })

        for _ in range(2):
            if "hits" in search_results.keys():
                search_results = search_results["hits"]

        # TODO: delete records

        # sort in Python
        migrants = sorted([self.deserialize(each_element['_source']) for each_element in search_results],
                          key=lambda m: m.timestamp,
                          reverse=True)
        # truncate to n migrants if too long
        return to_migrant_tuple(migrants[:n] if len(migrants) > n else migrants, n)


class ESMigrator(ESMigratorBase):
    '''
    ES migrator class that performs sorting using ES (faster?).
    '''

    def _welcome(self, island_id, n=0):
        # type: (str, int) -> Tuple[ndarray,ndarray,List[str]]
        '''
        Gets ``n`` incoming migrants for the given island and returns
        migrants sorted by timestamp descending.
        If ``n`` is zero, return all migrants.
        '''
        self.es_instance.indices.refresh(index=self.archipelago_id)
        search_results = self.es_instance.search(index=self.archipelago_id,
                                                 body={
                                                    "query": {
                                                        "term": {"to": island_id}
                                                    },
                                                    "sort": [
                                                        {
                                                        "timestamp": {"order":"desc"}
                                                        }
                                                    ],
                                                    "size": n
                                                })

        for _ in range(2):
            if "hits" in search_results.keys():
                search_results = search_results["hits"]

        # TODO: delete records

        return to_migrant_tuple(
            [self.deserialize(each_element['_source']) for each_element in search_results],
            n)

