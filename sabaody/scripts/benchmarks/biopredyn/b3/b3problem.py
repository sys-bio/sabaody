# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from __future__ import print_function, division, absolute_import

from sabaody.timecourse.timecourse_sim_base import StalledSimulation
from sabaody.timecourse.timecourse_sim_biopredyn import TimecourseSimBiopredyn
from sabaody.scripts.benchmarks.biopredyn.benchsetup import BioPreDynUDP

from numpy import array, mean, sqrt, maximum, minimum, vstack

import tellurium as te # used to patch roadrunner
from roadrunner import RoadRunner

from typing import SupportsFloat

class B3Problem(TimecourseSimBiopredyn):
    ''' Class that performs a timecourse simulation
    and evaluates the objective function for b1.'''

    def __init__(self, sbml):
        self.sbml = sbml
        self.r = RoadRunner(sbml)
        from data import measured_quantity_ids, exp_data
        self.measured_quantity_ids = measured_quantity_ids
        self.reference_values = exp_data
        self.reference_value_means_squared = mean(self.reference_values, axis=0)**2
        from params import new_param_ids as param_ids
        self.param_list = param_ids

        from data import GLC_ss_value_map
        for id,value in GLC_ss_value_map.items():
            if self.r[id] != value:
                print('discrepancy for {id}: {sbml} (sbml) vs {matlab} (matlab)'.format(id=id, sbml=self.r[id], matlab=value))

        print('alphaGLC := GLC/(GLC + pts_Kglc)')
        print('  {alphaGLC} := {GLC}/({GLC} + {pts_Kglc})'.format(
            alphaGLC=self.r.alphaGLC,
            GLC=self.r.GLC,
            pts_Kglc=self.r.pts_Kglc,
        ))
        # print('mu := alphaGLC*bm_muGLC + alphaACT*bm_muACT')
        # print('  {mu} := {alphaGLC}*{bm_muGLC} + {alphaACT}*{bm_muACT}'.format(
        #     mu=self.r.mu,
        #     alphaGLC=self.r.alphaGLC,
        #     bm_muGLC=self.r.bm_muGLC,
        #     alphaACT=self.r.alphaACT,
        #     bm_muACT=self.r.bm_muACT,
        # ))
        # print('g_acs = bm_k_expr*mu*((1 - CrpcAMP^g_acs_n/(CrpcAMP^g_acs_n + g_acs_Kcrp^g_acs_n))*g_acs_vcrp_unbound + (CrpcAMP^g_acs_n/(CrpcAMP^g_acs_n + g_acs_Kcrp^g_acs_n))*g_acs_vcrp_bound)')
        # print('  {g_acs} = {bm_k_expr}*{mu}*((1 - {CrpcAMP}^{g_acs_n}/({CrpcAMP}^{g_acs_n} + {g_acs_Kcrp}^{g_acs_n}))*{g_acs_vcrp_unbound} + ({CrpcAMP}^{g_acs_n}/({CrpcAMP}^{g_acs_n} + {g_acs_Kcrp}^{g_acs_n}))*{g_acs_vcrp_bound})'.format(
        #     g_acs=self.r.g_acs,
        #     bm_k_expr=self.r.bm_k_expr,
        #     mu=self.r.mu,
        #     CrpcAMP=self.r.CrpcAMP,
        #     g_acs_n=self.r.g_acs_n,
        #     g_acs_Kcrp=self.r.g_acs_Kcrp,
        #     g_acs_vcrp_unbound=self.r.g_acs_vcrp_unbound,
        #     g_acs_vcrp_bound=self.r.g_acs_vcrp_bound,
        # ))
        from params import getDefaultParamValues
        self.setParameterVector(getDefaultParamValues())
        # print('k_bm_PYR = alphaGLC*bm_GLC_PYR + alphaACT*bm_ACT_PYR')
        # print('  {k_bm_PYR} = {alphaGLC}*{bm_GLC_PYR} + {alphaACT}*{bm_ACT_PYR}'.format(
        #     k_bm_PYR=self.r.k_bm_PYR,
        #     alphaGLC=self.r.alphaGLC,
        #     bm_GLC_PYR=self.r.bm_GLC_PYR,
        #     alphaACT=self.r.alphaACT,
        #     bm_ACT_PYR=self.r.bm_ACT_PYR,
        # ))
        # print('e_PykF:  (PykF*e_PykF_kcat*PEP/e_PykF_Kpep)*(1 + PEP/e_PykF_Kpep)^(e_PykF_n - 1)/((1 + PEP/e_PykF_Kpep)^e_PykF_n + e_PykF_L/(1 + FBP/e_PykF_Kfbp)^e_PykF_n)')
        # print('  {e_PykF}: ({PykF}*{e_PykF_kcat}*{PEP}/{e_PykF_Kpep})*(1 + {PEP}/{e_PykF_Kpep})^({e_PykF_n} - 1)/((1 + {PEP}/{e_PykF_Kpep})^{e_PykF_n} + {e_PykF_L}/(1 + {FBP}/{e_PykF_Kfbp})^e_PykF_n)'.format(
        #     e_PykF=self.r.e_PykF,
        #     PykF=self.r.PykF,
        #     e_PykF_kcat=self.r.e_PykF_kcat,
        #     PEP=self.r.PEP,
        #     e_PykF_Kpep=self.r.e_PykF_Kpep,
        #     e_PykF_n=self.r.e_PykF_n,
        #     e_PykF_L=self.r.e_PykF_L,
        #     FBP=self.r.FBP,
        #     e_PykF_Kfbp=self.r.e_PykF_Kfbp,
        # ))
        print('e_GltA = {}'.format(self.r.e_GltA))
        print('e_Mdh = {}'.format(self.r.e_Mdh))
        print('e_PckA = {}'.format(self.r.e_PckA))
        print('e_Ppc = {}'.format(self.r.e_Ppc))
        print('d_OAA = {}'.format(self.r.d_OAA))
        print('OAA\' = {}'.format(self.r["OAA'"]))

        self.penalty_scale = 1.


    def evaluate(self, x):
        # type: (array) -> SupportsFloat
        """
        Evaluate and return the objective function.
        """
        from interruptingcow import timeout
        from data import time_end, n_points
        self.reset()
        self.setParameterVector(x)
        self.r.reset()
        def worker():
            sim = self.r.simulate(0., time_end, n_points, self.measured_quantity_ids)
            residuals = sim-self.reference_values
            normalized_mse_per_quantity = mean(residuals**2,axis=0)/self.reference_value_means_squared
            return sqrt(mean(normalized_mse_per_quantity))
        try:
            with timeout(10, StalledSimulation):
                return worker()
        except (RuntimeError, StalledSimulation):
            # if convergence fails, use a penalty score
            return 1e9*self.penalty_scale


    def plotQuantity(self, quantity_id, param_values):
        ''' Plot a simulated quantity vs its data points using Tellurium.'''
        from data import measured_quantity_ids, measured_quantity_id_to_name_map
        from data import t1, t2, time_end, n1, n2, n3
        quantity_name = measured_quantity_id_to_name_map.get(quantity_id,quantity_id)
        iq = measured_quantity_ids.index(quantity_id)
        reference_data = array(self.reference_values[:,iq])

        r = RoadRunner(self.sbml)
        r.reset()
        r.resetAll()
        r.resetToOrigin()
        self._setParameterVector(param_values, self.param_list, r)
        # r.oneStep(0., 10)
        # print('plotQuantity OAA\' = {}'.format(r["OAA'"]))
        sim = vstack((
            r.simulate(0., t1, n1, ['time', quantity_id]),
            r.simulate(t1, t2, n2, ['time', quantity_id]),
            r.simulate(t2, time_end, n3, ['time', quantity_id]),
            ))
        assert sim.shape[0] == reference_data.shape[0]
        residuals = sim[:,1] - reference_data

        r.reset()
        r.resetAll()
        r.resetToOrigin()
        self._setParameterVector(param_values, self.param_list, r)
        # self._setParameterVector(param_values, self.param_list, r)
        s = r.simulate(0,time_end,1000,['time',quantity_id])

        import tellurium as te
        te.plot(sim[:,0], reference_data, scatter=True,
            name=quantity_name+' data', show=False,
            title=quantity_name,
            error_y_pos=maximum(residuals,0),
            error_y_neg=-minimum(residuals,0))
        te.plot(s[:,0], s[:,1], name=quantity_name+' sim')


    def getParameterValue(self,param_index):
        from params import param_index_to_name_map
        try:
            return self.r[param_index_to_name_map[param_index]]
        except KeyError:
            raise KeyError('No such parameter for index {}, must be 0-1758 inclusive'.format(param_index))


class B4_UDP(BioPreDynUDP):
    def __init__(self, lb, ub, sbml_file='b4.xml'):
        super().__init__(lb=lb, ub=ub, sbml_file=sbml_file)

    def fitness(self, x):
        if self.evaluator is None:
            from b1problem import B1Problem
            self.evaluator = B1Problem(self.sbml_file)
        return (self.evaluator.evaluate(x),)
