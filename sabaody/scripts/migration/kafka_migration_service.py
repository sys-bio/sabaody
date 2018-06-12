from kafka import KafkaProducer
from kafka import KafkaConsumer
from uuid import uuid4
from interruptingcow import timeout
import json

class KafkaBuilder(object):
    _hosts = "128.208.17.254"
    _port = "9092"


    @staticmethod
    def build_producer():
        url = ",".join(each_host + ":" + KafkaBuilder._port for each_host in KafkaBuilder._hosts.split(","))
        return KafkaProducer(bootstrap_servers=url)


    @staticmethod
    def build_consumer(topic_name):
        url = ",".join(each_host + ":" + KafkaBuilder._port for each_host in KafkaBuilder._hosts.split(","))
        return KafkaConsumer(topic_name , bootstrap_servers=url , auto_offset_reset='earliest')



class KafkaMigration(object):
    _producer = None
    _buffer_size = 10
    _identifier = str(uuid4())
    _timeout = 10

    @staticmethod
    def set_migrants_buffer_size(buffer_size):
        KafkaMigration._buffer_size = buffer_size


    @staticmethod
    def set_timeout(timeout):
        KafkaMigration._timeout = timeout


    @staticmethod
    def migrate(migrants , from_island , to_island , num_generation):
        for each_migrant in migrants:
            topic_name = "_".join([to_island , KafkaMigration._identifier , str(num_generation)])
            KafkaMigration._producer.send(topic_name , key = from_island, value =KafkaMigration.serialize(each_migrant))


    @staticmethod
    def serialize(migrants):
        serialized_data = {"data":migrants}
        return json.dumps(serialized_data)


    @staticmethod
    def deserialize(migrant):
        return json.loads(migrant)["data"]


    @staticmethod
    def welcome(island,indegree, num_generation=1):
        replacement_policy_migrants = []
        source_ids = []
        topic_name = "_".join([island , KafkaMigration._identifier , str(num_generation-1)])
        consumer = KafkaBuilder.build_consumer(topic_name)
        try:
            with timeout(KafkaMigration._timeout , exception=RuntimeError):
                for each_migrant in consumer:
                    source_ids.append((each_migrant.key))
                    replacement_policy_migrants.append(KafkaMigration.deserialize(each_migrant.value))
                    if len(replacement_policy_migrants) >= KafkaMigration._buffer_size:
                        break
                    elif len(replacement_policy_migrants) >= indegree:
                        break
        except RuntimeError:
            print("Timeout for request from Island : {0} for generation : {1}".format(island,num_generation))
        replacement_policy_migrants = zip(*replacement_policy_migrants) # FIXME: needs to be a list?
        replacement_policy_migrants.append(source_ids)
        return replacement_policy_migrants

KafkaMigration._producer = KafkaBuilder.build_producer()