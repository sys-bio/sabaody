from sabaody.scripts.migration.kafka_migration_service import KafkaMigration


def test_migrate():
    KafkaMigration.migrate([1,2,3,4],"from-island","to-island",3)
    migrants = KafkaMigration.welcome("to-island",1,4)
    assert len(migrants) == 4