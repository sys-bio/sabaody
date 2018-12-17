# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

import arrow
from influxdb import InfluxDBClient

from numpy import array

from pprint import pprint
from ast import literal_eval

client = InfluxDBClient('luna')
tstart = arrow.get('2018-12-17 05:24:10')
results = client.query('SELECT island_id,best_f FROM champion', database='com.how2cell.sabaody.biopredyn.b4-driver.2c8d8bda-aef3-4e45-af0d-25b98a7ff686')
# pprint(results)
timepoints_by_island = {}
for result in results:
    for point in result:
        t = arrow.get(point['time'])-tstart
        island_id = point['island_id']
        best_f = literal_eval(point['best_f'])[0]
        timepoints_by_island.setdefault(island_id, []).append((t.seconds,best_f))
        # print(t.seconds,island_id,best_f)

import tellurium as te
for island_id,series in timepoints_by_island.items():
    trace = array(sorted(series, key=lambda t: t[0]))
    print(trace)
    te.plot(trace[:,0], trace[:,1], tag=island_id, show=False)
te.show()
