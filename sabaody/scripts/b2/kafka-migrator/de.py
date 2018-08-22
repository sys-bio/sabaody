# Run an archepelago consisting solely of DE algorithms using Kafka migration

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("b2-kafka-de")
sc = SparkContext(conf=conf)

from sabaody import Archipelago

from ..b2setup import B2Run

with B2Run('luna', 11211) as run:
    from b2problem import make_problem
    a = Archipelago(make_problem)
    a.set_mc_server(run.mc_host, run.mc_port, run.getNameQualifier())
    a.run(sc)

