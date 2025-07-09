#!/usr/bin/env bash

evfolder=${1%"/"}
database=${2%"/"}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for iev in $(ls --color=none "${evfolder}")
do
    eventid=$(echo "$iev" | sed 's/hydro_results_//' | sed 's$/$$')
    
    python3 "${SCRIPT_DIR}/fetch_Qnvectors_from_hdf5_database.py" "$database" "$eventid"
    
    mv "Qn_vectors_${eventid}.dat" "${evfolder}/$iev/"
    mv "particle_yield_and_meanpT_${eventid}.dat" "${evfolder}/$iev/"
    mv Ncoll* "${evfolder}/$iev/"
done