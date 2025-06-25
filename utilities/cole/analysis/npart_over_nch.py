import h5py
import sys
import numpy as np
import re

kinematicCutsDict = {
    "ALICE": {"pTmin": 0.2, "pTmax": 3.0, "etamin": -0.8, "etamax": 0.8},
    "CMS": {"pTmin": 0.3, "pTmax": 3.0, "etamin": -0.5, "etamax": 0.5},
    "ATLAS": {"pTmin": 0.5, "pTmax": 3.0, "etamin": -0.5, "etamax": 0.5},
}

centrality_cut_list = [0., 5., 10., 20., 30., 40., 50., 60., 70., 80., 90., 100.]

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

# Step 1: compute dN/dy for centrality sorting
dN_dy_mb = []
valid_event_ids = []

for event_id in event_ids:
    group = h5_data[event_id]
    try:
        vn_data = group["particle_9999_vndata_eta_-0.5_0.5.dat"]
        vn_data = np.nan_to_num(vn_data)
        dN_dy_mb.append(-vn_data[0, 1])  # negative sign to match original script
        valid_event_ids.append(event_id)
    except KeyError:
        continue

dN_dy_mb = np.array(dN_dy_mb)
sorted_indices = np.argsort(dN_dy_mb)[::-1]  # descending order
sorted_dN_dy = dN_dy_mb[sorted_indices]
sorted_event_ids = [valid_event_ids[i] for i in sorted_indices]

# Step 2: assign centrality class to each event
centrality_dict = {}
N_total = len(sorted_event_ids)
for i, event_id in enumerate(sorted_event_ids):
    frac = i / N_total
    for j in range(len(centrality_cut_list) - 1):
        cent_min = centrality_cut_list[j] / 100.
        cent_max = centrality_cut_list[j + 1] / 100.
        if cent_min <= frac < cent_max or (j == len(centrality_cut_list) - 2 and frac <= cent_max):
            centrality_dict[event_id] = (cent_min, cent_max)
            break

with open(output_file, "w") as fout:
    header = "EventID  centMin  centMax  Ncoll  Npart  " + "  ".join([f"Nch_{exp}" for exp in kinematicCutsDict]) + "\n"
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

        if event_id not in centrality_dict:
            continue

        centMin, centMax = centrality_dict[event_id]
        Ncoll = len(ncoll_data)
        Npart = np.count_nonzero(npart_data[:, 3] == 1)

        Nch_list = []
        for exp, cuts in kinematicCutsDict.items():
            vn_key = f"particle_9999_vndata_diff_eta_{cuts['etamin']}_{cuts['etamax']}.dat"
            try:
                vn_data = np.nan_to_num(group[vn_key])
                Nch = calculate_yield(cuts["pTmin"], cuts["pTmax"], vn_data)
            except KeyError:
                Nch = -1.0
            Nch_list.append(Nch)

        row = f"{id:<7d}  {centMin:<7.2f}  {centMax:<7.2f}  {Ncoll:<6d}  {Npart:<6d}  " + "  ".join(f"{nch:.4e}" for nch in Nch_list) + "\n"
        fout.write(row)

h5_data.close()