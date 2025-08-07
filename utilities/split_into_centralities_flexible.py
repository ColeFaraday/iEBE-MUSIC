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

# Flexible centrality categorization configurations
centrality_configs = {
    "central_dNdy": {
        "name": "Default dN/dy",
        "file": "particle_9999_vndata_eta_-0.5_0.5.dat",
        "function": lambda data: -data[0, 1],  # dN/dy from row 0, column 1
        "description": "Charged particle multiplicity in |eta| < 0.5"
    },
    # "central_ET": {
    #     "name": "Central ET",
    #     "file": "particle_9999_vndata_eta_-0.5_0.5.dat",
    #     "function": lambda data: -data[0, 1] * data[0, 2],  # dN/dy * <pT>
    #     "description": "Mean transverse energy in |eta| < 0.5"
    # },
    # "ATLAS_FCal": {
    #     "name": "ATLAS FCal-like",
    #     "file": "particle_9999_vndata_eta_3.1_4.9.dat",  # Forward region
    #     "function": lambda data: -data[0, 1] * data[0, 2],  # ET in forward region
    #     "description": "Forward calorimeter ET in 3.1 < eta < 4.9 (ATLAS FCal-like)"
    # },
    "ALICE_V0A": {
        "name": "ALICE V0A-like",
        "file": "particle_9999_vndata_eta_2.8_5.1.dat",  # V0A coverage
        "function": lambda data: -data[0, 1],
        "description": "ALICE V0A-like detector coverage (2.8 < eta < 5.1)"
    }#,
    # "ALICE_V0C": {
    #     "name": "ALICE V0C-like", 
    #     "file": "particle_9999_vndata_eta_-3.7_-1.7.dat",  # V0C coverage
    #     "function": lambda data: -data[0, 1],
    #     "description": "ALICE V0C-like detector coverage (-3.7 < eta < -1.7)"
    # },
    # "ALICE_V0_combined": {
    #     "name": "ALICE V0 Combined",
    #     "file": ["particle_9999_vndata_eta_2.8_5.1.dat", "particle_9999_vndata_eta_-3.7_-1.7.dat"],
    #     "function": lambda data_list: sum(-d[0, 1] for d in data_list),  # Sum V0A + V0C
    #     "description": "Combined ALICE V0A + V0C multiplicity"
    # },
    # "ALICE_FTOA": {
    #     "name": "ALICE FTOA-like",
    #     "file": "particle_9999_vndata_eta_3.1_4.9.dat",  # FTOA coverage
    #     "function": lambda data: -data[0, 1],
    #     "description": "ALICE FTOA-like detector coverage (3.1 < eta < 4.9)"
    # },
    # "ALICE_FTOC": {
    #     "name": "ALICE FTOC-like",
    #     "file": "particle_9999_vndata_eta_-3.9_-3.1.dat",  # FTOC coverage  
    #     "function": lambda data: -data[0, 1],
    #     "description": "ALICE FTOC-like detector coverage (-3.9 < eta < -3.1)"
    # },
    # "wide_eta": {
    #     "name": "Wide Pseudorapidity",
    #     "file": "particle_9999_vndata_eta_-2.5_2.5.dat",
    #     "function": lambda data: -data[0, 1],
    #     "description": "Wide pseudorapidity acceptance |eta| < 2.5"
    # },
    # "Ncoll": {
    #     "name": "Number of Collisions",
    #     "file": "NcollList500.dat",
    #     "function": lambda data: data[0] if len(data.shape) == 1 else data[0, 0],
    #     "description": "Number of binary nucleon-nucleon collisions"
    # },
    # "Npart": {
    #     "name": "Number of Participants", 
    #     "file": "NpartList500.dat",
    #     "function": lambda data: data[0] if len(data.shape) == 1 else data[0, 0],
    #     "description": "Number of participating nucleons"
    # }
}

centrality_cut_list = [0., 5., 10., 20., 30., 40., 50.,
                       60., 70., 80., 90., 100.]

def extract_centrality_variable(event_group, config):
    """Extract the centrality variable from event data using the specified config"""
    try:
        file_spec = config["file"]
        
        # Handle single file case
        if isinstance(file_spec, str):
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

def save_centrality_mapping(data_path, config_name, event_centrality_map):
    """Save the centrality mapping to a JSON file"""
    output_file = path.join(data_path, f"centrality_mapping_{config_name}.json")
    with open(output_file, 'w') as f:
        json.dump(event_centrality_map, f, indent=2)
    print(f"Centrality mapping saved to: {output_file}")

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
    sorted_indices = argsort(-centrality_values)
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
                "centrality_value": -float(centrality_values_sorted[valid_events_sorted.index(event_name)])
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
for event_name, event_info in physical_mapping.items():
    bin_name = event_info["centrality_bin"]
    if bin_name not in events_by_bin:
        events_by_bin[bin_name] = []
    events_by_bin[bin_name].append(event_name)

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