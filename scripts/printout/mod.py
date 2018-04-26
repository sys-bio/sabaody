def spark_method(x):
    #print('meth')
    from time import sleep
    #sleep(30)
    #sleep(5)
    import socket
    hostname = socket.gethostname()
    ## https://stackoverflow.com/questions/25407550/how-do-i-log-from-my-python-spark-script
    #log4jLogger = sc._jvm.org.apache.log4j
    #l = log4jLogger.LogManager.getLogger(__name__)
    hoststr = 'HOST: {} **********'.format(hostname)
    import logging
    l = logging.getLogger('worker')
    l.warn("pyspark script logger initialized")
    l.warn(hoststr)
    #return hostname
    ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    import sys
    n = 0
    for k in range(200000):
        n += k
    return (ip, hostname, sys.executable, n)