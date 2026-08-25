"""
Plotte L_DAW

C. Lincke, April 2026
"""
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
import math

def format_time(x, pos):
    minutes = int(x // 60)
    seconds = int(x % 60)
    return f"{minutes:02d}:{seconds:02d}"


for i in range(13):
    fig, ax = plt.subplots(figsize=(10, 5))
    l_daw_off = np.loadtxt(f"plls_relative/hv_{i + 1:02}_off_.txt")
    l_daw_on = np.loadtxt(f"plls_relative/hv_{i+1:02}_on_.txt")
    time = range(185) # 3:05 min
    ax.plot(time, l_daw_off, label=f"NC off")
    ax.plot(time, l_daw_on, label=f"NC on")

    ax.set_ylim(-48, 3)
    ax.set_yticks([-45,-40,-35,-30,-25,-20,-15,-10,-5,0])
    ax.xaxis.set_major_formatter(FuncFormatter(format_time))
    ax.xaxis.set_major_locator(MultipleLocator(30))

    ax.set_xlabel("$t\ [min]$")
    ax.set_ylabel("$L_{DAW}\ [dB]$")
    ax.legend()

    ax.grid(True)
    fig.suptitle("Ergebnis $L_{DAW}(t)$" + f" Hörversuch {i + 1:02}")
    fig.savefig(f"plots/l_daw/hv_{i + 1:02}.png")
