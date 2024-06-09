import pandas as pd
import matplotlib.pyplot as plt
import sys
from scipy.stats import gmean
import numpy as np


SIZE_SMALL = 20
SIZE_DEFAULT = 28
SIZE_LARGE = 32
plt.rc("font", weight="normal")  # controls default font
plt.rc("font", size=SIZE_SMALL)  # controls default text sizes
plt.rc("axes", titlesize=SIZE_LARGE)  # fontsize of the axes title
plt.rc("axes", labelsize=SIZE_LARGE)  # fontsize of the x and y labels
plt.rc("xtick", labelsize=SIZE_DEFAULT)  # fontsize of the tick labels
plt.rc("ytick", labelsize=SIZE_DEFAULT)  # fontsize of the tick labels

# Function to interpolate values
def interpolate(arr):
    new_length = 2 * len(arr) - 1
    new_arr = np.zeros(new_length)
    
    new_arr[0::2] = arr
    new_arr[1::2] = (arr[:-1] + arr[1:]) / 2
    
    return new_arr 

def interpolate_array(arr, x):
    for i in range(x):
        arr = interpolate(arr)
    return arr 

def plot_performance(csv_file, output_image_python, output_image_native):
    # Read the CSV file
    data = pd.read_csv(csv_file)

    # Create a column for total size
    data['Total Size'] = data['Size'].apply(lambda x: int(x.split('_')[0]) + int(x.split('_')[1]))
    data['HDBT Size'] = data['Size'].apply(lambda x: int(x.split('_')[0]))
    data['BPCP Size'] = data['Size'].apply(lambda x: int(x.split('_')[1]))


    # Calculate geometric mean IPC for each size combination
    geom_means = data.groupby(['Type', 'Size'])['IPC'].apply(gmean).reset_index()
    geom_means['Total Size'] = geom_means['Size'].apply(lambda x: int(x.split('_')[0]) + int(x.split('_')[1]))
    geom_means['Total Size Text'] = geom_means['Size'].apply(lambda x: x.split('_')[0] + ',' + x.split('_')[1])
    geom_means['Total Size Ticks'] = geom_means['Size'].apply(lambda x: int(x.split('_')[0]) + int(x.split('_')[1]))
    geom_means['HDBT Size'] = geom_means['Size'].apply(lambda x: int(x.split('_')[0]))

    geom_means = geom_means.sort_values(['Total Size', 'HDBT Size'])
    # Split the data into python and native
    geom_means_python = geom_means[geom_means['Type'] == 'python'].sort_values(by='Total Size')
    geom_means_native = geom_means[geom_means['Type'] == 'native'].sort_values(by='Total Size')
    
    baseline_python = geom_means_python[geom_means_python['Size'] == '256_256'].get('IPC')
    baseline_native = geom_means_native[geom_means_native['Size'] == '256_256'].get('IPC')
    geom_means_native['IPC'] = geom_means_native['IPC'] / baseline_native.values[0]
    geom_means_python['IPC'] = geom_means_python['IPC'] / baseline_python.values[0]

    python_baseline_improvement = 4.012660 / 3.318184
    native_baseline_improvement = 3.136336 / 3.140508
    
    geom_means_python['IPC'] = geom_means_python['IPC'] * python_baseline_improvement
    geom_means_native['IPC'] = geom_means_native['IPC'] * native_baseline_improvement

    # Plot for python programs
    fig, ax = plt.subplots(figsize=(18, 12))

    line = geom_means_python.groupby('Total Size', as_index=False).agg({'Total Size' : 'first', 'IPC' : ['mean']})
    sizes = line['Total Size'].to_numpy().squeeze()
    ipcs = line['IPC'].to_numpy().squeeze()
    sizes = interpolate_array(sizes, 8)
    ipcs = interpolate_array(ipcs, 8)
    coef = np.polyfit(sizes, ipcs,7)
    poly1d_fn = np.poly1d(coef) 
    xs = np.arange(sizes[0], sizes[-1] - 5, 5)
    
    ax.plot(xs, poly1d_fn(xs), linestyle='dashed', color='grey', lw=3)
    plot = ax.scatter(geom_means_python['Total Size'], geom_means_python['IPC'], label='{HDBT, BPCP}', lw=5, color='C1')

    # hdbt_bars = ax.bar(xs + width, 100 - optimized['HDBT hit rate'], width, label='HDBT')
    ax.tick_params(left=False)


    # Add annotations using iloc
    for i in range(len(geom_means_python)):
        if (i % 2 == 0):
            y_offset = 10
        else:
            y_offset = -25
        ax.annotate(geom_means_python['Total Size Text'].iloc[i], (geom_means_python['Total Size'].iloc[i], geom_means_python['IPC'].iloc[i]), textcoords="offset points", xytext=(0,y_offset), ha='center')
    
    ax.set_xlabel('Total Size of HDBT + BPCP (entries)', labelpad=25)
    ax.set_ylabel('Speedup', labelpad=25)

    ax.set_xscale('log')
    ax.set_xticks(geom_means_python['Total Size'].unique(), geom_means_python['Total Size Ticks'].unique())


    ax.yaxis.grid()    
    ax.legend(loc='lower right', prop={'size': 30})
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["top"].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    # ax.axhline(python_baseline_improvement, 0.025, 0.975, color='grey', linestyle='dashed')
    # ax.set_ylim([0, 1.45])
    plt.savefig(output_image_python, dpi=300)

        
    # Plot for Native programs
    fig, ax = plt.subplots(figsize=(18, 12))

    line = geom_means_native.groupby('Total Size', as_index=False).agg({'Total Size' : 'first', 'IPC' : ['mean']})
    sizes = line['Total Size'].to_numpy().squeeze()
    ipcs = line['IPC'].to_numpy().squeeze()
    interpolated_sizes = interpolate_array(sizes, 16)
    ipcs = interpolate_array(ipcs, 16)
    coef = np.polyfit(interpolated_sizes, ipcs,9)
    poly1d_fn = np.poly1d(coef) 
    xs = np.arange(sizes[0] + 2, sizes[-1] - 30)

    
    ax.plot(xs, poly1d_fn(xs), linestyle='dashed', color='grey', lw=3)
    plot = ax.scatter(geom_means_native['Total Size'], geom_means_native['IPC'], lw=5, label='{HDBT, BPCP}', color='C1')
    # hdbt_bars = ax.bar(xs + width, 100 - optimized['HDBT hit rate'], width, label='HDBT')
    ax.tick_params(left=False)
    ax.set_xscale('log')
    ax.set_xticks(geom_means_native['Total Size'].unique(), geom_means_native['Total Size Ticks'].unique())


    # Add annotations using iloc
    # Add annotations using iloc
    for i in range(len(geom_means_native)):
        y_offset = 10
        ax.annotate(geom_means_native['Total Size Text'].iloc[i], (geom_means_native['Total Size'].iloc[i], geom_means_native['IPC'].iloc[i]), textcoords="offset points", xytext=(0,y_offset), ha='center')
    
    ax.set_xlabel('Total Size of HDBT + BPCP (entries)', labelpad=25)
    ax.set_ylabel('Speedup', labelpad=25)
    ax.yaxis.grid()    
    ax.legend(loc='upper left', prop={'size': 30})
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["top"].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    # ax.axhline(python_baseline_improvement, 0.025, 0.975, color='grey', linestyle='dashed')
    # ax.set_ylim([0, 1.45])
        
    fig.tight_layout()
    plt.savefig(output_image_native, dpi=300)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python plot_performance.py <input_csv> <output_image_python> <output_image_native>")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    output_image_python = sys.argv[2]
    output_image_native = sys.argv[3]
    
    plot_performance(input_csv, output_image_python, output_image_native)
