# Sabaody

A distributed implementation of the island model for parameter fitting of dynamical systems biology models. Uses [Spark (on Python)](https://spark.apache.org/) for distributed computing, [pygmo2](https://esa.github.io/pagmo2/) for its various optimization algorithms, and the [Tellurium environment](http://tellurium.analogmachine.org/) for model simulation.

# Organization

* The application business logic is contained in the [sabaody directory](https://github.com/distrib-dyn-modeling/sabaody/tree/master/sabaody). This includes the [interface with pygmo](https://github.com/distrib-dyn-modeling/sabaody/blob/master/sabaody/pygmo_interf.py), the [migration logic](https://github.com/distrib-dyn-modeling/sabaody/blob/master/sabaody/migration.py), the [central migration server](https://github.com/distrib-dyn-modeling/sabaody/blob/master/sabaody/migration_central.py), and the [logic for calculating RMS errors for transient simulations](https://github.com/distrib-dyn-modeling/sabaody/blob/master/sabaody/timecourse/timecourse_sim.py).
* Runnable scripts are contained in the [scripts directory](https://github.com/distrib-dyn-modeling/sabaody/tree/master/sabaody/scripts). Instructions for running the scripts are [here](https://github.com/distrib-dyn-modeling/sabaody/tree/master/sabaody/scripts/b2).
* Finally, pytest tests are located in [tests](https://github.com/distrib-dyn-modeling/sabaody/tree/master/tests).

# Installation

This software relies on Spark, Memcached, InfluxDB, Elastic Search, and a number of Python packages.

## Installing the Python Packages

Please run `pip -r requirements.txt` on all machines in the cluster you wish to set up.

## Installing the other packages

An Ansible script is provided to allow automatically setting up Spark, Memcached, InfluxDB, etc.
First, you will need to create an inventory file to inform Ansible about your machines and respective configurations. You will also need to know your [JAVA_HOME](https://stackoverflow.com/questions/2025290/what-is-java-home-how-does-the-jvm-find-the-javac-path-stored-in-java-home/27716151) directory. Here is a sample inventory file:

```
host1 ansible_ssh_user=myuser java_home=/path/to/java-1.8.0/jre
host2 ansible_ssh_user=myuser java_home=/path/to/java-1.8.0/jre

[all:vars]
hdfshost=host1
pythonexe=/path/to/python-3.6/bin/python3
pipexe=/path/to/python-3.6/bin/pip3

[sqlhost]
host1 sqlpasswd=[SQL PASSWORD]
```

See [this page](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) for more information on working with inventory. Run the following command to start Ansible:

```
ansible-playbook -i my_inventory --connection=local /path/to/sabaody/ansible/playbooks/setup-deps.yaml
```
