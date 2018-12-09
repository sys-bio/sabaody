# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

import sabaody
from pprint import pprint

def retrieve(user, host, pw, db):
    import MySQLdb
    mariadb_connection = MySQLdb.connect(host=host,user=user,passwd=pw,db=db)
    cursor = mariadb_connection.cursor()
    query_string = 'SELECT PrimaryKey, Champions, Benchmark, Description, Rounds, Generations, MinScore, timediff(TimeEnd, TimeStart) FROM benchmark_runs ORDER BY MinScore;'
    cursor.execute(query_string)
    from pickle import loads
    t = cursor.fetchone()
    if t is None:
        raise RuntimeError('Entry not found for query {}'.format(query_string))
    key = int(t[0])
    champions = loads(t[1])
    benchmark = t[2]
    description = t[3]
    rounds = t[4]
    generations = t[5]
    score = t[6]
    duration = t[7]
    print('Retrieved {benchmark} {description} with {rounds} rounds, {generations} generations, {score} score, {duration} duration'.format(
        benchmark=benchmark,
        description=description,
        rounds=rounds,
        generations=generations,
        score=score,
        duration=duration,
    ))
    return champions

champions = retrieve('sabaody', 'luna', 'w00t', 'sabaody')

best_f, best_x = champions[0]
print('champ score {}'.format(best_f))
pprint(best_x)
