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


def plot_performance(csv_file, output_image_python, output_image_native, output_image_ideal, output_image_minimal):
    # Read the CSV file
    baseline_data = pd.read_csv(csv_file)
    
    trace_based = baseline_data.sort_values(by= ['Type', 'Trace File', 'Optimized'])
    geomeans = baseline_data.groupby(['Type', 'Optimized'])['IPC'].apply(gmean).reset_index()
    geomeans['Trace File'] = "Overall \n(gmean)"
    geomeans.sort_values(by= ['Type'], ascending=False)
    print(geomeans)
    trace_based = pd.concat([trace_based, geomeans], axis=0).reset_index()
    optimized_python = trace_based[(trace_based['Optimized'] == 'skip') & (trace_based['Type'] == 'python')]
    unoptimized_python = trace_based[(trace_based['Optimized'] == 'no') & (trace_based['Type'] == 'python')]
    optimized_native = trace_based[(trace_based['Optimized'] == 'skip') & (trace_based['Type'] == 'native')]
    unoptimized_native = trace_based[(trace_based['Optimized'] == 'no') & (trace_based['Type'] == 'native')]

    # Plot for python programs
    fig, ax = plt.subplots(figsize=(18, 12))
    xs = np.arange(len(optimized_python))
    xs[-1] = xs[-1] + 1
    
    disabled_bars = ax.bar(xs - 0.2, unoptimized_python['IPC'], 0.4, label='BFM disabled')
    enabled_bars = ax.bar(xs + 0.2, optimized_python['IPC'], 0.4, label='BFM enabled')
    ax.tick_params(bottom=False, left=False)
    ax.set_xticks(xs, optimized_python['Trace File'], rotation=25, ha='right')
    ax.set_xlabel('Benchmark Trace', labelpad=25)
    ax.set_ylabel('IPC', labelpad=25)
    ax.legend(prop={'size': 25})
    ax.yaxis.grid()    
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["top"].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    # ax.set_ylim([0, 5])
    ax.vlines((xs[-1] + xs[-2])/2, ymin=0, ymax=round(ax.get_ylim()[1]), colors='black', linestyle='dashed')

    bars_array = [enabled_bars, disabled_bars]
    for bars in bars_array:
        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                round(bar.get_height(), 1),
                horizontalalignment='center',
                color=bar.get_facecolor(),
                weight='bold',
                size=18
            )
    fig.tight_layout()
    plt.savefig(output_image_python, dpi=300)
    # plt.show()
    
    # Plot for native programs

    fig, ax = plt.subplots(figsize=(10, 8))
    xs = np.arange(len(optimized_native))
    xs[-1] = xs[-1] + 1

    disabled_bars = ax.bar(xs - 0.2, unoptimized_native['IPC'], 0.4, label='BFM disabled')
    enabled_bars = ax.bar(xs + 0.2, optimized_native['IPC'], 0.4, label='BFM enabled')
    ax.tick_params(bottom=False, left=False)
    ax.set_xticks(xs, optimized_native['Trace File'], rotation=25, ha='right')
    ax.set_xlabel('Benchmark Trace', labelpad=25)
    ax.set_ylabel('IPC', labelpad=25)
    ax.legend(prop={'size': 20})
    ax.yaxis.grid()    
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["top"].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    ax.set_ylim([0, 4.5])
    ax.vlines((xs[-1] + xs[-2])/2, ymin=0, ymax=round(ax.get_ylim()[1]), colors='black', linestyle='dashed')

    bars_array = [enabled_bars, disabled_bars]
    for bars in bars_array:
        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                round(bar.get_height(), 1),
                horizontalalignment='center',
                color=bar.get_facecolor(),
                weight='bold',
                size=18
            )
            
    fig.tight_layout()
    plt.savefig(output_image_native, dpi=300)

    # Plot ideal
    fig, ax = plt.subplots(figsize=(20, 8))
    
    bar_width = 0.3
        
    ideal_python = trace_based[(trace_based['Optimized'] == 'ideal') & (trace_based['Type'] == 'python')]
    ideal_native = trace_based[(trace_based['Optimized'] == 'ideal') & (trace_based['Type'] == 'native')]
    
    combined_ideal = pd.concat([ideal_python, ideal_native])
    combined_optimized = pd.concat([optimized_python, optimized_native])
    combined_unoptimized = pd.concat([unoptimized_python, unoptimized_native])
    
    xs = np.arange(len(combined_optimized))

    disabled_bars = ax.bar(xs - bar_width, combined_unoptimized['IPC'], bar_width, label='No BFM')
    enabled_bars = ax.bar(xs, combined_optimized['IPC'], bar_width, label='Baseline BFM')
    ideal_bars = ax.bar(xs + bar_width, combined_ideal['IPC'], bar_width, label='Ideal BFM', color='C4')

    ax.tick_params(bottom=False, left=False)
    ax.set_xticks(xs, combined_optimized['Trace File'], rotation=25, ha='right')
    ax.set_xlabel('Benchmark Trace', labelpad=25)
    ax.set_ylabel('IPC', labelpad=25)
    ax.legend(prop={'size': 20})
    ax.set_ylim([0, 6])
    ax.yaxis.grid()    
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["top"].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    ax.vlines((xs[-3] + xs[-4])/2, ymin=0, ymax=round(ax.get_ylim()[1]), colors='black', linestyle='dashed')

    bars_array = [ideal_bars, enabled_bars, disabled_bars]
    for bars in bars_array:
        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                round(bar.get_height(), 1),
                horizontalalignment='center',
                color=bar.get_facecolor(),
                weight='bold',
                size=18
            )
    

    fig.tight_layout()
    plt.savefig(output_image_ideal, dpi=300)
    
    # Plot minimal
    fig, ax = plt.subplots(figsize=(20, 12))
    
    bar_width = 0.3
        
    minmal_python = trace_based[(trace_based['Optimized'] == 'minmal') & (trace_based['Type'] == 'python')]
    print(minmal_python)
    
    xs = np.arange(len(minmal_python))


    disabled_bars = ax.bar(xs - bar_width, unoptimized_python['IPC'], bar_width, label='BFM disabled')
    enabled_bars = ax.bar(xs, optimized_python['IPC'], bar_width, label='Baseline BFM')
    minmal_bars = ax.bar(xs + bar_width, minmal_python['IPC'], bar_width, label='Minimal BFM')

    ax.tick_params(bottom=False, left=False)
    ax.set_xticks(xs, minmal_python['Trace File'], rotation=25, ha='right')
    ax.set_xlabel('Benchmark Trace', labelpad=25)
    ax.set_ylabel('IPC', labelpad=25)
    ax.legend(prop={'size': 20})
    ax.set_ylim([0, 5.5])
    ax.yaxis.grid()    
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["top"].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    ax.vlines((xs[-1] + xs[-2])/2, ymin=0, ymax=round(ax.get_ylim()[1]), colors='black', linestyle='dashed')

    bars_array = [minmal_bars, enabled_bars, disabled_bars]
    for bars in bars_array:
        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                round(bar.get_height(), 1),
                horizontalalignment='center',
                color=bar.get_facecolor(),
                weight='bold',
                size=18
            )
    

    fig.tight_layout()
    plt.savefig(output_image_minimal, dpi=300)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python plot_performance.py <input_csv> <baseline_csv>  <output_image_python> <output_image_native>")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    output_image_python = sys.argv[2]
    output_image_native = sys.argv[3]
    output_image_ideal = sys.argv[4]
    output_image_minimal = sys.argv[5]


    plot_performance(input_csv, output_image_python, output_image_native, output_image_ideal, output_image_minimal)
