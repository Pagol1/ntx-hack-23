## Reads EEG data through the serial port
## EEG data is pickled(stored) for future use

import serial
import time
from matplotlib import pyplot as plt
from collections import deque
import pickle

### Parameters ###
WIN_SIZE = 100      # Window size for FFT
BAUD_RATE = 115200
SAMPLE_FREQ = 100
SAMPLE_TIME = 1/SAMPLE_FREQ
RECORD_LEN = 10/SAMPLE_TIME
PLOT_DATA = False
SERIAL_PORT = '/dev/ttyACM0'
##################

def read_to_volt(read):
    return 5*read/1024

def plot_sig(fig, data):
    plt.clf()
    plt.plot(data)
    return fig

ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
time.sleep(2)

if PLOT_DATA:
    fig = plt.figure()

## Fill up intitial buffer
store = []
data = []
for i in range(WIN_SIZE):
    b = ser.readline()              # read a byte string
    string_n = b.decode()           # decode byte string into Unicode  
    string = string_n.rstrip()      # remove \n and \r
    try:
        volt = read_to_volt(float(string)) # convert string to float
        data.append(volt)                # add to the end of data list
        time.sleep(SAMPLE_TIME)                # wait (sleep) 0.01 seconds
    except ValueError:
        pass

## Spinning till plot is closed
data = deque(data)
plt.ion()
plt.show()
try:
    while len(store) < RECORD_LEN:
        b = ser.readline()              # read a byte string
        string_n = b.decode()           # decode byte string into Unicode  
        string = string_n.rstrip()      # remove \n and \r
        try:
            volt = read_to_volt(float(string)) # convert string to float
            data.append(volt)                # add to the end of data list
            store.append(data.popleft())
            # Plot the required data
            if PLOT_DATA:
                fig = plot_sig(fig, list(data))
                plt.draw()
            # Spin Again
                plt.pause(SAMPLE_TIME)
            time.sleep(SAMPLE_TIME)             # wait (sleep) 0.01 seconds
        except ValueError:
            pass
except KeyboardInterrupt:
    pass

ser.close()
print("Data Points Collected: " + str(len(store)))
with open("record.pkl", 'wb') as f:
    pickle.dump(store, f)
