from kafka import KafkaProducer
from kafka import KafkaConsumer
from uuid import uuid4
from interruptingcow import timeout


class KafkaBuilder(object):
    _hosts = "128.208.17.254"
    _port = "9092"


    @staticmethod
    def build_producer():
        url = ",".join(each_host + ":" + KafkaMigration._port for each_host in KafkaMigration._hosts.split(","))
        return KafkaProducer(bootstrap_servers=url)

    @staticmethod
    def build_consumer(topic_name):
        url = ",".join(each_host + ":" + KafkaMigration._port for each_host in KafkaMigration._hosts.split(","))
        return KafkaConsumer(topic_name , bootstrap_servers=url , auto_offset_reset='earliest')


class KafkaMigration(object):

    _producer = KafkaBuilder.build_producer()
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
        topic_name = "_".join([to_island , KafkaMigration._identifier , str(num_generation)])
        for each_migrant in migrants:
            KafkaMigration._producer.send(topic_name , key = from_island, value =str(each_migrant))



    @staticmethod
    def welcome(island,num_generation):
        replacement_policy_migrants = []
        topic_name = "_".join([island , KafkaMigration._identifier , str(num_generation-1)])
        consumer = KafkaBuilder.build_consumer(topic_name)
        try:
            with timeout(60 * 5 , exception=RuntimeError):
                for each_migrant in consumer:
                    replacement_policy_migrants.append(each_migrant.value)
                    if len(replacement_policy_migrants) >= KafkaMigration._buffer_size:
                        break
        except RuntimeError:
            print "Timeout for request from Island : {0} for generation : {1}".format(island,num_generation)
        return replacement_policy_migrants
