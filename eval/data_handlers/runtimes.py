import glob
import os
import json

from datetime import datetime
from typing import Dict, List, Union, Tuple

import pandas as pd

import softwares.dtn7go


parsing_functions = {
    "DTN7Go": softwares.dtn7go.parse_bundle_events_instance
}


def parse_instance_parameters(path: str) -> Dict[str, Union[str, int]]:
    params: Dict[str, Union[str, int]] = {}
    with open(path, "r") as f:
        for line in f:
            if "params =" in line:
                pseudo_json = line.split("=")[1].strip().replace("'", '"')
                params = json.loads(pseudo_json)
    return params


def parse_bundle_events_instance(
    instance_path: str,
) -> List[Dict[str, List[Dict[str, Union[str, datetime]]]]]:
    print(f"Parsing {instance_path}", flush=True)
    param_path = os.path.join(instance_path, "parameters.py")

    params = parse_instance_parameters(path=param_path)

    software = params['software']

    return parsing_functions[software](instance_path, params)


def parse_bundle_events(experiment_path: str) -> pd.DataFrame:
    experiment_paths = glob.glob(os.path.join(experiment_path, "*"))

    instance_paths = []
    for experiment_path in experiment_paths:
        instance_paths.extend(glob.glob(os.path.join(experiment_path, "*")))

    parsed_instances = [parse_bundle_events_instance(path) for path in instance_paths]
    bundle_events: List[Dict[str, Union[str, datetime]]] = []
    for instance in parsed_instances:
        for node in instance:
            for _, events in node.items():
                bundle_events += events
    event_frame = pd.DataFrame(bundle_events)
    event_frame = event_frame.sort_values(by="timestamp")

    print("Computing time delta", flush=True)
    time_df = pd.DataFrame()
    for _, instance in event_frame.groupby("Simulation ID"):
        instance_start = instance["timestamp"].iloc[0]
        instance["timestamp_relative"] = instance["timestamp"] - instance_start
        time_df = time_df.append(instance)

    event_frame = time_df

    print("Parsing done", flush=True)

    return event_frame


if __name__ == "__main__":
    event_frame = parse_bundle_events("/research_data/epidemic")
    event_frame.to_csv("/research_data/cadr.csv")
