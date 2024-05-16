#!/bin/bash

# List of trace files
trace_files=("binary_trees.trace" "nbody.trce" "fasta.trace" "knucleotide.trace")

# Arguments
skip=$1
instrs_to_run=$2
instr_to_skip=$3
log_name=$4
ideal=${5:-false}

# Directory paths (update these as needed)
LOGS_DIR="logs"
JSON_DIR="json"

# Create directories if they do not exist
mkdir -p $LOGS_DIR
mkdir -p $JSON_DIR

# Iterate over each trace file
for trace_file in "${trace_files[@]}"; do
    trace_file_base=$(basename "$trace_file" .trace)
    if [ "$ideal" == "true" ]; then
        json_log_name="${JSON_DIR}/${trace_file_base}_${log_name}_ideal"
        log_file="${LOGS_DIR}/${trace_file_base}_${log_name}_ideal"
        command="bin/champsim_ideal"
    elif [ "$skip" == "true" ]; then
        json_log_name="${JSON_DIR}/${trace_file_base}_${log_name}_skip"
        log_file="${LOGS_DIR}/${trace_file_base}_${log_name}_skip"
        command="bin/champsim_no_skip"
    else
        json_log_name="${JSON_DIR}/${trace_file_base}_${log_name}"
        log_file="${LOGS_DIR}/${trace_file_base}_${log_name}"
        command="bin/champsim_skip"
    fi

    # Run the command
    $command --warmup_instructions $instr_to_skip --simulation_instructions $instrs_to_run --bytecode --json $json_log_name $TRACES_ROOT/$trace_file >> $log_file
done