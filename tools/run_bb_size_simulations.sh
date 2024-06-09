#!/bin/bash

# List of trace files
trace_files=("binary_trees.trace" "nbody.trace" "fasta.trace" "knucleotide.trace" "recog_thread.trace" "decoder_thread.2.trace")
bb_sizes=("8_6" "16_2" "8_4" "16_4" "8_8" "16_1" "8_2" "16_3" "8_1")

# Arguments
instrs_to_run=$1
instr_to_skip=$2
log_name=$3

# Directory paths (update these as needed)
LOGS_DIR="logs"
JSON_DIR="json"
CONFIG_TESTED="bb_size"

# Create directories if they do not exist
mkdir -p $LOGS_DIR
mkdir -p $JSON_DIR
mkdir -p "${LOGS_DIR}/${CONFIG_TESTED}"

# Iterate over each trace file
for size in "${bb_sizes[@]}"; do
    for trace_file in "${trace_files[@]}"; do
        trace_file_base=$(basename "$trace_file" .trace)
        echo "Running: " $size " for trace file: " $trace_file " for BB" 
        json_log_name="${JSON_DIR}/${trace_file_base}_${log_name}_${size}"
        log_file="${LOGS_DIR}/${CONFIG_TESTED}/${trace_file_base}_${log_name}_${size}"
        command="bin/${CONFIG_TESTED}/${size}"
            

        # Check if log file already exists
        if [ -f "$log_file" ]; then
            echo "Log file $log_file already exists. Skipping..."
            continue
        fi
        # Run the command
        $command --warmup_instructions $instr_to_skip --simulation_instructions $instrs_to_run --bytecode --json $json_log_name $TRACES_ROOT/$trace_file >> $log_file
    done
done

