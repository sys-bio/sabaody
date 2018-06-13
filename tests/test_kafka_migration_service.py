# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley
from __future__ import print_function, division, absolute_import


def test_migrate():
    from sabaody.kafka_migration_service import KafkaMigrator, KafkaBuilder
    #migrator = KafkaMigrator(KafkaBuilder("128.208.17.254", "9092"))
    #migrator.migrate([1,2,3,4],"from-island","to-island",3)
    #migrants = migrator.welcome("to-island",1,4)
    #assert len(migrants) == 4