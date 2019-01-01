# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from numpy import array, allclose, zeros

from os.path import join, abspath, dirname, realpath

base_param_id_to_index_map = {
    'map3k7_n_nik': 0,
    'map3k7_k_nik': 1,
    'tau_nik': 2,
    'map3k7_n_mkk4': 3,
    'map3k7_k_mkk4': 4,
    'map3k1_n_mkk4': 5,
    'map3k1_k_mkk4': 6,
    'tau_mkk4': 7,
    'traf2_n_ask1': 8,
    'traf2_k_ask1': 9,
    'tau_ask1': 10,
    'traf2_n_map3k7': 11,
    'traf2_k_map3k7': 12,
    'tau_map3k7': 13,
    'ask1_n_mkk7': 14,
    'ask1_k_mkk7': 15,
    'map3k1_n_mkk7': 16,
    'map3k1_k_mkk7': 17,
    'tau_mkk7': 18,
    'tnfa_n_tnfr': 19,
    'tnfa_k_tnfr': 20,
    'tau_tnfr': 21,
    'egf_n_egfr': 22,
    'egf_k_egfr': 23,
    'tau_egfr': 24,
    'erk_n_ph': 25,
    'erk_k_ph': 26,
    'tau_ph': 27,
    'nfkb_n_ex': 28,
    'nfkb_k_ex': 29,
    'tau_ex': 30,
    'raf1_n_mek': 31,
    'raf1_k_mek': 32,
    'tau_mek': 33,
    'sos_n_ras': 34,
    'sos_k_ras': 35,
    'tau_ras': 36,
    'tnfr_n_traf2': 37,
    'tnfr_k_traf2': 38,
    'tau_traf2': 39,
    'nik_n_ikk': 40,
    'nik_k_ikk': 41,
    'tau_ikk': 42,
    'pi3k_n_akt': 43,
    'pi3k_k_akt': 44,
    'tau_akt': 45,
    'egfr_n_pi3k': 46,
    'egfr_k_pi3k': 47,
    'tau_pi3k': 48,
    'ex_n_ikb': 49,
    'ex_k_ikb': 50,
    'ikk_n_ikb': 51,
    'ikk_k_ikb': 52,
    'tau_ikb': 53,
    'ikb_n_nfkb': 54,
    'ikb_k_nfkb': 55,
    'tau_nfkb': 56,
    'jnk_n_cjun': 57,
    'jnk_k_cjun': 58,
    'tau_cjun': 59,
    'mkk7_n_jnk': 60,
    'mkk7_k_jnk': 61,
    'tau_jnk': 62,
    'ras_n_map3k1': 63,
    'ras_k_map3k1': 64,
    'tau_map3k1': 65,
    'mek_n_erk': 66,
    'mek_k_erk': 67,
    'tau_erk': 68,
    'ras_n_raf1': 69,
    'ras_k_raf1': 70,
    'tau_raf1': 71,
    'egfr_n_sos': 72,
    'egfr_k_sos': 73,
    'ph_n_sos': 74,
    'ph_k_sos': 75,
    'tau_sos': 76,
    'mkk4_n_p38': 77,
    'mkk4_k_p38': 78,
    'tau_p38': 79,
    'akt_n_gsk3': 80,
    'akt_k_gsk3': 81,
    'tau_gsk3': 82,
    'cjun_n_ap1': 83,
    'cjun_k_ap1': 84,
    'tau_ap1': 85,
}


import scipy.io
pnom = scipy.io.loadmat(abspath(join(dirname(realpath(__file__)), 'pnom.mat')))['pnom']

base_param_id_to_default_value_map = { id: pnom[0,index] for id,index in base_param_id_to_index_map.items() }
param_id_to_default_value_map      = { id: pnom[0,index] for id,index in base_param_id_to_index_map.items() }

extended_param_id_to_default_value_map = {
    'map3k7_nik_w': 1.,
    # Original is map3k7  AND mkk4.,
    'map3k7_mkk4_w': 0.,
    'map3k1_mkk4_w': 0.,
    'map3k7_map3k1_mkk4_AND_w': 1.,
    'traf2_ask1_w': 1.,
    'traf2_map3k7_w': 1.,
    'ask1_mkk7_w': 1.,
    'map3k1_mkk7_w': 1.,
    'ask1_map3k1_mkk7_AND_w': 0.,
    'tnfa_tnfr_w': 1.,
    'egf_egfr_w': 1.,
    'erk_ph_w': 1.,
    'nfkb_ex_w': 1.,
    'raf1_mek_w': 1.,
    'sos_ras_w': 1.,
    'tnfr_traf2_w': 1.,
    'nik_ikk_w': 1.,
    'pi3k_akt_w': 1.,
    'egfr_pi3k_w': 1.,
    # Original model was ex OR NOT ikk.,
    'ex_ikb_w': 1.,
    'ikk_ikb_w': 1.,
    'ex_ikk_ikb_AND_w': 0.,
    'ikb_nfkb_w': 1.,
    'jnk_cjun_w': 1.,
    'mkk7_jnk_w': 1.,
    'ras_map3k1_w': 1.,
    'mek_erk_w': 1.,
    'ras_raf1_w': 1.,
    # Original was egfr AND NOT ph.,
    'egfr_sos_w': 0.,
    'ph_sos_w': 0.,
    'egfr_ph_sos_AND_w': 1.,
    'mkk4_p38_w': 1.,
    'akt_gsk3_w': 1.,
    'cjun_ap1_w': 1.,
}

param_id_to_default_value_map.update(extended_param_id_to_default_value_map)

param_ids = ['']*86
for p,i in base_param_id_to_index_map.items():
    param_ids[i] = p
assert '' not in param_ids

from json import load
with open(join(dirname(realpath(__file__)), 'params.json')) as f:
    o = load(f)
    param_defaults = array(o['param_defaults'])
    param_lb       = array(o['param_lb'])
    param_ub       = array(o['param_ub'])

print(param_defaults - array([v for v in param_id_to_default_value_map.values()]))
assert allclose(param_defaults - array([v for v in param_id_to_default_value_map.values()]), zeros((120,)))

def getDefaultParamValues():
    # type: () -> array
    return param_defaults

def getUpperBound():
    # type: () -> array
    return param_ub

def getLowerBound():
    # type: () -> array
    return param_lb
