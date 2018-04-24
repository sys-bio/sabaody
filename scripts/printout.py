from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("printout")
sc = SparkContext(conf=conf)
sc.setLogLevel("ERROR")
from pprint import PrettyPrinter
pp = PrettyPrinter(2)


print('hello')
try:
    nexecutors = int(sc._conf.get('spark.executor.instances'))
    print('Using {} executors'.format(nexecutors))
except:
    nexecutors = 40
    print('Cannot determine number of executors, using default value {}'.format(nexecutors))

print('\n')

def spark_method(x):
    #print('meth')
    from time import sleep
    #sleep(30)
    import socket
    hostname = socket.gethostname()
    #return hostname
    #return [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    import sys
    n = 0
    for k in range(200000):
        n += k
    return (hostname, sys.executable, n)


results = sc.range(nexecutors).map(spark_method).collect()
print('Results:')
pp.pprint(results)
#print('\nUnique results:')
#print(set(results))

#nums = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 20])
#print(nums.collect())

#sumAndCount = nums.map(lambda x: (x, 1)).fold((0, 0), (lambda x, y: (x[0] + y[0], x[1] + y[1])))

#print(sumAndCount)