import glob
import os

from datetime import datetime
from typing import Dict, List, Union


def log_entry_time(line):
    time_string = line.split(' ')[0].split('"')[1]
    if time_string[-1] == "Z":
        time_string = time_string[:-1]
    return datetime.strptime(time_string, "%H:%M:%S.%f")


def log_entry_bundle_id(line):
    sub_line = line.split("bundle=\"", 1)[1]

    return sub_line.split('"')[0]


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
                if 'level=info msg="Transmission of bundle requested" bundle="dtn://n1/' in line:  # A bundle is created
                    event = "creation"

                elif 'level=info msg="Sending bundle to a CLA (ConvergenceSender)" bundle="dtn://n1/' in line: # A bundle is about to be sent
                    event = "sending"

                elif 'level=info msg="Processing newly received bundle" bundle="dtn://n1/' in line:  # Received bundle
                    event = "reception"

                elif 'level=info msg="Received bundle for local delivery" bundle="dtn://n1/' in line: # Bundle reached destination
                    event = "delivery"

                else:
                    continue

                bundle_id = log_entry_bundle_id(line)

                events = bundles.get(bundle_id, [])
                events.append(
                    {
                        "Simulation ID": sim_instance_id,
                        "Payload Size": payload_size,
                        "Timestamp": log_entry_time(line),
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
                print(f"Unexpected {err}, {type(err)}", flush=True)

    return bundles


def parse_bundle_events_instance(
    instance_path: str, params,
) -> List[Dict[str, List[Dict[str, Union[str, datetime]]]]]:
    print(f"Parsing {instance_path}", flush=True)
    node_paths = glob.glob(os.path.join(instance_path, "*.conf_dtngod.log"))

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
        for p in node_paths
    ]
    return parsed_nodes

