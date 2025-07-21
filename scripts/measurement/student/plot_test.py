import h5py
import numpy as np
import matplotlib.pyplot as plt

# Define the compression function
def compress_traces(traces, interval_size):
    num_traces, trace_length = traces.shape
    compressed_length = trace_length // interval_size
    compressed_traces = np.zeros((num_traces, compressed_length))

    for i in range(compressed_length):
        start_idx = i * interval_size
        end_idx = start_idx + interval_size
        compressed_traces[:, i] = np.sum(traces[:, start_idx:end_idx]**2, axis=1)

    return compressed_traces

# Load the HDF5 file
file_path = '../measures/F_250_MHZ/traces_400_125000.h5'  # Replace with your file path
with h5py.File(file_path, 'r') as f:
    plaintext = f['plaintext'][:]  # Assuming 'Plaintext' is the dataset name
    ciphertext = f['ciphertext'][:]
    traces = f['traces'][:]

# Compress the traces
interval_size = 100  # Define the time interval for compression
compressed_traces = compress_traces(traces, interval_size)

# Plot original and compressed traces
plt.figure(figsize=(12, 6))

# Plot one of the original traces
plt.subplot(2, 1, 1)
plt.plot(traces[0], label='Original Trace')
plt.title('Original Trace')
plt.xlabel('Time')
plt.ylabel('Power')
plt.legend()

# Plot the compressed trace
plt.subplot(2, 1, 2)
plt.plot(compressed_traces[0], label='Compressed Trace')
plt.title('Compressed Trace (Sum of Squared Values)')
plt.xlabel('Time Interval')
plt.ylabel('Power (Compressed)')
plt.legend()

plt.tight_layout()
plt.show()
