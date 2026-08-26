"""
berechne und plot mittelwert der messungen mit noise
die messungen werden in line 14 ausgewählt

C. Lincke, Mai 2026
"""

import glob
import os
import re
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from functools import reduce

messungen = "white85" # pink or white75 or white85

if messungen == "pink":
    measurements = [[2, 9],
                    [3, 5, 7],
                    [4, 6, 8],
                    [12, 14, 16],
                    [13, 15, 17]]
    labels = ["ohne KH",
              "NC off",
              "NC on",
              "NC off + Ohropax",
              "NC on + Ohropax"]

    ylabel = r"$\bar L_{pink, eq}\ [dB]$"
    title = r"Messung Noise Cancelling $\bar L_{pink, eq}(f)$"
    subtitle = ""
    filename = "ergebnis pink noise"
elif messungen == "white75":
    measurements = [[2, 10],
                    [3, 5, 7],
                    [4, 6, 8],
                    [11, 13, 15],
                    [12, 14, 16]]
    labels = ["ohne KH",
              "NC off",
              "NC on",
              "NC off + Ohropax",
              "NC on + Ohropax"]

    ylabel = r"$\bar L_{white, eq}\ [dB]$"
    title = r"Messung Noise Cancelling $\bar L_{white, eq}(f)$"
    subtitle = "Weißes Rauschen @ 75 dB(A)"
    filename = "ergebnis white noise 75"
elif messungen == "white85":
    measurements = [[2, 9],
                    [3, 5, 7],
                    [4, 6, 8],
                    [10, 12, 14],
                    [11, 13, 15]]
    labels = ["ohne KH",
              "NC off",
              "NC on",
              "NC off + Ohropax",
              "NC on + Ohropax"]

    ylabel = r"$\bar L_{white, eq}\ [dB]$"
    title = r"Messung Noise Cancelling $\bar L_{white, eq}(f)$"
    subtitle = "Weißes Rauschen @ 85 dB(A)"
    filename = "ergebnis white noise 85"

class Plotter:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 5))

    def set_title(self, title, subtitle):
        self.fig.suptitle(title, fontsize=16)  # acts like a title
        self.ax.set_title(subtitle, fontsize=12)  # acts like a subtitle

    def add_graph(self, freqs, mean, std, label):
        self.ax.plot(freqs, mean, label=label)
        self.ax.fill_between(freqs,mean-std,mean+std,alpha=0.3)
        #self.ax.errorbar(freqs, values, yerr=std, label=label)
        # plt.show()

    def make_pretty(self, y_label):
        # Log scale for frequency axis
        self.ax.set_xscale("log")

        # add legend
        self.ax.legend(loc="best")

        # Set cleaner ticks (octave bands)
        octave_ticks = [20, 100, 1000, 10000,
                        20000]  # [31.5, 63.0, 125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0, 16000.0]
        self.ax.set_xticks(octave_ticks)
        self.ax.set_xlim([20, 20000])

        self.ax.set_xlabel(r"$f\ [Hz]$")
        self.ax.set_ylabel(y_label)
        self.ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())

        # Optional: grid for readability
        self.ax.grid(True, which="both", linestyle="--", linewidth=0.5)

        # Rotate labels if needed
        for label in self.ax.get_xticklabels():
            label.set_rotation(45)

    def save(self, filename):
        # Save
        save_dir = "rta_plots"
        os.makedirs(save_dir, exist_ok=True)
        self.fig.savefig(f"{save_dir}/{filename}.png", bbox_inches="tight")

        plt.close(self.fig)

        print(f"Saved {save_dir}/{filename}.png")


def select_and_calc(files):
    # create empty df
    df = pd.DataFrame()

    # load
    for idx, dir in enumerate(files):
        print("load", dir)
        os.chdir(dir)
        logfile = glob.glob("*RTA_3rd_Report.csv")
        if idx == 0:
            df = pd.read_csv(logfile[0]).iloc[:, 3:]  # load file and throw away timestamps
        else:
            df = pd.concat([df, pd.read_csv(logfile[0]).iloc[:, 3:]])
        os.chdir("..")

    print("\nLOAD COMPLETE")

    df_mean = df.mean(axis=0).to_frame().T
    df_std = df.std(axis=0, ddof=0).to_frame().T

    freqs = df_mean.columns
    mean = df_mean.iloc[0]
    std = df_std.iloc[0]
    freqs = np.array(freqs).astype(float)

    return freqs, mean, std


if __name__ == "__main__":

    # init plotter
    plotter_avg = Plotter()

    # go up one dir and list all directories starting with "messung"
    os.chdir("..")
    os.chdir("Messungen XL2")
    if messungen == "pink":
        os.chdir("messungen NC pink noise")
    elif messungen == "white75":
        os.chdir("messungen NC white noise 75")
    elif messungen == "white85":
        os.chdir("messungen NC white noise 85")
    else:
        raise ValueError("Unkown messungen")

    for f_num, label in zip(measurements, labels):
        file_names = []
        for f in f_num:
            file_names += [glob.glob(f"Messung {f} *")[0]]
        freqs, values, sd = select_and_calc(file_names)
        plotter_avg.add_graph(freqs, values, sd, label)

    plotter_avg.make_pretty(ylabel)


    plotter_avg.set_title(title, subtitle)
    plotter_avg.save(filename)