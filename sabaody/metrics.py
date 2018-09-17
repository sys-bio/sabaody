# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley
from __future__ import print_function, division, absolute_import

from influxdb import InfluxDBClient

from uuid import uuid4

class Metric:
    pass

class InfluxDBMetric(Metric):
    '''
    Keeps metrics in an InfluxDB database.
    '''
    def __init__(self, host='localhost', port=8086, username='root', password='root', database=None, database_prefix=None, ssl=False, verify_ssl=False, timeout=None, retries=3, use_udp=False, udp_port=4444, proxies=None):
        self.client = InfluxDBClient(host=host, port=port, username=username, password=password, database=None, ssl=ssl, verify_ssl=verify_ssl, timeout=timeout, retries=retries, use_udp=use_udp, udp_port=udp_port, proxies=proxies)
      if database is None:
          if database_prefix is None:
              raise RuntimeError('Expected a database name')
          else:
              database = database_prefix + str(uuid4())
      self.database = database

    def process_deltas(self, deltas, src_ids, current_champ_score):
        self.client.write_points([
            { 'measurement': 'delta',
              'time': arrow.utcnow().isoformat(),
              'fields': {
                  'abs_delta': float(delta),
                  'delta_rel_to_champ': float(delta)/current_champ_score,
                  'src_id': src_id,
              }
            } for delta,src_id in zip(deltas,src_ids)])

    def __enter__(self):
        self.client.create_database(self.database)

    def __exit__(self, exception_type, exception_val, trace):
        self.client.drop_database(self.database)