from __future__ import print_function, division, absolute_import

import numpy as np

def expect(predicate, message):
    """
    Just tests a predicate and throws an exception if it's not satisfied.
    """
    if not predicate:
        raise RuntimeError(message)

def oneof(x,f):
    n = 0
    for e in x:
        if f(e):
            n += 1
    return n == 1

def check_vector(v):
    """
    Checks if the numpy array is a vector (vector of length 1 okay).
    """
    if v.ndim < 2:
        return
    elif v.ndim == 2:
        if oneof(v.shape, lambda x: x==1) or v.shape == (1,1):
            return
        else:
            raise RuntimeError('Array of dimensions {} is not a vector'.format(v.shape))
    else:
        raise RuntimeError('Array of dimension {} is not a vector'.format(v.ndim))

def vector_length(v):
    check_vector(v)
    return v.size

def getQualifiedName(*args):
    '''
    Gets a qualified RDNS name for this app.
    '''
    root = 'com.how2cell.sabaody'
    return '.'.join((root, *list(str(a) for a in args)))

def arrays_equal(u,v):
    '''
    Allpies array_equal to sequences.
    '''
    from numpy import array_equal
    for x,y in zip(u,v):
        if not array_equal(x,y):
            return False
    return True


def divergent(a):
    '''
    Returns true if the array a contains a nan or +-inf value.
    '''
    from numpy import isfinite
    return not isfinite(a).all()


def create_solo_benchmark_table(host, user, database, password, table):
    import MySQLdb
    mariadb_connection = MySQLdb.connect(host,user,password,database)
    cursor = mariadb_connection.cursor()
    from pickle import dumps
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS {table} (
            PrimaryKey INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
            Description TEXT NOT NULL,
            FinalScore DOUBLE NOT NULL,
            FinalParams BLOB NOT NULL,
            TimeStart DATETIME NOT NULL,
            TimeEnd DATETIME NOT NULL);'''.format(table=table))
    mariadb_connection.commit()


def commit_solo_benchmark_run(host, user, database, password, table, description, final_score, final_params, time_start, time_end):
    import MySQLdb
    mariadb_connection = MySQLdb.connect(host,user,password,database)
    cursor = mariadb_connection.cursor()
    from pickle import dumps
    cursor.execute('\n'.join([
        'INSERT INTO {table} (Description, FinalScore, FinalParams, TimeStart, TimeEnd)'.format(table=table),
        "VALUES ('{description}',{final_score},{final_params},'{time_start}','{time_end}');".format(
            description=description,
            final_score=final_score,
            final_params='0x{}'.format(dumps(final_params).hex()),
            time_start=time_start.format('YYYY-MM-DD HH:mm:ss'),
            time_end=time_end.format('YYYY-MM-DD HH:mm:ss'),
            )]))
    mariadb_connection.commit()
