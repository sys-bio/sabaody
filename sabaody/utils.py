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

def getQualifiedName(*args):
    '''
    Gets a qualified RDNS name for this app.
    '''
    root = 'com.how2cell.sabaody'
    return '.'.join((root, *args))