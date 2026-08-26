"""
Berechne Mittelwerte aus den Messungen mit KU100 und Musik / Podcast
speichert csv für Mittelwerte und plottet alle Ergebnisse
Referenz für spätere Berechnungen (L_KH)

C. Lincke, Mai 2026
"""
import glob, os, re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
import math

measurements = [[2,8]]#[[1, 4, 6, 7, 9]]
plot_params = ["LAeq_dt", "LZeq_dt"]
max_len = 185 # crop all to 185 seconds (3:05)


def format_time(x, pos):
    minutes = int(x // 60)
    seconds = int(x % 60)
    return f"{minutes}:{seconds:02d}"

if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(10, 5))
    # go to dir
    os.chdir("..")
    os.chdir("Messungen XL2")
    os.chdir("messungen Referenzschalldruckpegel")

    for files in measurements:

        # create empty array to store dfs
        data_frames_raw = []

        # load CSVs into dfs
        for f in files:
            match = glob.glob(f"Messung {f} *")
            os.chdir(match[0])
            logfile = glob.glob("*123_Log.csv")
            data_frames_raw.append(pd.read_csv(logfile[0]))
            os.chdir("..")

        data_frames_raw = [df.iloc[:max_len] for df in data_frames_raw]

        print("processing ...")

        # define relevant params
        params = np.array(["LASmax_dt", "LASmin_dt", "LAFmax_dt", "LAFmin_dt", "LAeq_dt", "LAeq", "LAPKmax_dt",
                  "LZSmax_dt", "LZSmin_dt", "LZFmax_dt", "LZFmin_dt", "LZeq_dt", "LZeq", "LZPKmax_dt"])

        # remove everything we dont need
        data_frames = [df[params] for df in data_frames_raw]

        # calculate mean
        # linear = [10 ** (df / 10) for df in data_frames]
        # mean_linear = np.mean(linear, axis=0)
        # mean_level = 10 * np.log10(mean_linear)
        # df_mean = pd.DataFrame(mean_level, columns=params)

        # direct averaging of levels (eww)
        stacked = pd.concat(data_frames, keys=range(len(data_frames)))
        # Compute mean and std per cell
        df_mean = stacked.groupby(level=1).mean()
        df_std = stacked.groupby(level=1).std()

        # concat to single csv
        df_out = pd.concat(
            {"mean": df_mean, "std": df_std},
            axis=1
        )
        # save csv
        os.makedirs("averages", exist_ok=True)
        filename_csv = f"averages/avg_l_kh-15.csv"
        df_out.to_csv(filename_csv, index=False)
        print(f"saved {filename_csv}")

        # make a report
        report = {"LAeq": f"{df_mean.at[max_len-1, 'LAeq']:.1f} ± {df_std.at[max_len-1, 'LAeq']:.1f}",
                  "LZeq": f"{df_mean.at[max_len-1, 'LZeq']:.1f} ± {df_std.at[max_len-1, 'LZeq']:.1f}"}
        df_report = pd.DataFrame(report, index=[0])
        df_report.to_csv("averages/report_l_kh-15.csv", index=False)

        time = np.arange(max_len)

        for p in plot_params:
            # make latex style label
            parts = p[1:].split("_")
            label = rf"$L_{{{','.join(parts)}}}$"
            ax.plot(time, df_mean[p], label=label)
            ax.fill_between(time, df_mean[p] - df_std[p], df_mean[p] + df_std[p], alpha=0.3)

    print("create plot ...")
    ax.set_xlabel(r"$t\ [min]$")
    ax.set_xlim([0, 185])
    ax.set_ylabel(r"$\bar{L}_{KH}\ [dB]$")
    ax.set_ylim([30, 80])
    ax.xaxis.set_major_formatter(FuncFormatter(format_time))
    ax.xaxis.set_major_locator(MultipleLocator(30))

    ax.legend(loc="best")
    ax.grid(True)
    fig.suptitle(r"Referenzschalldruckpegel KH bei $L_{DAW} = -15dB$")  # (title)
    filename_png = f"averages/avg_l_kh-15.png"
    fig.savefig(filename_png, bbox_inches="tight")
    print(f"saved {filename_png}")

