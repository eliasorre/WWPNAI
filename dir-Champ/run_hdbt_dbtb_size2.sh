#!/bin/bash

# List of trace files
trace_files=("nbody.trace" "knucleotide.trace" "mandelbrot.trace" "spectralnorm.trace" "fannkuch-redux.trace")
bb_sizes=("256_256" "128_256" "128_128" "64_128" "64_64" "64_32" "32_64" "32_32" "32_0" "16_32" "32_16" "16_16" "16_0" "8_8" "8_0")

# Arguments
instrs_to_run=$1
instr_to_skip=$2
log_name=$3

# Directory paths (update these as needed)
LOGS_DIR="logs"
JSON_DIR="json"
CONFIG_TESTED="hdbt_dbtb_size"

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
        $command --warmup_instructions $instr_to_skip --simulation_instructions $instrs_to_run --bytecode --json $json_log_name $NEW_TRACES_ROOT/$trace_file >> $log_file
    done
done
