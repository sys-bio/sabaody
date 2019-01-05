# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from abc import ABC, abstractmethod

class TerminatorBase(ABC):
    '''
    Evaluates criteria for terminating the fitting process (convergence etc.).
    '''
    @abstractmethod
    def should_stop(self, pg_island, monitor):
        pass
