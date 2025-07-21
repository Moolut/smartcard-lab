import matplotlib.pyplot as plt  # Add support for drawing figures
import load_traces  # Loads traces
from scipy import signal

def butter_highpass(cutoff, fs, order=6):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y
    
def butter_lowpass(cutoff, fs, order=6):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

# LOAD DATA AND TRACES
# open input file (path defined in load_traces)
input_data = load_traces.load_traces()

# Load measured traces into a matrix: trace-number x trace-length
traces = input_data.get_traces()
traces_filtered = butter_lowpass_filter(traces[0], 4800000, 125000000, 6)
#traces_filtered = butter_highpass_filter(traces[0], 4800000, 125000000, 6)

# PLOT FIRST POWER TRACE
plt.figure(1)
plt.plot(traces_filtered, lw=.5)
plt.xlabel('Samples')
plt.xlim(0, traces.shape[1])
plt.ylabel('Power Consumption')
plt.ylim(-500, 500)
plt.grid('on')
plt.title('Power trace')
plt.savefig('power_trace.pdf', format='pdf')

plt.show()
