### Measurement Scripts

This folder contains the measurement scripts used in the smart card and SIKA labs
by TUEISEC.

In order to record power traces, connect the oscilloscope to the computer and
attach the probe on channel A measurement amplifier output of the smart card.
Additionally, connect the picoscope's external trigger input (EXT) to the
trigger output on the smart card.

The connector names, to attach your BNC to SMB cables, are the following:

|            | SmartCard v3 (STMicro STM32F051) |
| ---------- | -------------------------------- |
| LNA Output | J3                               |
| Trigger    | J4                               |

In order to figure out how many traces you need and how the amplitudes have to set,
you can use the PicoScope-Software. Consider to play around with different sampling frequencies,
the amount of samples per trace and the voltage ranges in order to get the clearest traces.

Before running a measurement please adjust the settings in
`trace_measurement_picosdk.py` to your needs. All constants are defined in `pshelper_picosdk.py`

Then run a measurement by executing:
    python3 trace_measurement_picosdk.py

To plot the first measured trace adjust the trace filename path in load_traces.py and then run:
    python3 plot_trace.py

    Contains the measuring scripts.
  
    trace_measurement_picosdk.py
        Measuring script that records the traces of your AES.
        Please modify the settings in the configuration settings of the main
        function to match the length of you AES encryption.
    
    load_traces.py
        Loads a .h5 file.
    
    plot_trace.py
        Plots the first recorded trace inside the .h5 trace file.
