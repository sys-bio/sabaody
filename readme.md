# Sabaody

A distributed implementation of the island model for parameter fitting of dynamical systems biology models. Uses [Spark (on Python)](https://spark.apache.org/) for distributed computing, [pygmo2](https://esa.github.io/pagmo2/) for its various optimization algorithms, and the [Tellurium environment](http://tellurium.analogmachine.org/) for model simulation.

# Organization

* The application business logic is contained in the [sabaody directory](https://github.com/distrib-dyn-modeling/sabaody/tree/master/sabaody). This includes the [interface with pygmo](https://github.com/distrib-dyn-modeling/sabaody/blob/master/sabaody/pygmo_interf.py), the [migration logic](https://github.com/distrib-dyn-modeling/sabaody/blob/master/sabaody/migration.py), the [central migration server](https://github.com/distrib-dyn-modeling/sabaody/blob/master/sabaody/migration_central.py), and the [logic for calculating RMS errors for transient simulations](https://github.com/distrib-dyn-modeling/sabaody/blob/master/sabaody/timecourse_model.py).
* Runnable scripts are contained in the [scripts directory](https://github.com/distrib-dyn-modeling/sabaody/tree/master/sabaody/scripts). For example, to run the parameter fitting routine for model B2, the [b2-driver.py file](https://github.com/distrib-dyn-modeling/sabaody/tree/master/sabaody/scripts/b2) can be run via `spark-submit` as follows:
```
$ cd sabaody/scripts/b2
$ spark-submit --master spark://spark-master:7077 --deploy-mode client --driver-memory 1g --num-executors 4 --executor-cores 2 --files=../../../sbml/b2.xml --py-files=data.py,b2problem.py,params.py,b2setup.py b2-driver.py
```
* Finally, pytest tests are located in [tests](https://github.com/distrib-dyn-modeling/sabaody/tree/master/tests).
