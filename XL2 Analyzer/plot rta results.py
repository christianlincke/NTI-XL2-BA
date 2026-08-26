"""
Plottet RTA (Spektrum) Ergebnisse von ausgewählten Messungen
Nur enderegbnisse, also Leq(f) über die gesamte Messdauer

C. Lincke, April 2026
"""


import os, re, glob
import pandas as pd
from io import StringIO
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import time
import numpy as np

def find_files(dir):
    os.chdir(dir)

    report_csv_found = False
    report_frame = None

    csv_report_files = glob.glob("*RTA_3rd_Report.csv")
    if csv_report_files:
        print("Report CSV gefunden: " + csv_report_files[0])
        report_frame = pd.read_csv(csv_report_files[0])
    else:
        raise FileNotFoundError(f"Kein RTA *_Report.csv in '{dir}' gefunden")

    os.chdir("..")
    return report_frame

def plot(freqs, values, title, subtitle, y_lims):
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.suptitle(f"{title}\n{subtitle}")

    ax.plot(freqs, values)

    # Log scale for frequency axis
    ax.set_xscale("log")

    # Set cleaner ticks (octave bands)
    octave_ticks = [20, 100, 1000, 10000, 20000]#[31.5, 63.0, 125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0, 16000.0]
    ax.set_xticks(octave_ticks)
    ax.set_xlim([20,20000])
    if y_lims is not None:
        ax.set_ylim(y_lims)

    ax.set_xlabel("Frequenz")
    ax.set_ylabel(f"Leq [db]")
    ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())

    # Optional: grid for readability
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)

    # Rotate labels if needed
    plt.setp(ax.get_xticklabels(), rotation=45)

    # Save
    save_dir = "rta_plots"
    os.makedirs(save_dir, exist_ok=True)
    plt.savefig(f"{save_dir}/{subtitle}.png", bbox_inches="tight")

    plt.close(fig)


if __name__ == "__main__":
    # go to dir and list all directories starting with "messung"
    os.chdir("..")
    os.chdir("Messungen XL2")
    content = os.listdir()
    content = [
        x for x in content
        if x.lower().startswith("messung") and os.path.isdir(x)
    ]

    # print list and idx
    for idx, dir in enumerate(content):
        print(idx, dir)

    # choose dir by idx
    dir_selected = content[int(input(">> Choose directory by number: "))]
    print("Selected " + dir_selected)

    # change dir, list again
    os.chdir(dir_selected)
    content = os.listdir()
    content = [
        x for x in content
        if x.lower().startswith("messung") and os.path.isdir(x)
    ]
    content.sort(key=lambda x: int(re.search(r'\d+', x).group()))

    y_lims = np.array(input("Limits für die y-Achse").split(",")).astype(int)
    if len(y_lims) != 2:
        print("Ungültige eingabe")
        y_lims = None

    plot_sel = np.array([])
    report_sel = np.array([])

    # create empty string to store report
    # report_string = ""
    report_list = np.array([])

    for dir in content:
        # find Log.txt files
        report_frame = find_files(dir)

        time.sleep(0.1) # hickups

        # generate title and subtitle
        title = "Leq(f)"
        subtitle = dir
        freqs = report_frame.columns[3:]
        values = report_frame.iloc[0][freqs]
        freqs = np.array(freqs).astype(float)

        plot(freqs, values, title, subtitle, y_lims)
