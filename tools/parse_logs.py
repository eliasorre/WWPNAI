import os
import re
import csv
import sys

def extract_info(log_file):
    info = {}
    with open(log_file, 'r') as file:
        content = file.read()

        # Extract IPC
        ipc_match = re.search(r"CPU 0 cumulative IPC:\s+([0-9.]+)", content)
        if ipc_match:
            info['IPC'] = float(ipc_match.group(1))
            print(ipc_match.group(1))
        else:
            print(f"IPC not found in {log_file}")
            
        # Extract total instructions
        total_instruction_match = re.search(r"CPU 0 cumulative IPC:.*? instructions:\s+([0-9]+)", content)
        if total_instruction_match:
            info['Total instrs'] = int(total_instruction_match.group(1))
            print(total_instruction_match.group(1))
        else:
            print(f"Total instrs not found in {log_file}")

        # Extract Branch MPKI
        mpki_match = re.search(r"CPU 0 Branch Prediction Accuracy:.*?MPKI:\s+([0-9.]+)", content)
        if mpki_match:
            info['Branch MPKI'] = float(mpki_match.group(1))
        else:
            print(f"Branch MPKI not found in {log_file}")
            
        # Extract Indirect Branch MPKI
        mpki_indirect_match = re.search(r"BRANCH_INDIRECT:\s+([0-9.]+)", content)
        if mpki_indirect_match:
            info['Branch Indirect MPKI'] = float(mpki_indirect_match.group(1))
        else:
            print(f"Branch Indirect MPKI not found in {log_file}")

        # Cache loads
        L1D_loads_match = re.search(r'cpu0_L1D LOAD\s+ACCESS:\s+(\d+)\s+HIT:\s+\d+\s+MISS:\s+\d+', content)
        if L1D_loads_match:
            info['D-Cache Loads'] = int(L1D_loads_match.group(1))
        else:
            print (f"L1d Loads not found in {log_file}")
            
        L1D_loads_match = re.search(r'cpu0_L1D LOAD\s+ BYTECODE ACCESS:\s+(\d+)\s+HIT:\s+\d+\s+MISS:\s+\d+', content)
        if L1D_loads_match:
            info['D-Cache Loads'] = info['D-Cache Loads'] + int(L1D_loads_match.group(1))
        else:
            print (f"L1d Bytecode Loads not found in {log_file}")
            
        L1D_loads_match = re.search(r'cpu0_L1D LOAD\s+ DISPATCH TABLE ACCESS:\s+(\d+)\s+HIT:\s+\d+\s+MISS:\s+\d+', content)
        if L1D_loads_match:
            info['D-Cache Loads'] = info['D-Cache Loads'] + int(L1D_loads_match.group(1))
        else:
            print (f"L1d Dispatch Table Loads not found in {log_file}")
            
        L1I_loads_match = re.search(r'cpu0_L1I LOAD\s+ACCESS:\s+(\d+)\s+HIT:\s+\d+\s+MISS:\s+\d+', content)
        if L1I_loads_match:
            info['I-Cache Loads'] = int(L1I_loads_match.group(1))
        else:
            print (f"L1d Loads not found in {log_file}")
        
        L1I_loads_match = re.search(r'cpu0_L1I LOAD\s+ BYTECODE ACCESS:\s+(\d+)\s+HIT:\s+\d+\s+MISS:\s+\d+', content)
        if L1D_loads_match:
            info['I-Cache Loads'] = info['I-Cache Loads']  + int(L1I_loads_match.group(1))
        else:
            print (f"L1i Bytecode Loads not found in {log_file}")
            
        L1I_loads_match = re.search(r'cpu0_L1I LOAD\s+ DISPATCH TABLE ACCESS:\s+(\d+)\s+HIT:\s+\d+\s+MISS:\s+\d+', content)
        if L1D_loads_match:
            info['I-Cache Loads'] = info['I-Cache Loads']  + int(L1I_loads_match.group(1))
        else:
            print (f"L1i Dispatch Table Loads not found in {log_file}")
    
        # Extract Seen bytecodes
        bytecodes_match = re.search(r"Seen bytecodes:\s+(\d+)", content)
        if bytecodes_match:
            info['Seen bytecodes'] = int(bytecodes_match.group(1))
        else:
            print(f"Seen bytecodes not found in {log_file}")

        # Extract Skipped instructions
        skipped_instrs_match = re.search(r"Skipped instrs:\s+(\d+)", content)
        if skipped_instrs_match:
            info['Skipped instrs'] = int(skipped_instrs_match.group(1))
        else:
            print(f"Skipped instrs not found in {log_file}")
            


        # Extract Bytecode buffer hit percentage
        buffer_hit_percentage_match = re.search(r"BYTECODE BUFFER stats.*?percentage hits:\s+([0-9.]+)", content)
        if buffer_hit_percentage_match:
            info['Bytecode buffer hit percentage'] = float(buffer_hit_percentage_match.group(1))
        else:
            print(f"Bytecode buffer hit percentage not found in {log_file}")

        # Extract HDBT hit rate
        hdbt_hit_rate_match = re.search(r"BYTECODE HDBT stats.*?percentage hits:\s+([0-9.]+)", content)
        if hdbt_hit_rate_match:
            info['HDBT hit rate'] = float(hdbt_hit_rate_match.group(1))
        else:
            print(f"HDBT hit rate not found in {log_file}")

        # Extract BPCP hit rate 
        bpcp_stats_match = re.search(r"BYTECODE BTB - strong:\s+(\d+), weak:\s+(\d+), wrong:\s+(\d+)", content)
        if bpcp_stats_match:
            strong = int(bpcp_stats_match.group(1))
            weak = int(bpcp_stats_match.group(2))
            wrong = int(bpcp_stats_match.group(3))
            total = strong + weak + wrong
            if total > 0:
                info['BPCP hit rate'] = strong / total * 100
            else:
                info['BPCP hit rate'] = 0.0
        else:
            print(f"BPCP hit rate not found in {log_file}")
    
    return info

def main(log_folder, output_csv, size_test):
    fieldnames = ['Trace File', 'Optimized', 'Size', 'Type', 'IPC', 'Branch MPKI', 'Branch Indirect MPKI', 'Seen bytecodes', 'Skipped instrs', 'Total instrs', 'Bytecode buffer hit percentage', 'HDBT hit rate', 'BPCP hit rate', 'D-Cache Loads', 'I-Cache Loads']
    rows = []

    # Mapping of trace files to their types
    trace_types = {
        "nbody": "python",
        "binary": "python",
        "knucleotide": "python",
        "fasta": "python",
        "recog": "native",
        "decoder": "native",
        "spectralnorm" : "python",
        "mandelbrot" : "python",
        "fannkuch-redux" : "python"
    }

    for root, _, files in os.walk(log_folder):
        for file in files:
            log_path = os.path.join(root, file)
            print(f"Processing {log_path}...")
            info = extract_info(log_path)
            if not info:
                print(f"No relevant data found in {log_path}")
                continue
            trace_file = os.path.basename(log_path).split('_')[0]
            print(trace_file)
            log_type = "_".join(os.path.basename(log_path).split('_')[-2:])
            if size_test:
                size = log_type
                optimized = "skip"
            else: 
                size = "no"
                if ("skip" in log_type ):
                    optimized = "skip"
                elif ("ideal" in log_type ):
                    optimized = "ideal"
                elif ("minimal" in log_type ):
                    optimized = "minmal"
                else:
                    optimized = "no"
                
            trace_type = trace_types.get(trace_file, 'unknown')
            print(trace_type)
            row = {
                'Trace File': trace_file,
                'Size' : size,
                'Optimized' : optimized,
                'Type': trace_type,
                'IPC': info.get('IPC', 'N/A'),
                'Total instrs': info.get('Total instrs', 'N/A'),
                'Branch MPKI': info.get('Branch MPKI', 'N/A'),
                'Branch Indirect MPKI': info.get('Branch Indirect MPKI', 'N/A'),
                'Seen bytecodes': info.get('Seen bytecodes', 'N/A'),
                'Skipped instrs': info.get('Skipped instrs', 'N/A'),
                'Bytecode buffer hit percentage': info.get('Bytecode buffer hit percentage', 'N/A'),
                'HDBT hit rate': info.get('HDBT hit rate', 'N/A'),
                'BPCP hit rate': info.get('BPCP hit rate', 'N/A'),
                'I-Cache Loads': info.get('I-Cache Loads', 'N/A'),
                'D-Cache Loads': info.get('D-Cache Loads', 'N/A')
            }
            rows.append(row)
    
    if rows:
        with open(output_csv, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"CSV file created at {output_csv}")
    else:
        print("No data extracted. CSV file not created.")

if __name__ == "__main__":
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("Usage: python parse_logs.py <test_name> <log_folder> <output_csv>")
        sys.exit(1)
    
    log_folder = sys.argv[1]
    output_csv = sys.argv[2]
    size_test = len(sys.argv) == 4
    
    main(log_folder, output_csv, size_test)
