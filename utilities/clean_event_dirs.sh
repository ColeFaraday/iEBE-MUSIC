#!/usr/bin/env bash

# Usage: ./clean_event_dirs.sh /path/to/HYDRO_RESULTS/results
# This script cleans up each event directory by:
# 1. Moving results/TempasTauvsX.dat up one level
# 2. Deleting the results folder
# 3. Deleting run.log in the event directory

evfolder=${1%"/"}

for iev in $(ls --color=none "${evfolder}")
do
    eventdir="${evfolder}/$iev"
    # Only process directories
    if [ -d "$eventdir" ]; then
        # Move TempasTauvsX.dat up if it exists
        if [ -f "${eventdir}/results/TempasTauvsX.dat" ]; then
            mv "${eventdir}/results/TempasTauvsX.dat" "${eventdir}/"
        fi
        # Remove results directory if it exists
        if [ -d "${eventdir}/results" ]; then
            rm -r "${eventdir}/results"
        fi
        # Remove run.log if it exists
        if [ -f "${eventdir}/run.log" ]; then
            rm "${eventdir}/run.log"
        fi
    fi
done 