# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from numpy import array

# reverse engineering: second number maps to SBML parameter, e.g. substratGlud1_2-Oxoglutaratm maps to p_009 (note default value)
parameter_map = {
    'Km_Subset4_D-Glycerate_3-phosphate_c': (1, 1, 1000.0e0),
    'Km_Subset4_NAD_c': (2, 2, 1000.0e0),
    'Km_Subset4_L-Glutamate_c': (3, 3, 1000.0e0),
    'Km_Subset4_L-Leucine_c': (4, 4, 1000.0e0),
    'Km_Subset4_L-Methionine_c': (5, 5, 1000.0e0),
    'Km_Subset4_L-Aspartate_c': (6, 6, 1000.0e0),
    'Km_Subset4_L-Glutamine_c': (7, 7, 1000.0e0),
    'Km_Subset4_ATP_c': (8, 8, 1000.0e0),
    'substrate_Glud1_2-Oxoglutarate_m': (19, 9, 1.0e0),
    'substrate_Glud1_NADH_m': (20, 10, 1.0e0),
    'product_Glud1_L-Glutamate_m': (21, 11, 7.0e-1),
    'product_Glud1_NAD_m': (22, 12, 7.0e-1),
    'substrate_Glul_L-Glutamate_c': (23, 13, 0.7e0),
    'substrate_Glul_ATP_c': (24, 14, 0.7e0),
    'product_Glul_L-Glutamine_c': (25, 15, 2.0e-1),
    'product_Glul_ADP_c': (26, 16, 2.0e-1),
    'substrate_Got2_Oxaloacetate_m': (27, 17, 1.0e0),
    'substrate_Got2_L-Glutamate_m': (28, 18, 1.0e0),
    'product_Got2_2-Oxoglutarate_m': (29, 19, 7.0e-1),
    'product_Got2_L-Aspartate_m': (30, 20, 7.0e-1),
    'activator_Got2_L-Malate_m': (31, 21, 0.05e0),
    'substrate_Mdh2_L-Malate_m': (32, 22, 1.0e0),
    'substrate_Mdh2_NAD_m': (33, 23, 0.5e0),
    'product_Mdh2_Oxaloacetate_m': (34, 24, 7.0e-1),
    'product_Mdh2_NADH_m': (35, 25, 5.0e-1),
    'substrate_ND1_a_NADH_m': (36, 26, 2.0e0),
    'substrate_ND1_a_CoQ_m': (37, 27, 0.7e0),
    'substrate_ND1_a_H_in_m': (38, 28, 0.7e0),
    'product_ND1_a_NAD_m': (39, 29, 2.0e0),
    'product_ND1_a_CoQH_radical_m': (40, 30, 2.0e-1),
    'product_ND1_a_H_out_m': (41, 31, 2.0e-1),
    'substrate_Pklr_Phosphoenolpyruvate_c': (9, 32, 1.0e0),
    'substrate_Pklr_ADP_c': (10, 33, 0.7e0),
    'product_Pklr_Pyruvate_c': (11, 34, 2.0e-1),
    'product_Pklr_ATP_c': (12, 35, 2.1e-1),
    'substrate_Subset0_Oxaloacetate_m': (42, 36, 1.0e0),
    'substrate_Subset0_NAD_m': (43, 37, 0.7e0),
    'substrate_Subset0_Pyruvate_c': (44, 38, 1.0e0),
    'product_Subset0_2-Oxoglutarate_m': (45, 39, 2.0e-1),
    'product_Subset0_NADH_m': (46, 40, 2.0e-1),
    'activator_Subset0_ADP_m': (47, 41, 0.05e0),
    'inhibitor_Subset0_ATP_m': (49, 42, 1.0e-2),
    'substrate_Subset1_NAD_c': (50, 43, 0.7e0),
    'substrate_Subset1_beta-D-Glucose_c': (51, 44, 1.0e0),
    'product_Subset1_NADH_c': (52, 45, 5.0e-1),
    'product_Subset1_D-Glycerate_3-phosphate_c': (53, 46, 1.0e0),
    'activator_Subset1_ADP_c': (54, 47, 0.04e0),
    'inhibitor_Subset1_ADP_c': (55, 48, 1.0e-2),
    'inhibitor_Subset1_ATP_c': (56, 49, 1.0e-2),
    'inhibitor_Subset1_Phosphoenolpyruvate_c': (57, 50, 1.0e-2),
    'substrate_Subset2_2-Oxoglutarate_c': (58, 51, 1.0e0),
    'substrate_Subset2_L-Aspartate_c': (59, 52, 1.0e0),
    'substrate_Subset2_NADH_c': (60, 53, 0.5e0),
    'product_Subset2_L-Glutamate_c': (61, 54, 1.0e0),
    'product_Subset2_L-Malate_c': (62, 55, 1.0e0),
    'product_Subset2_NAD_c': (63, 56, 5.0e-1),
    'activator_Subset2_L-Malate_c': (64, 57, 0.1e0),
    'inhibitor_Subset2_L-Glutamine_c': (65, 58, 1.0e-1),
    'substrate_Subset26_ADP_m': (66, 59, 0.5e0),
    'substrate_Subset26_Phosphoenolpyruvate_c': (67, 60, 1.0e0),
    'substrate_Subset26_L-Malate_m': (68, 61, 1.0e0),
    'product_Subset26_Oxaloacetate_m': (69, 62, 1.0e0),
    'product_Subset26_ATP_m': (70, 63, 3.0e-1),
    'product_Subset26_L-Malate_c': (71, 64, 1.0e0),
    'substrate_Subset3_Pyruvate_c': (72, 65, 1.0e0),
    'substrate_Subset3_NADH_c': (73, 66, 0.7e0),
    'product_Subset3_L-Lactate_f': (74, 67, 4.0e-1),
    'product_Subset3_NAD_c': (75, 68, 7.0e-1),
    'substrate_Subset35_D-Glycerate_3-phosphate_c': (76, 69, 1.0e0),
    'product_Subset35_Phosphoenolpyruvate_c': (77, 70, 7.0e-1),
    'substrate_Subset37_H_in_m': (78, 71, 0.7e0),
    'substrate_Subset37_CoQH_radical_m': (79, 72, 2.0e0),
    'product_Subset37_H_out_m': (80, 73, 2.0e-1),
    'product_Subset37_CoQ_m': (81, 74, 2.0e0),
    'substrate_Subset5_2-Oxoglutarate_m': (82, 75, 1.0e0),
    'substrate_Subset5_NAD_m': (83, 76, 0.7e0),
    'substrate_Subset5_CoQ_m': (84, 77, 0.7e0),
    'substrate_Subset5_Orthophosphate_m': (85, 78, 0.2e0),
    'substrate_Subset5_ADP_m': (86, 79, 0.7e0),
    'product_Subset5_L-Malate_m': (87, 80, 5.0e-1),
    'product_Subset5_NADH_m': (88, 81, 2.1e-1),
    'product_Subset5_CoQH_radical_m': (89, 82, 2.0e-1),
    'product_Subset5_ATP_m': (90, 83, 2.0e-1),
    'inhibitor_Subset5_Oxaloacetate_m': (93, 84, 1.0e-2),
    'substrate_adencarr_ADP_c': (96, 85, 2.0e0),
    'substrate_adencarr_ATP_m': (97, 86, 2.0e0),
    'product_adencarr_ADP_m': (98, 87, 2.0e0),
    'product_adencarr_ATP_c': (99, 88, 2.0e0),
    'substrate_akgcarr_2-Oxoglutarate_m': (100, 89, 2.0e0),
    'substrate_akgcarr_L-Malate_c': (101, 90, 2.0e0),
    'product_akgcarr_2-Oxoglutarate_c': (102, 91, 2.0e0),
    'product_akgcarr_L-Malate_m': (103, 92, 2.0e0),
    'substrate_aspglucarr_L-Aspartate_m': (104, 93, 1.0e0),
    'substrate_aspglucarr_L-Glutamate_c': (105, 94, 1.0e0),
    'product_aspglucarr_L-Aspartate_c': (106, 95, 1.0e0),
    'product_aspglucarr_L-Glutamate_m': (107, 96, 1.0e0),
    'substrate_atpase_ATP_c': (108, 97, 1.0e0),
    'product_atpase_ADP_c': (109, 98, 5.0e-1),
    'substrate_atpase1_ADP_m': (110, 99, 0.7e0),
    'substrate_atpase1_Orthophosphate_m': (111, 100, 0.7e0),
    'substrate_atpase1_H_out_m': (112, 101, 2.0e0),
    'product_atpase1_ATP_m': (113, 102, 2.0e-1),
    'product_atpase1_H_in_m': (114, 103, 2.0e0),
    'substrate_dicarr_L-Malate_c': (115, 104, 1.0e0),
    'substrate_dicarr_Orthophosphate_m': (116, 105, 1.0e0),
    'product_dicarr_L-Malate_m': (117, 106, 7.0e-1),
    'substrate_feed_glc_beta-D-Glucose_f': (118, 107, 1.0e0),
    'product_feed_glc_beta-D-Glucose_c': (119, 108, 7.0e-1),
    'substrate_feed_leu_L-Leucine_f': (120, 109, 1.0e0),
    'product_feed_leu_L-Leucine_c': (121, 110, 7.0e-1),
    'substrate_feed_met_L-Methionine_f': (122, 111, 1.0e0),
    'product_feed_met_L-Methionine_c': (123, 112, 7.0e-1),
    'substrate_glucarr_L-Glutamate_m': (124, 113, 2.0e0),
    'product_glucarr_L-Glutamate_c': (125, 114, 2.0e0),
    'substrate_mitphocarr_H_out_m': (126, 115, 0.7e0),
    'product_mitphocarr_Orthophosphate_m': (127, 116, 2.0e-1),
    'product_mitphocarr_H_in_m': (128, 117, 2.0e-1),
}

i2_to_name_map = {v[1]: name for name,v in parameter_map.items()}
for k in range(1,117+1):
    assert k in i2_to_name_map.keys()

parameter_list = list(name for i,name in sorted(i2_to_name_map.items(), key=lambda x: x[0]))
assert len(parameter_list) == 117
name_to_id_map = {name: 'p_{:03}'.format(i) for i,name in i2_to_name_map.items()}
param_ids = [name_to_id_map[name] for name in parameter_list]

default_values = [parameter_map[name][2] for name in parameter_list]
from math import log
default_log_values = [log(v, 10.) for v in default_values]
param_array = array(default_log_values)

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
