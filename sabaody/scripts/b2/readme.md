# Running the B2 Problem

The `b2-driver.py` file contains the entrypoint for running the B2 problem on a cluster. The script is intended to be run with command arguments controlling the archepelago topology and migration settings:

## Spark configuration options

The island model is designed to run a certain number of islands on an equal or slightly larger number of single-core executors (the Python interpreter isn't thread safe so specifying multiple cores per executor adds no benefit). Thus, when submitting the script, always ensure that you specify `spark.executor.cores=1` and set `spark.cores.max` to a value equal to or slightly larger than your number of islands. In practice, the cluster will become memory bound after reaching a certain number of executors (in this problem, 8 executors per node will consume roughly 20 GB on each node), so set your limits accordingly. Start with a small number of islands/executors and work your way up, monitoring memory usage for each configuration.

The number of islands should not exceed the number of executors, because in this situation Spark may queue up the excess islands and run them once the first set of islands has completely finished, rendering migration to/from the excess islands pointless.

## Command line arguments

* `--topology`: The name of the topology to use. Can be `bidir-ring` or `one-way-ring` (more to come).
* `--migration`: Controls the migration scheme. Can be `null`, `central`, or `kafka`.
* `--num-islands`: The number of islands in the archepelago. This should be less than or equal to `spark.cores.max` for optimal operation.
* `host`: A positional argument, specifies the hostname of the Spark master node (the script always uses port 7077).

```
spark-submit --deploy-mode client --conf "spark.cores.max=17" --conf "spark.executor.cores=1" b2-driver.py --topology bidir-ring --migration central --num-islands 16 HOSTNAME
```
