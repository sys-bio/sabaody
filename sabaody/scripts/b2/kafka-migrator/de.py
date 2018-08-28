# Run an archepelago consisting solely of DE algorithms using Kafka migration

from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("b2-kafka-de")
sc = SparkContext(conf=conf)

from sabaody import Archipelago

from ..b2setup import B2Run

topology = 'one-way-ring'
n_islands = 100

with B2Run('luna', 11211) as run:
    from b2problem import make_problem
    def make_algorithm():
        return pg.de(gen=10)

    topology_factory = TopologyFactory(make_problem, run.getNameQualifier(), run.mc_host, run.mc_port)

    if topology == 'ring' or topology == 'bidir-ring':
        a = Archipelago(topology_factory.createBidirRing(make_algorithm,n_islands))
    elif topology == 'one-way-ring':
        a = Archipelago(topology_factory.createOneWayRing(make_algorithm,n_islands))
    else:
        raise RuntimeError('Unrecognized topology')
    a.set_mc_server(run.mc_host, run.mc_port, run.getNameQualifier())
    a.run(sc)

