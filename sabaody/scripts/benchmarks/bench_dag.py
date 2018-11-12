# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from airflow.operators.python_operator import PythonOperator
from airflow.operators.mysql_operator import MySqlOperator

def topology_generator(n_islands, island_size, migrant_pool_size):
            from sabaody import TopologyGenerator
            import MySQLdb
            mariadb_connection = MySQLdb.connect('localhost','sabaody','w00t','sabaody')
            cursor = mariadb_connection.cursor()

            generator = TopologyGenerator(island_size=island_size, migrant_pool_size=migrant_pool_size)
            major,minor,patch = generator.get_version()
            cursor.execute('SELECT COUNT(DISTINCT VersionMajor, VersionMinor, VersionPatch) FROM topology_sets;')
            n_matches = int(cursor.fetchone())
            print('n_matches',n_matches)

            if n_matches == 0:
                serialized_topologies = generator.generate_all()
                # store in database
                n_matches = cursor.execute('\n'.join(
                    'INSERT INTO topology_sets (TopologySetID, VersionMajor, VersionMinor, VersionPatch, NumIslands, IslandSize, MigrantPoolSize, Content',
                    'VALUES ({id},{major},{minor},{patch},{n_islands},{island_size},{migrant_pool_size},{content});'.format(
                        id='topology_set({})'.format(generator.get_version_string()),
                        major=major,
                        minor=minor,
                        patch=patch,
                        n_islands=n_islands,
                        island_size=island_size,
                        migrant_pool_size=migrant_pool_size,
                        content=serialized_topologies)))
                cursor.commit()

class TaskFactory():
    def create(self, dag):
        self.setup_tables = MySqlOperator(
            task_id='setup_tables',
            database='sabaody',
            sql='''
                CREATE TABLE IF NOT EXISTS topology_sets (
                  PrimaryKey INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                  TopologySetID VARCHAR(255) NOT NULL,
                  VersionMajor INT NOT NULL,
                  VersionMinor INT NOT NULL,
                  VersionPatch INT NOT NULL,
                  NumIslands INT NOT NULL,
                  IslandSize INT NOT NULL,
                  MigrantPoolSize INT NOT NULL,
                  Content BLOB(100) NOT NULL);''',
          dag=dag)

        self.generate_topologies = PythonOperator(
            task_id='generate_topologies',
            python_callable=topology_generator,
            op_kwargs={
                'n_islands': 10,
                'island_size': 10,
                'migrant_pool_size': 2},
            dag=dag)

        self.setup_tables >> self.generate_topologies
