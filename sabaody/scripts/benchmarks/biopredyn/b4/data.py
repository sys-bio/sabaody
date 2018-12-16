# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from numpy import array, zeros

quantity_names = ['Product_protein', 'L-Methionine', 'L-Leucine', 'L-Lactate', 'beta-D-Glucose', 'L-Aspartate', 'L-Malate', 'Pyruvate', 'Oxaloacetate', 'ATP', 'ATP', 'ADP', 'ADP_c']

timecourse_data = array([
    [0,     29.54174187, 5110.119691, 4999.956639, 1.056682831, 449958.4343, 1009.945764, 988.3517969, 996.1405443, 839.7703035, 3314.558385, 2968.296835, 1016.447754, 1029.663149],
    [23.9759, 29.06135825, 4427.537773, 4990.471667, 19033.05068, 499628.9405, 514.889607, 1883.981851, 4115.730274, 443.5222307, 3298.082924, 3588.716676, 701.1769714, 841.6656476],
    [48.4337, 31.56920926, 4649.633023, 4706.446115, 29713.37459, 498137.7445, 614.0882509, 1999.234422, 5088.17481, 457.2654501, 3144.678363, 3524.003949, 534.3245626, 898.4469128],
    [72.8916, 32.58992629, 4642.175831, 4703.420191, 52653.84782, 469436.4399, 667.144403, 1977.174384, 4941.17988, 452.1008571, 3343.981672, 3274.933898, 637.1604048, 748.7508252],
    [90.3614, 32.93492455, 4581.482695, 4580.779761, 62491.60793, 458816.0559, 706.4697945, 2027.556359, 5561.084132, 416.1288178, 3305.264733, 3377.224218, 608.6810043, 760.8237877],
    [115.984, 33.80995822, 4231.998041, 4576.568758, 71665.49964, 441725.8779, 748.837145, 1834.640732, 4711.566421, 433.6235068, 2664.13707, 3359.281519, 608.5031107, 746.0614226],
    [140.442, 34.67192676, 4609.073999, 4388.444795, 93744.69241, 371353.6441, 761.4219172, 1741.34438, 4466.968205, 471.9681186, 3276.842196, 3268.007202, 609.2855454, 770.8013591],
    [164.9, 35.64086504, 4379.397091, 4823.258118, 96012.12538, 409872.6888, 913.9581526, 2054.553359, 4841.62543, 462.4384044, 3326.232934, 3375.331315, 657.6144762, 747.1622156],
    [210.321, 35.1073701, 4047.37735, 4757.799632, 131633.9417, 429309.5792, 838.4429003, 2023.441102, 4741.87247, 463.3431076, 2838.535673, 3344.113884, 606.0191858, 696.1165299],
    [233.614, 34.78766884, 4354.532227, 4267.505383, 139701.0391, 377830.4707, 864.115653, 2012.727053, 4982.305375, 451.6411544, 3445.146289, 3384.49464, 596.595147, 747.4997328],
    [258.072, 35.10275329, 3893.078648, 3946.812817, 156106.4324, 376607.9654, 1019.41341, 2077.935601, 4932.876021, 432.2633547, 3185.845081, 3123.317817, 606.9552722, 742.2563724],
    [282.53, 39.16229127, 4223.934695, 4229.786474, 189350.8377, 350136.0051, 945.7524046, 2018.02482, 4965.805674, 459.569613, 3248.126308, 3303.223152, 634.2843344, 740.5121927],
    [300, 39.36873083, 3819.952372, 3226.591797, 170253.9838, 362466.0386, 962.815767, 2167.954632, 4922.316021, 461.1326466, 3189.167366, 3335.671338, 664.509921, 757.3732437],
    ])

time_values = array(timecourse_data[:,0])

n_obs = 13
n_quantities = len(quantity_names)

timecourse_stddev = array([
    [0,     0.916516259, 220.2393825, 0.086722941, 0.113365662, 100083.1314, 19.8915281, 23.29640617, 7.718911471, 320.4593929, 629.11677, 63.40633065, 32.89550786, 59.32629796],
    [23.9759, 3.42708349, 859.4844544, 266.3833335, 524.0986472, 27089.88103, 72.52278599, 1.363702921, 13.17945154, 67.9675385, 110.2258472, 512.6933529, 67.11194286, 169.2792952],
    [48.4337, 0.072781474, 197.1939541, 83.56777088, 13530.25082, 50101.48902, 8.871498249, 109.6688443, 1402.38962, 25.79309975, 208.3432738, 361.1878982, 244.5448747, 294.6078256],
    [72.8916, 0.345652583, 11.22833874, 111.2603823, 145.6956478, 17694.8798, 11.00519392, 1.408768357, 800.1597591, 29.84428584, 184.2633444, 149.0122046, 26.80319038, 1.191650429],
    [90.3614, 0.103150906, 5.585389682, 4.179521469, 2222.584132, 13862.11186, 0.953588928, 72.01271842, 1881.128264, 99.10036436, 104.3694651, 49.86843658, 78.08799131, 27.79957543],
    [115.984, 0.003516434, 495.8039179, 193.3375168, 15030.00072, 4663.755834, 0.759709907, 343.8585363, 3.332842875, 61.44498639, 1179.74586, 8.403037386, 72.83977854, 0.150845275],
    [140.442, 0.186053515, 442.6879971, 1.429589001, 515.5848117, 112764.7117, 48.67616557, 548.4312396, 616.2835899, 16.98823721, 45.18439211, 177.4455966, 67.99290924, 50.07871826],
    [164.9, 0.604730081, 164.3741824, 1052.096236, 22589.74924, 12874.62245, 190.2563052, 67.32671764, 29.79086077, 0.791191271, 144.5058684, 35.34263088, 30.52495245, 2.300431195],
    [210.321, 3.228859795, 170.8252992, 1250.019264, 372.1165486, 67335.15833, 70.03419938, 0.977796603, 311.3950597, 2.654215273, 828.1886549, 27.87223266, 71.86362837, 102.5249403],
    [233.614, 5.262062329, 608.8844539, 434.830766, 8311.921766, 14941.05855, 69.51269399, 20.40589406, 115.4107506, 20.1576913, 387.132577, 53.48928055, 91.2997059, 1.854534475],
    [258.072, 6.079093429, 142.482705, 35.01436682, 49.13512714, 3973.930766, 190.684819, 114.9912025, 29.80795876, 58.42129056, 128.8298377, 467.6643662, 71.7674556, 14.94525519],
    [282.53, 0.608382544, 688.7293909, 700.4329474, 42607.67548, 27959.98971, 4.487190854, 2.669639537, 1.328651269, 3.420773959, 1.32738423, 106.1736951, 18.79533114, 21.39761464],
    [300,     0.008461654, 0.624744428, 1186.096406, 12180.03246, 11498.07728, 3.204466046, 309.209264, 110.2279582, 0.074706795, 116.9052678, 39.83732302, 40.18584194, 10.01248736],
    ])

css = array([
    100000,
    1,
    1000,
    1000,
    30,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    3000,
    1000,
    1000,
    1000,
    100,
    100,
    100,
    100,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    3000,
    100000,
    1000,
    1000,
    1000,
])

conc_indices = list(k for k in [5, 4, 3, 2, 1, 29, 27, 21, 15, 13, 30, 32, 11])

conc_ids = list('c_{:02d}'.format(i) for i in conc_indices)
name_to_id_map = {name: conc_ids[k] for k,name in enumerate(quantity_names)}

scaled_data = zeros((n_obs, n_quantities))
for k in range(len(conc_indices)):
    scaled_data[:,k] = timecourse_data[:,k+1]/css[conc_indices[k]-1]

scaled_error = zeros((n_obs, n_quantities))
for k in range(len(conc_indices)):
    scaled_error[:,k] = timecourse_stddev[:,k+1]/css[conc_indices[k]-1]

# unfortunately both are the same, so this is useless
assert scaled_data.shape == (n_obs,n_quantities)
assert scaled_error.shape == (n_obs,n_quantities)
# instead test some of the values
assert scaled_data[0,0] == timecourse_data[0,1]/css[5-1]
assert scaled_data[n_obs-1,0] == timecourse_data[n_obs-1,1]/css[5-1]
assert scaled_error[0,0] == timecourse_stddev[0,1]/css[5-1]
assert scaled_error[n_obs-1,0] == timecourse_stddev[n_obs-1,1]/css[5-1]