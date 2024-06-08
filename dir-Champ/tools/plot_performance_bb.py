import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy.stats import gmean

SIZE_SMALL = 20
SIZE_DEFAULT = 28
SIZE_LARGE = 32
plt.rc("font", weight="normal")  # controls default font
plt.rc("font", size=SIZE_DEFAULT)  # controls default text sizes
plt.rc("axes", titlesize=SIZE_LARGE)  # fontsize of the axes title
plt.rc("axes", labelsize=SIZE_LARGE)  # fontsize of the x and y labels
plt.rc("xtick", labelsize=SIZE_DEFAULT)  # fontsize of the tick labels
plt.rc("ytick", labelsize=SIZE_DEFAULT)  # fontsize of the tick labels

def plot_performance(csv_file, output_image_python, output_image_native):
    # Read the CSV file
    data = pd.read_csv(csv_file)


    # Calculate geometric mean IPC for each size combination
    geom_means = data.groupby(['Type', 'Size'])['IPC'].apply(gmean).reset_index()
    geom_means['Total Size'] = geom_means['Size'].apply(lambda x: int(x.split('_')[0]) * int(x.split('_')[1]))
    geom_means['Total Size Text'] = geom_means['Total Size'].apply(lambda x: str(x) )

    # Split the data into python and native
    geom_means_python = geom_means[geom_means['Type'] == 'python']
    geom_means_native = geom_means[geom_means['Type'] == 'native']

    baseline_python = geom_means_python[geom_means_python['Size'] == '8_6'].get('IPC')
    baseline_native = geom_means_native[geom_means_native['Size'] == '8_6'].get('IPC')
    geom_means_native['IPC'] = geom_means_native['IPC'] / baseline_native.values[0]
    geom_means_python['IPC'] = geom_means_python['IPC'] / baseline_python.values[0]

    python_baseline_improvement = 4.012660 / 3.318184
    native_baseline_improvement = 3.136336 / 3.140508
    
    geom_means_python['IPC'] = geom_means_python['IPC'] * python_baseline_improvement
    geom_means_native['IPC'] = geom_means_native['IPC'] * native_baseline_improvement
    # Separate the data into 8-byte and 16-byte rows
    geom_means_python_8 = geom_means_python[geom_means_python['Size'].str.startswith('8_')].sort_values(by='Total Size')
    geom_means_python_16 = geom_means_python[geom_means_python['Size'].str.startswith('16_')].sort_values(by='Total Size')
    geom_means_native_8 = geom_means_native[geom_means_native['Size'].str.startswith('8_')].sort_values(by='Total Size')
    geom_means_native_16 = geom_means_native[geom_means_native['Size'].str.startswith('16_')].sort_values(by='Total Size')
    new_row = pd.DataFrame({'Total Size': [8], 'IPC': [0]})
    geom_means_native_16 = pd.concat([new_row, geom_means_native_16])
    geom_means_python_16 = pd.concat([new_row, geom_means_python_16])

    # Plot for python programs
    fig, ax = plt.subplots(figsize=(18, 12))
    xs = np.arange(len(geom_means_python_8))
    width = 0.4
    
    bb8_bars = ax.bar(xs - width/2, geom_means_python_8['IPC'], width, label='4 Bytecode Sized Rows')
    bb16_bars = ax.bar(xs + width/2, geom_means_python_16['IPC'], width, label='8 Bytecode Sized Rows')
    # hdbt_bars = ax.bar(xs + width, 100 - optimized['HDBT hit rate'], width, label='HDBT')
    ax.tick_params(bottom=False, left=False)
    ax.set_xticks(xs, geom_means_python_8['Total Size Text'])

    ax.set_xlabel('Total Size of BB (entries)', labelpad=25)
    ax.set_ylabel('Speedup', labelpad=25)
    ax.legend(loc='upper left', prop={'size': 25})
    ax.yaxis.grid()    
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["top"].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    ax.axhline(python_baseline_improvement, 0.025, 0.975, color='grey', linestyle='dashed')
    ax.set_ylim([1, 1.25])
    
    bars_array = [bb16_bars, bb8_bars]
    for bars in bars_array:
        for bar in bars:
            if (bar.get_height() == 0):
                continue
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.0025,
                round(bar.get_height(), 3),
                horizontalalignment='center',
                color=bar.get_facecolor(),
                weight='bold',
                size=20
            )
    fig.tight_layout()
    plt.savefig(output_image_python, dpi=300)
    # plt.show()

    # Plot for native programs
     # Plot for python programs
    fig, ax = plt.subplots(figsize=(18, 12))
    xs = np.arange(len(geom_means_native_8))
    width = 0.4
    
    bb8_bars = ax.bar(xs - width/2, geom_means_native_8['IPC'], width, label='4 Bytecode Sized Rows')
    bb16_bars = ax.bar(xs + width/2, geom_means_native_16['IPC'], width, label='8 Bytecode Sized Rows')
    # hdbt_bars = ax.bar(xs + width, 100 - optimized['HDBT hit rate'], width, label='HDBT')
    ax.tick_params(bottom=False, left=False)
    ax.set_xticks(xs, geom_means_native_8['Total Size Text'])

    ax.set_xlabel('Total Size of BB (entries)', labelpad=25)
    ax.set_ylabel('Speedup', labelpad=25)
    ax.legend(loc='upper left', prop={'size': 25})
    ax.yaxis.grid()    
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["top"].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    ax.axhline(native_baseline_improvement, 0.025, 0.975, color='grey', linestyle='dashed')
    ax.set_ylim([0.94, 1.02])
    
    bars_array = [bb8_bars, bb16_bars]
    for bars in bars_array:
        for bar in bars:
            if (bar.get_height() == 0):
                continue
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.001,
                round(bar.get_height(), 3),
                horizontalalignment='center',
                color=bar.get_facecolor(),
                weight='bold',
                size=20
            )
    fig.tight_layout()
    plt.savefig(output_image_native, dpi=300)
    # plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python plot_performance.py <input_csv> <output_image_python> <output_image_native>")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    output_image_python = sys.argv[2]
    output_image_native = sys.argv[3]
    
    plot_performance(input_csv, output_image_python, output_image_native)
