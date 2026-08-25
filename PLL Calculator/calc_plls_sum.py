"""
berechne L_total(t) aus L_DAW, L_KH,ref und L_Lärm
berechnet auch L_eq

C. Lincke, Mai 2026
"""
import glob
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
import math

# CONSTANTS
t_start = 20 # default: 0
t_end = 185 # default: 185

# helper function for formatting
def format_time(x, pos):
    minutes = int(x // 60)
    seconds = int(x % 60)
    return f"{minutes:02d}:{seconds:02d}"

# get all hv log files in "plls_relative/"
csv_log_files = glob.glob("plls_relative/hv*")
num_files = len(csv_log_files)

# find reference files
reference_file = glob.glob("referenzmessungen/avg*")

df_ref = pd.read_csv(reference_file[0], header=[0, 1])
data_kh_mean = df_ref["mean"]["LZeq_dt"]
data_kh_std = df_ref["std"]["LZeq_dt"]

df_laerm_off = pd.read_csv("referenz_laerm/avg_laerm_nc_off_ohropax.csv", header=[0, 1])
df_laerm_on = pd.read_csv("referenz_laerm/avg_laerm_nc_on_ohropax.csv", header=[0, 1])

data_laerm_off_mean = np.array(df_laerm_off["mean"]["LZeq_dt"])
data_laerm_off_std = np.array(df_laerm_off["std"]["LZeq_dt"])
data_laerm_on_mean = np.array(df_laerm_on["mean"]["LZeq_dt"])
data_laerm_on_std = np.array(df_laerm_on["std"]["LZeq_dt"])

df_report = pd.DataFrame(columns=["Proband_in", "L_Zeq_off", "L_Zeq_on", "Delta_L"])

# plot for combined plots
fig_all, axs_all = plt.subplots(nrows=6, ncols=2, figsize=(10, 15))

#iterate HVs
for p in range(int(num_files/2)):
    pll_rel_off = np.loadtxt(f"plls_relative/hv_{(p+1):02}_off_.txt", delimiter=',')
    pll_rel_on = np.loadtxt(f"plls_relative/hv_{(p+1):02}_on_.txt", delimiter=',')

    # calculate actual PLL
    # TODO add noise to calculation
    pll_tot_off = 10 * np.log10((10 ** ( (data_kh_mean - abs(pll_rel_off)) * 0.1) +
                                 10 ** ( data_laerm_off_mean * 0.1) ) )
    pll_tot_on = 10 * np.log10((10 ** ( (data_kh_mean - abs(pll_rel_on)) * 0.1) +
                                10 ** ( data_laerm_on_mean * 0.1) ) )

    #std_off = 10 * np.log10(1 + (10 ** ( (data_kh_std * 0.1) + 10 ** ( data_laerm_off_std * 0.1) ) ) / pll_tot_off)
    #std_on = 10 * np.log10(1 + (10 ** ((data_kh_std * 0.1) + 10 ** (data_laerm_on_std * 0.1))) / pll_tot_on)
    std_off = data_laerm_off_std + data_kh_std
    std_on = data_laerm_on_std + data_kh_std

    # DIN 45641 says in formula (7) / (12):
    # L_eq = 10 * lg(1/n * SUM(i=1, n, 10^(0.1 * L_eq_i)) ) db

    lzeq_off = round(10 * math.log10( np.sum( np.pow(10, pll_tot_off * 0.1) ) / (t_end - t_start) ), 1)
    lzeq_on = round(10 * math.log10( np.sum( np.pow(10, pll_tot_on * 0.1) ) / (t_end - t_start) ), 1)
    lzeq_off_std = round(10 * math.log10( np.sum( np.pow(10, std_off * 0.1) ) / (t_end - t_start) ), 1)
    lzeq_on_std = round(10 * math.log10(np.sum(np.pow(10, std_on * 0.1)) / (t_end - t_start)), 1)

    result = {"Proband_in": (p+1),
              "L_Zeq_off": f"{lzeq_off} ± {lzeq_off_std}",
              "L_Zeq_on": f"{lzeq_on} ± {lzeq_on_std}",
              "Delta_L": f"{(lzeq_on - lzeq_off):.1f} ± {(lzeq_on_std + lzeq_off_std):.1f}",}

    df_report = pd.concat([df_report, pd.DataFrame([result])])

    #####################################

    fig, ax = plt.subplots(figsize=(10, 5))

    # Create time axis (1 seconds interval)
    dt = 1  # 1 s
    time = [i * dt for i in range(185)]

    ax.plot(time[t_start:t_end], pll_tot_off[t_start:t_end], label="NC off")
    ax.fill_between(time[t_start:t_end],
                    pll_tot_off[t_start:t_end] - std_off[t_start:t_end],
                    pll_tot_off[t_start:t_end] + std_off[t_start:t_end],
                    alpha=0.3)

    ax.plot(time[t_start:t_end], pll_tot_on[t_start:t_end], label="NC on")
    ax.fill_between(time[t_start:t_end],
                    pll_tot_on[t_start:t_end] - std_on[t_start:t_end],
                    pll_tot_on[t_start:t_end] + std_on[t_start:t_end],
                    alpha=0.3)

    ax.xaxis.set_major_formatter(FuncFormatter(format_time))
    ax.xaxis.set_major_locator(MultipleLocator(30))
    ax.set_xlabel("$t\ [min]$")
    ax.set_ylim([60, 110])
    ax.set_ylabel(r"$L_{total,eq}\ [dB(Z)]$")
    ax.legend()
    plt.title(r"$L_{total,Zeq}(t)$" + f" Proband:in {p+1} " )
    plt.grid(True)
    os.makedirs(f"plots/total", exist_ok=True)
    plt.savefig(f"plots/total/HV_{(p+1):02}_tot.png")
    #plt.show()


    if p != 6:
        if p > 6:
            x = (p-1) // 2
            y = (p-1) % 2
        else:
            x = p // 2
            y = p % 2

        axs_all[x][y].plot(time[t_start:t_end], pll_tot_off[t_start:t_end], label="NC off")
        axs_all[x][y].fill_between(time[t_start:t_end],
                    pll_tot_off[t_start:t_end] - std_off[t_start:t_end],
                    pll_tot_off[t_start:t_end] + std_off[t_start:t_end],
                    alpha=0.3)

        axs_all[x][y].plot(time[t_start:t_end], pll_tot_on[t_start:t_end], label="NC on")
        axs_all[x][y].fill_between(time[t_start:t_end],
                        pll_tot_on[t_start:t_end] - std_on[t_start:t_end],
                        pll_tot_on[t_start:t_end] + std_on[t_start:t_end],
                        alpha=0.3)

        axs_all[x][y].xaxis.set_major_formatter(FuncFormatter(format_time))
        axs_all[x][y].xaxis.set_major_locator(MultipleLocator(30))
        axs_all[x][y].set_xlabel("$t\ [min]$")
        axs_all[x][y].set_ylim([60, 100])
        axs_all[x][y].set_ylabel(r"$\bar L_{total,eq}\ [dB(Z)]$")
        axs_all[x][y].legend()
        axs_all[x][y].set_title(r"$L_{total,Zeq,dt}(t)$" + f" Proband:in {p + 1} ")
        axs_all[x][y].grid(True)

fig_all.tight_layout()
fig_all.savefig(f"plots/ltotal_all.png")
df_report.to_csv("plots/total_report.csv", index=False)
