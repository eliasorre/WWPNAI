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


def plot_performance(csv_file, baseline_csv, output_image_python, output_image_native, output_image_indirect_miss):
    # Read the CSV file
    data = pd.read_csv(csv_file)
    baseline_data = pd.read_csv(baseline_csv)

    geomean_mpki = baseline_data.groupby(['Type', 'Optimized'])['Branch MPKI'].apply(gmean).reset_index()

    geomean_mpki_id = baseline_data.groupby(['Type', 'Optimized'])['Branch Indirect MPKI'].apply(gmean).reset_index()
    geomean_mpki['Branch Indirect MPKI'] = geomean_mpki_id['Branch Indirect MPKI']
    
    
    geomean_mpki_python = geomean_mpki[(geomean_mpki['Type'] == 'python') & (geomean_mpki['Optimized'] == 'skip')]
    geomean_mpki_native = geomean_mpki[(geomean_mpki['Type'] == 'native') & (geomean_mpki['Optimized'] == 'skip')]
    print(geomean_mpki_python['Branch MPKI'].values[0])
    # Added from baseline numbers
    python_baseline_improvement = 4.012660 
    native_baseline_improvement = 3.136336
    new_row_python = pd.DataFrame({'Size': ['1024_4096'], 'Branch MPKI': [geomean_mpki_python['Branch MPKI'].values[0]], 'Branch Indirect MPKI': [geomean_mpki_python['Branch Indirect MPKI'].values[0]], 'IPC': [python_baseline_improvement], 'Type': ['python']})
    new_row_native = pd.DataFrame({'Size': ['1024_4096'], 'Branch MPKI': [geomean_mpki_native['Branch MPKI'].values[0]], 'Branch Indirect MPKI': [geomean_mpki_native['Branch Indirect MPKI'].values[0]], 'IPC': [native_baseline_improvement], 'Type': ['native']})

    print(data[data['Branch MPKI'] == 0])
    # Append the dictionary to the DataFrame
    data = data._append(new_row_python, ignore_index=True)
    data = data._append(new_row_native, ignore_index=True)
    print(data)

    # Reset the index
    data = data.reset_index(drop=True)

    # Calculate geometric mean IPC for each size combination
    geom_means = data.groupby(['Type', 'Size'])['IPC'].apply(gmean).reset_index()

    geom_means['Total Size'] = geom_means['Size'].apply(lambda x: int(x.split('_')[0]) * 8 + int(x.split('_')[1]))
    geom_means['Total Size Text'] = geom_means['Size'].apply(lambda x: x.split('_')[0] + ',' + str(int(x.split('_')[1]) - 512))
    geom_means['Total Size Ticks'] = geom_means['Size'].apply(lambda x: int(x.split('_')[0]) * 8 + int(x.split('_')[1]) - 512)
    geom_means['Indirect Size'] = geom_means['Size'].apply(lambda x: int(x.split('_')[1]))

    geom_means = geom_means.sort_values(['Total Size', 'Indirect Size'])
    # Split the data into python and native
    geom_means_python = geom_means[geom_means['Type'] == 'python'].sort_values(by='Total Size')
    geom_means_native = geom_means[geom_means['Type'] == 'native'].sort_values(by='Total Size')
    
    geom_means_native['IPC'] = geom_means_native['IPC'] / 3.318184
    geom_means_python['IPC'] = geom_means_python['IPC'] / 3.140508

    # Plot for python programs
    fig, ax = plt.subplots(figsize=(18, 12))

    plot = ax.scatter(geom_means_python['Total Size'], geom_means_python['IPC'], label='{BTB sets, BTB indirect entries}', lw=5, color='C1')

    # hdbt_bars = ax.bar(xs + width, 100 - optimized['HDBT hit rate'], width, label='HDBT')
    ax.tick_params(left=False, bottom=False)


    # Add annotations using iloc
    for i in range(len(geom_means_python)):
        y_offset = 10
        ax.annotate(geom_means_python['Total Size Text'].iloc[i], (geom_means_python['Total Size'].iloc[i], geom_means_python['IPC'].iloc[i]), textcoords="offset points", xytext=(0,y_offset), ha='center')
    
    ax.set_xlabel('BTB sets and indirect BTB entries', labelpad=25)
    ax.set_ylabel('Speedup', labelpad=25)

    ax.set_xscale('log')
    ax.set_xticks([])
    ax.set_xticks([], minor=True)
    print(geom_means_python['Total Size Ticks'].unique())
    print(geom_means_python['Total Size'].unique())


    ax.yaxis.grid()    
    ax.legend(loc='upper left', prop={'size': 30})
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

    plot = ax.scatter(geom_means_native['Total Size'], geom_means_native['IPC'], lw=5, label='{BTB sets, BTB indirect entries}', color='C1')
    # hdbt_bars = ax.bar(xs + width, 100 - optimized['HDBT hit rate'], width, label='HDBT')
    ax.tick_params(left=False)
    ax.set_xscale('log')
    ax.set_xticks([])
    ax.set_xticks([], minor=True)


    # Add annotations using iloc
    for i in range(len(geom_means_native)):
        y_offset = 15
        ax.annotate(geom_means_native['Total Size Text'].iloc[i], (geom_means_native['Total Size'].iloc[i], geom_means_native['IPC'].iloc[i]), textcoords="offset points", xytext=(0,y_offset), ha='center')
    
    ax.set_xlabel('BTB sets and indirect BTB entries', labelpad=25)
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
    
    
    data['BTB Sets'] = data['Size'].apply(lambda x: int(x.split('_')[0]))
    python_data = data[(data['Type'] == 'python') & (data['BTB Sets'] == 1024)]
    not_optimized_mpki = geomean_mpki[(geomean_mpki['Type'] == 'python') & (geomean_mpki['Optimized'] == 'no')]['Branch Indirect MPKI'].values[0]
    
    geomean_mpki = python_data.groupby(['Size'])['Branch MPKI'].apply(gmean).reset_index()
    geomean_mpki_ind = python_data.groupby(['Size'])['Branch Indirect MPKI'].apply(gmean).reset_index()
    geomean_mpki['Branch Indirect MPKI'] = geomean_mpki_ind['Branch Indirect MPKI']
    print(geomean_mpki)
    print(geomean_mpki['Size'])
    geomean_mpki['Total Size'] = geomean_mpki['Size'].apply(lambda x: int(x.split('_')[0]) * 8 + int(x.split('_')[1]) - 512)

    
    
    # Plot for mpki
    fig, ax = plt.subplots(figsize=(18, 12))

    geomean_mpki['Total Size Text'] = geomean_mpki['Size'].apply(lambda x: str(int(x.split('_')[1]) - 512))
    geomean_mpki['Total Size Ticks'] = geomean_mpki['Size'].apply(lambda x: int(x.split('_')[0]) * 8 + int(x.split('_')[1]) - 512)

    plot = ax.scatter(geomean_mpki['Total Size'], geomean_mpki['Branch Indirect MPKI'], lw=5, color='C1', label='BFM enabled')
    # hdbt_bars = ax.bar(xs + width, 100 - optimized['HDBT hit rate'], width, label='HDBT')
    ax.tick_params(left=False)
    ax.set_xscale('log')
    ax.set_xticks([])
    ax.set_xticks([], minor=True)
    ax.set_xticks(geomean_mpki['Total Size'], geomean_mpki['Total Size Text'])


    # Add annotations using iloc
    for i in range(len(geomean_mpki)):
        y_offset = 15
        ax.annotate(geomean_mpki['Total Size Text'].iloc[i], (geomean_mpki['Total Size'].iloc[i], geomean_mpki['Branch Indirect MPKI'].iloc[i]), textcoords="offset points", xytext=(0,y_offset), ha='center')
    
    ax.set_xlabel('Indirect BTB Size', labelpad=25)
    ax.set_ylabel('Indirect Branch MPKI', labelpad=25)
    ax.yaxis.grid()    
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["top"].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    ax.axhline(not_optimized_mpki, 0.025, 0.975, color='blue', linestyle='dashed', lw=4)
    ax.annotate('Non-optimzed indirect MPKI', (geomean_mpki['Total Size'].iloc[1], not_optimized_mpki), textcoords="offset points", xytext=(0,10), ha='center')
    ax.set_ylim([0, 0.5])
    
    ax.legend(prop={'size': 30})
    fig.tight_layout()
    plt.savefig(output_image_indirect_miss, dpi=300)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python plot_performance.py <input_csv>  <baseline_csv>  <output_image_python> <output_image_native> <output_image_indirect_miss>")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    baseline_csv = sys.argv[2]
    output_image_python = sys.argv[3]
    output_image_native = sys.argv[4]
    output_image_indirect_miss = sys.argv[5]
    
    plot_performance(input_csv, baseline_csv, output_image_python, output_image_native, output_image_indirect_miss)
