from __future__ import print_function, division, absolute_import

from obj import B2Model
from params import getDefaultParamValues

m = B2Model()
m.evaluate(getDefaultParamValues())
m.plotQuantity('cpep')