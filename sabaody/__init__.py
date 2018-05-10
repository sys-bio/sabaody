from __future__ import print_function, division, absolute_import

__version__ = '0.1.0'


#from .diffevo import differential_evolution
from .pygmo_interf import Evaluator, Archipelago, Island, run_island, problem_constructor
#from .timecourse_model import TimecourseModel
from .utils import getQualifiedName