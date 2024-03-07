import glob
import os
import json

from typing import Dict, Union

import pandas as pd


PIDSTAT_NUMERICS = [
    "UID",
    "PID",
    "%usr",
    "%system",
    "%guest",
    "%wait",
    "%CPU",
    "CPU",
    "minflt/s",
    "majflt/s",
    "VSZ",
    "RSS",
    "%MEM",
    "StkSize",
    "StkRef",
    "kB_rd/s",
    "kB_wr/s",
    "kB_ccwr/s",
    "iodelay",
]

def parse_instance_parameters(path: str) -> Dict[str, Union[str, int]]:
    params: Dict[str, Union[str, int]] = {}
    with open(os.path.join(path, "parameters.py"), "r") as f:
        # I don't know any better way to do this
        # I tried executing the code with exec() and then accessing the assigned variables
        # but that doesn't work. Probably because of some namespacing issue...
        # (I can see the variables with the correct values in the debugger, but I can't access them in code
        for line in f:
            if "params =" in line:
                pseudo_json = line.split("=")[1].strip().replace("'", '"')
                params = json.loads(pseudo_json)
    return params


def parse_pidstat_file(pidstat_path):
    node = os.path.basename(pidstat_path).split(".")[0]
    modify_date = pd.to_datetime(int(os.path.getmtime(pidstat_path)), unit="s").date()

    with open(pidstat_path, "r") as pidstat_file:
        snaps = pidstat_file.read().split("\n\n")
        csv_header = snaps[1].splitlines()[0].split()[1:]
        stats_list = [
            line.split() for snap in snaps[1:] for line in snap.splitlines()[1:]
        ]

        pidstat_df = pd.DataFrame(stats_list, columns=csv_header)
        pidstat_df = pidstat_df.loc[pidstat_df["Command"].isin(["dtngod", "dtnrs", "dtnd", "servald"])] 
        pidstat_df[PIDSTAT_NUMERICS] = pidstat_df[PIDSTAT_NUMERICS].apply(pd.to_numeric)
        pidstat_df = pidstat_df[["Time", "%CPU", "RSS"]]

        pidstat_df["Time"] = pd.to_datetime(pidstat_df["Time"])
        pidstat_df["Node"] = node

        dir_path = os.path.dirname(pidstat_path)
        parameters = parse_instance_parameters(dir_path)

        pidstat_df["Software"] = parameters["software"]
        pidstat_df["CLA"] = parameters["cla"]
        pidstat_df["Loss"] = parameters["loss"]
        pidstat_df["# Node"] = parameters["node_count"]
        pidstat_df["# Payloads"] = parameters["num_payloads"]
        pidstat_df["Payload Size"] = parameters["payload_size"]
        pidstat_df["Simulation ID"] = parameters["simInstanceId"]


        return pidstat_df


def parse_pidstat_instance(instance_path):
    print(f"Parsing configuarion {instance_path}")

    pidstat_paths = glob.glob(os.path.join(instance_path, "*.conf_pidstat.log"))

    parsed_pidstats = [parse_pidstat_file(path) for path in pidstat_paths]

    pidstat_df = pd.concat(parsed_pidstats)

    pidstat_df = pidstat_df.sort_values(["Time", "Node"]).reset_index()
    pidstat_df["dt"] = (
        pidstat_df["Time"] - pidstat_df["Time"].iloc[0]
    )

    return pidstat_df


def parse_pidstat(binary_files_path, experiment_ids):
    event_frames = []
    for experiment_id in experiment_ids:
        experiment_paths = glob.glob(os.path.join(binary_files_path, str(experiment_id), "*"))

        parsed_instances = [parse_pidstat_instance(path) for path in experiment_paths]
        df = pd.concat(parsed_instances, sort=False)

        df = df.set_index("dt")
        df = df.groupby(["Software", "CLA", "Loss", "# Node", "# Payloads", "Payload Size"], as_index=True).resample("1S").mean(numeric_only=True)
        df = df.drop(columns=["index", "Loss", "# Node", "# Payloads", "Payload Size"])
        
        event_frames.append(df)

    return pd.concat(event_frames)
