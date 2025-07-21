import matplotlib.pyplot as plt  # Add support for drawing figures
import load_traces  # Loads traces

# LOAD DATA AND TRACES
# open input file (path defined in load_traces)

traces_path = './traces_1.h5'
input_data = load_traces.load_traces(traces_path)


# Load measured traces into a matrix: trace-number x trace-length
traces = input_data.get_traces()

# PLOT FIRST POWER TRACE
plt.subplot(2,1,1)
plt.plot(traces[0], lw=.5)
plt.xlabel('Samples')
plt.xlim(0, traces.shape[1])
plt.ylabel('Power Consumption')
plt.ylim(-500, 500)
plt.grid('on')
plt.title('Power trace 1')
plt.savefig('power_trace.pdf', format='pdf')


traces_path = './traces_200.h5'
input_data = load_traces.load_traces(traces_path)


# Load measured traces into a matrix: trace-number x trace-length
traces = input_data.get_traces()

# PLOT FIRST POWER TRACE
plt.subplot(2,1,2)
plt.plot(traces[0], lw=.5)
plt.xlabel('Samples')
plt.xlim(0, traces.shape[1])
plt.ylabel('Power Consumption')
plt.ylim(-500, 500)
plt.grid('on')
plt.title('Power trace 200')
plt.savefig('power_trace.pdf', format='pdf')


plt.show()
