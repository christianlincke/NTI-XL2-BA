"""
Plotte L_DAW aller Proband:innen (außer 7) in einer großen Figure

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



fig, axs = plt.subplots(nrows=6,ncols=2, figsize=(10, 15))

for i, p in enumerate([1,2,3,4,5,6,8,9,10,11,12,13]):
    x = i // 2
    y = i % 2

    l_daw_off = np.loadtxt(f"plls_relative/hv_{p:02}_off_.txt")
    l_daw_on = np.loadtxt(f"plls_relative/hv_{p:02}_on_.txt")
    time = range(185) # 3:05 min
    axs[x][y].plot(time, l_daw_off, label=f"NC off")
    axs[x][y].plot(time, l_daw_on, label=f"NC on")

    axs[x][y].set_ylim(-38, 3)
    axs[x][y].set_yticks([-35,-30,-25,-20,-15,-10,-5,0])
    axs[x][y].xaxis.set_major_formatter(FuncFormatter(format_time))
    axs[x][y].xaxis.set_major_locator(MultipleLocator(30))

    axs[x][y].set_xlabel("$t\ [min]$")
    axs[x][y].set_ylabel("$L_{DAW}\ [dB]$")
    axs[x][y].legend()

    axs[x][y].grid(True)
    axs[x][y].set_title(f"Proband:in {p:02}", size=10)
fig.suptitle("Ergebnisse $L_{DAW}(t)$")
plt.tight_layout()
#plt.show()
fig.savefig(f"plots/all_ldaw.png")
