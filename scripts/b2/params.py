from __future__ import print_function, division, absolute_import

from .utils import expect, check_vector

from collections import OrderedDict
from numpy import array

d = {
  'cdhap_init': 0.167,
  'ce4p_init': 0.098,
  'cf6p_init': 0.6,
  'cfdp_init': 0.272,
  'cg1p_init': 0.653,
  'cg6p_init': 3.48,
  'cgap_init': 0.218,
  'cpep_init': 2.67,
  'cpg_init': 0.808,
  'cpg2_init': 0.399,
  'cpg3_init': 2.13,
  'cpgp_init': 0.008,
  'cpyr_init': 2.67,
  'crib5p_init': 0.398,
  'cribu5p_init': 0.111,
  'csed7p_init': 0.276,
  'cxyl5p_init': 0.138,
  'cglcex_init': 2,
  'kALDOdhap': 0.088,
  'kALDOeq': 0.144,
  'kALDOfdp': 1.75,
  'kALDOgap': 0.088,
  'kALDOgapinh': 0.6,
  'KDAHPSe4p': 0.035,
  'KDAHPSpep': 0.0053,
  'KENOeq': 6.73,
  'KENOpep': 0.135,
  'KENOpg2': 0.1,
  'KG1PATatp': 4.42,
  'KG1PATfdp': 0.119,
  'KG1PATg1p': 3.2,
  'KG3PDHdhap': 1,
  'KG6PDHg6p': 14.4,
  'KG6PDHnadp': 0.0246,
  'KG6PDHnadphg6pinh': 6.43,
  'KG6PDHnadphnadpinh': 0.01,
  'KGAPDHeq': 0.63,
  'KGAPDHgap': 0.683,
  'KGAPDHnad': 0.252,
  'KGAPDHnadh': 1.09,
  'KGAPDHpgp': 1.04e-05,
  'KPDHpyr': 1159,
  'KpepCxylasefdp': 0.7,
  'KpepCxylasepep': 4.07,
  'KPFKadpa': 128,
  'KPFKadpb': 3.89,
  'KPFKadpc': 4.14,
  'KPFKampa': 19.1,
  'KPFKampb': 3.2,
  'KPFKatps': 0.123,
  'KPFKf6ps': 0.325,
  'KPFKpep': 3.26,
  'KPGDHatpinh': 208,
  'KPGDHnadp': 0.0506,
  'KPGDHnadphinh': 0.0138,
  'KPGDHpg': 37.5,
  'KPGIeq': 0.1725,
  'KPGIf6p': 0.266,
  'KPGIf6ppginh': 0.2,
  'KPGIg6p': 2.9,
  'KPGIg6ppginh': 0.2,
  'KPGKadp': 0.185,
  'KPGKatp': 0.653,
  'KPGKeq': 1934.4,
  'KPGKpg3': 0.473,
  'KPGKpgp': 0.0468,
  'KPGluMueq': 0.188,
  'KPGluMupg2': 0.369,
  'KPGluMupg3': 0.2,
  'KPGMeq': 0.196,
  'KPGMg1p': 0.0136,
  'KPGMg6p': 1.038,
  'KPKadp': 0.26,
  'KPKamp': 0.2,
  'KPKatp': 22.5,
  'KPKfdp': 0.19,
  'KPKpep': 0.31,
  'KPTSa1': 3082.3,
  'KPTSa2': 0.01,
  'KPTSa3': 245.3,
  'KPTSg6p': 2.15,
  'KR5PIeq': 4,
  'KRPPKrib5p': 0.1,
  'KRu5Peq': 1.4,
  'KSerSynthpg3': 1,
  'KSynth1pep': 1,
  'KSynth2pyr': 1,
  'KTAeq': 1.05,
  'kTISdhap': 2.8,
  'kTISeq': 1.39,
  'kTISgap': 0.3,
  'KTKaeq': 1.2,
  'KTKbeq': 10,
  'LPFK': 5629067,
  'LPK': 1000,
  'nDAHPSe4p': 2.6,
  'nDAHPSpep': 2.2,
  'nG1PATfdp': 1.2,
  'nPDH': 3.68,
  'npepCxylasefdp': 4.21,
  'nPFK': 11.1, # Hill param
  'nPK': 4, # Hill param
  'nPTSg6p': 3.66,
  'rmaxALDO': 17.41464425,
  'rmaxDAHPS': 0.1079531227,
  'rmaxENO': 330.4476151,
  'rmaxG1PAT': 0.007525458026,
  'rmaxG3PDH': 0.01162042696,
  'rmaxG6PDH': 1.380196955,
  'rmaxGAPDH': 921.5942861,
  'rmaxMetSynth': 0.0022627,
  'rmaxMurSynth': 0.00043711,
  'rmaxPDH': 6.059531017,
  'rmaxpepCxylase': 0.1070205858,
  'rmaxPFK': 1840.584747,
  'rmaxPGDH': 16.23235977,
  'rmaxPGI': 650.9878687,
  'rmaxPGK': 3021.773771,
  'rmaxPGluMu': 89.04965407,
  'rmaxPGM': 0.8398242773,
  'rmaxPK': 0.06113150238,
  'rmaxPTS': 7829.78,
  'rmaxR5PI': 4.83841193,
  'rmaxRPPK': 0.01290045226,
  'rmaxRu5P': 6.739029475,
  'rmaxSerSynth': 0.025712107,
  'rmaxSynth1': 0.01953897003,
  'rmaxSynth2': 0.07361855055,
  'rmaxTA': 10.87164108,
  'rmaxTIS': 68.67474392,
  'rmaxTKa': 9.473384783,
  'rmaxTKb': 86.55855855,
  'rmaxTrpSynth': 0.001037,
  #'VALDOblf': 2, # TODO: aldolase parameter, needs more investigation
  #'cfeed': 110.96, # carbon influx, don't fit
  #'Dil': 2.78e-05, # dilution, don't fit
  #'mu': 2.78e-05, # not a parameter, possibly volume factor
}

# sort by name and make ordered dict
params = OrderedDict(sorted(d.items(), key=lambda t: t[0]))
param_array = array(map(lambda t: t[0], params))

param_list = list(params.keys())

def applyParamVec(r, p):
    # type: (RoadRunner, array) -> None
    '''
    Applies a parameter vector p to a RoadRunner instance r.
    '''
    expect(len(p) != len(param_list), 'Parameter vector size mismatch')
    for k,v in enumerate(p):
        r[param_list[k]] = v


def getDefaultParamValues():
    # type: () -> array
    return param_array

def getUpperBound():
    '''
    1/10 original value.
    '''
    return 0.1*getDefaultParamValues()

def getLowerBound():
    '''
    10x original value.
    '''
    return 10.*getDefaultParamValues()