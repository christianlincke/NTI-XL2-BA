"""
Berechne Mittelwerte aus den Messungen mit KU100 und WFS
speichert csv für Mittelwerte und plottet alle Ergebnisse

Referenz für spätere Messungen

C. Lincke, Mai 2026
"""
import glob, os, re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
import math

measurements = [[1, 12],
                [2, 4, 10],
                [3, 5, 11],
                [13, 15, 18],
                [14, 16, 19]]
labels = ["ohne KH",
          "NC off",
          "NC on",
          "NC off + Ohropax",
          "NC on + Ohropax"]
plot_param = "LZeq_dt"
max_len = 185 # crop all to 185 seconds (3:05)


def format_time(x, pos):
    minutes = int(x // 60)
    seconds = int(x % 60)
    return f"{minutes}:{seconds:02d}"

if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(10, 5))
    # go to "messungen wfs kunstkopf"
    os.chdir("..")
    os.chdir("Messungen XL2")
    os.chdir("messungen wfs kunstkopf")

    df_report = pd.DataFrame(columns=["Setting", "LAeq", "LZeq"])

    for files, label in zip(measurements, labels):

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

        print(f"processing {label} ...")

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

        # make a nice filename
        filename = "avg_"
        for i in files:
            filename += str(i) + "_"
        filename += "Log"

        # concat to single csv
        df_out = pd.concat(
            {"mean": df_mean, "std": df_std},
            axis=1
        )
        # save csv
        os.makedirs("averages", exist_ok=True)
        filename_csv = f"averages/avg_laerm_{label}.csv"
        df_out.to_csv(filename_csv, index=False)
        print(f"saved {filename_csv}")

        # make a report file
        la_eq_mean = np.mean([df.at[184, "LAeq"] for df in data_frames_raw])
        la_eq_std = np.std([df.at[184, "LAeq"] for df in data_frames_raw], ddof=1)
        lz_eq_mean = np.mean([df.at[184, "LZeq"] for df in data_frames_raw])
        lz_eq_std = np.std([df.at[184, "LZeq"] for df in data_frames_raw], ddof=1)

        report = {"Setting": label,
                  "LAeq": f"{la_eq_mean:.1f} ± {la_eq_std:.1f}",
                  "LZeq": f"{lz_eq_mean:.1f} ± {lz_eq_std:.1f}"}
        df_report = pd.concat([df_report, pd.DataFrame([report])])

        time = np.arange(max_len)
        ax.plot(time, df_mean[plot_param], label=label)
        ax.fill_between(time, df_mean[plot_param] - df_std[plot_param], df_mean[plot_param] + df_std[plot_param], alpha=0.3)

    print("create plot ...")
    ax.set_xlabel(r"$t\ [min]$")
    ax.set_xlim([0, 185])
    ax.set_ylabel(r"$\bar{L}_{Lärm,Zeq}\ [dB\ (Z)]$")
    ax.set_ylim([50, 110])
    ax.xaxis.set_major_formatter(FuncFormatter(format_time))
    ax.xaxis.set_major_locator(MultipleLocator(30))

    ax.legend(loc="best")
    ax.grid(True)
    fig.suptitle(r"Referenzschalldruckpegel $\bar{L}_{Lärm,Zeq}(t)$")  # (title)
    filename_png = f"averages/avg_laerm_{plot_param}.png"
    fig.savefig(filename_png, bbox_inches="tight")
    print(f"saved {filename_png}")

    df_report.to_csv("averages/report_laerm.csv", index=False)

