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
parser.add_argument('tsv',
                    help='The input tsv.')
args = parser.parse_args()
tsv = args.tsv

if __name__ == '__main__':
    d = read_csv(tsv, sep='\t', header=0)

    replicates = d.groupby(('NumIslands','Description'))

    fastest_time = None
    fastest_hours = None
    for (n_islands, desc), group in replicates:
        mean_hours = group['Hours'].mean()
        if fastest_time == None or mean_hours < fastest_time:
            fastest_time = mean_hours
            fastest_hours = DataFrame(group['Hours'])

    summary = DataFrame(columns=['Number of Islands','Connectivity','Algorithm(s)','Hours (Mean)','Hours (SD)','Min. Score (Mean)','Min. Score (SD)','Ratio vs. Fastest','Converged?'])
    for (n_islands, desc), group in replicates:
        desc = desc.replace('Bidirectional chain', 'Singleton')
        topology, algorithm = desc.split(', ')

        mean_hours = group['Hours'].mean()
        std_hours = group['Hours'].std()

        mean_min_score = group['MinScore'].mean()
        std_min_score = group['MinScore'].std()

        mean_rounds = group['ActualAvgRounds'].mean()
        stddev_rounds = group['ActualAvgRounds'].std()

        ratio_vs_fastest = round(mean_hours / fastest_time, 2)
        converged = bool(mean_rounds < 999)

        from scipy.stats import ttest_ind
        tval,pval = ttest_ind(group['Hours'], fastest_hours)

        summary = summary.append({
            'Number of Islands': n_islands,
            'Connectivity': topology,
            'Algorithm(s)': algorithm,
            'Hours (Mean)': mean_hours,
            'Hours (SD)': std_hours,
            'Min. Score (Mean)': mean_min_score,
            'Min. Score (SD)': std_min_score,
            'Ratio vs. Fastest': ratio_vs_fastest,
            'Converged?': 'Yes' if converged else 'No',
            'p-value (If Converged)': pval[0] if converged else None,
        }, ignore_index=True)

    print(summary)
