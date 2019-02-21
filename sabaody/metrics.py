# Sabaody
# Copyright 2018-2019 Shaik Asifullah and J Kyle Medley
from __future__ import print_function, division, absolute_import

from influxdb import InfluxDBClient
import arrow

from uuid import uuid4

class Metric:
    def __init__(self, database):
        self.database = database

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
        super().__init__(database)
        # self.database = database.replace('.','_').replace('-','_')


    def getClient(self):
        return self.client


    def process_deltas(self, deltas, src_ids, round):
        self.getClient().write_points([
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
        self.getClient().write_points([
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
        self.getClient().create_database(self.database)
        return self


    def __exit__(self, exception_type, exception_val, trace):
        pass
        # self.getClient().drop_database(self.database)


class SingletonMetricConstructor:
    '''InfluxDB singleton instance'''
    __instance = None
    __instance_opts = None

    @classmethod
    def init(cls, host='localhost', port=8086, username='root', password='root', database=None, database_prefix=None,
                    ssl=False, verify_ssl=False, timeout=None, retries=3, use_udp=False, udp_port=4444, proxies=None):
        cls.__instance_opts = dict(host=host, port=port, username=username, password=password,
                            database=database, database_prefix=database_prefix, ssl=ssl, verify_ssl=verify_ssl, timeout=timeout, retries=retries,
                            use_udp=use_udp, udp_port=udp_port, proxies=proxies)
        return cls.__instance_opts

    @classmethod
    def getInstance(cls, instance_opts):
        if cls.__instance == None:
            # if cls.__instance_opts == None:
                # raise RuntimeError('Need to call init first')
            cls.__instance = InfluxDBMetric(**instance_opts)
        return cls.__instance


class SingletonInfluxDBMetric(InfluxDBMetric):
    def __init__(self, *args, **kwargs):
        self.instance_opts = SingletonMetricConstructor.init(*args, **kwargs)
        Metric.__init__(self, self.instance_opts['database'])


    def getClient(self):
        return SingletonMetricConstructor.getInstance(self.instance_opts).getClient()
