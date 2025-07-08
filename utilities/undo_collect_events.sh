#!/usr/bin/env bash

usage="$0 fromFolder toFolder"

fromFolder=$1
toFolder=$2

if [ -z "$fromFolder" ]
then
    echo $usage
    exit 1
fi
if [ -z "$toFolder" ]
then
    echo $usage
    exit 1
fi

fromFolder=${fromFolder%"/"}
toFolder=${toFolder%"/"}

folderName=`echo $fromFolder | rev | cut -d "/" -f 1 | rev`
target_folder=${toFolder}/${folderName}
target_hydro_folder=${target_folder}/HYDRO_RESULTS
target_urqmd_folder=${target_folder}/URQMD_RESULTS
target_spvn_folder=${target_folder}/SPVN_RESULTS

event_folder_name="EVENT_RESULTS_"
hydro_folder_name="hydro_results_"
UrQMD_file_name="particle_list_"
spvn_folder_name="spvn_results_"

# Undo HYDRO_RESULTS
if [ -d "$target_hydro_folder" ]; then
    for hydro_dir in $target_hydro_folder/${hydro_folder_name}*/; do
        [ -d "$hydro_dir" ] || continue
        # Extract event_id from folder name
        base_hydro_dir=$(basename "$hydro_dir")
        event_id=$(echo $base_hydro_dir | rev | cut -f 1 -d "_" | rev)
        # Find the original event folder
        orig_event_dir=$(find "$fromFolder" -type d -name "${event_folder_name}${event_id}")
        if [ -n "$orig_event_dir" ]; then
            echo "Moving $hydro_dir back to $orig_event_dir"
            mv "$hydro_dir" "$orig_event_dir/"
        else
            echo "Original event directory for $hydro_dir not found. Skipping."
        fi
    done
fi

# Undo URQMD_RESULTS
if [ -d "$target_urqmd_folder" ]; then
    for urqmd_file in $target_urqmd_folder/${UrQMD_file_name}*.gz; do
        [ -e "$urqmd_file" ] || continue
        base_urqmd_file=$(basename "$urqmd_file")
        event_id=$(echo $base_urqmd_file | rev | cut -f 1 -d "_" | rev | cut -f 1 -d ".")
        orig_event_dir=$(find "$fromFolder" -type d -name "${event_folder_name}${event_id}")
        if [ -n "$orig_event_dir" ]; then
            echo "Moving $urqmd_file back to $orig_event_dir"
            mv "$urqmd_file" "$orig_event_dir/"
        else
            echo "Original event directory for $urqmd_file not found. Skipping."
        fi
    done
fi

# Undo SPVN_RESULTS
if [ -d "$target_spvn_folder" ]; then
    for spvn_file in $target_spvn_folder/${spvn_folder_name}*.h5; do
        [ -e "$spvn_file" ] || continue
        base_spvn_file=$(basename "$spvn_file")
        event_id=$(echo $base_spvn_file | rev | cut -f 1 -d "_" | rev | cut -f 1 -d ".")
        orig_event_dir=$(find "$fromFolder" -type d -name "${event_folder_name}${event_id}")
        if [ -n "$orig_event_dir" ]; then
            echo "Moving $spvn_file back to $orig_event_dir"
            mv "$spvn_file" "$orig_event_dir/"
        else
            echo "Original event directory for $spvn_file not found. Skipping."
        fi
    done
fi

# Move .h5 file back if it exists
if [ -f ${target_folder}/${folderName}.h5 ]; then
    echo "Moving ${target_folder}/${folderName}.h5 back to $fromFolder"
    mv ${target_folder}/${folderName}.h5 $fromFolder/
fi

echo "Undo complete. Please verify the results." 