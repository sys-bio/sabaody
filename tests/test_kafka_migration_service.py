# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley
from __future__ import print_function, division, absolute_import

from numpy import array, array_equal

def test_migrate():
    from sabaody.kafka_migration_service import KafkaMigrator, KafkaBuilder
    migrator = KafkaMigrator(None, None, None, KafkaBuilder('localhost', 9092))

    migrator._migrate('to-island', array([1,2,3,4]), array([0.]), 'from-island')

    migrants,fitness,src_ids = migrator._welcome("to-island",n=1)

    assert array_equal(migrants, array([[1,2,3,4]]))
    assert array_equal(fitness, array([[0.]]))
    assert src_ids == ['from-island']

def test_most_recent_migrants():
    from sabaody.kafka_migration_service import KafkaMigrator, KafkaBuilder
    migrator = KafkaMigrator(None, None, None, KafkaBuilder('localhost', 9092))

    for k in range(10):
        migrator._migrate('to-island', array([k]), array([0.]), 'from-island')

    migrants,fitness,src_ids = migrator._welcome("to-island",n=5)

    assert array_equal(migrants, array([[4],[3],[2],[1],[0]]))
    assert src_ids == ['from-island']*5