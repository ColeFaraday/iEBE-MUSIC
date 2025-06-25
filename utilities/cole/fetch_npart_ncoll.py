#!/usr/bin/env python3

import h5py
import sys
import os
import numpy as np
from glob import glob
import re

def help_message():
    print(f"Usage: {sys.argv[0]} database_file")
    sys.exit(1)

def find_output_folder(event_id):
    """
    Look for the output folder corresponding to event_id
    inside HYDRO_RESULTS/, either directly or in subfolders (for centrality binning)
    """
    pattern = f"HYDRO_RESULTS/*/hydro_results_{event_id}"
    matches = glob(pattern)
    if matches:
        return matches[0]
    
    alt_pattern = f"HYDRO_RESULTS/hydro_results_{event_id}"
    if os.path.isdir(alt_pattern):
        return alt_pattern
    
    return None

if len(sys.argv) < 2:
    help_message()

database_file = sys.argv[1]

if not os.path.isfile(database_file):
    print(f"Error: file {database_file} not found")
    sys.exit(1)

with h5py.File(database_file, "r") as h5_data:
    for event_id in h5_data.keys():
        id = int(re.search(r'\d+', event_id).group())
        group = h5_data[event_id]
        try:
            ncoll_data = np.array(group[f"NcollList{id}.dat"])
            npart_data = np.array(group[f"NpartList{id}.dat"])
        except KeyError as e:
            print(f"Warning: missing data for event {id}: {e}")
            continue

        output_dir = find_output_folder(id)
        if output_dir is None:
            print(f"Warning: could not find output folder for event {id}")
            continue

        ncoll_outfile = os.path.join(output_dir, f"NcollList{id}.txt")
        npart_outfile = os.path.join(output_dir, f"NpartList{id}.txt")

        np.savetxt(ncoll_outfile, ncoll_data, fmt="%.6e")
        np.savetxt(npart_outfile, npart_data, fmt="%.6e")

        print(f"Wrote raw Ncoll and Npart for event {id} to {output_dir}")