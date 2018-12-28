# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from numpy import array

param_id_to_index_map = {
    'env_M_ACT': 1,
    'env_M_GLC': 2,
    'env_uc': 3,
    'e_AceA_kcat': 4,
    # 'e_AceA_n': 5, # not fitted
    'e_AceA_L': 6,
    'e_AceA_Kict': 7,
    'e_AceA_Kpep': 8,
    'e_AceA_Kpg3': 9,
    'e_AceA_Kakg': 10,
    'e_AceB_kcat': 11,
    'e_AceB_Kglx': 12,
    'e_AceB_Kacoa': 13,
    'e_AceB_Kglxacoa': 14,
    'e_AceK_kcat_ki': 15,
    'e_AceK_kcat_ph': 16,
    # 'e_AceK_n': 17, # not fitted
    'e_AceK_L': 18,
    'e_AceK_Kicd': 19,
    'e_AceK_Kicd_P': 20,
    'e_AceK_Kpep': 21,
    'e_AceK_Kpyr': 22,
    'e_AceK_Koaa': 23,
    'e_AceK_Kglx': 24,
    'e_AceK_Kakg': 25,
    'e_AceK_Kpg3': 26,
    'e_AceK_Kict': 27,
    'e_Acoa2act_kcat': 28,
    # 'e_Acoa2act_n': 29, # not fitted
    'e_Acoa2act_L': 30,
    'e_Acoa2act_Kacoa': 31,
    'e_Acoa2act_Kpyr': 32,
    'e_Acs_kcat': 33,
    'e_Acs_Kact': 34,
    'e_Akg2mal_kcat': 35,
    'e_Akg2mal_Kakg': 36,
    'e_CAMPdegr_kcat': 37,
    'e_CAMPdegr_KcAMP': 38,
    'e_Cya_kcat': 39,
    'e_Cya_KEIIA': 40,
    'e_Emp_kcat_f': 41,
    'e_Emp_kcat_r': 42,
    'e_Emp_Kfbp': 43,
    'e_Emp_Kpg3': 44,
    'e_Eno_kcatf': 45,
    'e_Eno_kcatr': 46,
    'e_Eno_Kpg3': 47,
    'e_Eno_Kpep': 48,
    'e_Fdp_kcat': 49,
    # 'e_Fdp_n': 50, # not fitted
    'e_Fdp_L': 51,
    'e_Fdp_Kfbp': 52,
    'e_Fdp_Kpep': 53,
    'e_GltA_kcat': 54,
    'e_GltA_Koaa': 55,
    'e_GltA_Kacoa': 56,
    'e_GltA_Koaaacoa': 57,
    'e_GltA_Kakg': 58,
    'e_Icd_kcat': 59,
    # 'e_Icd_n': 60, # not fitted
    'e_Icd_L': 61,
    'e_Icd_Kict': 62,
    'e_Icd_Kpep': 63,
    'e_Mdh_kcat': 64,
    'e_Mdh_n': 65,
    'e_Mdh_Kmal': 66,
    'e_MaeAB_kcat': 67,
    # 'e_MaeAB_n': 68, # not fitted
    'e_MaeAB_L': 69,
    'e_MaeAB_Kmal': 70,
    'e_MaeAB_Kacoa': 71,
    'e_MaeAB_Kcamp': 72,
    'e_PckA_kcat': 73,
    'e_PckA_Koaa': 74,
    'e_PckA_Kpep': 75,
    'e_Pdh_kcat': 76,
    # 'e_Pdh_n': 77, # not fitted
    'e_Pdh_L': 78,
    'e_Pdh_Kpyr': 79,
    'e_Pdh_KpyrI': 80,
    'e_Pdh_Kglx': 81,
    'e_PfkA_kcat': 82,
    # 'e_PfkA_n': 83, # not fitted
    'e_PfkA_L': 84,
    'e_PfkA_Kg6p': 85,
    'e_PfkA_Kpep': 86,
    'e_Ppc_kcat': 87,
    # 'e_Ppc_n': 88, # not fitted
    'e_Ppc_L': 89,
    'e_Ppc_Kpep': 90,
    'e_Ppc_Kfbp': 91,
    'e_PpsA_kcat': 92,
    # 'e_PpsA_n': 93, # not fitted
    'e_PpsA_L': 94,
    'e_PpsA_Kpyr': 95,
    'e_PpsA_Kpep': 96,
    'e_PykF_kcat': 97,
    # 'e_PykF_n': 98, # not fitted
    'e_PykF_L': 99,
    'e_PykF_Kpep': 100,
    'e_PykF_Kfbp': 101,
    'pts_k1': 102,
    'pts_km1': 103,
    'pts_k4': 104,
    'pts_KEIIA': 105,
    'pts_Kglc': 106,
    'tf_Cra_scale': 107,
    'tf_Cra_kfbp': 108,
    'tf_Cra_n': 109,
    'tf_Crp_scale': 110,
    'tf_Crp_kcamp': 111,
    'tf_Crp_n': 112,
    'tf_PdhR_scale': 113,
    'tf_PdhR_kpyr': 114,
    'tf_PdhR_n': 115,
    'g_aceBAK_vcra_unbound': 116,
    'g_aceBAK_vcra_bound': 117,
    'g_aceBAK_Kcra': 118,
    # 'g_aceBAK_aceBfactor': 119, # not fitted
    # 'g_aceBAK_aceKfactor': 120, # not fitted
    'g_aceBAK_KDNA': 121,
    'g_aceBAK_KP': 122,
    'g_aceBAK_KPprime': 123,
    'g_aceBAK_KG': 124,
    'g_aceBAK_L': 125,
    'g_aceBAK_kcat_iclr': 126,
    'g_aceBAK_DNA': 127,
    'g_aceBAK_vcrp_bound': 128,
    'g_aceBAK_vcrp_unbound': 129,
    'g_aceBAK_Kcrp': 130,
    'g_acs_vcrp_unbound': 131,
    'g_acs_vcrp_bound': 132,
    'g_acs_n': 133,
    'g_acs_Kcrp': 134,
    'g_akg2mal_vcrp_unbound': 135,
    'g_akg2mal_vcrp_bound': 136,
    'g_akg2mal_Kcrp': 137,
    'g_akg2mal_n': 138,
    'g_emp_vcra_unbound': 139,
    'g_emp_vcra_bound': 140,
    'g_emp_Kcra': 141,
    'g_emp_vcrp_unbound': 142,
    'g_emp_vcrp_bound': 143,
    'g_emp_Kcrp': 144,
    'g_eno_vcra_unbound': 145,
    'g_eno_vcra_bound': 146,
    'g_eno_Kcra': 147,
    'g_fdp_vcra_unbound': 148,
    'g_fdp_vcra_bound': 149,
    'g_fdp_Kcra': 150,
    'g_gltA_vcrp_unbound': 151,
    'g_gltA_vcrp_bound': 152,
    'g_gltA_Kcrp': 153,
    'g_gltA_n': 154,
    'g_icd_vcra_unbound': 155,
    'g_icd_vcra_bound': 156,
    'g_icd_Kcra': 157,
    'g_mdh_vcrp_unbound': 158,
    'g_mdh_vcrp_bound': 159,
    'g_mdh_Kcrp': 160,
    'g_pckA_vcra_unbound': 161,
    'g_pckA_vcra_bound': 162,
    'g_pckA_Kcra': 163,
    'g_pdh_vpdhr_unbound': 164,
    'g_pdh_vpdhr_bound': 165,
    'g_pdh_Kpdhr': 166,
    'g_pfkA_vcra_unbound': 167,
    'g_pfkA_vcra_bound': 168,
    'g_pfkA_Kcra': 169,
    'g_ppsA_vcra_unbound': 170,
    'g_ppsA_vcra_bound': 171,
    'g_ppsA_Kcra': 172,
    'g_pykF_vcra_unbound': 173,
    'g_pykF_vcra_bound': 174,
    'g_pykF_Kcra': 175,
    # 'd_k_degr': 176, # not fitted
    # 'bm_k_expr': 177, # not fitted
    'bm_muACT': 178,
    'bm_muGLC': 179,
    'bm_GLC_ACoA': 180,
    'bm_GLC_AKG': 181,
    'bm_GLC_G6P': 182,
    'bm_GLC_OAA': 183,
    'bm_GLC_PEP': 184,
    'bm_GLC_PG3': 185,
    'bm_GLC_PYR': 186,
    'bm_ACT_ACoA': 187,
    'bm_ACT_AKG': 188,
    'bm_ACT_G6P': 189,
    'bm_ACT_OAA': 190,
    'bm_ACT_PEP': 191,
    'bm_ACT_PG3': 192,
    'bm_ACT_PYR': 193,
}

param_ids = [id for index,id in sorted(param_index_to_name_map.items(), key=lambda x: x[1])]

param_id_to_default_value_map = {
    'env_M_ACT': 60.05,
    'env_M_GLC': 180.156,
    'env_uc': 9.5E-07,
    'e_AceA_kcat': 614,
    'e_AceA_n': 4,
    'e_AceA_L': 5.01E+04,
    'e_AceA_Kict': 0.022,
    'e_AceA_Kpep': 0.055,
    'e_AceA_Kpg3': 0.72,
    'e_AceA_Kakg': 0.827,
    'e_AceB_kcat': 47.8,
    'e_AceB_Kglx': 0.95,%0.504,
    'e_AceB_Kacoa': 0.755,
    'e_AceB_Kglxacoa': 0.719,
    'e_AceK_kcat_ki': 3.4E+12,
    'e_AceK_kcat_ph': 1.7E+09,
    'e_AceK_n': 2,
    'e_AceK_L': 1.0E+08,
    'e_AceK_Kicd': 0.043,
    'e_AceK_Kicd_P': 0.643,
    'e_AceK_Kpep': 0.539,
    'e_AceK_Kpyr': 0.038,
    'e_AceK_Koaa': 0.173,
    'e_AceK_Kglx': 0.866,
    'e_AceK_Kakg': 0.82,
    'e_AceK_Kpg3': 1.57,
    'e_AceK_Kict': 0.137,
    'e_Acoa2act_kcat': 3079,
    'e_Acoa2act_n': 2,
    'e_Acoa2act_L': 6.39E+05,
    'e_Acoa2act_Kacoa': 0.022,
    'e_Acoa2act_Kpyr': 0.022,
    'e_Acs_kcat': 340/0.000036201*0.001096222,
    'e_Acs_Kact': 1.0E-03,
    'e_Akg2mal_kcat': 1530,
    'e_Akg2mal_Kakg': 0.548,
    'e_CAMPdegr_kcat': 1.00E+03,
    'e_CAMPdegr_KcAMP': 0.1,
    'e_Cya_kcat': 993,
    'e_Cya_KEIIA': 1.7E-03,
    'e_Emp_kcat_f': 1000/0.011389032*0.011515593,
    'e_Emp_kcat_r': 848/0.011389032*0.011515593,
    'e_Emp_Kfbp': 5.92,
    'e_Emp_Kpg3': 16.6,
    'e_Eno_kcatf': 695/0.011389032*0.011552813,
    'e_Eno_kcatr': 522/0.011389032*0.011552813,
    'e_Eno_Kpg3': 4.76,
    'e_Eno_Kpep': 1.11,
    'e_Fdp_kcat': 192/0.000074810*0.000157492,
    'e_Fdp_n': 4,
    'e_Fdp_L': 4.0E+06,
    'e_Fdp_Kfbp': 3.0E-03,
    'e_Fdp_Kpep': 0.3,
    'e_GltA_kcat': 1614/0.000292771*0.001029612,
    'e_GltA_Koaa': 0.029,
    'e_GltA_Kacoa': 0.212,
    'e_GltA_Koaaacoa': 0.029,
    'e_GltA_Kakg': 0.63,
    'e_Icd_kcat': 695,
    'e_Icd_n': 2,
    'e_Icd_L': 127,
    'e_Icd_Kict': 1.6E-04,
    'e_Icd_Kpep': 0.334,
    'e_Mdh_kcat': 773/0.000491491*0.00345727,
    'e_Mdh_n': 1.7,
    'e_Mdh_Kmal': 10.1,
    'e_MaeAB_kcat': 1879,
    'e_MaeAB_n': 1.33,
    'e_MaeAB_L': 1.04E+05,
    'e_MaeAB_Kmal': 6.24E-03,
    'e_MaeAB_Kacoa': 3.64,
    'e_MaeAB_Kcamp': 6.54,
    'e_PckA_kcat': 55.5/0.000336947*0.002290892,
    'e_PckA_Koaa': 0.184,
    'e_PckA_Kpep': 1000,
    'e_Pdh_kcat': 1179/0.001*0.004647401,
    'e_Pdh_n': 2.65,
    'e_Pdh_L': 3.4,
    'e_Pdh_Kpyr': 0.128,
    'e_Pdh_KpyrI': 0.231,
    'e_Pdh_Kglx': 0.218,
    'e_PfkA_kcat': 9.08E+05/0.000242131*0.000143816,
    'e_PfkA_n': 4,
    'e_PfkA_L': 9.5E+07,
    'e_PfkA_Kg6p': 0.022,
    'e_PfkA_Kpep': 0.138,
    'e_Ppc_kcat': 5635/0.000377962*0.000999714,
    'e_Ppc_n': 3,
    'e_Ppc_L': 5.2E+06,
    'e_Ppc_Kpep': 0.048,
    'e_Ppc_Kfbp': 0.408,
    'e_PpsA_kcat': 1.32,
    'e_PpsA_n': 2,
    'e_PpsA_L': 1.0E-79,
    'e_PpsA_Kpyr': 1.77E-03,
    'e_PpsA_Kpep': 1.0E-03,
    'e_PykF_kcat': 5749/0.002501893*0.005977168,
    'e_PykF_n': 4,
    'e_PykF_L': 1.0E+05,
    'e_PykF_Kpep': 5,
    'e_PykF_Kfbp': 0.413,
    'p(a.p.pts.k1)': 116,
    'p(a.p.pts.km1)': 46.3,
    'p(a.p.pts.k4)': 2520,
    'p(a.p.pts.KEIIA)': 8.5E-03,
    'p(a.p.pts.Kglc)': 1.2E-03,
    'tf_Cra_scale': 100,
    'tf_Cra_kfbp': 1.36,
    'tf_Cra_n': 2,
    'tf_Crp_scale': 1.0E+08,
    'tf_Crp_kcamp': 0.895,
    'tf_Crp_n': 1,
    'tf_PdhR_scale': 100,
    'tf_PdhR_kpyr': 0.164,
    'tf_PdhR_n': 1,
    'g_aceBAK_vcra_unbound': 1.9E-09,
    'g_aceBAK_vcra_bound': 2.0E-06,
    'g_aceBAK_Kcra': 3.65E-03,
    'g_aceBAK_aceBfactor': 0.3,
    'g_aceBAK_aceKfactor': 0.03,
    'g_aceBAK_KDNA': 2.19,
    'g_aceBAK_KP': 0.897,
    'g_aceBAK_KPprime': 3.01E-03,
    'g_aceBAK_KG': 4.88E-03,
    'g_aceBAK_L': 923,
    'g_aceBAK_kcat_iclr': 9.3E-04,
    'g_aceBAK_DNA': 1,
    'g_aceBAK_vcrp_bound': 2.3E-10,
    'g_aceBAK_vcrp_unbound': 2.0E-08,
    'g_aceBAK_Kcrp': 0.341,
    'g_acs_vcrp_unbound': 0,
    'g_acs_vcrp_bound': 1.2E-06*0.000036201/0.001096222,
    'g_acs_n': 2.31,
    'g_acs_Kcrp': 4.7E-03,
    'g_akg2mal_vcrp_unbound': 0,
    'g_akg2mal_vcrp_bound': 1.4E-06,
    'g_akg2mal_Kcrp': 0.091,
    'g_akg2mal_n': 0.74,
    'g_emp_vcra_unbound': 6.2E-07*0.011389032/0.011515593,
    'g_emp_vcra_bound': 0,
    'g_emp_Kcra': 0.09,
    'g_emp_vcrp_unbound': 0,
    'g_emp_vcrp_bound': 4.7E-07,
    'g_emp_Kcrp': 0.012,
    'g_eno_vcra_unbound': 6.8E-07*0.011389032/0.011552813,
    'g_eno_vcra_bound': 0,
    'g_eno_Kcra': 0.016,
    'g_fdp_vcra_unbound': 0,
    'g_fdp_vcra_bound': 4.5E-08*0.000074810/0.000157492,
    'g_fdp_Kcra': 1.18E-03,
    'g_gltA_vcrp_unbound': 0,
    'g_gltA_vcrp_bound': 2.3E-06*0.000292771/0.001029612,
    'g_gltA_Kcrp': 0.04,
    'g_gltA_n': 1.07,
    'g_icd_vcra_unbound': 1.1E-07,
    'g_icd_vcra_bound': 8.5E-07,
    'g_icd_Kcra': 1.17E-03,
    'g_mdh_vcrp_unbound': 0,
    'g_mdh_vcrp_bound': 9.1E-06*0.000491491/0.00345727,
    'g_mdh_Kcrp': 0.06,
    'g_pckA_vcra_unbound': 0,
    'g_pckA_vcra_bound': 2.5E-06*0.000336947/0.002290892,
    'g_pckA_Kcra': 5.35E-03,
    'g_pdh_vpdhr_unbound': 3.6E-07*0.001/0.004647401,
    'g_pdh_vpdhr_bound': 1.3E-09*0.001/0.004647401,
    'g_pdh_Kpdhr': 3.4E-03,
    'g_pfkA_vcra_unbound': 8.2E-07*0.000242131/0.000143816,
    'g_pfkA_vcra_bound': 6.6E-09*0.000242131/0.000143816,
    'g_pfkA_Kcra': 6.3E-07,
    'g_ppsA_vcra_unbound': 0,
    'g_ppsA_vcra_bound': 3.3E-06,
    'g_ppsA_Kcra': 0.017,
    'g_pykF_vcra_unbound': 3.9E-07*0.002501893/0.005977168,
    'g_pykF_vcra_bound': 2.1E-09*0.002501893/0.005977168,
    'g_pykF_Kcra': 2.3E-03,
    'd_k_degr': 2.8E-05,
    'bm_k_expr': 2.0E+04,
    'bm_muACT': 5.6E-05,
    'bm_muGLC': 1.8E-04,
    'bm_GLC_ACoA': 1.88,
    'bm_GLC_AKG': 0.978,
    'bm_GLC_G6P': 0.154,
    'bm_GLC_OAA': 6.4,
    'bm_GLC_PEP': 0.423,
    'bm_GLC_PG3': 0.049,
    'bm_GLC_PYR': 0.553,
    'bm_ACT_ACoA': 0.108,
    'bm_ACT_AKG': 0.056,
    'bm_ACT_G6P': 0.076,
    'bm_ACT_OAA': 1.43,
    'bm_ACT_PEP': 0.047,
    'bm_ACT_PG3': 0.066,
    'bm_ACT_PYR': 5.185,
}