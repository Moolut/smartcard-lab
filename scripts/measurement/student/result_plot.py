import pandas as pd
import matplotlib.pyplot as plt

# Load the Excel file and the specific sheet
file_path = "../results/data/dpa_attack_benchmark4_results.xlsx"  # Replace with the correct file path
sheet_name = "Sheet1"  # Replace with the correct sheet name
data = pd.read_excel(file_path, sheet_name=sheet_name)

# Ensure numeric types for analysis
data['Window Size'] = data['Window Size'].astype(int)
data['Success Rate'] = data['Success Rate'].astype(float)
data['Duration'] = data['Duration'].astype(float)

# Identify the best compression method and window size
best_row = data.loc[data['Success Rate'].idxmax()]
best_method = best_row['Compression Method']
best_window_size = best_row['Window Size']
best_success_rate = best_row['Success Rate']
best_duration = best_row['Duration']

# Plot Success Rate vs. Window Size for each method
plt.figure(figsize=(10, 6))
for method in data['Compression Method'].unique():
    subset = data[data['Compression Method'] == method]
    plt.plot(subset['Window Size'], subset['Success Rate'], marker='o', label=method)

# Highlight the best success rate
plt.annotate(
    f"Best: {best_success_rate:.2f} (Method: {best_method}, Size: {best_window_size})",
    xy=(best_window_size, best_success_rate),
    xytext=(best_window_size + 1, best_success_rate + 0.05),
    arrowprops=dict(facecolor='red', arrowstyle="->"),
    fontsize=10,
    color='red'
)

plt.title('Success Rate vs. Window Size')
plt.xlabel('Window Size')
plt.ylabel('Success Rate')
plt.legend(title='Compression Method')
plt.grid(True)
plt.savefig("../results/plots/success_rate_vs_window_size.png", dpi=300)  # Save the plot

# Plot Duration vs. Window Size for each method
plt.figure(figsize=(10, 6))
for method in data['Compression Method'].unique():
    subset = data[data['Compression Method'] == method]
    plt.plot(subset['Window Size'], subset['Duration'], marker='o', label=method)

# Highlight the best success rate's corresponding duration
plt.annotate(
    f"Best: {best_duration:.2f} sec (Method: {best_method}, Size: {best_window_size})",
    xy=(best_window_size, best_duration),
    xytext=(best_window_size + 1, best_duration + 0.5),
    arrowprops=dict(facecolor='blue', arrowstyle="->"),
    fontsize=10,
    color='blue'
)

plt.title('Average Duration vs. Window Size')
plt.xlabel('Window Size')
plt.ylabel('Duration (seconds)')
plt.legend(title='Compression Method')
plt.grid(True)
plt.savefig("../results/plots/duration_vs_window_size.png", dpi=300)  # Save the plot

# Display the best results
print(f"Best Compression Method: {best_method}")
print(f"Best Window Size: {best_window_size}")
print(f"Best Success Rate: {best_success_rate}")
print(f"Best Duration: {best_duration}")


# Load the Excel file and the first sheet
file_path = '../results/data/dpa_attack_benchmark4_results.xlsx'
data = pd.read_excel(file_path, sheet_name=0)

# Remove rows where 'Traces' contains non-numeric values (like 'Mean')
data = data[pd.to_numeric(data['Traces'], errors='coerce').notna()]

# Convert columns to appropriate data types
data['Traces'] = data['Traces'].astype(int)
data['Success'] = data['Success'].astype(bool)
data['Window Size'] = data['Window Size'].astype(int)

# Filter the data to include only rows where 'Window Size' is 7
filtered_data = data[data['Window Size'] == 7]

# Calculate the average success rate grouped by number of traces and compression method
grouped_data = filtered_data.groupby(['Traces', 'Compression Method'], as_index=False)['Success'].mean()
grouped_data = grouped_data.rename(columns={'Success': 'Average Success Rate'})

# Plot the success rate vs number of traces for each compression method
plt.figure(figsize=(12, 6))

for method in grouped_data['Compression Method'].unique():
    method_data = grouped_data[grouped_data['Compression Method'] == method]
    plt.plot(
        method_data['Traces'], 
        method_data['Average Success Rate'], 
        marker='o', linestyle='-', label=f'Compression Method: {method}'
    )

plt.title('Average Success Rate vs Number of Traces (Window Size = 7)', fontsize=14)
plt.xlabel('Number of Traces', fontsize=12)
plt.ylabel('Average Success Rate', fontsize=12)
plt.xticks(grouped_data['Traces'].unique(), rotation=45)  # Ensure all x-axis values are visible
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(title='Compression Methods')
plt.tight_layout()  # Adjust layout to prevent overlap
plt.savefig("../results/plots/traces_vs_success_rate_by_method.png", dpi=300)  # Save the plot


# Load the Excel files
uncompressed_file_path = '../results/data/dpa_attack_benchmark_results.xlsx'
compressed_file_path = '../results/data/dpa_attack_benchmark4_results.xlsx'

# Load the data
uncompressed_data = pd.read_excel(uncompressed_file_path, sheet_name=0)
compressed_data = pd.read_excel(compressed_file_path, sheet_name=0)

# Ensure numeric types for analysis
uncompressed_data['Traces'] = pd.to_numeric(uncompressed_data['Traces'], errors='coerce').dropna().astype(int)
uncompressed_data['Duration'] = pd.to_numeric(uncompressed_data['Duration'], errors='coerce')

compressed_data = compressed_data[pd.to_numeric(compressed_data['Traces'], errors='coerce').notna()]
compressed_data['Traces'] = compressed_data['Traces'].astype(int)
compressed_data['Duration'] = compressed_data['Duration'].astype(float)
compressed_data['Window Size'] = compressed_data['Window Size'].astype(int)

# Filter compressed data to include only rows with Window Size = 7
compressed_data_filtered = compressed_data[compressed_data['Window Size'] == 7]

# Group the uncompressed data by 'Traces' and calculate average duration
uncompressed_grouped = uncompressed_data.groupby('Traces')['Duration'].mean().reset_index()

# Group the compressed data by 'Traces' and 'Compression Method', calculate average duration
compressed_grouped = compressed_data_filtered.groupby(['Traces', 'Compression Method'])['Duration'].mean().reset_index()

# Plotting the results
plt.figure(figsize=(12, 6))

# Plot uncompressed data
plt.plot(uncompressed_grouped['Traces'], uncompressed_grouped['Duration'], marker='o', label='Uncompressed', color='black')

# Plot compressed data for each method
for method in compressed_grouped['Compression Method'].unique():
    method_data = compressed_grouped[compressed_grouped['Compression Method'] == method]
    plt.plot(method_data['Traces'], method_data['Duration'], marker='o', label=f'Compressed ({method})')

# Plot details
plt.title('Duration of Attack: Uncompressed vs Compressed (Window Size = 7)', fontsize=14)
plt.xlabel('Number of Traces', fontsize=12)
plt.ylabel('Duration (seconds)', fontsize=12)
plt.legend(title='Data Type')
plt.grid(True)
plt.tight_layout()
plt.savefig("../results/plots/compressed_vs_uncompressed_duration.png", dpi=300)  # Save the plot


# Ensure numeric types for success rate analysis
uncompressed_data['Success'] = uncompressed_data['Success'].astype(bool)
compressed_data_filtered['Success'] = compressed_data_filtered['Success'].astype(bool)

# Group the uncompressed data by 'Traces' and calculate average success rate
uncompressed_success_grouped = uncompressed_data.groupby('Traces')['Success'].mean().reset_index()
uncompressed_success_grouped.rename(columns={'Success': 'Success Rate'}, inplace=True)

# Group the compressed data by 'Traces' and 'Compression Method', calculate average success rate
compressed_success_grouped = compressed_data_filtered.groupby(['Traces', 'Compression Method'])['Success'].mean().reset_index()
compressed_success_grouped.rename(columns={'Success': 'Success Rate'}, inplace=True)

# Plotting the success rate results
plt.figure(figsize=(12, 6))

# Plot uncompressed data success rate
plt.plot(uncompressed_success_grouped['Traces'], uncompressed_success_grouped['Success Rate'], marker='o', label='Uncompressed', color='black')

# Plot compressed data success rate for each method
for method in compressed_success_grouped['Compression Method'].unique():
    method_data = compressed_success_grouped[compressed_success_grouped['Compression Method'] == method]
    plt.plot(method_data['Traces'], method_data['Success Rate'], marker='o', label=f'Compressed ({method})')

# Plot details
plt.title('Success Rate: Uncompressed vs Compressed (Window Size = 7)', fontsize=14)
plt.xlabel('Number of Traces', fontsize=12)
plt.ylabel('Success Rate', fontsize=12)
plt.legend(title='Data Type')
plt.grid(True)
plt.tight_layout()
plt.savefig("../results/plots/compressed_vs_uncompressed_succ_rate.png", dpi=300)  # Save the plot



