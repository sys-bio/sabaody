# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley
from __future__ import print_function, division, absolute_import

from .migration import Migrator

from numpy import array, ndarray
import arrow

from uuid import uuid4
import json
import typing

from .kafka_migration_service import convert_to_2d_array


class ESMigrator(Migrator):
    '''
    A migrator which sends / receives migrants using Elastic Search.
    '''

    def __init__(self, selection_policy, ReplacementPolicyBase, topology_id):
        # type: (str, SelectionPolicyBase, ReplacementPolicyBase, str) -> None
        '''
        Constructor for KafkaMigrator.

        :param timeout: Time limit (in seconds) to wait for incoming migrants.
        '''
        self.topology_id = topology_id


    def migrate(self, dest_island_id, migrants, fitness, src_island_id=None, expiration_time=arrow.utcnow().shift(days=+1)):
        # type: (str, ndarray, ndarray, str, arrow.Arrow) -> None
        """
        :param application_id:
        :param topology_id:
        :param from_island:
        :param to_island:
        :param migrants:
        :return:

        database_name : index
        table : type
        row : document
        column: field

        application_id --> INDEX
        topology_id --> type
        """
        push_body = {
            "gen": generation,
            "to": dest_island_id,
            "from": src_island_id, # FIXME: can be none, how to handle?
            "migrants": migrants ,
            "timestamp": expiration_time.isoformat() # replace with message timestamp?
        }
        es.create(index=application_id , doc_type=self.topology_id , id=str(uuid4()) , body=push_body)


    def welcome(self, island_id, n=0):
        # type: (str, int) -> typing.Tuple[ndarray,ndarray,typing.List[str]]
        '''
        Gets ``n`` incoming migrants for the given island and returns them.
        If ``n`` is zero, return all migrants.
        '''
        search_object = {
            "query": {
                "term": {"to": island}
            }
        }
        return es.search(index=application_id , doc_type=self.topology_id , body=json.dumps(search_object))

