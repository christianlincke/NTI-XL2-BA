"""
Berechne Mittelwert (Schalldruckpegel) von mehreren Messungen

C. Lincke, April 2026
"""
import glob, os, re
import numpy as np
import pandas as pd
import math


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

    # print measurements in the selected directoriy
    for idx, dir in enumerate(content):
        print(idx + 1, dir)

    measurements_sel = np.array(input("Select measurements for averaging ").strip().split(",")).astype(np.int8)
    measurements_sel = np.array(content)[measurements_sel - 1]
    num_files = measurements_sel.shape[0]

    # create empty array to store dfs
    data_frames = []

    # load CSVs into dfs
    for dir in measurements_sel:
        print("load", dir)
        os.chdir(dir)
        logfile = glob.glob("*123_Report.csv")
        data_frames.append(pd.read_csv(logfile[0]))
        os.chdir("..")

    print("\nLOAD COMPLETE")

    # get param names
    params = np.array(data_frames[0].columns[3:])

    # create empty dict for average
    average_dict = {}


    dfs_processed = []
    for df, name in zip(data_frames, measurements_sel):
        # drop first 3 columns
        df_trimmed = df.iloc[:, 3:].copy()

        # add Name column
        df_trimmed.insert(0, "Name", name)

        dfs_processed.append(df_trimmed)

    for p in params:
        sum = 0
        valid = True  # assume column is valid unless proven otherwise

        for df in data_frames:
            val = pd.to_numeric(df.iloc[0][p], errors='coerce')

            if pd.isna(val):  # if ANY invalid → reject whole column
                valid = False
                break

            sum += pow(10, 0.1 * val)

        if valid:
            average = round(10 * math.log10(sum / len(data_frames)), 1)
            average_dict[p] = average
        else:
            # skip OR explicitly store NaN
            average_dict[p] = float('nan')  # or just continue

    average_df = pd.DataFrame([average_dict])
    average_df.insert(0, "Name", "Mittelwert")
    dfs_processed.append(average_df)

    final_df = pd.concat(dfs_processed, ignore_index=True)

    # make a nice filename
    filename = "average_Messung"
    meas_sel_str = ""
    for i in measurements_sel:
        meas_sel_str += "_" + i.split(" ")[1]
    filename += meas_sel_str

    # save csv
    os.makedirs("averages", exist_ok=True)
    final_df.to_csv(f"averages/{filename}.csv", index=False)


