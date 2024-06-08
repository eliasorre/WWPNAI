import re
import sys

def extract_cycles(file_content):
    match = re.search(r'CPU 0 cumulative IPC: [\d.]+ instructions: \d+ cycles: (\d+)', file_content)
    if match:
        return int(match.group(1))
    return None

def extract_skipped_instructions(file_content):
    skipped_instrs = re.search(r'Skipped instrs: (\d+)', file_content)
    total_instrs = re.search(r'CPU 0 cumulative IPC: [\d.]+ instructions: (\d+) cycles: \d+', file_content)
    if skipped_instrs and total_instrs:
        return int(skipped_instrs.group(1)), int(total_instrs.group(1))
    return None, None

def extract_cache_loads(file_content, cache_type):
    pattern = re.compile(rf'{cache_type} LOAD\s+ACCESS:\s+(\d+)\s+HIT:\s+\d+\s+MISS:\s+\d+')
    match = pattern.search(file_content)
    if match:
        return int(match.group(1))
    return None

def compute_stats(file1_content, file2_content):
    # Cut cycles
    cycles_1 = extract_cycles(file1_content)
    cycles_2 = extract_cycles(file2_content)
    cut_cycles = 100 * (1 - cycles_1 / cycles_2) if cycles_1 and cycles_2 else None

    # Skipped instructions
    skipped_instrs, total_instrs = extract_skipped_instructions(file1_content)
    skipped_instructions = 100 * (skipped_instrs / total_instrs) if skipped_instrs and total_instrs else None

    # Removed data cache loads
    l1d_loads_1 = extract_cache_loads(file1_content, 'cpu0_L1D')
    l1d_loads_2 = extract_cache_loads(file2_content, 'cpu0_L1D')
    removed_dcache_loads = 100 * (1 - l1d_loads_1 / l1d_loads_2) if l1d_loads_1 and l1d_loads_2 else None

    # Removed instruction cache loads
    l1i_loads_1 = extract_cache_loads(file1_content, 'cpu0_L1I')
    l1i_loads_2 = extract_cache_loads(file2_content, 'cpu0_L1I')
    removed_icache_loads = 100 * (1 - l1i_loads_1 / l1i_loads_2) if l1i_loads_1 and l1i_loads_2 else None

    return {
        "cut_cycles": cut_cycles,
        "skipped_instructions": skipped_instructions,
        "removed_dcache_loads": removed_dcache_loads,
        "removed_icache_loads": removed_icache_loads
    }

def main(file1_path, file2_path):
    with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
        file1_content = file1.read()
        file2_content = file2.read()

    stats = compute_stats(file1_content, file2_content)
    
    for key, value in stats.items():
        print(f"{key}: {value:.6f}" if value is not None else f"{key}: Data not found")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <file1> <file2>")
    else:
        file1_path = sys.argv[1]
        file2_path = sys.argv[2]
        main(file1_path, file2_path)
