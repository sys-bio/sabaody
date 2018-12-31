# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley
from __future__ import print_function, division, absolute_import

from influxdb import InfluxDBClient
import arrow

from uuid import uuid4

class Metric:
    pass

class InfluxDBMetric(Metric):
    '''
    InfluxDB metric processor.
    '''
    def __init__(self, host='localhost', port=8086, username='root', password='root', database=None, database_prefix=None, ssl=False, verify_ssl=False, timeout=None, retries=3, use_udp=False, udp_port=4444, proxies=None):
        self.client = InfluxDBClient(host=host, port=port, username=username, password=password, database=None, ssl=ssl, verify_ssl=verify_ssl, timeout=timeout, retries=retries, use_udp=use_udp, udp_port=udp_port, proxies=proxies)
        if database is None:
            if database_prefix is None:
                raise RuntimeError('Expected a database name')
            else:
                database = database_prefix + str(uuid4())
        self.database = database
        # self.database = database.replace('.','_').replace('-','_')


    def process_deltas(self, deltas, src_ids, round):
        self.client.write_points([
            { 'measurement': 'delta',
              'time': arrow.utcnow().isoformat(),
              'fields': {
                  'abs_delta': float(delta),
                  # 'delta_rel_to_champ': float(delta)/current_champ_score,
                  'src_id': src_id,
                  'round': round,
              }
            } for delta,src_id in zip(deltas,src_ids)], database=self.database)


    def process_champion(self, island_id, best_f, best_x, round):
        self.client.write_points([
            { 'measurement': 'champion',
              'time': arrow.utcnow().isoformat(),
              'fields': {
                  'island_id': island_id,
                  'best_f': repr(best_f.tolist()),
                  'best_x': repr(best_x.tolist()),
                  'round': round,
              }
            }], database=self.database)


    def __enter__(self):
        self.client.create_database(self.database)
        return self


    def __exit__(self, exception_type, exception_val, trace):
        pass
        # self.client.drop_database(self.database)
