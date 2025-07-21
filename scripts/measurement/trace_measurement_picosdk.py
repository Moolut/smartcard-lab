#!/usr/bin/env python3

# The output is a hdf5 file with three datasets (plaintext, ciphertext and traces)
# Each value of plain- and ciphertext is stored as a np.uint8-value
# Each value of the trace is stored as a np.int16-value

from functools import partial
import time
import signal
import sys
import os
import random
import h5py
import numpy as np
import logging
from smartcard.CardService import CardService
from smartcard.util import toBytes
from smartcard.CardType import ATRCardType
from smartcard.CardConnection import CardConnection
from smartcard.CardRequest import CardRequest
from picosdk.ps5000 import ps5000 as ps
from picosdk.functions import adc2mV, assert_pico_ok, mV2adc
import ctypes

###################################################################################################
# configuration start
n_traces  = 200    # number of traces to capture
n_samples = 125000  # number of samples per trace (before falling trigger edge)


# Protection Mode encoded in P1 field
# Select between:
# REFERENCE             :
# DUMMYOPS              :
# SHUFFLE_BIASED        :
# SHUFFLE               :
# SHUFFLE_DUMMYOPS      :
# MASK                  :
# MASK_BIASED           :
# MASK_DUMMYOPS         :
# MASK_SHUFFLE_DUMMYOPS :
# UNPROTECTED           :
protect_mode = "REFERENCE"

# sample_rate = "F_125_MHZ"  # sample rate [S/sec]
sample_rate = "F_250_MHZ"  # sample rate [S/sec]
o_file = "./traces_200.h5"  # output file name

# defines the chunksize of the plaintext dataset in the hdf5 file
chunksize_plaintext = (n_traces, 16)
# defines the chunksize of the ciphertext dataset in the hdf5 file
chunksize_ciphertext = (n_traces, 16)
# defines the chunksize of the traces dataset in the hdf5 file
chunksize_traces = (n_traces, n_samples)

# compression settings for the HDF5 file output
compression           = None  # no compression
compression_opts      = None
# compression         =   "gzip"  # good compression
# compression_opts    =   4
# compression         =   "lzf"  # fast compression
# compression_opts    =   None

# configuration end

###################################################################################################


class ColorFormatter(logging.Formatter):

    okblue = "\033[94m"
    okcyan = "\033[96m"
    okgreen = "\033[92m"
    warning = "\033[93m"
    fail = "\033[91m"
    endc = "\033[0m"
    log_format = "%(asctime)s : %(name)s : %(levelname)s: %(message)s"

    FORMATS = dict()
    FORMATS[logging.DEBUG] = okblue + log_format + endc
    FORMATS[logging.INFO] = log_format
    FORMATS[logging.WARNING] = warning + log_format + endc
    FORMATS[logging.ERROR] = fail + log_format + endc
    FORMATS[logging.CRITICAL] = fail + log_format + endc

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# create a logger
logger = logging.getLogger(os.path.basename(__file__))
formatter = ColorFormatter()
if logger.hasHandlers():
    logger.handlers.clear()
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)


###################################################################################################
def progressbar(iterable, prefix="", size=100):
    len_iterable = len(iterable)
    start_time = time.time()

    def update(index):
        elapsed_time = time.time() - start_time
        percent = (index / len_iterable) * 100
        estimated_time = elapsed_time if index == len_iterable else 0 if percent == 0 else (100 - percent) * (elapsed_time / percent)
        progress = int(size * index / len_iterable)
        status = "%s[%s%s] %i/%i %.1f%% %.1fs" % (prefix, "#" * progress, "-" * (size - progress), index, len_iterable, percent, estimated_time)
        status = status.ljust(os.get_terminal_size(0)[0], " ")
        status += "\r"
        sys.stdout.write(status)
        sys.stdout.flush()

    update(0)
    for i, item in enumerate(iterable):
        yield item
        update(i + 1)
    sys.stdout.write("\n")
    sys.stdout.flush()


###################################################################################################
class SmartCard:
    def connect(self):
        # detect the smart card based on the content of the ATR (card-centric approach)
        protect_mode_dict = {
            "REFERENCE": 0,
            "DUMMYOPS": 1,
            "SHUFFLE_BIASED": 2,
            "SHUFFLE": 3,
            "SHUFFLE_DUMMYOPS": 4,
            "MASK": 5,
            "MASK_BIASED": 6,
            "MASK_DUMMYOPS": 7,
            "MASK_SHUFFLE_DUMMYOPS": 8,
            "UNPROTECTED": 9,
        }
        self.countermeasure = protect_mode_dict[protect_mode]

        logger.info("Initializing card connection...")
        try:
            cardtype = ATRCardType(toBytes("3B 90 11 00"))
            cardrequest = CardRequest(cardType=cardtype)
            self.cardservice = cardrequest.waitforcard()
            logger.info("Card connection established correctly")
        except TimeoutError:
            logger.warning("ERROR: Timeout exceeded")
            sys.exit(0)
        # connect to the card using T0 protocol.
        self.cardservice.connection.connect(CardConnection.T0_protocol)

    def decrypt(self, key):
        # format the command to be sent to the card:
        DECRYPT_KEY  = [0x88, 0x10, int(self.countermeasure), 0, len(key)] + key
        GET_RESPONSE = [0x88, 0xC0, 0x00, 0x00, 0x10]
        # send the commands and retrieve the responses
        # detecting a transmission error
        # signal.alarm(2)
        try:
            time.sleep(0.01)  # this can prevent the transmission error
            response, sw1, sw2 = self.cardservice.connection.transmit(DECRYPT_KEY)  # This function doesn't terminate sometimes
        # wait and try again after a transmission error
        except Exception as exc:
            print(exc)
            response, sw1, sw2 = self.cardservice.connection.transmit(DECRYPT_KEY)
        response, sw1, sw2 = self.cardservice.connection.transmit(GET_RESPONSE)
        return response


###################################################################################################
class HDF5File:
    def init(self, o_file, n_traces, n_samples, chunksize_plaintext, chunksize_ciphertext, chunksize_traces, compression, compression_opts):
        if os.path.isfile(o_file):
            logger.warning("File " + o_file + " already exists, overwriting...")
            os.remove(o_file)
        self.filehandle = h5py.File(o_file, mode="a")

        self.FHplaintext = self.filehandle.create_dataset("plaintext", (n_traces, 16), chunks=chunksize_plaintext, dtype=np.uint8, compression=compression, compression_opts=compression_opts)
        self.FHciphertext = self.filehandle.create_dataset("ciphertext", (n_traces, 16), chunks=chunksize_ciphertext, dtype=np.uint8, compression=compression, compression_opts=compression_opts)
        self.FHtraces = self.filehandle.create_dataset("traces", (n_traces, n_samples), chunks=chunksize_traces, dtype=np.int16, compression=compression, compression_opts=compression_opts)

    def file_close(self):
        self.filehandle.close()

    def add_data(self, plaintext, ciphertext, trace_number, trace_data):
        self.FHplaintext[trace_number, :] = plaintext
        self.FHciphertext[trace_number, :] = ciphertext
        self.FHtraces[trace_number, :] = trace_data


###################################################################################################


class Oscilloscope:
    def __init__(self, nSamples, sampleRate):

        # time base configuration for some selected sampling frequencies
        self.ps5000_timebases = dict()
        self.ps5000_timebases["F_1_GHZ"] = 0
        self.ps5000_timebases["F_500_MHZ"] = 1
        self.ps5000_timebases["F_250_MHZ"] = 0
        self.ps5000_timebases["F_250_MHZ"] = 2
        self.ps5000_timebases["F_125_MHZ"] = 3
        self.ps5000_timebases["F_62_50_MHZ"] = 4
        self.ps5000_timebases["F_25_MHZ"] = 7
        self.ps5000_timebases["F_12_50_MHZ"] = 12
        self.ps5000_timebases["F_6_25_MHZ"] = 22
        self.ps5000_timebases["F_5_MHZ"] = 27
        self.ps5000_timebases["F_2_50_MHZ"] = 52
        self.ps5000_timebases["F_1_25_MHZ"] = 102
        self.ps5000_timebases["F_1_MHZ"] = 127
        self.ps5000_timebases["F_500_KHZ"] = 252
        self.ps5000_timebases["F_250_KHZ"] = 502
        self.ps5000_timebases["F_125_KHZ"] = 1002
        self.ps5000_timebases["F_100_KHZ"] = 1252
        self.ps5000_timebases["F_50_KHZ"] = 2502

        # Create chandle and status ready for use
        self.chandle = ctypes.c_int16()
        self.status = {}

        # Open 5000 series PicoScope
        # Returns handle to chandle for use in future API functions
        self.status["openunit"] = ps.ps5000OpenUnit(ctypes.byref(self.chandle))
        assert_pico_ok(self.status["openunit"])

        # Set up channel A
        # handle = chandle
        self.channel = ps.PS5000_CHANNEL["PS5000_CHANNEL_A"]
        # enabled = 1
        self.coupling_type = 0  # AC=0, DC=1
        self.chARange = ps.PS5000_RANGE["PS5000_500MV"]
        # analogue offset = 0 V
        self.status["setChA"] = ps.ps5000SetChannel(self.chandle, self.channel, 1, self.coupling_type, self.chARange)
        assert_pico_ok(self.status["setChA"])

        # find maximum ADC count value
        # handle = chandle
        # pointer to value = ctypes.byref(maxADC)
        self.maxADC = ctypes.c_int16(32512)

        # Set up single trigger
        # handle = chandle
        # enabled = 1
        source = ps.PS5000_CHANNEL["PS5000_EXTERNAL"]
        self.chEXTRange = ps.PS5000_RANGE["PS5000_5V"]
        threshold = int(mV2adc(500, self.chEXTRange, self.maxADC))
        # trigger directions
        direction = 3  # rising 2 falling 3
        # delay = 0 s
        # auto Trigger = 5000 ms
        self.status["trigger"] = ps.ps5000SetSimpleTrigger(self.chandle, 1, source, threshold, direction, 0, 5000)
        assert_pico_ok(self.status["trigger"])

        # Set number of pre and post trigger samples to be collected
        self.preTriggerSamples = nSamples
        self.postTriggerSamples = 0
        self.maxSamples = self.preTriggerSamples + self.postTriggerSamples

        # Get timebase information
        # handle = chandle
        self.timebase = self.ps5000_timebases[sampleRate]
        # noSamples = maxSamples
        # pointer to timeIntervalNanoseconds = ctypes.byref(timeIntervalns)
        self.oversample = 1
        # pointer to maxSamples = ctypes.byref(returnedMaxSamples)
        # segment index = 0
        timeIntervalns = ctypes.c_float()
        self.returnedMaxSamples = ctypes.c_int32()
        self.status["getTimebase"] = ps.ps5000GetTimebase(self.chandle, self.timebase, self.maxSamples, ctypes.byref(timeIntervalns), self.oversample, ctypes.byref(self.returnedMaxSamples), 0)
        assert_pico_ok(self.status["getTimebase"])

    def arm(self):
        # Run block capture
        # handle = chandle
        # number of pre-trigger samples = preTriggerSamples
        # number of post-trigger samples = PostTriggerSamples
        # timebase = 8 = 80 ns (see Programmer's guide for mre information on timebases)
        # oversample = 1
        # time indisposed ms = None (not needed in the example)
        # segment index = 0
        # lpReady = None (using ps5000IsReady rather than ps5000BlockReady)
        # pParameter = None
        self.status["runBlock"] = ps.ps5000RunBlock(self.chandle, self.preTriggerSamples, self.postTriggerSamples, self.timebase, self.oversample, None, 0, None, None)
        assert_pico_ok(self.status["runBlock"])

    def capture(self):
        # Check for data collection to finish using ps5000IsReady
        ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)
        while ready.value == check.value:
            self.status["isReady"] = ps.ps5000IsReady(self.chandle, ctypes.byref(ready))

        # Create buffers ready for assigning pointers for data collection
        bufferAMax = (ctypes.c_int16 * self.maxSamples)()
        bufferAMin = (ctypes.c_int16 * self.maxSamples)()  # used for downsampling

        # Set data buffer location for data collection from channel A
        # handle = chandle
        source = ps.PS5000_CHANNEL["PS5000_CHANNEL_A"]
        # pointer to buffer max = ctypes.byref(bufferAMax)
        # pointer to buffer min = ctypes.byref(bufferAMin)
        # buffer length = maxSamples
        self.status["setDataBuffersA"] = ps.ps5000SetDataBuffers(self.chandle, source, ctypes.byref(bufferAMax), ctypes.byref(bufferAMin), self.maxSamples)
        assert_pico_ok(self.status["setDataBuffersA"])

        # create overflow loaction
        overflow = ctypes.c_int16(0)
        # create converted type maxSamples
        cmaxSamples = ctypes.c_int32(self.maxSamples)

        # Retried data from scope to buffers assigned above
        # handle = chandle
        # start index = 0
        # pointer to number of samples = ctypes.byref(cmaxSamples)
        # downsample ratio = 1
        # downsample ratio mode = PS5000_RATIO_MODE_NONE
        # pointer to overflow = ctypes.byref(overflow))
        self.status["getValues"] = ps.ps5000GetValues(self.chandle, 0, ctypes.byref(cmaxSamples), 1, 0, 0, ctypes.byref(overflow))
        assert_pico_ok(self.status["getValues"])

        if overflow:
            logger.warning("measurement overshoot change channel range")

        # # convert ADC counts data to mV
        adc2mVChAMax = adc2mV(bufferAMax, self.chARange, self.maxADC)
        return adc2mVChAMax

        # return raw adc count
        # return np.array(bufferAMax, np.int16)

    def stop(self):
        # Stop the scope
        # handle = chandle
        self.status["stop"] = ps.ps5000Stop(self.chandle)
        assert_pico_ok(self.status["stop"])

    def close(self):
        # Close unit Disconnect the scope
        # handle = chandle
        self.status["close"] = ps.ps5000CloseUnit(self.chandle)
        assert_pico_ok(self.status["close"])


###################################################################################################
def signal_handler(start_time, signal, frame):
    logger.warning("\nClosing connections...")
    hdf5file.file_close()
    oscilloscope.close()
    end_time = time.time()
    logger.info("Elapsed time: %f seconds" % (end_time - start_time))
    logger.info("Done!")
    sys.exit(0)


###################################################################################################
logger.info("Starting")
start_time = time.time()

logger.info("Initialization of hdf file")
hdf5file = HDF5File()
hdf5file.init(o_file, n_traces, n_samples, chunksize_plaintext, chunksize_ciphertext, chunksize_traces, compression, compression_opts)
logger.info("Initialization of smartcard")
smartcard = SmartCard()
smartcard.connect()
logger.info("Initialization of oscilloscope")
oscilloscope = Oscilloscope(n_samples, sample_rate)

# connect signal handler
signal.signal(signal.SIGINT, partial(signal_handler, start_time))

# dummy measurements to warm up setup
logger.info("Taking few dummy measurements")
for i in range(3):
    oscilloscope.arm()
    smartcard.decrypt([0 for i in range(16)])
    oscilloscope.capture()

# start collecting power traces
logger.info("Starting capture... ")
for i in progressbar(range(n_traces), prefix="Capturing: ", size=100):

    # generate a new random data vector
    ciphertext_data = [random.randint(0, 255) for x in range(16)]

    # arm the oscilloscope
    oscilloscope.arm()
    # send data to the card to be decrypted
    plaintext_data = smartcard.decrypt(ciphertext_data)
    # plaintext_data = ciphertext_data

    # get the power trace
    trace_data = oscilloscope.capture()

    # save trace, plain-text and cipher-text into an hdf5 file
    hdf5file.add_data(plaintext_data, ciphertext_data, i, trace_data)

# close and exit
logger.info("Closing hdf5 file")
hdf5file.file_close()
logger.info("Closing smartcard connection")
# smartcard.close()
logger.info("Closing oscilloscope connection")
oscilloscope.close()
end_time = time.time()
logger.info("Elapsed time: %f seconds" % (end_time - start_time))
logger.info("Done!")
sys.exit(0)
