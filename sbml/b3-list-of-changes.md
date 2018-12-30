* Villaverde et al. used the steady state values under glucose for a modified parameter set as the initial values to their Matlab model. The initial values for both the state variables and parameters do not correspond between the Matlab model (b3_initial.m) and the SBML model (b3.xml).
  - In our version of the SBML model, we adjusted the initial values but not the parameters as they are set by our algorithm (see b3/data.py).
  - We also changed two hard-coded constants corresponding to the steady state values of Ppc and MaeAB which were affected by the aforementioned changes.
  - Finally, we changed the shift1 and shift2 variables to better match the time values of discontinuities in the Matlab implementation.
