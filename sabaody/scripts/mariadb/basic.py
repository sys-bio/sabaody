#import mysql.connector as mariadb
import MySQLdb

# https://stackoverflow.com/questions/1720244/create-new-user-in-mysql-and-give-it-full-access-to-one-database
#mariadb_connection = mariadb.connect(user='sabaody', password='w00t', database='sabaody')
#cursor = mariadb_connection.cursor()

mariadb_connection = MySQLdb.connect('localhost','sabaody','w00t','sabaody')
cursor = mariadb_connection.cursor()