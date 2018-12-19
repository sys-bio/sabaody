from __future__ import print_function, division, absolute_import

from sabaody.utils import expect

from collections import OrderedDict
from numpy import array

d = {
  # initial conditions
  #'cdhap_init': 0.167,
  #'ce4p_init': 0.098,
  #'cf6p_init': 0.6,
  #'cfdp_init': 0.272,
  #'cg1p_init': 0.653,
  #'cg6p_init': 3.48,
  #'cgap_init': 0.218,
  #'cpep_init': 2.67,
  #'cpg_init': 0.808,
  #'cpg2_init': 0.399,
  #'cpg3_init': 2.13,
  #'cpgp_init': 0.008,
  #'cpyr_init': 2.67,
  #'crib5p_init': 0.398,
  #'cribu5p_init': 0.111,
  #'csed7p_init': 0.276,
  #'cxyl5p_init': 0.138,
  #'cglcex_init': 2.,

  # not mass-action constants
  # appear to be equilibrium binding constants
  'kALDOdhap': 0.088,
  'kALDOeq': 0.144,
  'kALDOfdp': 1.75,
  'kALDOgap': 0.088,
  'kALDOgapinh': 0.6,

  # Michaelis constants
  'KDAHPSe4p': 0.035,
  'KDAHPSpep': 0.0053,
  'KENOeq': 6.73,
  'KENOpep': 0.135,
  'KENOpg2': 0.1,
  'KG1PATatp': 4.42,
  'KG1PATfdp': 0.119,
  'KG1PATg1p': 3.2,
  'KG3PDHdhap': 1.,
  'KG6PDHg6p': 14.4,
  'KG6PDHnadp': 0.0246,
  'KG6PDHnadphg6pinh': 6.43,
  'KG6PDHnadphnadpinh': 0.01,
  'KGAPDHeq': 0.63,
  'KGAPDHgap': 0.683,
  'KGAPDHnad': 0.252,
  'KGAPDHnadh': 1.09,
  'KGAPDHpgp': 1.04e-05,
  'KPDHpyr': 1159.,
  'KpepCxylasefdp': 0.7,
  'KpepCxylasepep': 4.07,
  'KPFKadpa': 128.,
  'KPFKadpb': 3.89,
  'KPFKadpc': 4.14,
  'KPFKampa': 19.1,
  'KPFKampb': 3.2,
  'KPFKatps': 0.123,
  'KPFKf6ps': 0.325,
  'KPFKpep': 3.26,
  'KPGDHatpinh': 208.,
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
  'KR5PIeq': 4.,
  'KRPPKrib5p': 0.1,
  'KRu5Peq': 1.4,
  'KSerSynthpg3': 1.,
  'KSynth1pep': 1.,
  'KSynth2pyr': 1.,
  'KTAeq': 1.05,
  'kTISdhap': 2.8,
  'kTISeq': 1.39,
  'kTISgap': 0.3,
  'KTKaeq': 1.2,
  'KTKbeq': 10.,
  'LPFK': 5629067.,
  'LPK': 1000.,

  # Hill params
  'nDAHPSe4p': 2.6,
  'nDAHPSpep': 2.2,
  'nG1PATfdp': 1.2,
  'nPDH': 3.68,
  'npepCxylasefdp': 4.21,
  'nPFK': 11.1,
  'nPK': 4.,
  'nPTSg6p': 3.66,

  # Vmax's
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

  'VALDOblf': 2., # aldolase parameter, needs more investigation

  #'cfeed': 110.96, # carbon influx, don't fit
  #'Dil': 2.78e-05, # dilution, don't fit
  #'mu': 2.78e-05, # not a parameter, possibly volume factor
}

# sort by name and make ordered dict
params = OrderedDict(sorted(d.items(), key=lambda t: t[0]))
from math import log
param_array = array(list(log(float(v), 10.) for v in params.values()))

param_list = list(params.keys())

def applyParamVec(r, p):
    # type: (RoadRunner, array) -> None
    '''
    Applies a parameter vector p to a RoadRunner instance r.
    '''
    expect(len(p) != len(param_list), 'Parameter vector size mismatch')
    from math import exp
    for k,v in enumerate(p):
        r[param_list[k]] = exp(v)


def getDefaultParamValues():
    # type: () -> array
    return param_array

def getUpperBound():
    '''
    10x original value.
    '''
    return getDefaultParamValues()+1

def getLowerBound():
    '''
    1/10 original value.
    '''
    return getDefaultParamValues()-1

def getBestKnownValues():
    '''
    Return the values from the best known solution.
    '''
    from math import log
    # 030a95e1-ec24-4daf-b82d-2fd8b08d81f4, 19 hours, 2000 rounds, 0.16290388241021264 score
    return array([ -0.87427506, -1.42586653,  1.16247845, -0.29501387, -1.02381028,
                    0.21189874, -0.87493892,  0.15331484, -0.32353108,  0.3283232 ,
                   -1.82980594,  1.17203518, -1.93470144,  0.15572785,  0.09924167,
                   -1.37893591,  0.37120835, -4.699349  ,  3.79860843,  2.22600005,
                    0.01550745,  0.45112647,  0.90138762,  0.40495501, -1.55558966,
                   -0.85360301,  0.65788029,  2.40470885, -1.14382524, -1.80442397,
                    0.9335869 , -0.76665758, -0.06382697, -1.61606282, -0.51881952,
                    0.07891459, -1.68843198,  0.26458866,  2.80538937, -0.6124788 ,
                   -0.60716577, -0.67772597, -2.02432678, -0.37911674, -1.15808416,
                    0.25984712, -1.05119781, -1.5418919 , -0.95110117,  0.98066539,
                   -0.05568079, -0.76754891,  3.69434084, -2.59025545,  1.54516602,
                   -0.12969073, -0.39386919, -0.02708373,  1.09279266,  0.88159732,
                   -0.27543622, -0.09834288,  0.95992359,  0.93229798,  1.94672096,
                   -0.11731093,  0.63839029,  7.07915525,  2.26330512, -0.2087071 ,
                   -1.33781301, -0.55777794, -0.41720646, -1.84572959,  0.74025447,
                    0.53116324, -0.29208086,  0.40060191,  0.19311755, -0.05282572,
                   -0.90716299,  0.83388537,  0.85333809,  1.56929155,  0.2558239 ,
                    0.56676609,  1.66203223, -0.22627624,  3.51415632, -2.93814652,
                   -1.29712107,  0.06140037,  3.66154468, -3.31189161, -2.50613137,
                    0.38732009,  3.39944586,  1.24505971,  2.86175107,  3.31370095,
                   -0.89260735,  1.51179894, -1.1256291 ,  3.32028965, -0.05346415,
                   -2.68900598,  1.19286523, -2.09798945, -1.49708487, -1.82154691,
                    1.87288799,  1.43093803,  1.88194732,  2.93363469, -3.90402163,
                   -1.07349865])
    # return  array([ -4.14442575,  -5.54903953,   0.99830493,  -2.26370362,
    #                 -1.67841194,   1.43026645,  -1.99979415,   1.9032382 ,
    #                 -0.49243458,   2.03784746,  -3.36480631,   2.85457384,
    #                 -4.97458047,  -0.38087244,  -0.15153516,  -1.47235738,
    #                  0.06432666, -11.65500201,   7.63836277,   5.03100429,
    #                  0.7652608 ,   1.32805616,   2.72550445,   0.56578125,
    #                 -1.657895  ,  -1.38132886,   1.4180673 ,   5.34439947,
    #                 -3.26931524,  -3.9188252 ,   3.43119732,  -2.1606558 ,
    #                 -1.19633234,  -1.56133188,   0.85321662,  -1.40483763,
    #                 -2.16167292,  -1.02176182,   8.54384113,   0.03973449,
    #                 -3.48156296,  -1.35110393,  -4.41411177,  -0.42235041,
    #                 -0.71294663,  -0.32423518,  -1.33118941,  -0.62939608,
    #                 -1.30128854,   3.66428988,  -1.98814187,  -1.97359529,
    #                  7.72605868,  -4.69184802,   5.60961186,   0.89798692,
    #                  0.93490002,  -2.47271   ,   0.54927723,  -0.58462609,
    #                  0.24591996,   0.49058008,   0.2169503 ,   0.22419074,
    #                  1.82335709,  -0.48471044,   1.75252976,  14.93281492,
    #                  6.31278076,   0.64820473,  -2.1050478 ,  -2.43318415,
    #                  0.63923799,  -2.26815923,  -1.08323046,   1.77808738,
    #                  0.22138514,  -0.44596973,   0.67546858,   0.72376581,
    #                  0.63389114,   1.56080212,   2.50957958,   1.76794639,
    #                  1.21342852,   1.33610813,   3.08932218,  -2.07132696,
    #                  6.32842772,  -5.22934073,  -4.96081373,   0.29648174,
    #                  6.81921816,  -6.68739602,  -7.90574657,   1.64083136,
    #                  7.7557265 ,   2.32856674,   6.47885161,   9.01165499,
    #                 -0.34723263,   3.6786438 ,  -2.31775406,   8.29993758,
    #                  1.67149736,  -4.55931583,   1.58842742,  -4.00267441,
    #                 -4.36212642,  -2.28026195,   3.22776573,   4.4449608 ,
    #                  2.22045199,   3.5704277 ,  -7.25391057,  -2.50637287])/log(10.)
