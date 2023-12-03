## Tests our Hypothesis a

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

names = ['su', 'pb', 'yl', 'pn', 'nd']
for name in names:
    with open("record_"+name+"_focus.pkl", 'rb') as f:
        data_focus = np.array(pickle.load(f))

    with open("record_"+name+"_music_c.pkl", 'rb') as f:
        data_music = np.array(pickle.load(f))

    with open("record_"+name+"_music_d.pkl", 'rb') as f:
        data_music_b = np.array(pickle.load(f))
    
    (focus_f, focus_t, focus_Zxx) = stft(data_focus, FREQ_SAMPLE)
    (music_f, music_t, music_Zxx) = stft(data_music, FREQ_SAMPLE)
    (musicb_f, musicb_t, musicb_Zxx) = stft(data_music_b, FREQ_SAMPLE)
    cmap = colormaps['viridis']
    mu_dict[name] = (np.mean(np.abs(focus_Zxx), axis=1), np.mean(np.abs(music_Zxx), axis=1), np.mean(np.abs(musicb_Zxx), axis=1))
    var_dict[name] = (np.var(np.abs(focus_Zxx), axis=1), np.var(np.abs(music_Zxx), axis=1), np.var(np.abs(musicb_Zxx), axis=1))
    freq_dict[name] = (focus_f, music_f, musicb_f)
    EB[name] = (\
            np.sum(mu_dict[name][0][wave_idx(FREQ_SAMPLE/2, len(focus_f), 14) : wave_idx(FREQ_SAMPLE/2, len(focus_f), 20)]), \
            np.sum(mu_dict[name][1][wave_idx(FREQ_SAMPLE/2, len(music_f), 14) : wave_idx(FREQ_SAMPLE/2, len(music_f), 20)]), \
            np.sum(mu_dict[name][2][wave_idx(FREQ_SAMPLE/2, len(musicb_f), 14) : wave_idx(FREQ_SAMPLE/2, len(musicb_f), 20)]), \
        )
    EA[name] = (\
            np.sum(mu_dict[name][0][wave_idx(FREQ_SAMPLE/2, len(focus_f), 8) : wave_idx(FREQ_SAMPLE/2, len(focus_f), 13)]), \
            np.sum(mu_dict[name][1][wave_idx(FREQ_SAMPLE/2, len(music_f), 8) : wave_idx(FREQ_SAMPLE/2, len(music_f), 13)]), \
            np.sum(mu_dict[name][2][wave_idx(FREQ_SAMPLE/2, len(musicb_f), 8) : wave_idx(FREQ_SAMPLE/2, len(musicb_f), 13)]), \
        )

fig = plt.figure()
plt.title(name)
ax = plt.gca()
# cycle = ax._get_lines.prop_cycler.copy()
for idx in range(3):
    plt.subplot(3, 3, idx+1)
    ax.set_prop_cycle(None)
    for name in names:
        color = next(ax._get_lines.prop_cycler)['color']
        ## STFT averaged over time
        plt.plot(freq_dict[name][idx], mu_dict[name][idx], label=name, color=color)
        ## Average Power in Beta Region
        plt.plot(freq_dict[name][idx], len(freq_dict[name][idx])*[np.mean(mu_dict[name][idx][42:60])], label=name, color=color)

for idx in range(3):
    plt.subplot(3, 3, idx+4)
    for name in names:
        ## Variance of the STFT over time
        plt.plot(freq_dict[name][idx], var_dict[name][idx], label=name)
    plt.legend()

for idx in range(3):
    plt.subplot(3, 3, idx+7)
    ax.set_prop_cycle(None)
    for i, name in enumerate(names):
        ## Indicator Function Energy in Beta Waves v/s Alpha Waves
        color = next(ax._get_lines.prop_cycler)['color']
        plt.scatter(i, EB[name][idx]/EA[name][idx], label=name, color=color)
    plt.legend()
plt.show()
