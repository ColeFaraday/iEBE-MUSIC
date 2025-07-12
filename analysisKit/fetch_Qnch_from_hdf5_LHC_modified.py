#!/usr/bin/env python3

import h5py
import sys
import pickle
import numpy as np

NORDER = 9
kinematicCutsDict = {
    "ALICE_eta_-0p4_0p4": {"pTmin": 0.2, "pTmax": 3,
                           "etamin": -0.4, "etamax": 0.4},
    "ALICE_eta_-0p8_-0p4": {"pTmin": 0.2, "pTmax": 3,
                            "etamin": -0.8, "etamax": -0.4},
    "ALICE_eta_0p4_0p8": {"pTmin": 0.2, "pTmax": 3,
                          "etamin": 0.4, "etamax": 0.8},
    "ALICE_eta_-0p8_0p8": {"pTmin": 0.2, "pTmax": 3,
                           "etamin": -0.8, "etamax": 0.8},
}

pidList = [('pi+', '211'), ('pi-', '-211'), ('K+', '321'), ('K-', '-321'),
           ('p', '2212'), ('pbar', '-2212')]

def help_message():
    print("Usage: {0} database_file".format(sys.argv[0]))
    exit(0)

def calcualte_yield_and_meanpT(pT_low, pT_high, data):
    """
        this function calculates the pT-integrated particle yield and mean pT
        given pT range (pT_low, pT_high) for every event in the data
    """
    npT = 50
    pT_inte_array = np.linspace(pT_low, pT_high, npT)
    dpT = pT_inte_array[1] - pT_inte_array[0]
    dN_event = data[:, 1]
    pT_event = data[:, 0]
    dN_interp = np.exp(np.interp(pT_inte_array, pT_event,
                                 np.log(dN_event+1e-30)))
    N = 2.*np.pi*np.sum(dN_interp*pT_inte_array)*dpT
    meanpT = (np.sum(dN_interp*pT_inte_array**2.)
              / np.sum(dN_interp*pT_inte_array))
    res_array = [N, meanpT]
    return res_array

def get_eta_range_filename(etamin, etamax):
    """Convert eta range to filename format used in the database"""
    if etamin == -0.4 and etamax == 0.4:
        return "particle_9999_vndata_diff_eta_-0.5_0.5.dat"
    elif etamin == -0.8 and etamax == -0.4:
        return "particle_9999_vndata_diff_eta_-1_-0.5.dat"
    elif etamin == 0.4 and etamax == 0.8:
        return "particle_9999_vndata_diff_eta_0.5_1.dat"
    elif etamin == -0.8 and etamax == 0.8:
        return "particle_9999_vndata_diff_eta_-0.8_0.8.dat"
    else:
        # Fallback to closest available range
        return "particle_9999_vndata_diff_eta_-0.5_0.5.dat"

try:
    database_file = str(sys.argv[1])
except IndexError:
    help_message()

h5_data = h5py.File(database_file, "r")
eventList = list(h5_data.keys())

outdata = {}

for ievent, event_i in enumerate(eventList):
    if ievent % 100 == 0:
        print("fetching event: {0} from the database {1} ...".format(
            event_i, database_file))
    eventGroup = h5_data.get(event_i)
    outdata[event_i] = {}
    
    # Get charged particle data
    vn_filename = "particle_9999_vndata_diff_eta_-0.5_0.5.dat"
    vn_data = np.nan_to_num(eventGroup.get(vn_filename))
    dN_vector = calcualte_yield_and_meanpT(0.0, 3.0, vn_data)
    outdata[event_i]["Nch"] = dN_vector[0]
    outdata[event_i]["mean_pT_ch"] = dN_vector[1]
    
    # Get eccentricity data
    ecc_filename = "eccentricities_evo_ed_tau_0.4.dat"
    if ecc_filename in eventGroup:
        eccn_data = np.nan_to_num(eventGroup.get(ecc_filename))
        outdata[event_i]["ecc_n"] = eccn_data[2:]
    else:
        outdata[event_i]["ecc_n"] = np.zeros(8)  # Default if not available
    
    # Get gluon estimators if available
    fileList = list(eventGroup.keys())
    for filename in fileList:
        if "NgluonEstimators" in filename:
            data = np.nan_to_num(eventGroup.get(filename))
            outdata[event_i]['NgluonEst'] = data[0]
            break
    
    # Get identified particle data
    for pidName, pid in pidList:
        vn_filename = "particle_{}_vndata_diff_y_-0.5_0.5.dat".format(pid)
        if vn_filename in eventGroup:
            vn_data = np.nan_to_num(eventGroup.get(vn_filename))
            dN_vector = calcualte_yield_and_meanpT(0.0, 3.0, vn_data)
            outdata[event_i]["{}_dNdy_meanpT".format(pidName)] = dN_vector
        else:
            # If not available, use zeros
            outdata[event_i]["{}_dNdy_meanpT".format(pidName)] = [0.0, 0.0]
    
    # Get flow vectors for different eta ranges
    for exp_i, expName in enumerate(kinematicCutsDict):
        pTetacut = kinematicCutsDict[expName]
        eta_filename = get_eta_range_filename(pTetacut['etamin'], pTetacut['etamax'])
        
        if eta_filename in eventGroup:
            vn_data = np.nan_to_num(eventGroup.get(eta_filename))
            # Create a simple flow vector array
            # Format: [N, meanpT, Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, totalN]
            N = vn_data[0, 1] if len(vn_data) > 0 else 0.0
            meanpT = vn_data[0, 0] if len(vn_data) > 0 else 0.0
            totalN = vn_data[-1, -1] if len(vn_data) > 0 else 0.0
            
            # Extract flow vectors (assuming they're in columns 2,3,4,5,6,7,8,9,10)
            flow_vectors = []
            for iorder in range(1, NORDER+1):
                if len(vn_data) > 0 and 2*iorder < vn_data.shape[1]:
                    real_part = vn_data[0, 2*iorder] if 2*iorder < vn_data.shape[1] else 0.0
                    imag_part = vn_data[0, 2*iorder+1] if 2*iorder+1 < vn_data.shape[1] else 0.0
                    flow_vectors.append(real_part + 1j*imag_part)
                else:
                    flow_vectors.append(0.0 + 0.0j)
            
            Vn_vector = [N, meanpT] + flow_vectors + [totalN]
            outdata[event_i][expName] = np.array(Vn_vector)
        else:
            # If file not found, create default array
            default_vector = [0.0, 0.0] + [0.0+0.0j]*NORDER + [0.0]
            outdata[event_i][expName] = np.array(default_vector)

print("nev = {}".format(len(eventList)))
with open('QnVectors.pickle', 'wb') as pf:
    pickle.dump(outdata, pf)

h5_data.close()
print("Successfully created QnVectors.pickle") 