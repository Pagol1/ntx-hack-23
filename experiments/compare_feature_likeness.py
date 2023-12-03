### Checks our Hypothesis for Music Enjoyment

from matplotlib import pyplot as plt
from matplotlib import colormaps
from scipy.signal import stft
import pickle
import numpy as np
import itertools

FREQ_SAMPLE = 100
mu_dict = {}
var_dict = {}
freq_dict = {}
EB = {}
EA = {}

## Beta Wave: 14-20
## Alpha Wave: 8-13

def wave_idx(freq_range, num_points, freq_idx):
    return int(num_points*freq_idx/freq_range)

names = ['A-DP', 'B-Car', 'C-RS', 'D-KZ', 'E-CB']
rating = []

for name in names:
    with open("record_pb_"+name+".pkl", 'rb') as f:
        data_focus = np.array(pickle.load(f))
    
    (focus_f, focus_t, focus_Zxx) = stft(data_focus, FREQ_SAMPLE)
    cmap = colormaps['viridis']
    mu_dict[name] = [np.mean(np.abs(focus_Zxx), axis=1)]
    var_dict[name] = [np.var(np.abs(focus_Zxx), axis=1)]
    freq_dict[name] = [focus_f]
    EB[name] = [np.sum(mu_dict[name][0][wave_idx(FREQ_SAMPLE/2, len(focus_f), 14) : wave_idx(FREQ_SAMPLE/2, len(focus_f), 20)])]
    EA[name] = [np.sum(mu_dict[name][0][wave_idx(FREQ_SAMPLE/2, len(focus_f), 8) : wave_idx(FREQ_SAMPLE/2, len(focus_f), 13)])]

fig = plt.figure()
plt.title(name)
ax = plt.gca()
for idx in range(1):
    plt.subplot(3, 1, idx+1)
    ax.set_prop_cycle(None)
    for name in names:
        color = next(ax._get_lines.prop_cycler)['color']
        plt.plot(freq_dict[name][idx], mu_dict[name][idx], label=name, color=color)

for idx in range(1):
    plt.subplot(3, 1, idx+2)
    for name in names:
        plt.plot(freq_dict[name][idx], var_dict[name][idx], label=name)
    plt.legend()

for idx in range(1):
    plt.subplot(3, 1, idx+3)
    ax.set_prop_cycle(None)
    for i, name in enumerate(names):
        color = next(ax._get_lines.prop_cycler)['color']
        plt.scatter(i, EB[name][idx]/EA[name][idx], label=name, color=color)
    plt.legend()

plt.show()
