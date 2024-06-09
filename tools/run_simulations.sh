#!/bin/bash

# List of trace files
trace_files=("binary_trees.trace" "nbody.trace" "fasta.trace" "knucleotide.trace" "recog_thread.trace" "decoder_thread.2.trace" "mandelbrot.trace" "spectralnorm.trace" "fannkuch-redux.trace")

# Arguments
bin=$1
instrs_to_run=$2
instr_to_skip=$3
log_name=$4
log_dir=$5

# Directory paths (update these as needed)
JSON_DIR="json"
if [ -z "$log_dir"]; then
    LOGS_DIR="logs"
else 
    LOGS_DIR="logs/${log_dir}"
fi

# Create directories if they do not exist
mkdir -p $LOGS_DIR
mkdir -p $JSON_DIR

# Iterate over each trace file
for trace_file in "${trace_files[@]}"; do
    echo " "
    trace_file_base=$(basename "$trace_file" .trace)
    if [ "$bin" == "ideal" ]; then
        json_log_name="${JSON_DIR}/${trace_file_base}_${log_name}_ideal"
        log_file="${LOGS_DIR}/${trace_file_base}_${log_name}_ideal"
        command="bin/champsim_ideal"
    elif [ "$bin" == "skip" ]; then
        json_log_name="${JSON_DIR}/${trace_file_base}_${log_name}_skip"
        log_file="${LOGS_DIR}/${trace_file_base}_${log_name}_skip"
        command="bin/champsim_skip"
    elif [ "$bin" == "l2" ]; then
        json_log_name="${JSON_DIR}/${trace_file_base}_${log_name}_l2"
        log_file="${LOGS_DIR}/${trace_file_base}_${log_name}_l2"
        command="bin/champsim_l2"
    elif  [ "$bin" == "no_skip" ]; then
        json_log_name="${JSON_DIR}/${trace_file_base}_${log_name}"
        log_file="${LOGS_DIR}/${trace_file_base}_${log_name}"
        command="bin/champsim_no_skip"
    elif  [ "$bin" == "minimal" ]; then
        json_log_name="${JSON_DIR}/${trace_file_base}_${log_name}_minimal"
        log_file="${LOGS_DIR}/${trace_file_base}_${log_name}_minimal"
        command="bin/champsim_minimal"
    else 
        echo "Not a valid option: " $bin 
    fi

    # Check if log file already exists
    if [ -f "$log_file" ]; then
        echo "Log file $log_file already exists. Skipping..."
        continue
    elif [! -f "$trace_file"]; then 
        echo "Trace file $trace_file does not exists. Skipping..."
        continue
    fi
    # Run the command
    echo "Running: " "$trace_file" " with " "$command" for "$log_name" 
    $command --warmup_instructions $instr_to_skip --simulation_instructions $instrs_to_run --bytecode --json $json_log_name $TRACES_ROOT/$trace_file >> $log_file
done