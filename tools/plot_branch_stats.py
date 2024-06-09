import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from scipy.stats import gmean

SIZE_SMALL = 20
SIZE_DEFAULT = 28
SIZE_LARGE = 32
plt.rc("font", weight="normal")  # controls default font
plt.rc("font", size=SIZE_SMALL)  # controls default text sizes
plt.rc("axes", titlesize=SIZE_LARGE)  # fontsize of the axes title
plt.rc("axes", labelsize=SIZE_LARGE)  # fontsize of the x and y labels
plt.rc("xtick", labelsize=SIZE_DEFAULT)  # fontsize of the tick labels
plt.rc("ytick", labelsize=SIZE_DEFAULT)  # fontsize of the tick labels


def plot_performance(csv_file, output_image_python, output_image_native):
    # Read the CSV file
    baseline_data = pd.read_csv(csv_file)
    
    trace_based = baseline_data.sort_values(by= ['Type', 'Trace File', 'Optimized'])
    optimized_python = trace_based[(trace_based['Optimized'] == 'skip') & (trace_based['Type'] == 'python')]
    unoptimized_python = trace_based[(trace_based['Optimized'] == 'no') & (trace_based['Type'] == 'python')]
    optimized_native = trace_based[(trace_based['Optimized'] == 'skip') & (trace_based['Type'] == 'native')]
    unoptimized_native = trace_based[(trace_based['Optimized'] == 'no') & (trace_based['Type'] == 'native')]

    # Plot for python programs
    fig, ax = plt.subplots(figsize=(18, 12))
    xs = np.arange(len(optimized_python))
    
    disabled_bars = ax.bar(xs - 0.2, unoptimized_python['Branch MPKI'], 0.4, label='BFM disabled')
    enabled_bars = ax.bar(xs + 0.2, optimized_python['Branch MPKI'], 0.4, label='BFM enabled', color='C1')
    indirect_bars = ax.bar(xs - 0.2, unoptimized_python['Branch Indirect MPKI'], 0.4, color='green', alpha=0.75, label='Indirect Branch MPKI', edgecolor='green', hatch='//')
    indirect_bars = ax.bar(xs + 0.2, optimized_python['Branch Indirect MPKI'], 0.4, color='green', alpha=0.75, edgecolor='green', hatch='//')
    ax.tick_params(bottom=False, left=False)
    ax.set_xticks(xs, optimized_python['Trace File'], rotation=25, ha='right')
    ax.set_xlabel('Benchmark Trace', labelpad=25)
    ax.set_ylabel('MPKI', labelpad=25)
    ax.legend(prop={'size': 25})
    ax.yaxis.grid()    
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["top"].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    fig.tight_layout()
    plt.savefig(output_image_python, dpi=300)
    # plt.show()
    
    # Plot for native programs
    fig, ax = plt.subplots(figsize=(14, 12))
    xs = np.arange(len(optimized_native))
    
    disabled_bars = ax.bar(xs - 0.2, unoptimized_native['Branch MPKI'], 0.4, label='BFM disabled')
    enabled_bars = ax.bar(xs + 0.2, optimized_native['Branch MPKI'], 0.4, label='BFM enabled', color='C1')
    indirect_bars = ax.bar(xs - 0.2, unoptimized_native['Branch Indirect MPKI'], 0.4, color='green', alpha=0.75, label='Indirect Branch MPKI', edgecolor='green', hatch='//')
    indirect_bars = ax.bar(xs + 0.2, optimized_native['Branch Indirect MPKI'], 0.4, color='green', alpha=0.75, edgecolor='green', hatch='//')
    ax.tick_params(bottom=False, left=False)
    ax.set_xticks(xs, optimized_native['Trace File'], rotation=25, ha='right')
    ax.set_xlabel('Benchmark Trace', labelpad=25)
    ax.set_ylabel('MPKI', labelpad=25)
    ax.legend(prop={'size': 25})
    ax.yaxis.grid()    
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["top"].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    fig.tight_layout()
    plt.savefig(output_image_native, dpi=300)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python plot_performance.py <input_csv> <baseline_csv>  <output_image_python> <output_image_native>")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    output_image_python = sys.argv[2]
    output_image_native = sys.argv[3]

    plot_performance(input_csv, output_image_python, output_image_native)
