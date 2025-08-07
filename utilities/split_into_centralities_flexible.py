#! /usr/bin/env python
"""
     This script performs read in a minimum bias database and outputs
     the event id for different centrality bins with flexible centrality definitions. Based on `split_into_centralities.py`.
"""

from sys import argv, exit
from os import path, mkdir
from glob import glob
from numpy import *
import h5py
import shutil
import json

min = __builtins__.min # fix for pollution of global namespace with numpy

# Available files
#
#'NcollList0.dat', 'NgluonEstimators0.dat', 'NpartList0.dat', 'eccentricities_evo_ed_tau_0.4.dat', 'eccentricities_evo_ed_tau_0.45.dat', 'eccentricities_evo_ed_tau_0.55.dat', 'eccentricities_evo_ed_tau_0.65.dat', 'eccentricities_evo_eta_-0.5_0.5.dat', 'eccentricities_evo_nB_tau_0.4.dat', 'eccentricities_evo_nB_tau_0.45.dat', 'eccentricities_evo_nB_tau_0.55.dat', 'eccentricities_evo_nB_tau_0.65.dat', 'inverse_Reynolds_number_eta_-0.5_0.5.dat', 'meanpT_estimators_eta_-0.5_0.5.dat', 'meanpT_estimators_tau_0.4.dat', 'meanpT_estimators_tau_0.45.dat', 'meanpT_estimators_tau_0.55.dat', 'meanpT_estimators_tau_0.65.dat', 'momentum_anisotropy_eta_-0.5_0.5.dat', 'momentum_anisotropy_tau_0.4.dat', 'momentum_anisotropy_tau_0.45.dat', 'momentum_anisotropy_tau_0.55.dat', 'momentum_anisotropy_tau_0.65.dat', 'particle_-211_dNdy_pT_0.2_3.dat', 'particle_-211_vndata_diff_y_-0.5_0.5.dat', 'particle_-211_vndata_y_-0.5_0.5.dat', 'particle_-2212_dNdeta_pT_0.2_3.dat', 'particle_-2212_dNdy_pT_0.2_3.dat', 'particle_-2212_vndata_diff_eta_-0.5_0.5.dat', 'particle_-2212_vndata_diff_y_-0.5_0.5.dat', 'particle_-2212_vndata_eta_-0.5_0.5.dat', 'particle_-2212_vndata_y_-0.5_0.5.dat', 'particle_-3122_dNdy_pT_0.2_3.dat', 'particle_-3122_vndata_diff_y_-0.5_0.5.dat', 'particle_-3122_vndata_y_-0.5_0.5.dat', 'particle_-321_dNdy_pT_0.2_3.dat', 'particle_-321_vndata_diff_y_-0.5_0.5.dat', 'particle_-321_vndata_y_-0.5_0.5.dat', 'particle_-3312_dNdy_pT_0.2_3.dat', 'particle_-3312_vndata_diff_y_-0.5_0.5.dat', 'particle_-3312_vndata_y_-0.5_0.5.dat', 'particle_-3334_dNdy_pT_0.2_3.dat', 'particle_-3334_vndata_diff_y_-0.5_0.5.dat', 'particle_-3334_vndata_y_-0.5_0.5.dat', 'particle_211_dNdy_pT_0.2_3.dat', 'particle_211_vndata_diff_y_-0.5_0.5.dat', 'particle_211_vndata_y_-0.5_0.5.dat', 'particle_2212_dNdeta_pT_0.2_3.dat', 'particle_2212_dNdy_pT_0.2_3.dat', 'particle_2212_vndata_diff_eta_-0.5_0.5.dat', 'particle_2212_vndata_diff_y_-0.5_0.5.dat', 'particle_2212_vndata_eta_-0.5_0.5.dat', 'particle_2212_vndata_y_-0.5_0.5.dat', 'particle_3122_dNdy_pT_0.2_3.dat', 'particle_3122_vndata_diff_y_-0.5_0.5.dat', 'particle_3122_vndata_y_-0.5_0.5.dat', 'particle_321_dNdy_pT_0.2_3.dat', 'particle_321_vndata_diff_y_-0.5_0.5.dat', 'particle_321_vndata_y_-0.5_0.5.dat', 'particle_3312_dNdy_pT_0.2_3.dat', 'particle_3312_vndata_diff_y_-0.5_0.5.dat', 'particle_3312_vndata_y_-0.5_0.5.dat', 'particle_3334_dNdy_pT_0.2_3.dat', 'particle_3334_vndata_diff_y_-0.5_0.5.dat', 'particle_3334_vndata_y_-0.5_0.5.dat', 'particle_333_dNdy_pT_0.2_3.dat', 'particle_333_vndata_diff_y_-0.5_0.5.dat', 'particle_333_vndata_y_-0.5_0.5.dat', 'particle_9999_Cmnk_eta_-1_1.dat', 'particle_9999_Cmnk_eta_-2_2.dat', 'particle_9999_Cmnk_os_eta_-1_1.dat', 'particle_9999_Cmnk_os_eta_-2_2.dat', 'particle_9999_Cmnk_ss_eta_-1_1.dat', 'particle_9999_Cmnk_ss_eta_-2_2.dat', 'particle_9999_Cn2_os_eta_-1_1.dat', 'particle_9999_Cn2_os_eta_-2_2.dat', 'particle_9999_Cn2_ss_eta_-1_1.dat', 'particle_9999_Cn2_ss_eta_-2_2.dat', 'particle_9999_Cn4_eta_-1_1.dat', 'particle_9999_Cn4_eta_-2_2.dat', 'particle_9999_SCmn_eta_-1_1.dat', 'particle_9999_SCmn_eta_-2_2.dat', 'particle_9999_dNdeta_pT_0.15_2.dat', 'particle_9999_dNdeta_pT_0.2_2.dat', 'particle_9999_dNdeta_pT_0.2_3.dat', 'particle_9999_dNdeta_pT_0.3_3.dat', 'particle_9999_dNdeta_pT_0.4_2.dat', 'particle_9999_dNdeta_pT_0.4_4.dat', 'particle_9999_dNdeta_pT_0.5_5.dat', 'particle_9999_vn2_eta_-1_1.dat', 'particle_9999_vn2_eta_-2_2.dat', 'particle_9999_vndata_diff_eta_-0.5_0.5.dat', 'particle_9999_vndata_diff_eta_-0.8_0.8.dat', 'particle_9999_vndata_diff_eta_-1_-0.5.dat', 'particle_9999_vndata_diff_eta_-1_1.dat', 'particle_9999_vndata_diff_eta_-2.4_2.4.dat', 'particle_9999_vndata_diff_eta_-2.5_-0.5.dat', 'particle_9999_vndata_diff_eta_-2.5_2.5.dat', 'particle_9999_vndata_diff_eta_-2_2.dat', 'particle_9999_vndata_diff_eta_-3.7_-1.7.dat', 'particle_9999_vndata_diff_eta_-3.9_-3.1.dat', 'particle_9999_vndata_diff_eta_-4.9_-3.1.dat', 'particle_9999_vndata_diff_eta_-5.1_-2.8.dat', 'particle_9999_vndata_diff_eta_0.5_1.dat', 'particle_9999_vndata_diff_eta_0.5_2.5.dat', 'particle_9999_vndata_diff_eta_1.7_3.7.dat', 'particle_9999_vndata_diff_eta_2.8_5.1.dat', 'particle_9999_vndata_diff_eta_3.1_3.9.dat', 'particle_9999_vndata_diff_eta_3.1_4.9.dat', 'particle_9999_vndata_eta_-0.5_0.5.dat', 'particle_9999_vndata_eta_-0.8_0.8.dat', 'particle_9999_vndata_eta_-1_-0.5.dat', 'particle_9999_vndata_eta_-1_1.dat', 'particle_9999_vndata_eta_-2.4_2.4.dat', 'particle_9999_vndata_eta_-2.5_-0.5.dat', 'particle_9999_vndata_eta_-2.5_2.5.dat', 'particle_9999_vndata_eta_-2_2.dat', 'particle_9999_vndata_eta_-3.7_-1.7.dat', 'particle_9999_vndata_eta_-3.9_-3.1.dat', 'particle_9999_vndata_eta_-4.9_-3.1.dat', 'particle_9999_vndata_eta_-5.1_-2.8.dat', 'particle_9999_vndata_eta_0.5_1.dat', 'particle_9999_vndata_eta_0.5_2.5.dat', 'particle_9999_vndata_eta_1.7_3.7.dat', 'particle_9999_vndata_eta_2.8_5.1.dat', 'particle_9999_vndata_eta_3.1_3.9.dat', 'particle_9999_vndata_eta_3.1_4.9.dat'

# Flexible centrality categorization configurations
centrality_configs = {
    "central_dNdy": {
        "name": "Default dN/dy",
        "file": "particle_9999_vndata_eta_-0.5_0.5.dat",
        "function": lambda data: data[0, 1],  # dN/dy from row 0, column 1
        "description": "Charged particle multiplicity in |eta| < 0.5"
    },
    "central_ET": {
        "name": "Central ET",
        "file": "particle_9999_dNdeta_pT_0.2_3.dat",  # Central region with pT cuts
        "function": lambda data: sum(data[(abs(data[:, 0]) <= 0.5), -2]),  # Integrate dET/deta over |eta| <= 0.5
        "description": "Central transverse energy in |eta| <= 0.5 and 0.2 <= pT <= 3 GeV"
    },
    "ATLAS_FCal": {
        "name": "ATLAS FCal-like",
        "file": "particle_9999_dNdeta_pT_0.3_3.dat",  # Forward region
        "function": lambda data: sum(data[(data[:, 0] >= 3.2) & (data[:, 0] <= 4.9), -2]),  # Integrate dET/deta over eta ∈ [3.2, 4.9]
        "description": "Forward calorimeter ET in 3.2 < eta < 4.9 and 0.3 <= pT <= 3 GeV (ATLAS centrality determination)"
    },
    "ALICE_V0A": {
        "name": "ALICE V0A-like",
        "file": "particle_9999_vndata_eta_2.8_5.1.dat",  # V0A coverage
        "function": lambda data: data[0, 1],
        "description": "ALICE V0A-like detector coverage (2.8 < eta < 5.1)"
    },
    "ALICE_V0C": {
        "name": "ALICE V0C-like", 
        "file": "particle_9999_vndata_eta_-3.7_-1.7.dat",  # V0C coverage
        "function": lambda data: data[0, 1],
        "description": "ALICE V0C-like detector coverage (-3.7 < eta < -1.7)"
    },
    "ALICE_V0_combined": {
        "name": "ALICE V0 Combined",
        "file": ["particle_9999_vndata_eta_2.8_5.1.dat", "particle_9999_vndata_eta_-3.7_-1.7.dat"],
        "function": lambda data_list: sum([d[0, 1] for d in data_list]),  # Sum V0A + V0C - use list instead of generator
        "description": "Combined ALICE V0A + V0C multiplicity"
    },
    "ALICE_FTOA": {
        "name": "ALICE FTOA-like",
        "file": "particle_9999_vndata_eta_3.1_4.9.dat",  # FTOA coverage
        "function": lambda data: data[0, 1],
        "description": "ALICE FTOA-like detector coverage (3.1 < eta < 4.9)"
    },
    "ALICE_FTOC": {
        "name": "ALICE FTOC-like",
        "file": "particle_9999_vndata_eta_-3.9_-3.1.dat",  # FTOC coverage  
        "function": lambda data: data[0, 1],
        "description": "ALICE FTOC-like detector coverage (-3.9 < eta < -3.1)"
    },
    "wide_eta": {
        "name": "Wide Pseudorapidity",
        "file": "particle_9999_vndata_eta_-2.5_2.5.dat",
        "function": lambda data: data[0, 1],
        "description": "Wide pseudorapidity acceptance |eta| < 2.5"
    },
    "Ncoll": {
        "name": "Number of Collisions",
        "file": "NcollList*.dat",
        "function": lambda data: data.shape[0],  # Count number of collision points
        "description": "Number of binary nucleon-nucleon collisions. Not used by any experiments (that I know of), but in PbPb is correlated with impact parameter, N_part etc."
    },
    "Npart": {
        "name": "Number of Participants", 
        "file": "NpartList*.dat",
        "function": lambda data: sum(data[:, 3]),  # Count nucleons with collided flag = 1
        "description": "Number of participating nucleons. Similar to ZDC-based centrality."
    }
}

centrality_cut_list = [0., 5., 10., 20., 30., 40., 50.,
                       60., 70., 80., 90., 100.]

def extract_centrality_variable(event_group, config):
    """Extract the centrality variable from event data using the specified config"""
    try:
        import fnmatch
        file_spec = config["file"]
        
        # Handle single file case (including wildcards)
        if isinstance(file_spec, str):
            # Check if it contains wildcards
            if '*' in file_spec or '?' in file_spec:
                # Find files matching the pattern
                available_files = list(event_group.keys())
                matching_files = [f for f in available_files if fnmatch.fnmatch(f, file_spec)]
                
                if not matching_files:
                    return None
                
                # Use the first matching file (assuming only one per event)
                file_name = matching_files[0]
                temp_data = event_group.get(file_name)
            else:
                # Regular file name
                temp_data = event_group.get(file_spec)
            
            if temp_data is None:
                return None
            temp_data = nan_to_num(temp_data)
            return config["function"](temp_data)
        
        # Handle multiple file case (e.g., V0 combined)
        elif isinstance(file_spec, list):
            data_list = []
            for file_name in file_spec:
                temp_data = event_group.get(file_name)
                if temp_data is None:
                    return None
                temp_data = nan_to_num(temp_data)
                data_list.append(temp_data)
            return config["function"](data_list)
        
        else:
            return None
            
    except Exception as e:
        print(f"Error extracting centrality variable: {e}")
        return None

try:
    data_path = path.abspath(argv[1])
    
    # Check if a specific centrality config is requested for PHYSICAL file organization
    if len(argv) > 2:
        physical_config_key = argv[2]
        if physical_config_key not in centrality_configs:
            print(f"Unknown centrality configuration: {physical_config_key}")
            print(f"Available configurations: {list(centrality_configs.keys())}")
            exit(1)
    else:
        physical_config_key = "central_dNdy"  # Default for physical organization
        print(f"Using default centrality configuration for physical organization: {physical_config_key}")
    
    physical_config = centrality_configs[physical_config_key]
    print(f"Physical organization using: {physical_config['name']}")
    print(f"Description: {physical_config['description']}")
    print(f"Using file: {physical_config['file']}")
    
    folder_name = data_path.split("/")[-1]
    data_filename = path.join(data_path, "{}.h5".format(folder_name))
    print("input data: {}".format(data_filename))
    
    hydro_surface_flag = False
    urqmd_flag = False
    hydro_folder = path.join(data_path, "HYDRO_RESULTS")
    urqmd_folder = path.join(data_path, "URQMD_RESULTS")
    
    if path.exists(hydro_folder):
        print("This run has hydro surface!")
        hydro_surface_flag = True
    if path.exists(urqmd_folder):
        print("This run has UrQMD outputs!")
        urqmd_flag = True
    if not hydro_surface_flag and not urqmd_flag: 
        print("No hydro or UrQMD outputs! Exiting.")
        exit(0)
        
except IndexError:
    print(f"Usage: {argv[0]} results_folder [physical_centrality_config]")
    print(f"Available centrality configurations: {list(centrality_configs.keys())}")
    exit(1)

hf = h5py.File(data_filename, "r")
event_list = list(hf.keys())

print(f"\nGenerating centrality mappings for ALL configurations...")
print(f"Physical file organization will use: {physical_config['name']}")
print("="*60)

# Generate mappings for ALL centrality configurations
all_centrality_mappings = {}

for config_key, config in centrality_configs.items():
    print(f"\nProcessing {config['name']}...")
    
    # Extract centrality variable for all events using this config
    centrality_values = []
    valid_events = []
    for ifolder, event_name in enumerate(event_list):
        event_group = hf.get(event_name)
        cent_value = extract_centrality_variable(event_group, config)
        if cent_value is not None:
            centrality_values.append(cent_value)
            valid_events.append(event_name)

    if len(centrality_values) == 0:
        print(f"  No valid events found for {config['name']}, skipping...")
        continue
        
    centrality_values = array(centrality_values)
    # Sort in descending order for centrality (highest values = most central)
    sorted_indices = argsort(-centrality_values)  # Remove the extra negative!
    centrality_values_sorted = centrality_values[sorted_indices]
    valid_events_sorted = [valid_events[i] for i in sorted_indices]

    print(f"  Valid events: {len(centrality_values_sorted)}")

    # Create centrality mapping for this configuration
    event_centrality_map = {}

    for icen in range(len(centrality_cut_list) - 1):
        if centrality_cut_list[icen+1] < centrality_cut_list[icen]: 
            continue

        centrality_bin_name = f"C{int(centrality_cut_list[icen])}-{int(centrality_cut_list[icen + 1])}"

        # Calculate centrality cuts
        cent_cut_high = centrality_values_sorted[
            int(len(centrality_values_sorted) * centrality_cut_list[icen] / 100.)
        ]
        
        if centrality_cut_list[icen+1] == 100.:
            cent_cut_low = centrality_values_sorted[-1]
        else:
            cent_cut_low = centrality_values_sorted[
                min(len(centrality_values_sorted) - 1,
                    int(len(centrality_values_sorted) * centrality_cut_list[icen+1] / 100.))
            ]

        # Select events for this centrality bin
        selected_events_list = []
        for i, event_name in enumerate(valid_events_sorted):
            cent_val = centrality_values_sorted[i]
            
            if centrality_cut_list[icen+1] == 100.:
                if cent_val >= cent_cut_low and cent_val <= cent_cut_high:
                    selected_events_list.append(event_name)
            else:
                if cent_val > cent_cut_low and cent_val <= cent_cut_high:
                    selected_events_list.append(event_name)

        # Initialize centrality bin in mapping if not exists
        if centrality_bin_name not in event_centrality_map:
            event_centrality_map[centrality_bin_name] = {}

        # Store events for this centrality bin
        for event_name in selected_events_list:
            event_centrality_map[centrality_bin_name][event_name] = {
                "centrality_range": [centrality_cut_list[icen]/100.0, centrality_cut_list[icen+1]/100.0],
                "centrality_value": float(centrality_values_sorted[valid_events_sorted.index(event_name)])  # Keep positive
            }

        nev = len(selected_events_list)
        print(f"    {centrality_cut_list[icen]}%-{centrality_cut_list[icen+1]}%: {nev} events")

    # Store this configuration's mapping
    all_centrality_mappings[config_key] = event_centrality_map

print("\n" + "="*60)
print("PHYSICAL FILE ORGANIZATION")
print("="*60)

# Now do the physical file organization using the specified configuration
physical_mapping = all_centrality_mappings[physical_config_key]

# Create physical directory structure
for icen in range(len(centrality_cut_list) - 1):
    if centrality_cut_list[icen+1] < centrality_cut_list[icen]: 
        continue

    centrality_bin_name = f"C{int(centrality_cut_list[icen])}-{int(centrality_cut_list[icen + 1])}"
    
    hydro_directory_path = path.join(hydro_folder, centrality_bin_name)
    urqmd_directory_path = path.join(urqmd_folder, centrality_bin_name)

    if hydro_surface_flag:
        if path.exists(hydro_directory_path):
            shutil.rmtree(hydro_directory_path)
        mkdir(hydro_directory_path)

    if urqmd_flag:
        if path.exists(urqmd_directory_path):
            shutil.rmtree(urqmd_directory_path)
        mkdir(urqmd_directory_path)

# Group events by centrality bin for physical organization
events_by_bin = {}
for bin_name, events_dict in physical_mapping.items():
    events_by_bin[bin_name] = list(events_dict.keys())

# Move files to physical centrality folders
for bin_name, selected_events_list in events_by_bin.items():
    hydro_directory_path = path.join(hydro_folder, bin_name)
    urqmd_directory_path = path.join(urqmd_folder, bin_name)
    
    print(f"\nMoving {len(selected_events_list)} events to {bin_name}...")
    
    for ev_i_name in selected_events_list:
        event_id = ev_i_name.split("_")[-1]
        if hydro_surface_flag:
            hydro_event_name = "hydro_results_{}".format(event_id)
            source_path = path.join(hydro_folder, hydro_event_name)
            if path.exists(source_path):
                shutil.move(source_path, hydro_directory_path)
        if urqmd_flag:
            urqmd_event_name = "particle_list_{}.gz".format(event_id)
            source_path = path.join(urqmd_folder, urqmd_event_name)
            if path.exists(source_path):
                shutil.move(source_path, urqmd_directory_path)

# Save centrality mappings - only the summary file
print("\n" + "="*60)
print("SAVING CENTRALITY MAPPINGS")
print("="*60)

# Save a summary file with all mappings
summary_file = path.join(data_path, "centrality_mappings_all.json")
with open(summary_file, 'w') as f:
    json.dump({
        "physical_organization": physical_config_key,
        "configurations": {key: config["description"] for key, config in centrality_configs.items()},
        "mappings": all_centrality_mappings
    }, f, indent=2)
print(f"Summary mapping file saved to: {summary_file}")

hf.close()
print(f"\nCentrality classification complete!")
print(f"Physical organization: {physical_config['name']}")
print(f"Generated mappings for {len(all_centrality_mappings)} configurations.")