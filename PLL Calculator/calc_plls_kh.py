"""
berechne PLL (L_KH) aus L_DAW (reaper automation) L_KH,ref
NUR MUSIK & PODCAST (kein Lärm)

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
df_mean = df_ref["mean"]
df_std = df_ref["std"]

ref_params = df_mean.columns
for idx, c in enumerate(ref_params):
    print(idx, c)
ref_selected = int(input("Select reference param "))

mean_data = np.array(df_mean[ref_params[ref_selected]])
std_data = np.array(df_std[ref_params[ref_selected]])

df_report = pd.DataFrame(columns=["Proband_in", "L_Aeq_off", "L_Aeq_on", "L_Zeq_off", "L_Zeq_on"])

fig_all, axs_all = plt.subplots(nrows=6, ncols=2, figsize=(10, 15))

#iterate HVs
for p in range(int(num_files/2)):
    pll_rel_off = np.loadtxt(f"plls_relative/hv_{(p+1):02}_off_.txt", delimiter=',')
    pll_rel_on = np.loadtxt(f"plls_relative/hv_{(p+1):02}_on_.txt", delimiter=',')

    # calculate actual PLL
    # TODO add noise to calculation
    pll_kh_off = pll_rel_off + mean_data
    pll_kh_on = pll_rel_on + mean_data

    #######################################
    # calc l_eq
    #######################################

    # load laeq and lzeq refs
    ref_laeq = df_mean["LAeq_dt"]
    ref_lzeq = df_mean["LZeq_dt"]
    ref_laeq_std = df_std["LAeq_dt"]
    ref_lzeq_std = df_std["LZeq_dt"]

    # DIN 45641 says in formula (7) / (12):
    # L_eq = 10 * lg(1/n * SUM(i=1, n, 10^(0.1 * L_eq_i)) ) db
    # calc std the same way
    sum_laeq_off = 0
    sum_laeq_on = 0
    sum_lzeq_off = 0
    sum_lzeq_on = 0

    # std
    sum_laeq_std = 0
    sum_lzeq_std = 0

    for i in range(t_start, t_end):
        sum_laeq_off += pow(10, 0.1 * (ref_laeq[i] + pll_rel_off[i]))
        sum_laeq_on += pow(10, 0.1 * (ref_laeq[i] + pll_rel_on[i]))
        sum_lzeq_off += pow(10, 0.1 * (ref_lzeq[i] + pll_rel_off[i]))
        sum_lzeq_on += pow(10, 0.1 * (ref_lzeq[i] + pll_rel_on[i]))

        # std
        sum_laeq_std += pow(10, 0.1 * (ref_laeq_std[i]))
        sum_lzeq_std += pow(10, 0.1 * (ref_lzeq_std[i]))

    laeq_off = round(10 * math.log(sum_laeq_off / (t_end-t_start), 10), 1)
    laeq_on = round(10 * math.log(sum_laeq_on / (t_end-t_start), 10), 1)
    lzeq_off = round(10 * math.log(sum_lzeq_off / (t_end - t_start), 10), 1)
    lzeq_on = round(10 * math.log(sum_lzeq_on / (t_end - t_start), 10), 1)

    # std
    laeq_std = round(10 * math.log(sum_laeq_std / (t_end - t_start), 10), 1)
    lzeq_std = round(10 * math.log(sum_lzeq_std / (t_end - t_start), 10), 1)

    result = {"Proband_in": (p+1),
              "L_Aeq_off": f"{laeq_off} ± {laeq_std}",
              "L_Aeq_on": f"{laeq_on} ± {laeq_std}",
              "L_Zeq_off": f"{lzeq_off} ± {lzeq_std}",
              "L_Zeq_on": f"{lzeq_on} ± {lzeq_std}" }

    df_report = pd.concat([df_report, pd.DataFrame([result])])

    #####################################

    fig, ax = plt.subplots(figsize=(10, 5))

    # Create time axis (1 seconds interval)
    dt = 1  # 1 s
    time = [i * dt for i in range(185)]

    param = ref_params[ref_selected]

    # latext style label / title
    parts = ["KH"] + param[1:].split("_")
    title = rf"$L_{{{','.join(parts)}}}(t)$"
    ylabel = rf"$L_{{{','.join(parts)}}}\ [dB]$"


    ax.plot(time[t_start:t_end], pll_kh_off[t_start:t_end], label="NC off")
    ax.fill_between(time[t_start:t_end], pll_kh_off[t_start:t_end]-std_data[t_start:t_end],
                    pll_kh_off[t_start:t_end]+std_data[t_start:t_end], alpha=0.3)
    ax.plot(time[t_start:t_end], pll_kh_on[t_start:t_end], label="NC on")
    ax.fill_between(time[t_start:t_end], pll_kh_on[t_start:t_end] - std_data[t_start:t_end],
                    pll_kh_on[t_start:t_end] + std_data[t_start:t_end], alpha=0.3)
    ax.xaxis.set_major_formatter(FuncFormatter(format_time))
    ax.xaxis.set_major_locator(MultipleLocator(30))
    ax.set_xlabel("$t\ [min]$")
    ax.set_ylim([30, 90])
    ax.set_ylabel(ylabel)
    ax.legend()
    fig.suptitle(fr"PLL Proband:in {p + 1} " + title)
    plt.grid(True)
    os.makedirs(f"plots/{param}", exist_ok=True)
    fig.savefig(f"plots/{param}/HV_{p+1}_{param}")
    #plt.show()

    if p != 6:
        if p > 6:
            x = (p-1) // 2
            y = (p-1) % 2
        else:
            x = p // 2
            y = p % 2

        axs_all[x][y].plot(time[t_start:t_end], pll_kh_off[t_start:t_end], label="NC off")
        axs_all[x][y].fill_between(time[t_start:t_end], pll_kh_off[t_start:t_end] - std_data[t_start:t_end],
                        pll_kh_off[t_start:t_end] + std_data[t_start:t_end], alpha=0.3)
        axs_all[x][y].plot(time[t_start:t_end], pll_kh_on[t_start:t_end], label="NC on")
        axs_all[x][y].fill_between(time[t_start:t_end], pll_kh_on[t_start:t_end] - std_data[t_start:t_end],
                        pll_kh_on[t_start:t_end] + std_data[t_start:t_end], alpha=0.3)
        axs_all[x][y].xaxis.set_major_formatter(FuncFormatter(format_time))
        axs_all[x][y].xaxis.set_major_locator(MultipleLocator(30))
        axs_all[x][y].set_xlabel("$t\ [min]$")
        axs_all[x][y].set_ylim([50, 90])
        axs_all[x][y].set_ylabel(ylabel)
        axs_all[x][y].legend()
        axs_all[x][y].set_title(fr"PLL Proband:in {p + 1} " + title)
        axs_all[x][y].grid(True)

fig_all.tight_layout()
fig_all.savefig(f"plots/lkh_all.png")
df_report.to_csv("plots/Leq_report.csv", index=False)
