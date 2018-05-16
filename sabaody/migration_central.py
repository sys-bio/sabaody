# Sabaody
# Copyright 2018 J Kyle Medley
from __future__ import print_function, division, absolute_import

from requests import post
from yarl import URL

from urllib.parse import urljoin

def purge_all():
    # type: () -> None
    '''
    Wipe the island definitions and all migrants.
    Return to state at service startup.
    '''
    pass

def define_island(root_url, id, param_vector_size):
    # type: (str, array) -> None
    '''
    Sends an island definition to the server.
    '''
    r = post(URL(root_url) / 'define-island' / str(id), json={'param_vector_size': param_vector_size})