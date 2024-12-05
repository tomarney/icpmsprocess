import os
import pandas as pd
import numpy as np
from numpy.random import randn
from datetime import datetime, timedelta

np.random.seed(42)


def generate_file(file_name, num, is_std):
    time_start = datetime.now() - timedelta(days=2) + timedelta(seconds=80 * num)
    times = [
        (time_start + timedelta(seconds=1.12 * i)).strftime("%H:%M:%S:%f")[:-3]
        for i in range(60)
    ]
    text = ["lorem", "ipsum", "dolor", "sit", "amet"]
    df_list = ["Neptune Analysis Data Report"]
    df_list = df_list + (text * 4) + ["\t\t\t\t\t"]

    data = pd.DataFrame(
        {
            "Cycle": range(1, 61),
            "Time": times,
            "202Hg": 7e-3 + (randn() - 0.5) * 1e-3 + (randn(60) - 0.5) * 1e-2,
            "204Pb": 1.4 + (randn() - 0.5) * 0.005 + (randn(60) - 0.5) * 0.005,
            "206Pb": 24 + (randn() - 0.5) * 0.08 + (randn(60) - 0.5) * 0.02,
            "207Pb": 22 + (randn() - 0.5) * 0.00002 + (randn(60) - 0.5) * 0.02,
            "208Pb": 52 + (randn() - 0.5) * 2 + (randn(60) - 0.5) * 0.1,
        }
    )

    data.iloc[0:29, 2:] *= 1e-6  # make the blank tiny

    # simulate a difference between the standard and the samples
    if not is_std:
        data.iloc[30:, 4] += 2.7  # 206Pb
        data.iloc[30:, 5] += 0.1  # 207Pb
        data.iloc[30:, 6] += 4  # 208Pb

    df_list = df_list + data.to_csv(index=False, sep="\t").split(os.linesep)
    df_list = df_list + ["*** Some more lines"] * 12 + [""] * 2

    with open(file_name, "w") as f:
        f.write("\n".join(df_list))


def generate_run_data(run_len: int = 50) -> None:
    """Generate example run data files"""
    sample_map = []
    std_counter = 1
    ctrl_counter = 1
    smpl_counter = 1

    os.makedirs("example-data", exist_ok=True)

    for i in range(1, run_len + 1):
        file_name = f"S-{i:03d}.exp"

        if i <= 2 or i > run_len - 2 or (i + 3) % 10 == 0:
            sample_map.append([file_name, f"NIST610_{std_counter:03d}", "standard"])
            std_counter += 1
            generate_file(f"example-data/{file_name}", i, is_std=True)
        elif (i + 4) % 20 == 0:
            sample_map.append([file_name, f"NIST612_{ctrl_counter:03d}", "control"])
            ctrl_counter += 1
            generate_file(f"example-data/{file_name}", i, is_std=True)
        else:
            sample_map.append([file_name, f"my_smpl_{smpl_counter:03d}", "sample"])
            smpl_counter += 1
            generate_file(f"example-data/{file_name}", i, is_std=False)

    sample_map_df = pd.DataFrame(
        sample_map, columns=["file_name", "sample_name", "type"]
    )
    sample_map_df.to_csv("example-data/sample_map.csv", index=False)
