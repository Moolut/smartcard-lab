import h5py
from dpa_attack import dpa
from AES import compare_result, hexVector2number
from compression import compress_traces
import numpy as np
import time
from openpyxl import Workbook
from collections import Counter
from scipy.signal import correlate
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# SHUFFLE ICIN 110000 SAMPLES
# 10000 traces
# ilk 2000 ve son 100000'i kes geriye 98000 sample kalması lazım
# cliplemeden de çalışıyor ve 125000 sampleda da çalışıyor


MEASUREMENT_FREQUENCY = [250] #[125,250]
MEASUREMENT_TRACE_COUNT =  [6000]#[100,150,200,250,300,350,400,450,500,1000] #[2000] 
MEASUREMENT_SAMPLE_COUNT = [290000]
COMPRESS= True
WINDOW_SIZE = [25]#[3, 5, 7, 10, 25, 50, 100, 200]#[200,100,50,25,10,5,0]
MASTER_KEY = np.array([162., 208., 241.,  36.,  74., 170., 148., 208., 167.,  37.,  79.,  38., 235., 109., 136.,   5.])
MASTER_KEY_SHUFFLE = MASTER_KEY = np.array([44., 210., 105., 247., 55., 67., 128., 46., 94., 100., 7., 169., 250., 128., 201., 1.])

COMPRESS_METHOD = ['squared', 'absolute', "max"] #['absolute'] 

# TODO: Save the predicted key in different settings: SAMPLE_COUNT, TRACE_COUNT, FREQUENCY, WINDOW_SIZE, COMPRESS_METHOD
# TODO: Save plots for each setting and get a optimal setting for the attack depending on the settings



# Read the data from the HDF5 file
def read_h5_fields(file_path, fields):
    data = {}
    with h5py.File(file_path, 'r') as h5file:
        for field in fields:
            if field in h5file:
                data[field] = h5file[field][:]
    return data

def compare_key(predicted_key, master_key, debug=False):
    # Find differing indices
    differences = np.where(predicted_key != master_key)[0]

    # Print differences
    if debug:
        for idx in differences:
            print(f"Byte {idx}: predicted_key = {predicted_key[idx]}, master_key = {master_key[idx]}")

    print(f"Total number of differing bytes: {len(differences)}")
    if len(differences) == 0:
        print("SUCCESS")
        return True
    else:
        print("FAILED")
        return False


def align_traces(traces, reference_trace):
    aligned_traces = []
    for trace in traces:
        correlation = correlate(trace, reference_trace, mode='full')
        shift = np.argmax(correlation) - len(trace) + 1
        aligned_traces.append(np.roll(trace, shift))
    return np.array(aligned_traces)

def preprocess_traces(traces):
    # Normalize traces
    traces = (traces - np.mean(traces, axis=0)) / np.std(traces, axis=0)
    
    # Apply PCA to reduce noise
    pca = PCA(n_components=50)  # Keep 50 principal components
    reduced_traces = pca.fit_transform(traces)
    
    return reduced_traces



# wb = Workbook()
# ws = wb.active
# ws.title = "DPA Attack Results"
# headers = ["Frequency", "Trace Count", "Sample Count", "Compress Method", "Window Size","Success", "Predicted Key", "Key Comparison"]
# ws.append(headers)

all_found_keys = []
ct_1 = 0
pt_1 = 0



for trace_count in MEASUREMENT_TRACE_COUNT:
    print(f"--------------------{trace_count} traces")
    for freq in MEASUREMENT_FREQUENCY:
        print(f"----------------{freq} MHZ")
        for sample_count in MEASUREMENT_SAMPLE_COUNT:
            print(f"------------{sample_count} samples")
            for window_size in WINDOW_SIZE:
                print(f"--------WS: {window_size}")
                for compress_method in COMPRESS_METHOD:
                    print(f"----Compresion Method: {compress_method}")
                    
                    # FILE_PATH = f"../measures/F_{freq}_MHZ/traces_{trace_count}_{sample_count}.h5"

                    
                    # FILE_PATH = f"../correct_REF_SHUFFLE_10000traces_110000samples.h5"
                    # FILE_PATH = f"../ref_SHUFFLE_10000traces.h5"
                    # FILE_PATH = f"../REF_DUMMYOPS_6000traces_350000samples.h5"
                    # fields_to_read = ['ciphertext', 'plaintext',"key" , "traces"]  


                    # data = read_h5_fields(
                    #     file_path=FILE_PATH,
                    #     fields=fields_to_read)
                    
                    FILE_PATH = f"../REF_DUMMYOPS_6000traces_350000samples.h5"
                    FILE_PATH2 = f"../REF_DUMMYOPS_6000traces_350000samples2.h5"
                    fields_to_read = ['ciphertext', 'plaintext', "traces"]  


                    data1 = read_h5_fields(
                        file_path=FILE_PATH,
                        fields=fields_to_read)

                    data2 = read_h5_fields(
                        file_path=FILE_PATH2,
                        fields=fields_to_read)

                    # Concatenate the data from data1 and data2
                    data = {
                        field: np.concatenate((data1[field], data2[field]), axis=0)
                        for field in fields_to_read
                    }
                    

                    plaintext = data['plaintext']
                    ciphertext = data['ciphertext']
                    traces = data['traces']

                    traces = np.array([row[30000:340000] for row in traces])
                    # # Plot a few traces before alignment
                    # plt.figure(figsize=(10, 5))
                    # plt.plot(traces[1], label=f'Trace {1}')
                    # plt.title("Before Alignment")
                    # plt.legend()

                    # Apply alignment
                    # aligned_traces = align_traces(traces, traces[0])
                    # # Plot the same traces after alignment
                    # plt.figure(figsize=(10, 5))
                    # plt.plot(traces[1], label=f'Trace {1}')
                    # plt.title("After Alignment")
                    # plt.legend()
                    # plt.show()
                    ct_1 = ciphertext[0]
                    pt_1 = plaintext[0]
                    
                    print(f"The shape of the traces: {traces.shape}")
                    

                    # print(f"orginal trace shape: {traces.shape}")
                    if COMPRESS and window_size > 1:
                        traces = compress_traces(
                            traces=traces,
                            num_traces=traces.shape[0],
                            num_samples=traces.shape[1], 
                            window_size=window_size,
                            method=compress_method)
                    
                    # traces = preprocess_traces(traces)

                        
                    # print(f"compressed trace shape: {traces.shape}")   
                    
                    # print(f"-------Starting DPA attack for {sample_count} S | {trace_count} T | {freq} MHZ | {compress_method} | WS:{window_size}-------")
                    
                    # start_time = time.time()
                    master_key, correlations = dpa(
                        plaintext=plaintext,
                        traces=traces,  
                        debug=False,
                        showPlot=True,
                        # plot_save_path=f"../results/corr_graph/{compress_method}/W_{window_size}/F_{freq}_T_{trace_count}_S_{sample_count}_W_{window_size}_C_{compress_method}.png")
                        plot_save_path=f"../results/ref_dummy_ops_corr_graph/F_{freq}_T_{trace_count}_S_{sample_count}_W_{window_size}_C_{compress_method}.png")
                    
                    # end_time = time.time()
                    
                    # print(f"Time taken for the attack: {end_time - start_time} seconds")
                    # print(correlations)
                    # print("\n\n\n")
                    # print(f"Key Comparison ")
                    print("Master Key")
                    # prin the key in {hex, hex, hex format without the 0x} and pad with 0
                    for(i,byte) in enumerate(master_key):
                        byte = hex(int(byte))
                        byte = byte[2:]
                        byte = byte.zfill(2)
                        print(byte, end=" ")
                        
                        
                        
                    # print("")
                    
                    # is_correct = compare_key(
                    #     master_key, 
                    #     MASTER_KEY_SHUFFLE,
                    #     debug=False)
                    master_key = hexVector2number(master_key)
                    
                    all_found_keys.append(master_key)
                    
                    print("\n")
                    
                    # convert everything to string
                    
                    # ws.append([str(freq), str(trace_count), str(sample_count), compress_method, str(window_size), str(is_correct), str(master_key), str(is_correct)])                    
                    
                    res = compare_result(
                        ct=data['ciphertext'][0],
                        pt=data['plaintext'][0],
                        key= master_key)
                    
                    if res:
                        print(f"The master key is correct")
                        break
                    else:
                        print(f"The master key is incorrect")
                    
                    
                    # print("\n\n\n")
                    # print(f"IS THE MASTER KEY CORRECT FOR {sample_count} S | {trace_count} T | {freq} MHZ: {res}")
                    
                    # print(f"\n\n---------------------------------DPA attack for {sample_count} samples completed---------------------------------\n\n")
    
grouped_bytes = list(zip(*all_found_keys))

most_common_keys = []

for position_bytes in grouped_bytes:
    
    counts = Counter(position_bytes)
    
    most_common_byte, _ = counts.most_common(1)[0]
    most_common_keys.append(most_common_byte)
    
print(f"Most common keys: {most_common_keys}")

# print("\n\n\n")


if compare_result(ct_1, pt_1, bytes(most_common_keys)):
    print(f"The master key is correct")


# output_file = "../results/dpa_attack_results.xlsx"
# wb.save(output_file)

# print(f"Results saved to {output_file}")

# Most common keys: [49, 198, 150, 71, 25, 83, 77, 35, 0, 7, 65, 34, 139, 98, 79, 112]
"""
31 c6 96 47 19 e1 4d 23 58 07 41 22 8b 62 4f 70

The master key is incorrect
----Compresion Method: absolute
The shape of the traces: (6000, 335000)
Master Key
31 c6 96 47 da 53 4d a2 00 07 2f 22 8b 62 4f 70

The master key is incorrect
----Compresion Method: max
The shape of the traces: (6000, 335000)
Master Key
31 f6 96 47 19 53 4d 23 00 07 54 22 8b 62 4f 70

The master key is incorrect
Most common keys: [49, 198, 150, 71, 25, 83, 77, 35, 0, 7, 65, 34, 139, 98, 79, 112]
"""