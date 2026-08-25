"""
Plottet endergebnisse der berechneten L_KH

C. Lincke, Mai 2026
"""

import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd

# method for calculating mean
# mean of levels or mean of intensities / pressure (converted back to level)
method = "level" # level or int or pres

def calc_stats_intensity(data):
    mean_lin = np.mean(10 ** (data / 10) * 1e-12, axis=0)
    mean_db = 10 * np.log10(mean_lin / 1e-12)

    sum_std = 0
    for i in data:
        sum_std += (10 ** (i / 10) * 1e-12 - mean_lin) ** 2

    std_int = math.sqrt( sum_std / ( len(data) - 1) )
    std_db = 10 * math.log10( std_int / mean_lin)

    return mean_db, abs(std_db)

def calc_stats_pressure(data):
    mean_lin = np.mean(10 ** (data / 20) * 2e-5, axis=0) #/ len(data)
    mean_db = 20 * np.log10(mean_lin / 2e-5)

    sum_std = 0
    for i in data:
        sum_std += (10 ** (i / 20) * 2e-5 - mean_lin) ** 2

    std_int = math.sqrt( sum_std / ( len(data) - 1) )
    std_db = 20 * math.log10( std_int / mean_lin)

    return mean_db, abs(std_db)


def calc_stats_level(data):
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    return mean, std


if __name__ == '__main__':
    df_l_eq = pd.read_csv('plots/Leq_report.csv')
    data_nc_off = np.array([i.strip().split("±")[0] for i in df_l_eq["L_Aeq_off"]]).astype(float)
    data_nc_on = np.array([i.strip().split("±")[0] for i in df_l_eq["L_Aeq_on"]]).astype(float)
    data_delta = data_nc_on - data_nc_off

    if method == "level":
        mean_off, std_off = calc_stats_level(data_nc_off)
        mean_on, std_on = calc_stats_level(data_nc_on)
        mean_delta, std_delta = calc_stats_level(data_delta)
    elif method == "int":
        mean_off, std_off = calc_stats_intensity(data_nc_off)
        mean_on, std_on = calc_stats_intensity(data_nc_on)
        mean_delta, std_delta = calc_stats_intensity(data_delta)
    elif method == "pres":
        mean_off, std_off = calc_stats_pressure(data_nc_off)
        mean_on, std_on = calc_stats_pressure(data_nc_on)
        mean_delta, std_delta = calc_stats_pressure(data_delta)
    else:
        raise ValueError("Method must be either 'level' or 'int'")

    fig, ax1 = plt.subplots(figsize=(10,5))
    #ax2 = plt.twinx(ax1)

    ax1.errorbar(0, mean_off, std_off, label="NC_off", fmt='o', capsize=8, capthick=2, elinewidth=2)
    ax1.errorbar(1, mean_on, std_on, label="NC_on", fmt='o', capsize=8, capthick=2, elinewidth=2)
    """
    ax1.errorbar(2, (mean_on + mean_off) / 2, abs(mean_delta)/2,
                 label="NC_delta", fmt='none', capsize=8, color='r', capthick=2, elinewidth=2)
    ax1.errorbar(
        2,
        (mean_on + mean_off) / 2,
        abs(abs(mean_delta) / 2 - std_delta / 2),
        label="NC_delta",
        fmt='none',
        capsize=5,
        color='r'
    )
    container = ax1.errorbar(
        2,
        (mean_on + mean_off) / 2,
        abs(mean_delta) / 2 + std_delta / 2,
        label="NC_delta",
        fmt='none',
        capsize=5,
        color='r'
    )
    for barlinecol in container[2]:
        barlinecol.set_linestyle(':')
    for cap in container[1]:
        cap.set_linestyle(':')
    """

    ax1.set_xticks([0, 1], [r"$NC\ off$", r"$NC\ on$"]) #, r"$\Delta L$"])
    ax1.set_xlim(-0.5, 1.5)
    ax1.set_ylim(60, 83)
    ax1.set_yticks([60,65,70,75,80])
    ax1.grid()

    print(f"NC off: {mean_off:.1f} ± {std_off:.1f}")
    print(f"NC on: {mean_on:.1f} ± {std_on:.1f}")
    print(f"delta L: {mean_delta:.1f} ± {std_delta:.1f}")

    ax1.set_ylabel(r"$L_{KH,Aeq}\ [dB(A)]$")
    #ax2.set_ylabel(r"$\overline{ \Delta L}_{KH}\ [dB]$", color='r')
    fig.suptitle(r"Mittelwerte $\bar L_{KH,Aeq}$ ") #und $\overline{ \Delta L}_{KH}$")
    #plt.grid()
    plt.show()

    print(f"NC off: {mean_off} ± {std_off}")
    print(f"NC on: {mean_on} ± {std_on}")
    print(f"delta L: {mean_delta} ± {std_delta}")




