import glob
import os
import traceback

from datetime import datetime
from typing import Dict, List, Union


def log_entry_time(line, event):
    if event == "creation":
        time_string = line.split(",")[1].strip()
        return datetime.fromtimestamp(float(time_string))

    time_string = line.split()[1].strip()
    return datetime.strptime(time_string, "%H:%M:%S,%f")


def log_entry_bundle_id(line, event):
    if event == "creation":
        return line.split(",")[2].strip().split("/")[-1]

    return line.split("/")[-1]


def parse_node(
    node_path,
    software,
    bps,
    cla,
    node_count,
    num_payloads,
    payload_size,
    sim_instance_id,
) -> Dict[str, List[Dict[str, Union[str, int, datetime]]]]:

    bundles = {}
    node_id = node_path.split("/")[-1].split(".")[0]


    with open(node_path, "r") as f:
        for line in f.readlines():
            try:

                if "n1.conf_forban_insert.log" in node_path:
                    event = "creation"

                else:
                    if '- forban_opportunistic - INFO - local file smaller - from' in line: # A bundle is about to be sent
                        if int(node_id[1:]) != int(node_count):
                            event = "sending"
                        else:
                            continue

                    elif '- forban_opportunistic - INFO - saved local file' in line:  # Received bundle
                        if int(node_id[1:]) == int(node_count):
                            event = "delivery"
                        else:
                            event = "reception"

                    else:
                        continue

                bundle_id = log_entry_bundle_id(line, event)

                events = bundles.get(bundle_id, [])
                events.append(
                    {
                        "Simulation ID": sim_instance_id,
                        "Payload Size": payload_size,
                        "Timestamp": log_entry_time(line, event),
                        "Event": event,
                        "Node": node_id,
                        "Bundle": bundle_id,
                        "Software": software,
                        "Bundles per Second": bps,
                        "CLA": cla,
                        "# Nodes": node_count,
                        "# Payloads": num_payloads,
                    }
                )
                bundles[bundle_id] = events

            except KeyError as err:
                print(f"Key Error: {err}, node: {node_id}, line: {line}", flush=True)
            except ValueError as err:
                print(f"Value Error: {err}, line: {line}", flush=True)
            except BaseException as err:
                print(f"Unexpected {err}", flush=True)
                traceback.print_exception(err)

    return bundles


def parse_bundle_events_instance(
    instance_path: str, params,
) -> List[Dict[str, List[Dict[str, Union[str, datetime]]]]]:
    node_insert_paths = glob.glob(os.path.join(instance_path, "*.conf_forban_insert.log"))
    node_opp_paths = glob.glob(os.path.join(instance_path, "*.conf_forban_var_log_forban_opportunistic.log"))

    parsed_nodes = [
        parse_node(
            node_path=p,
            software=params["software"],
            bps=params["bps"],
            cla=params["cla"],
            node_count=params["node_count"],
            num_payloads=params["num_payloads"],
            payload_size=params["payload_size"],
            sim_instance_id=params["simInstanceId"],
        )
        for p in node_insert_paths + node_opp_paths
    ]
    return parsed_nodes

