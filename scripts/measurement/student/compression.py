import numpy as np

def compress_traces(traces, num_traces, num_samples, window_size, method='squared'):

    compressed_length = num_samples // window_size
    compressed_traces = np.zeros((num_traces, compressed_length))

    for i in range(compressed_length):
        start_idx = i * window_size
        end_idx = start_idx + window_size
        interval_data = traces[:, start_idx:end_idx]
        
        if method == 'squared':
            compressed_traces[:, i] = np.sum(interval_data**2, axis=1)
        elif method == 'absolute':
            compressed_traces[:, i] = np.sum(np.abs(interval_data), axis=1)
        elif method == 'max':
            compressed_traces[:, i] = np.max(interval_data, axis=1)
        else:
            raise ValueError("Invalid method. Choose 'squared' or 'absolute'.")
    
    return compressed_traces
