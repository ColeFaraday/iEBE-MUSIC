#!/usr/bin/env python3
"""
    Collects per-event summary info from a main HDF5 database and outputs to a new HDF5 file.
    Info collected per event: v_n, meanpT, Ncoll, Npart, total particle multiplicity.
    Usage:
        python collect_event_summary_to_h5.py input_database.h5 output_summary.h5
"""
import sys
import h5py
import numpy as np
import fnmatch

def nan_to_num(data):
    return np.nan_to_num(data)

def get_vn_meanpT_mult(event_group):
    # Try to get vn, meanpT, multiplicity from typical file
    vn_file = 'particle_9999_vndata_diff_eta_-0.5_0.5.dat'
    data = event_group.get(vn_file)
    if data is None:
        return None, None, None
    data = nan_to_num(data)
    # v_n: take first event row, columns 2,3,... (real/imag pairs)
    vn = []
    for i in range(1, min(10, (data.shape[1]-1)//2)):
        vn_real = data[0, 2*i]
        vn_imag = data[0, 2*i+1]
        vn.append(complex(vn_real, vn_imag))
    # meanpT: column 0 is pT, column 1 is dN/dpT, so meanpT = sum(pT*dN)/sum(dN)
    pT = data[:,0]
    dN = data[:,1]
    meanpT = np.sum(pT*dN)/np.sum(dN) if np.sum(dN) > 0 else 0.0
    # total multiplicity: sum dN
    multiplicity = float(np.sum(dN))
    return vn, meanpT, multiplicity

def get_ncoll_npart(event_group):
    # Ncoll
    ncoll = None
    for fname in event_group.keys():
        if fnmatch.fnmatch(fname, 'NcollList*.dat'):
            data = event_group.get(fname)
            if data is not None:
                ncoll = int(data.shape[0])
                break
    # Npart
    npart = None
    for fname in event_group.keys():
        if fnmatch.fnmatch(fname, 'NpartList*.dat'):
            data = event_group.get(fname)
            if data is not None:
                # Usually column 3 is 'collided' flag
                npart = int(np.sum(data[:,3]))
                break
    return ncoll, npart

def main():
    if len(sys.argv) < 3:
        print("Usage: python collect_event_summary_to_h5.py input_database.h5 output_summary.h5")
        sys.exit(1)
    input_h5 = sys.argv[1]
    output_h5 = sys.argv[2]
    hf_in = h5py.File(input_h5, 'r')
    hf_out = h5py.File(output_h5, 'w')
    event_list = list(hf_in.keys())
    for event_name in event_list:
        event_group = hf_in.get(event_name)
        vn, meanpT, multiplicity = get_vn_meanpT_mult(event_group)
        ncoll, npart = get_ncoll_npart(event_group)
        g = hf_out.create_group(event_name)
        if vn is not None:
            g.create_dataset('vn', data=np.array(vn, dtype='complex128'))
        if meanpT is not None:
            g.create_dataset('meanpT', data=meanpT)
        if multiplicity is not None:
            g.create_dataset('multiplicity', data=multiplicity)
        if ncoll is not None:
            g.create_dataset('Ncoll', data=ncoll)
        if npart is not None:
            g.create_dataset('Npart', data=npart)
    hf_in.close()
    hf_out.close()
    print(f"Wrote summary for {len(event_list)} events to {output_h5}")

if __name__ == "__main__":
    main()
