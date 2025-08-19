#!/usr/bin/env bash

# Determine the directory where this script resides
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage="$0 fromFolder toFolder [--destructive]"

fromFolder=$1
toFolder=$2
destructive=false

if [ "$3" == "--destructive" ]; then
    destructive=true
fi

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

if [ "$destructive" = true ]; then
    echo "collecting events from " $fromFolder " to " $toFolder " (destructive: moving files)"
    move_or_copy=mv
else
    echo "collecting events from " $fromFolder " to " $toFolder " (non-destructive: copying files)"
    move_or_copy=cp
fi

folderName=`echo $fromFolder | rev | cut -d "/" -f 1 | rev`
target_folder=${toFolder}/${folderName}
mkdir -p ${target_folder}
cp ${fromFolder}/parameters_dict_*.py ${target_folder}/
cp -r ${fromFolder}/model_parameters ${target_folder}/
target_hydro_folder=${target_folder}/HYDRO_RESULTS
mkdir -p ${target_hydro_folder}
target_urqmd_folder=${target_folder}/URQMD_RESULTS
mkdir -p ${target_urqmd_folder}
target_spvn_folder=${target_folder}/SPVN_RESULTS
mkdir -p ${target_spvn_folder}

event_folder_name="EVENT_RESULTS_"
hydro_folder_name="hydro_results_"
UrQMD_file_name="particle_list_"
spvn_folder_name="spvn_results_"

total_eventNum=0
collected_eventNum=0
for ijob in `ls --color=none $fromFolder | grep "event" `;
do
    eventsPath=${fromFolder}/${ijob}
    for iev in `ls --color=none $eventsPath | grep $event_folder_name`
    do
        echo $iev
        event_id=`echo $iev | rev | cut -f 1 -d "_" | rev`
        hydro_folder="${eventsPath}/${iev}/${hydro_folder_name}*${event_id}/"
        urqmd_file="${eventsPath}/${iev}/${UrQMD_file_name}*${event_id}.gz"
        hydrostatus=false
        urqmdstatus=false
        if [ -d $hydro_folder ]; then
            hydrostatus1=`tail -n 1 ${eventsPath}/${iev}/${hydro_folder_name}*${event_id}/run.log | cut -f 4 -d " "`
            echo $hydrostatus1
            if [ "$hydrostatus1" == "Finished." ]; then
                hydrostatus=true
            fi
        fi
        if [ -e $urqmd_file ]; then
            # Find the URQMD folder (remove .gz and possible file extension)
            urqmd_folder_path=$(dirname $urqmd_file)
            if [ -d "$urqmd_folder_path" ]; then
                if [ -z "$(ls -A "$urqmd_folder_path")" ]; then
                    echo "URQMD folder $urqmd_folder_path is empty. Skipping this event."
                    urqmdstatus=false
                else
                    urqmdstatus=true
                fi
            else
                urqmdstatus=true
            fi
        fi
        if [ -a ${eventsPath}/${iev}/${spvn_folder_name}*${event_id}.h5 ]; then
            if [ "$hydrostatus" = true ]; then
                $move_or_copy -r ${eventsPath}/${iev}/${hydro_folder_name}*${event_id} $target_hydro_folder
            fi
            if [ "$urqmdstatus" = true ]; then
                $move_or_copy ${eventsPath}/${iev}/${UrQMD_file_name}*${event_id}.gz $target_urqmd_folder
            fi
            $move_or_copy ${eventsPath}/${iev}/${spvn_folder_name}*${event_id}.h5 $target_spvn_folder
            ((collected_eventNum++))
        fi
        ((total_eventNum++))
    done
done

echo "Collected events number: " $collected_eventNum " out of " $total_eventNum

if [ -f ${target_folder}/${folderName}.h5 ]; then
    $move_or_copy ${target_folder}/${folderName}.h5 ${target_spvn_folder}
fi
"${SCRIPT_DIR}/combine_multiple_hdf5.py" ${target_spvn_folder} --output ${target_folder}/${folderName}.h5
if [ "$destructive" = true ]; then
    rm -fr $target_spvn_folder
fi
