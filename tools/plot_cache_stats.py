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

def plot_performance(csv_file, output_image):
    # Read the CSV file
    baseline_data = pd.read_csv(csv_file)
    
    trace_based = baseline_data.sort_values(by= ['Type', 'Trace File', 'Optimized'])
    optimized = trace_based[trace_based['Optimized'] == 'skip'].sort_values(['Type', 'Trace File']).reset_index()
    unoptimized = trace_based[(trace_based['Optimized'] == 'no')].sort_values(['Type', 'Trace File']).reset_index()


    optimized['I-Cache Loads'] = (optimized['I-Cache Loads'] / unoptimized['I-Cache Loads']) * 100
    optimized['D-Cache Loads'] = (optimized['D-Cache Loads'] / unoptimized['D-Cache Loads']) * 100

    print (optimized)
    print (unoptimized)
    optimized_native = optimized[optimized['Type'] == 'native']
    optimized = optimized[optimized['Type'] == 'python']
    optimized = pd.concat([optimized, optimized_native])

    # Plot
    fig, ax = plt.subplots(figsize=(18, 12))
    xs = np.arange(len(optimized))
    
    i_bars = ax.bar(xs - 0.2, 100 - optimized['I-Cache Loads'], 0.4, label='L1I')
    d_bars = ax.bar(xs + 0.2, 100 - optimized['D-Cache Loads'], 0.4, label='L1D')
    ax.tick_params(bottom=False, left=False)
    ax.set_xticks(xs, optimized['Trace File'], rotation=25, ha='right')
    ax.set_xlabel('Benchmark Trace', labelpad=25)
    ax.set_ylabel('Reduced Number of Loads (%)', labelpad=25)
    ax.legend(loc='upper left', prop={'size': 25})
    ax.yaxis.grid()    
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["top"].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    ax.set_ylim([0, 105])
    
    bars_array = [i_bars, d_bars]
    for bars in bars_array:
        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                round(bar.get_height()),
                horizontalalignment='center',
                color=bar.get_facecolor(),
                weight='bold',
                size=20
            )
    fig.tight_layout()
    plt.savefig(output_image, dpi=300)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python plot_performance.py <input_csv> <baseline_csv>  <output_image>")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    output_image = sys.argv[2]

    plot_performance(input_csv, output_image)
