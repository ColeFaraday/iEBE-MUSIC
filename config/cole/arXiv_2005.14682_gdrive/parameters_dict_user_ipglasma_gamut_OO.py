#!/usr/bin/env python3
"""
    This script contains all the user modified parameters in
    the iEBE-MUSIC package.
"""

# control parameters
control_dict = {
    'initial_state_type': "IPGlasma",  # 3DMCGlauber, IPGlasma
    'walltime': "100:00:00",  # walltime to run
    'save_ipglasma_results': False,   # flag to save IPGlasma results
    'save_kompost_results': False,
    'save_hydro_surfaces': True,    # flag to save hydro surfaces
    'save_UrQMD_files': False,      # flag to save UrQMD files
}


# IPGlasma
ipglasma_dict = {
    #'type': "fixed",  # minimumbias or fixed
    #'database_name_pattern': "/wsu/home/groups/maj-shen/Initial_conditions/IPGlasma_Qsnormfixed/PbPb2760/PbPb2760_C0-5.h5",
    #'type': "minimumbias",  # minimumbias or fixed
    #'database_name_pattern': "/wsu/home/groups/maj-shen/IPGlasma_Qsnormfixed/AuAu200/AuAu200_C{}.h5",
    'type': "self",  # minimumbias or fixed
    'bmin': 0.,
    'bmax': 20.,
    'lightNucleusOption': 2,
    'Projectile': "O",
    'Target': "O",
    'roots': 5360.,
    'SigmaNN': 69.,
    'useConstituentQuarkProton': 3,   # 0: round proton; 3: fluctuating proton
}


# MUSIC
music_dict = {
    'Initial_profile': 9,    # type of initial condition 
                             # 9: IPGlasma (full Tmunu),
                             #   -- 91: e and u^\mu,
                             #   -- 92: e only,
                             #   -- 93: e, u^\mu, and pi^\munu
    's_factor': 0.235,       # normalization factor read in initial data file
    'Initial_time_tau_0': 0.4,  # starting time of the hydrodynamic evolution (fm/c)
    'Delta_Tau': 0.005,         # time step to use in the evolution [fm/c]
    'boost_invariant':  1,      # whether the simulation is boost-invariant
    'EOS_to_use': 9,            # type of the equation of state
                                # 9: hotQCD EOS with UrQMD
    # transport coefficients
    'quest_revert_strength': 1.0,          # the strength of the viscous regulation
    'Viscosity_Flag_Yes_1_No_0': 1,        # turn on viscosity in the evolution
    'Include_Shear_Visc_Yes_1_No_0': 1,    # include shear viscous effect
    'Shear_to_S_ratio': 0.12,              # value of \eta/s
    'T_dependent_Shear_to_S_ratio': 0,     # flag to use temperature dep. \eta/s(T)
    'Include_Bulk_Visc_Yes_1_No_0': 1,     # include bulk viscous effect
    'T_dependent_zeta_over_s': 8,          # parameterization of \zeta/s(T)
    'Include_second_order_terms': 1,       # include second order non-linear coupling terms
    'Bulk_relaxation_time_type': 0,
    'Include_vorticity_terms': 0,          # include vorticity coupling terms

    # switches to output evolution information
    'output_evolution_data': 2,     # flag to output evolution history to file
    'output_evolution_T_cut': 0.140,
    'outputBinaryEvolution': 1,     # output evolution file in binary format
    'output_evolution_every_N_eta': 1,  # output evolution file every Neta steps
    'output_evolution_every_N_x':  4,   # output evolution file every Nx steps
    'output_evolution_every_N_y': 4,    # output evolution file every Ny steps
    'output_evolution_every_N_timesteps': 40,  # output evolution every Ntime steps

    # parameters for freeze out and Cooper-Frye
    'N_freeze_out': 1,
    'eps_freeze_max': 0.18,
    'eps_freeze_min': 0.18,
}


# iSS
iss_dict = {
    'hydro_mode': 1,    # mode for reading in freeze out information 
    'include_deltaf_shear': 1,      # include delta f contribution from shear
    'include_deltaf_bulk': 1,       # include delta f contribution from bulk
    'sample_upto_desired_particle_number': 1,  # 1: flag to run sampling until desired
                                               # particle numbers is reached
    'number_of_particles_needed': 50000,      # number of hadrons to sample
    'local_charge_conservation': 0,  # flag to impose local charge conservation
    'global_momentum_conservation': 0,  # flag to impose GMC
}


# hadronic afterburner toolkit
hadronic_afterburner_toolkit_dict = {
    'event_buffer_size': 100000,       # the number of events read in at once
    'compute_correlation': 1,       # flag to compute correlation function
    'flag_charge_dependence': 1,    # flag to compute charge dependence correlation
    'compute_corr_rap_dep': 0,      # flag to compute the rapidity dependent multi-particle correlation
    'resonance_weak_feed_down_flag': 0,  # include weak feed down contribution
}