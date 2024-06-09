import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from scipy.stats import gmean

SIZE_DEFAULT = 14
SIZE_LARGE = 16
plt.rc("font", weight="normal")  # controls default font
plt.rc("font", size=SIZE_DEFAULT)  # controls default text sizes
plt.rc("axes", titlesize=SIZE_LARGE)  # fontsize of the axes title
plt.rc("axes", labelsize=SIZE_LARGE)  # fontsize of the x and y labels
plt.rc("xtick", labelsize=SIZE_DEFAULT)  # fontsize of the tick labels
plt.rc("ytick", labelsize=SIZE_DEFAULT)  # fontsize of the tick labels

# def create_plot()

#     # Plot for python programs
#     fig, ax = plt.subplots(figsize=(12, 8))

#     ax.plot(geom_means_python_8['Total Size'], geom_means_python_8['IPC'], marker='o', linestyle='-', label='8-byte row size')
#     ax.plot(geom_means_python_16['Total Size'], geom_means_python_16['IPC'], marker='s', label='16-byte row size')
#     ax.set_xticks(geom_means_python['Total Size'].unique())  # Set x-axis ticks to the total sizes
#     ax.set_xlabel('Total Size (bytes)')
#     ax.set_ylabel('Performance Improvement (IPC)')
#     ax.legend(prop={'size': 20})
#     ax.yaxis.grid()    
#     ax.spines["right"].set_visible(False)
#     ax.spines["left"].set_visible(True)
#     ax.spines["top"].set_visible(False)
#     plt.savefig(output_image_python, dpi=300)


def plot_performance(csv_file):
    # Read the CSV file
    data = pd.read_csv(csv_file)
    data = data[data['Optimized'] == True]
    data['Dispatch Footprint'] = data['Skipped instrs'] / data['Total instrs']
    data['Avg Ex length'] = (data['Total instrs'] - data['Skipped instrs']) / data['Seen bytecodes']
    print(data[['Trace File', 'Avg Ex length', 'Dispatch Footprint']])

    # trace_based = data.sort_values(by= ['Type', 'Trace File', 'Optimized'])
    # print(trace_based)
    # skipped_ins = data.groupby(['Type', 'Optimized'])
    # print(skipped_ins)
    
    # geomeans = data.groupby(['Type', 'Optimized'])['IPC'].apply(gmean).reset_index()
    # geomeans['Trace File'] = geomeans['Type'] + " \n(gmean)"
    # trace_based = pd.concat([trace_based, geomeans], axis=0).reset_index()
    # print(trace_based)
    # optimized_results = trace_based[trace_based['Optimized'] == True]
    # unoptimized_results = trace_based[trace_based['Optimized'] != True]
    
    # Create a column for total size
    # data['Total Size'] = data['Size'].apply(lambda x: int(x.split('_')[0]) * int(x.split('_')[1]))

    # # Calculate geometric mean IPC for each size combination
    # trace_files = data.groupby(['Trace File', 'Size'])['IPC'].apply(gmean).reset_index()
    # geom_means['Total Size'] = geom_means['Size'].apply(lambda x: int(x.split('_')[0]) * int(x.split('_')[1]) * 2)

    # # Split the data into python and native
    # geom_means_python = geom_means[geom_means['Type'] == 'python']
    # geom_means_native = geom_means[geom_means['Type'] == 'native']

    # geom_means = data.groupby(['Trace File', 'Size'])['IPC'].apply(gmean).reset_index()


    # # Separate the data into 8-byte and 16-byte rows
    # geom_means_python_8 = geom_means_python[geom_means_python['Size'].str.startswith('8_')].sort_values(by='Total Size')
    # geom_means_python_16 = geom_means_python[geom_means_python['Size'].str.startswith('16_')].sort_values(by='Total Size')
    # geom_means_native_8 = geom_means_native[geom_means_native['Size'].str.startswith('8_')].sort_values(by='Total Size')
    # geom_means_native_16 = geom_means_native[geom_means_native['Size'].str.startswith('16_')].sort_values(by='Total Size')

    # Plot for python programs
    # fig, ax = plt.subplots(figsize=(18, 8))
    # xs = np.arange(len(optimized_results))
    
    # ax.bar(xs + 0.2, optimized_results['IPC'], 0.4, label='BFM enabled')
    # ax.bar(xs - 0.2, unoptimized_results['IPC'], 0.4, label='BFM disabled')
    # ax.set_xticks(xs, optimized_results['Trace File'])
    # ax.set_xlabel('Benchmark')
    # ax.set_ylabel('IPC')
    # ax.legend(prop={'size': 20})
    # ax.yaxis.grid()    
    # ax.spines["right"].set_visible(False)
    # ax.spines["left"].set_visible(True)
    # ax.spines["top"].set_visible(False)
    # plt.savefig(output_image_python, dpi=300)
    # plt.show()

    # # Plot for native programs
    # plt.figure(figsize=(12, 8))
    # plt.plot(geom_means_native_8['Total Size'], geom_means_native_8['IPC'], marker='o', label='8-byte rows')
    # plt.plot(geom_means_native_16['Total Size'], geom_means_native_16['IPC'], marker='s', label='16-byte rows')
    # plt.xlabel('Total Size (bytes)')
    # plt.ylabel('Performance (IPC)')
    # plt.title('Performance in terms of Geometric Mean IPC (Native Programs)')
    # plt.legend()
    # plt.grid(True)
    # plt.savefig(output_image_native)
    # # plt.show()

if __name__ == "__main__":
    input_csv = sys.argv[1]
    
    plot_performance(input_csv)
