#!/usr/bin/env python3

import h5py
import sys
import numpy as np

kinematicCutsDict = {
    "ALICE": {"pTmin": 0.2, "pTmax": 3.0, "etamin": -0.8, "etamax": 0.8},
    "CMS": {"pTmin": 0.3, "pTmax": 3.0, "etamin": -0.5, "etamax": 0.5},
    "ATLAS": {"pTmin": 0.5, "pTmax": 3.0, "etamin": -0.5, "etamax": 0.5},
}

def help_message():
    print(f"Usage: {sys.argv[0]} input_file.h5 output_file.txt")
    sys.exit(1)

def calculate_yield(pT_low, pT_high, data):
    npT = 50
    pT_array = np.linspace(pT_low, pT_high, npT)
    dpT = pT_array[1] - pT_array[0]
    pT_event = data[:, 0]
    dN_event = data[:, 1]
    dN_interp = np.exp(np.interp(pT_array, pT_event, np.log(dN_event + 1e-30)))
    N = 2. * np.pi * np.sum(dN_interp * pT_array) * dpT
    return N

if len(sys.argv) != 3:
    help_message()

input_file = sys.argv[1]
output_file = sys.argv[2]

try:
    h5_data = h5py.File(input_file, "r")
except OSError:
    print(f"Error: Could not open file {input_file}")
    sys.exit(1)

event_ids = list(h5_data.keys())

with open(output_file, "w") as fout:
    header = "EventID  Ncoll  Npart  Ntemp  " + "  ".join([f"Nch_{exp}" for exp in kinematicCutsDict]) + "\n"
    fout.write(header)

    for event_id in event_ids:
        group = h5_data[event_id]
        id = int(re.search(r'\d+', event_id).group())

        try:
            ncoll_data = np.array(group[f"NcollList{id}.dat"])
            npart_data = np.array(group[f"NpartList{id}.dat"])
        except KeyError as e:
            print(f"Warning: missing data for event {id}: {e}")
            continue

        Ncoll = len(ncoll_data)
        Npart = np.count_nonzero(npart_data[:, 2] == 1)
        Ntemp = np.count_nonzero(npart_data[:, 3] == 1) # not sure which of these is really npart

        Nch_list = []
        for exp, cuts in kinematicCutsDict.items():
            vn_key = f"particle_9999_vndata_diff_eta_{cuts['etamin']}_{cuts['etamax']}.dat"
            try:
                vn_data = np.nan_to_num(group[vn_key])
                Nch = calculate_yield(cuts["pTmin"], cuts["pTmax"], vn_data)
            except KeyError:
                Nch = -1.0  # use -1.0 to flag missing data
            Nch_list.append(Nch)

        row = f"{id:<7d}  {Ncoll:<6d}  {Npart:<6d}  {Ntemp:<6d}  " + "  ".join(f"{nch:.4e}" for nch in Nch_list) + "\n"
        fout.write(row)

h5_data.close()