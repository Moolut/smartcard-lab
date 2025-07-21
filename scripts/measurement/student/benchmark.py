import h5py
from dpa_attack import dpa
import numpy as np
import time
from openpyxl import Workbook
from compression import compress_traces


def read_h5_fields(file_path, fields):
    data = {}
    with h5py.File(file_path, 'r') as h5file:
        for field in fields:
            if field in h5file:
                data[field] = h5file[field][:]
    return data


def compare_key(predicted_key):
    # Find differing indices
    master_key = np.array([162., 208., 241.,  36.,  74., 170., 148., 208., 167.,  37.,  79.,  38., 235., 109., 136.,   5.])
    differences = np.where(predicted_key != master_key)[0]
    if len(differences) == 0:
        return True
    else:
        return False



startTrace = 1000
stepSize = 25

numberOfSteps = startTrace // stepSize




wb = Workbook()
ws = wb.active
ws.title = "DPA Attack Benchmark Results"
headers = ["Traces", "Duration", "Success", "Compression Method", "Window Size"]
ws.append(headers)

COMPRESS_METHOD = ['squared','absolute','max']
WINDOW_SIZE = [5,6,7,8,9,10,15,20,25,50] 
COUNTERMEASURES = ["100DUMOPS", "MASKING", "SHUFFLE"]

# Initialize variables to track the highest success rate case
highest_success_rate = 0
best_case_details = None

total_number_of_cases = len(COMPRESS_METHOD) * len(WINDOW_SIZE) * numberOfSteps * len(COUNTERMEASURES) * 2
counter = 0

for countermeasure in COUNTERMEASURES:
    for sample_count in [125000, 62500]:
        
        FILE_PATH = f"../OWN_OS_{countermeasure}_1000traces_{sample_count}samples.h5"
        fields_to_read = ['ciphertext', 'plaintext' , "traces"]
            
        data = read_h5_fields(
                                file_path=FILE_PATH,
                                fields=fields_to_read)
                            
        plaintext = data['plaintext']
        ciphertext = data['ciphertext']
        traces = data['traces']
        successRate = 0
        
        best_case_details = {
                        "mean_time": 0,
                        "success_rate": 0,
                        "method": 0,
                        "window_size": 0,
                        "num_traces": 0  # Save the number of traces for the best case
                    }
        
        for method in COMPRESS_METHOD:
            for window_size in WINDOW_SIZE:
                durations = np.zeros(numberOfSteps)
                results = np.zeros(numberOfSteps)

                for case in range(numberOfSteps):
                    case_traces = traces[stepSize * case:, :]
                    case_plaintext = plaintext[stepSize * case:, :]
                    case_ciphertext = ciphertext[stepSize * case:, :]

                    # print(f"Case {case + 1}: {case_traces.shape[0]} traces for window size {window_size} and method {method}")

                    if window_size > 0:
                        case_traces = compress_traces(case_traces, case_traces.shape[0], case_traces.shape[1], window_size, method=method)

                    start_time = time.time()
                    guessed_key, correlations = dpa(case_plaintext, case_traces, debug=False, showPlot=False)
                    end_time = time.time()

                    duration = end_time - start_time
                    is_correct = compare_key(guessed_key)

                    durations[case] = duration
                    results[case] = is_correct

                    ws.append([case_traces.shape[0], duration, is_correct, method, window_size, countermeasure, sample_count])
                    
                    counter += 1
                    print(f"Progress: {counter} / {total_number_of_cases}")

                meanTime = np.mean(durations)
                successRate = np.mean(results)
                print("\n\n")

                # Check if this is the highest success rate case
                if successRate > highest_success_rate:
                    highest_success_rate = successRate
                    best_case_details = {
                        "mean_time": meanTime,
                        "success_rate": successRate,
                        "method": method,
                        "window_size": window_size,
                        "num_traces": case_traces.shape[0]  # Save the number of traces for the best case
                    }
        

                ws.append(["Mean", meanTime, successRate, method, window_size, countermeasure, sample_count])
        
        ws.append(["Highest Success Rate Case for Countermeasure", countermeasure, sample_count])
        ws.append(["Mean Time", "Success Rate", "Compression Method", "Window Size", "Number of Traces", "Number of Samples", "Countermeasure"])  
        ws.append([
            best_case_details["mean_time"],
            best_case_details["success_rate"],
            best_case_details["method"],
            best_case_details["window_size"],
            best_case_details["num_traces"],
            sample_count,
            countermeasure
        ])

# Append the best case details at the end of the file
ws.append([])
# ws.append(["Highest Success Rate Case"])
# ws.append(["Mean Time", "Success Rate", "Compression Method", "Window Size", "Number of Traces", "Number of Samples"])
# ws.append([
#     best_case_details["mean_time"],
#     best_case_details["success_rate"],
#     best_case_details["method"],
#     best_case_details["window_size"],
#     best_case_details["num_traces"],
#     125000
# ])

output_file = "../results/data/own_os_hardened_dpa_v2.xlsx"
wb.save(output_file)




