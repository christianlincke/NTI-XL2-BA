"""
plotte alle Messergebnisse eines augewählten Vezeichnisses

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

    lvl_csv_found = False
    rta_csv_found = False
    report_csv_found = False

    lvl_frame = None
    rta_frame = None
    report_frame = None

    csv_log_files = glob.glob("*Log.csv")
    for f in csv_log_files:
        if "123" in f:
            lvl_csv_found = True
            print("Pegel LOG csv gefunden: " + f)
            lvl_frame = pd.read_csv(f)
        elif "RTA" in f:
            rta_csv_found = True
            print("RTA LOG csv gefunden: " + f)
            rta_frame = pd.read_csv(f)

    csv_report_files = glob.glob("*123_Report.csv")
    if csv_report_files:
        print("Report CSV gefunden: " + csv_report_files[0])
        report_frame = pd.read_csv(csv_report_files[0])

    if not lvl_csv_found:
        raise FileNotFoundError(f"Kein .csv für die Pegelmessung in '{dir}' gefunden")

    if not rta_csv_found:
        raise FileNotFoundError(f"Kein .csv für die RTA in '{dir}' gefunden")

    os.chdir("..")
    return lvl_frame, rta_frame, report_frame

def plot(lvl_frame, rta_frame, params, title, subtitle, save_dir):

    lvl_frame["Timer"] = pd.to_datetime(lvl_frame["Timer"], format="%H:%M:%S")
    rta_frame["Timer"] = pd.to_datetime(rta_frame["Timer"], format="%H:%M:%S")

    fig, axs = plt.subplots(2, figsize=(10, 8))
    fig.suptitle(f"{title}\n{subtitle}", fontsize=20)

    for p in params:
        parts = p[1:].split("_")
        label = rf"$L_{{{','.join(parts)}}}$"
        axs[0].plot(lvl_frame["Timer"], lvl_frame[p], label=label)

    axs[0].legend()
    axs[0].set_xlabel(r"$t\ [min]$")
    axs[0].set_ylabel(r"$L\ [db]$")
    #axs[0].set_ylim([55, 100])
    axs[0].margins(x=0)
    axs[0].set_title('Level Measurement')
    axs[0].xaxis.set(major_formatter=mdates.DateFormatter("%M:%S"))
    axs[0].grid(True)

    frequencies = list(rta_frame.columns[8:]) # start at index 8 for f0 = 20Hz
    frequencies_form = [(str(float(f) / 1000) + " k") if (float(f) > 1000) else f for f in frequencies]
    span_data = rta_frame[frequencies]

    mesh = axs[1].pcolormesh(
        rta_frame["Timer"],
        frequencies_form,
        span_data.T,  # transpose so freq is vertical
        shading='auto',
        cmap='viridis',
        vmin=20, # limit lower
        vmax=110 # limit higher
    )
    axs[1].set_title('Spectrum Measurement')
    axs[1].set_xlabel(r"$t\ [min]$")
    axs[1].set_ylabel(r"$f\ [Hz]$")
    axs[1].xaxis.set(major_formatter=mdates.DateFormatter("%M:%S"))
    axs[1].yaxis.set(major_locator=ticker.MaxNLocator(nbins=12))

    cax = fig.add_axes([0.9, 0.075, 0.02, 0.34])  # [left, bottom, width, height]
    cbar = fig.colorbar(mesh, cax=cax)  # create colorbar
    cbar.set_label("[dB]", rotation=0)

    fig.tight_layout(rect=[0, 0, 0.9, 1])

    plt.savefig(f'{save_dir}/{subtitle}.png')

    #plt.show()

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
    # content.sort(key=lambda x: int(re.search(r'\d+', x).group()))

    plot_sel = np.array([])
    report_sel = np.array([])

    # create empty string to store report
    # report_string = ""
    report_list = np.array([])

    for idx, dir in enumerate(content):
        # find Log.txt files
        lvl_frame, rta_frame, report_frame = find_files(dir)

        # if this is the first iteration, ask for values to plot and report
        if idx == 0:
            params = np.array(lvl_frame.columns[3:])
            for i, p in enumerate(params):
                print(i, " ", p)

            # ask for values to plot
            plot_sel = np.array(input("Welchen parameter plotten? ").strip().split(","))
            plot_sel = plot_sel.astype(np.int8)

            # ask for values to report
            report_sel = np.array(input("Welchen parameter reporten? ").strip().split(","))
            report_sel = report_sel.astype(np.int8)
            report_params = params[report_sel]
            report_columns = np.insert(report_params, 0, "Messung")
            report_df = pd.DataFrame(columns=report_columns)

        time.sleep(0.5) # hickups

        # generate title and subtitle
        title = "Schalldruckpegelmessung Lärm" #dir_selected.split("/")[-1]
        subtitle = dir[8:]

        # make a dir to save the plots
        save_dir = "plots_" + "_".join(params[plot_sel])
        os.makedirs(save_dir, exist_ok=True)

        # add report values to data frame
        report_dict = {}
        report_dict["Messung"] = subtitle
        for p in params[report_sel]:
            val = report_frame.iloc[0][p]

            report_dict[p] = val
        report_df.loc[len(report_df)] = report_dict

        # plot data and save it
        plot(lvl_frame, rta_frame, params[plot_sel], title, subtitle, save_dir)

    report_df.to_csv(f"{save_dir}/Report.csv", index=False)

