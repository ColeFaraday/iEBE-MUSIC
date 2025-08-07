# iEBE-MUSIC
This is a repository is an overarching numerical framework for event-by-event simulations of relativistic heavy-ion collisions.

If you have any questions, please email to the iEBE-MUSIC google groups, iebe-music@googlegroups.com

## Setup & Ingradients:
All the code packages can be downloaded from online git repositories. Please use `codes/get_code_packages.sh` to download the code packages and `codes/compile_code_packages.sh` to compile all the packages before event-by-event simulations.

Initial conditions:

- [IPGlasma](https://github.com/schenke/ipglasma)
- [3DMCGlauber](https://github.com/chunshen1987/3dMCGlauber): a 3D Monte-Carlo Glauber model for heavy-ion collisions

Pre-equilibrium evolution:

- [KoMPoST](https://github.com/KMPST/KoMPoST)

Hydrodynamics:

- [MUSIC](https://github.com/MUSIC-fluid/MUSIC)

Particlization & hadronic transport:

- [iSS](https://github.com/chunshen1987/iSS) + [UrQMD](https://Chunshen1987@bitbucket.org/Chunshen1987/urqmd_afterburner.git)

## Usage:

type `./generate_jobs.py -h` for help information

## Parameters:
Users can pass model parameters through a python script `parameters_dict_user.py`. It contains multiple dictionaries, which are related to each code module inside the iEBE-MUSIC framework. This script will update the master parameters dictionaries in `config/parameters_dict_master.py`. One can read `config/parameters_dict_master.py` for all the available parameters options for each module. If a user want to modify any parameters, he can add it in the `parameters_dict_user.py`.

#### initial_dict
The `initial_dict` dictionary specify the type of the initial condition to use,

- IPGlasma
- 3DMCGlauber

For the IPGlasma initial condition, the user needs to specify the HDF5 database filename. 

For the 3DMCGlauber initial condition,

1. If `database_name : "self"`, initial condition will be generated on the fly with the rest part of the simulations.

2. If `database_name : database_file`, the code package will use the pre-generated initial coniditions stored in the database (HDF5).

#### music_dict
The `music_dict` has all the parameters to run MUSIC for (3+1)D hydrodynamic simulations. 

    'Initial_profile': 9,  for IPGlasma initial condition
        - 9: IPGlasma (full Tmunu),
        - 91: e and u^\mu,
        - 92: e only,
        - 93: e, u^\mu, and pi^\munu
    'Initial_profile': 13,  for 3D MCGlauber initial condition
        - 13: 3D MCGlauber initial condition with dynamical initialization,
        - 131: 3D MCGlauber initial condition with instantaneous initialization

## Settings on NERSC:

The clusters on NERSC does not use utf-8 as default. To run the script properly, one needs to add the following commands in the ~/.bashrc.ext file,

```
export PYTHONIOENCODING=utf-8
export LC_CTYPE=en_US.UTF8
```

## Docker Support

The iEBE-MUSIC has its official docker image on docker hub [iebe-music](https://hub.docker.com/r/chunshen1987/iebe-music).

## Coding Style

We use YAPF to impose coding format for the python scripts. Before every commit, please use

    yapf -i filename.py

to apply the uniformed format to the source code files

# Hadronic Afterburner Toolkit - Particle Analysis Files

## Overview
The Hadronic Afterburner Toolkit generates flow analysis data for heavy-ion collision simulations. Particle files contain event-averaged observables and flow coefficients for different particle species and kinematic cuts.

## File Generation
- **Location**: Generated in `src/Analysis.cpp` during the main analysis workflow
- **Process**: Multiple `singleParticleSpectra` objects are created with different `particle_monval` values
- **Filtering**: In `src/particleSamples.cpp`, particles are filtered based on species, charge, and other properties

## Particle Identifiers
- **9999**: All charged hadrons
- **99999**: All hadrons (including neutrals)
- **211**: π⁺
- **-211**: π⁻
- **321**: K⁺
- **-321**: K⁻
- **2212**: p (proton)
- **-2212**: p̄ (antiproton)
- **333**: φ(1020)
- **3122**: Λ
- **-3122**: Λ̄
- **And many more**: See PDG particle codes

## Output File Format
**File naming**: `particle_[monval]_vndata_[rap_type]_[rap_min]_[rap_max].dat`
**Examples**: 
- `particle_9999_vndata_eta_-0.5_0.5.dat` (charged hadrons, η ∈ [-0.5, 0.5])
- `particle_211_vndata_y_-1.0_1.0.dat` (π⁺, y ∈ [-1.0, 1.0])
- `particle_9999_vndata_eta_-2.5_2.5_weakFD.dat` (with weak feed-down)

**File structure**:
```
# n  Qn_real  Qn_real_err  Qn_imag  Qn_imag_err
0    dN/dη     dN/dη_err    ⟨pT⟩     ⟨pT⟩_err
1    v1_real   v1_real_err  v1_imag  v1_imag_err
2    v2_real   v2_real_err  v2_imag  v2_imag_err
...
99   total_N   n_events     0.0      0.0
```

## Key Data Rows

### n = 0 Row: Event-Averaged Observables
- **Column 2**: `dN/dη` or `dN/dy` - Event-averaged yield per unit rapidity/pseudorapidity
- **Column 4**: `⟨pT⟩` - Average transverse momentum
- **Usage**: Primary observables for yield and mean pT analysis

### n = 1-6 Rows: Flow Coefficients
- **Columns 2,4**: Real and imaginary parts of vn flow coefficients
- **Columns 3,5**: Statistical errors on flow coefficients
- **Usage**: Anisotropic flow analysis (v1, v2, v3, etc.)

### n = 99 Row: Summary Statistics
- **Column 2**: Total number of particles across all events
- **Column 3**: Total number of events analyzed
- **Usage**: Normalization checks and cross-validation

## File Types and Naming Conventions

### Integrated Flow Files
- **Format**: `particle_[monval]_vndata_[rap_type]_[rap_min]_[rap_max].dat`
- **Content**: pT-integrated flow coefficients and yields

### Differential Flow Files
- **Format**: `particle_[monval]_vndata_diff_[rap_type]_[rap_min]_[rap_max].dat`
- **Content**: pT-differential flow coefficients and spectra

### Correlation Files
- **Format**: `particle_[monval]_[correlation_type]_[rap_type]_[rap_min]_[rap_max].dat`
- **Examples**: 
  - `particle_9999_vn2_eta_-0.5_0.5.dat` (2-particle correlations)
  - `particle_9999_Cn2_ss_eta_-0.5_0.5.dat` (same-sign correlations)
  - `particle_9999_Cn2_os_eta_-0.5_0.5.dat` (opposite-sign correlations)

## Common Analysis Use Cases

### Mean pT vs dN/dη Plot
```python
# Read from any particle file
dN_deta = data[0, 1]  # n=0 row, column 2
mean_pT = data[0, 3]  # n=0 row, column 4
```

### Flow Coefficient Analysis
```python
# Extract v2 (elliptic flow)
v2_real = data[2, 1]  # n=2 row, column 2
v2_imag = data[2, 3]  # n=2 row, column 4
v2 = sqrt(v2_real**2 + v2_imag**2)
```

### Particle Yield Comparison
```python
# Compare yields between different particles
pion_yield = data_pion[0, 1]      # π⁺ yield
kaon_yield = data_kaon[0, 1]      # K⁺ yield
proton_yield = data_proton[0, 1]  # p yield
```

## Technical Details
- **File format**: Plain text DAT files with scientific notation
- **Precision**: 8 decimal places
- **Rapidity types**: 
  - `eta`: Pseudorapidity (η)
  - `y`: Rapidity (y)
- **Kinematic cuts**: Applied based on file naming convention
- **Statistical errors**: Provided for all observables
- **Special flags**: 
  - `weakFD`: Weak feed-down included
  - `ss`: Same-sign correlations
  - `os`: Opposite-sign correlations

## Analysis Scripts
The `ebe_scripts/` directory contains Python scripts for:
- Averaging over multiple events
- Computing multi-particle correlations
- Extracting integrated observables
- Generating plots and comparisons

## References
- **Source files**: `src/Analysis.cpp`, `src/single_particleSpectra.cpp`, `src/particleSamples.cpp`
- **Configuration**: `parameters.dat` for analysis settings
- **Particle codes**: See PDG (Particle Data Group) standard codes