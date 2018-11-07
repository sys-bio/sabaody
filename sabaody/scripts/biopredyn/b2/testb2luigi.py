import luigi
from luigi.contrib.spark import SparkSubmitTask, PySparkTask
from itertools import product
from uuid import uuid4


num_islands = list(range(4 , 5))
topology = ["bidir-ring"]
migration = ["central"]
migration_policy = ["uniform"]
host = ["luna"]
command = ["run"]


class B2SparkSubmit(SparkSubmitTask):
    executor_cores = 1
    conf = "spark.cores.max=17,spark.executor.cores=1"
    deploy_mode = 'client'

    app = "b2-driver.py"

    topology = luigi.Parameter()
    num_islands = luigi.IntParameter()
    migration = luigi.Parameter()
    migration_policy = luigi.Parameter()
    host = luigi.Parameter()
    command = luigi.Parameter()

    def app_options(self):
        app_command = [self.command]
        app_command += self._text_arg('--topology' , self.topology)
        app_command += self._text_arg('--migration' , self.migration)
        app_command += self._text_arg('--migration-policy' , self.migration_policy)
        app_command += self._text_arg('--num-islands' , self.num_islands)
        app_command += self._text_arg('--host' , self.host)
        return app_command

    def output(self):
        return luigi.LocalTarget("square{0}s.txt".format(str(uuid4())))






class B2Suite(luigi.WrapperTask):
    def requires(self):
        global num_islands, topology, migration_policy, migration
        tasks = []
        combinations = list(product(topology, num_islands, migration, migration_policy,host,command))
        for arrangement in combinations:
            yield B2SparkSubmit(**{
                "topology" : arrangement[0],
                "num_islands" : arrangement[1],
                "migration" : arrangement[2],
                "migration_policy" : arrangement[3],
                "host" : arrangement[4],
                "command" : arrangement[5]
            })

        

    def complete(self):
        return all(r.complete() for r in self.requires())



