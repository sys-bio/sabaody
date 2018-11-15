#import mysql.connector as mariadb
import MySQLdb

mariadb_connection = MySQLdb.connect(host='luna',user='sabaody',passwd='w00t',db='sabaody')
cursor = mariadb_connection.cursor()

cursor.execute('SELECT Content FROM topology_sets WHERE PrimaryKey=1;')
from pickle import loads
topologies = loads(cursor.fetchone()[0])

from sabaody import TopologyGenerator
t = TopologyGenerator.find('One-way ring, de+nelder mead',topologies)
