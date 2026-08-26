"""
converts XL2 log files to csv for ease of use

C. Lincke, April 2026
"""

import os, re, glob
import pandas as pd
from io import StringIO

def extract_log_results(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start_idx = None
    end_idx = None

    # Find start and end markers
    for i, line in enumerate(lines):
        if re.search(r"# .* LOG Results\s*$", line):
            start_idx = i + 1  # Data starts AFTER this line
        elif re.search(r"# .* whole log period", line):
            end_idx = i
            break

    if start_idx is None or end_idx is None:
        print("start_idx: " + str(start_idx))
        print("end_idx: " + str(end_idx))
        raise ValueError("Could not find data section markers in file.")

    if "RTA" in filepath:
        start_idx += 1

    # Extract only data lines
    data_lines = lines[start_idx:end_idx]

    # Convert to DataFrame
    data_str = "".join(data_lines)

    df = pd.read_csv(StringIO(data_str), sep=r"\s+", engine="python")

    if "RTA" in filepath:
        df.drop(df.columns[-2:], axis=1, inplace=True)
        df.columns = ["Date", "Time", "Timer", '6.3', '8.0', '10.0', '12.5', '16.0', '20.0', '25.0', '31.5', '40.0',
                      '50.0', '63.0', '80.0', '100.0', '125.0', '160.0', '200.0', '250.0', '315.0', '400.0', '500.0',
                      '630.0', '800.0', '1000.0', '1250.0', '1600.0', '2000.0', '2500.0', '3150.0', '4000.0', '5000.0',
                      '6300.0', '8000.0', '10000.0', '12500.0', '16000.0', '20000.0']

    df = df[1:]

    return df

def extract_report_results(filepath, columns):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start_idx = None
    end_idx = None

    # Find start and end markers
    for i, line in enumerate(lines):
        if (re.search(r"# Broadband LOG Results over whole log period", line) or
                re.search(r"# RTA LOG Results over the whole log period", line)):
            start_idx = i + 1  # Data starts AFTER this line
        elif re.search(r"#CheckSum", line):
            end_idx = i
            break

    if start_idx is None or end_idx is None:
        print("start_idx: " + str(start_idx))
        print("end_idx: " + str(end_idx))
        raise ValueError("Could not find data section markers in file.")

    # Extract only data lines
    data_lines = lines[start_idx:end_idx]

    # Convert to DataFrame
    data_str = "".join(data_lines)

    df = pd.read_csv(StringIO(data_str), sep=r"\s+", engine="python", names=columns)

    return df

def convert_files(dir, add_offset):
    os.chdir(dir)

    lvl_frame = None
    rta_frame = None
    report_frame = None

    for f in glob.glob("*Log.txt"):
        if "123" in f:
            print("Pegel .txt: " + f)
            lvl_frame = extract_log_results(f)
            report_frame = extract_report_results(f, lvl_frame.columns)
            if add_offset:
                lvl_frame[lvl_frame.select_dtypes(include="number").columns] += 1.7
                report_frame[report_frame.select_dtypes(include="number").columns] += 1.7
            # save csvs
            lvl_frame.to_csv(f[:-4] + ".csv", index=False)
            report_frame.to_csv(f[:-7] + "Report.csv", index=False)
        elif "RTA" in f:
            print("RTA .txt: " + f)
            rta_frame = extract_log_results(f)
            report_frame = extract_report_results(f, rta_frame.columns)
            if add_offset:
                rta_frame[rta_frame.select_dtypes(include="number").columns] += 1.7
                report_frame[report_frame.select_dtypes(include="number").columns] += 1.7
            # save csv
            rta_frame.to_csv(f[:-4] + ".csv", index=False)
            report_frame.to_csv(f[:-7] + "Report.csv", index=False)

    os.chdir("..")

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
    content.sort()

    # values measured with KU100 need correction of 1.7dB
    add_offset = True if input("Apply 1.7dB correction? [y/n]").lower() == "y" else False

    for idx, dir in enumerate(content):
        # find Log.txt files
        convert_files(dir, add_offset)

