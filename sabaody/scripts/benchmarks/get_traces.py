from pandas import read_csv, DataFrame

from os.path import join, dirname, realpath
from pprint import pprint
import arrow
from influxdb import InfluxDBClient
from ast import literal_eval
# from numpy import array
import json

import argparse
parser = argparse.ArgumentParser(description='Run central migration service.')
parser.add_argument('database',
                    help='The input database.')
args = parser.parse_args()
database = args.database

if __name__ == '__main__':
    tstart = None
    client = InfluxDBClient('luna')
    results = client.query('SELECT island_id,best_f,best_x FROM champion', database=database)
    for result in results:
        for point in result:
            t = arrow.get(point['time'])
            if tstart == None or t < tstart:
                tstart = t

    timepoints_by_island = {}
    min_f = None
    best_x = None

    for result in results:
        for point in result:
            t = arrow.get(point['time'])-tstart
            island_id = point['island_id']
            best_f = literal_eval(point['best_f'])[0]
            if min_f is None or best_f < min_f:
                min_f = best_f
                best_x = literal_eval(point['best_x'])
            timepoints_by_island.setdefault(island_id, []).append((t.days*24. + t.seconds/3600.,best_f))

    traces = {}
    for island_id,series in timepoints_by_island.items():
        traces[island_id] = sorted(series, key=lambda t: t[0])

    with open(join(dirname(realpath(__file__)), '.'.join([database,'json'])), 'w') as f:
        json.dump(traces, f)
