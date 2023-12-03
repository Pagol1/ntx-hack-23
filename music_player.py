####### Music Player with Focus-based Recommendation #######
## Reads live EEG data though serial port and analyzes Beta Wave activity
## Swaps tracks when enjoyment (mapped as focus) is low

import serial
import time
from matplotlib import pyplot as plt
from collections import deque
import pickle
import atexit

from threading import Thread
import pygame

from scipy.signal import stft
import numpy as np

### Parameters ###
WINDOW_SIZE = 2000
BAUD_RATE = 115200
SAMPLE_FREQ = 1000
SAMPLE_TIME = 1/SAMPLE_FREQ
SERIAL_PORT = '/dev/ttyACM0'        ## Serial Port to read from
STD_THRESH = 0.8
STD_BASE = None
## Music List ##
# list of tuples: (track_name, file_path)
music_list = []
###################


def read_to_volt(read):
    return 5*read/1024

fig = None
ser = None
data = deque([])
std_log = []
music_list = []

def get_data():
    global ser
    try:
        try:
            b = ser.readline()              # read a byte string
            string_n = b.decode()           # decode byte string into Unicode  
            string = string_n.rstrip()      # remove \n and \r
            volt = read_to_volt(float(string)) # convert string to float
            return volt
        except ValueError:
            return None
    except KeyboardInterrupt:
        return None

@atexit.register
def close_port():
    global ser
    ser.close()
    pygame.mixer.stop()

def open_port():
    global ser
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    time.sleep(2)

def spin_port():
    global data, WINDOW_SIZE, SAMPLE_TIME
    try:
        while True:
            volt = get_data()
            if volt is not None:
                data.append(volt)
                if len(data) > WINDOW_SIZE:
                    data.popleft()
                time.sleep(SAMPLE_TIME)
    except KeyboardInterrupt:
        pass

def check_data():
    global data
    time.sleep(2)
    print(len(data))

def init_fig():
    global fig
    fig = plt.figure()

##################
###   Player   ###
##################

def wait_till_full():
    global data
    while len(data) < WINDOW_SIZE:
        time.sleep(0.1)
        pass

def wave_idx(freq_range, num_points, freq):
    # Map frequency to index
    return int(num_points*freq/freq_range)

def plot_eeg_data():
    global data, std_log, fig
    (f, t, Zxx) = stft(data, SAMPLE_FREQ)
    # Trim to get beta waves [14-20] Hz
    fb = f[wave_idx(SAMPLE_FREQ/2, len(f), 14):wave_idx(SAMPLE_FREQ/2, len(f), 20)]
    Zxxb = np.abs(Zxx[:, wave_idx(SAMPLE_FREQ/2, len(f), 14):wave_idx(SAMPLE_FREQ/2, len(f), 20)])
    # Standard Deviation
    beta_std = np.sqrt( np.var(Zxxb, axis=1) )
    std_log.append(np.mean(beta_std))
    plt.clf()
    plt.plot(t, beta_std)

def start_music(title, mfile):
    pygame.mixer.music.unload()
    if mfile is not None:
        print("Now Playing: " + title)
        pygame.mixer.music.load(mfile)
        pygame.mixer.music.play()
    else:
        print("Calibrating...")

def check_music(calib):
    ## Retrun True if music is to be swapped
    global std_log, STD_THRESH, STD_BASE
    print("Getting stats...")
    mean_std = np.mean(np.array(std_log))
    std_log = []
    if calib:
        # Set the base state
        STD_BASE = mean_std
        print("Baseline: " + str(STD_BASE))
        return True
    else:
        if mean_std < STD_BASE * STD_THRESH:
            print("\tYou like this song! Will keep playing :)")
            return False    # Focus is high
        else:
            print("\tYou didn't like the song. We'll swap to something else :(")
            return True

def stop_music():
    print("Stopping Track...")
    pygame.mixer.music.stop()

def main_loop():
    global fig
    wait_till_full()
    # Get a baseline reading
    try:
        start_music("", None)
        # Time for 10s
        ts = time.time()
        tf = time.time()
        while tf-ts < 1:
            plt.draw()
            plt.pause(SAMPLE_TIME)
            #time.sleep(SAMPLE_TIME)
            tf = time.time()
    except KeyboardInterrupt:
        pass
    check_music(True)
    # Loop over music-list

if __name__ == "__main__":
    init_fig()
    open_port()
    pygame.mixer.init()
    th = Thread(target = spin_port)
    th.start()
    main_loop()
