# Sabaody

A distributed implementation of the island model for parameter fitting of dynamical systems biology models. Uses [Spark (on Python)](https://spark.apache.org/) for distributed computing, [pygmo2](https://esa.github.io/pagmo2/) for its various optimization algorithms, and the [Tellurium environment](http://tellurium.analogmachine.org/) for model simulation.

# Organization

* The application business logic is contained in the [sabaody directory](https://github.com/distrib-dyn-modeling/sabaody/tree/master/sabaody). This includes the [interface with pygmo](https://github.com/distrib-dyn-modeling/sabaody/blob/master/sabaody/pygmo_interf.py), the [migration logic](https://github.com/distrib-dyn-modeling/sabaody/blob/master/sabaody/migration.py), the [central migration server](https://github.com/distrib-dyn-modeling/sabaody/blob/master/sabaody/migration_central.py), and the [logic for calculating RMS errors for transient simulations](https://github.com/distrib-dyn-modeling/sabaody/blob/master/sabaody/timecourse_model.py).
* Runnable scripts are contained in the [scripts directory](https://github.com/distrib-dyn-modeling/sabaody/tree/master/sabaody/scripts). Instructions for running the scripts are [here](https://github.com/distrib-dyn-modeling/sabaody/tree/master/sabaody/scripts/b2).
* Finally, pytest tests are located in [tests](https://github.com/distrib-dyn-modeling/sabaody/tree/master/tests).
