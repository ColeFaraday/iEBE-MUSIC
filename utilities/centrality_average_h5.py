#!/usr/bin/env python3
"""
Centrality-average arbitrary HDF5 files.
Given an input HDF5 file with event groups (e.g., spvn_event_1, spvn_event_2, ...),
and a centrality mapping JSON file, outputs a new HDF5 file with centrality-averaged datasets.
Each centrality class (e.g., "C0-5") will contain averaged datasets for all keys found in the events.
Usage:
    python centrality_average_h5.py input_events.h5 centrality_map.json output.h5 [mapping_key]
"""
import sys
import json
import h5py
import numpy as np
import os

def load_centrality_mapping(json_path, mapping_key=None):
    with open(json_path, 'r') as f:
        mapping = json.load(f)
    if mapping_key is None:
        mapping_key = list(mapping['mappings'].keys())[0]
    return mapping['mappings'][mapping_key], mapping_key

def load_all_centrality_mappings(json_path):
    with open(json_path, 'r') as f:
        mapping = json.load(f)
    return mapping['mappings']

def average_datasets(event_names, hf):
    # Find all dataset names in all events
    dataset_names = set()
    for event_name in event_names:
        if event_name in hf:
            group = hf[event_name]
            for ds_name in group.keys():
                dataset_names.add(ds_name)
    avg_data = {}
    for ds_name in dataset_names:
        data_list = []
        for event_name in event_names:
            if event_name in hf:
                group = hf[event_name]
                if ds_name in group:
                    data = np.array(group[ds_name][...])
                    data = np.nan_to_num(data)
                    data_list.append(data)
        if not data_list:
            continue
        # Average over events
        try:
            stacked = np.stack(data_list)
            avg = np.mean(stacked, axis=0)
        except Exception:
            # Scalar case or shape mismatch
            avg = np.mean(data_list)
        avg_data[ds_name] = avg
    return avg_data

def main():
    if len(sys.argv) < 4:
        print("Usage: python centrality_average_h5.py input_events.h5 centrality_map.json output.h5 [mapping_key]")
        sys.exit(1)
    input_h5 = sys.argv[1]
    centrality_json = sys.argv[2]
    output_h5 = sys.argv[3]
    mapping_key = sys.argv[4] if len(sys.argv) > 4 else None

    if os.path.exists(output_h5):
        resp = input(f"Output file '{output_h5}' exists. Overwrite? (y/n): ").strip().lower()
        if resp == 'y':
            os.remove(output_h5)
            print(f"Deleted '{output_h5}'. Proceeding...")
        else:
            print("Aborted.")
            sys.exit(0)

    with h5py.File(input_h5, 'r') as hf, h5py.File(output_h5, 'w') as out_h5:
        if mapping_key is not None:
            centrality_map, used_mapping_key = load_centrality_mapping(centrality_json, mapping_key)
            print(f"Using centrality mapping: {used_mapping_key}")
            mapping_group = out_h5.create_group(used_mapping_key)
            centrality_maps = {used_mapping_key: centrality_map}
        else:
            centrality_maps = load_all_centrality_mappings(centrality_json)
            print(f"Using all centrality mappings: {list(centrality_maps.keys())}")
        for used_mapping_key, centrality_map in centrality_maps.items():
            mapping_group = out_h5.create_group(used_mapping_key)
            for cent_class, event_dict in centrality_map.items():
                print(f"Processing centrality class: {cent_class} (mapping: {used_mapping_key})")
                class_group = mapping_group.create_group(cent_class)
                event_names = list(event_dict.keys())
                avg_data = average_datasets(event_names, hf)
                for ds_name, avg in avg_data.items():
                    # Only use compression for non-scalar datasets
                    if np.isscalar(avg) or (hasattr(avg, 'shape') and avg.shape == ()): 
                        class_group.create_dataset(ds_name, data=avg)
                    else:
                        class_group.create_dataset(ds_name, data=avg, compression="gzip", compression_opts=9)
    print("Done.")

if __name__ == "__main__":
    main()
