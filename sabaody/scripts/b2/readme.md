* suggested spark command:
```
spark-submit --master spark://YOURHOST:7077 --deploy-mode client --driver-memory 1g --num-executors 4 --executor-cores 2 --files=../../../sbml/b2.xml --py-files=data.py,b2problem.py,params.py,b2setup.py b2-driver.py
```
