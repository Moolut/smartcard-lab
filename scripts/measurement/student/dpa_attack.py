import numpy as np
from vars import HW_S_BOX, S_BOX, HW_8BIT_TABLE
import matplotlib.pyplot as plt

def pearson_correlation(H, T_diff, T_diff_sum_squared, num_traces):

    H_diff = np.array((H - (np.sum(H, 0) / np.double(num_traces))).T, np.double)
    
    R = np.dot(H_diff, T_diff) / np.sqrt(T_diff_sum_squared * np.sum(H_diff**2))
    
    return R


def plot_correlation_overlay(R_correct, key_byte, save_path=None):
    """
    Plot the correlation of the correct key for all bytes overlayed in a single graph.

    Parameters:
        R_correct (list): List of correlation traces for the correct key for each byte.
        key_byte (list): List of key bytes corresponding to the correct key (floats will be converted to integers).
        save_path (str, optional): Path to save the plot.
    """
    plt.figure(figsize=(15, 8))
    for byte_num, R in enumerate(R_correct):
        plt.plot(R, label=f"Byte {byte_num}: 0x{int(key_byte[byte_num]):02X}")  # Cast to int for formatting

    plt.title("Correlation Traces for Correct Keys", fontsize=16)
    plt.xlabel("Sample Index", fontsize=14)
    plt.ylabel("Correlation Coefficient", fontsize=14)
    plt.legend(loc='upper right', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
        

def plot_correlation_heatmap_combined(combined_heatmap, round_key, save_path=None):
    """
    Plot a single heatmap for all bytes and highlight the correct keys.

    Parameters:
        combined_heatmap (np.array): Heatmap data for all bytes (16 x 256).
        round_key (np.array): The estimated round key.
        save_path (str, optional): Path to save the plot.
    """
    plt.figure(figsize=(20, 10))
    plt.title("Combined Heatmap of Correlations for All Bytes", fontsize=16)
    plt.imshow(combined_heatmap, aspect='auto', cmap='viridis', interpolation='nearest')
    plt.colorbar(label="Correlation Coefficient")
    plt.xlabel("Key Guess", fontsize=14)
    plt.ylabel("Byte Index", fontsize=14)

    # Highlight the correct key guesses
    for byte_num, key in enumerate(round_key):
        plt.scatter(int(key), byte_num, color='red', label="Correct Key" if byte_num == 0 else "", zorder=5)

    plt.legend(loc='upper right', fontsize=12)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()


def dpa(plaintext, traces, debug=False,showPlot = False, plot_save_path=None):

    # Initialize the round key array
    round_key = np.zeros(16)
    
    correlations = np.zeros(256)
    
    T_mean = np.mean(traces, axis=0)
    T_diff = traces - T_mean
    T_diff_sum_squared = np.sum(T_diff**2, axis=0)
    
    # Prepare for plotting if enabled
    if showPlot:
        # Set up plotting parameters with increased figure size
        fig, axes = plt.subplots(4, 4, figsize=(30, 20))  # Increased figure size to 25x15
        # fig.suptitle(f"{plot_save_path.replace("../results/corr_graph/", "").replace(".png", "")}", fontsize=20)  # Add a suptitle
        axes = axes.flatten()  # Flatten for easier access
        rMaxValue = 0  # To adjust plot limits later
    
    
    if showPlot:
        R_correct = []
        combined_heatmap = []

    new_code = False
    # Iterate over each byte of the key
    for byte_num in range(16):
        # Generate key guesses (0 to 255)
        key_guesses = np.arange(256)
        
        # Calculate hypothetical power consumption for each key guess
        
        if new_code:
            int1 = np.tile(plaintext[:, byte_num], (256, 1)).T^key_guesses.T
            int2 = S_BOX[int1]
            H = HW_8BIT_TABLE[int1 ^ int2]
        else:
            H = HW_S_BOX[np.tile(plaintext[:, byte_num], (256, 1)).T ^ key_guesses.T]
        
        
        # Compute correlation coefficients between H and traces
        R = pearson_correlation(H, T_diff, T_diff_sum_squared, traces.shape[0])
        R_abs = np.abs(R)
        
        # Find the maximum correlation and its corresponding key byte
        max_corr_idx = np.unravel_index(np.argmax(R_abs), R_abs.shape)
        key_byte = max_corr_idx[0]
        R_max = R[max_corr_idx]
        t_max = max_corr_idx[1]
        # Save the key byte to the round key array
        round_key[byte_num] = key_byte
        correlations[byte_num] = R_max
        
        if showPlot:
            R_correct.append(R[key_byte,:])
            combined_heatmap.append(np.max(R, axis=1))
        
        if debug:
            print(f"Key Byte {byte_num:02d}: 0x{key_byte:02X} | Correlation: {R_max:.4f} | Sample Index: {t_max}")
        
        # Plotting for this byte if enabled
        if showPlot:
            ax = axes[byte_num]
            ax.set_title(f"Byte {byte_num}: 0x{key_byte:02X}", fontsize=20)
            
            # Mask to exclude the correct key byte
            mask = np.ones(256, dtype=bool)
            mask[key_byte] = False
            
            # Calculate the upper and lower curves (max/min correlations of incorrect guesses)
            upper_curve = np.amax(R[mask, :], axis=0)
            lower_curve = np.amin(R[mask, :], axis=0)
            
            # Plot the shaded area between upper and lower curves
            ax.fill_between(range(R.shape[1]), upper_curve, lower_curve, color='0.8', label='Other Keys')
            
            # Plot the correct key's correlation trace
            ax.plot(R[key_byte, :], label='Correct Key')
            
            # Highlight the maximum correlation point
            ax.scatter(t_max, R_max, color='red', label='Max Correlation', zorder=5)
            
            # ax.set_xlabel("Sample Index", fontsize=10)
            # ax.set_ylabel("Correlation Coefficient", fontsize=10)
            
            # Update limits for all plots based on the maximum correlation
            rMaxValue = max(rMaxValue, abs(R_max))
            
    
    
    # Adjust y-axis limits for all plots and finalize the layout
    if showPlot:
        # plot_correlation_overlay(R_correct, round_key, save_path=plot_save_path +"_overlay.png")
        # combined_heatmap = np.array(combined_heatmap)

        # plot_correlation_heatmap_combined(combined_heatmap, round_key, save_path=plot_save_path + "_combined_heatmap.png")
        for ax in axes:
            ax.set_ylim(-rMaxValue, rMaxValue)
        plt.tight_layout()
        plt.savefig(plot_save_path)
        plt.close()

    return (round_key, correlations)


    
    
    
