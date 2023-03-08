import glob
import os

from datetime import datetime
from typing import Dict, List, Union


def log_entry_time(line):
    time_string = line.split(' ')[0]
    return datetime.fromtimestamp(float(time_string))


def log_entry_bundle_id(line):
    return line.split('[')[1].split(']')[0]


def parse_node(
    node_path,
    software,
    bps,
    cla,
    loss,
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
                if 'NOTICE BundleCore: Bundle received' in line and "/ibrdtn (local)" in line:  # A bundle is created
                    event = "creation"

                elif 'QueueBundleEvent: New bundle queued' in line and 'dtn://n1/ibrdtn' in line: # A bundle is about to be sent
                    event = "sending"

                elif 'NOTICE BundleEvent: bundle [' in line and 'dtn://n1/ibrdtn received' in line:  # Received bundle
                    if int(node_id[1:]) == int(node_count):
                        event = "delivery"
                    else:
                        event = "reception"

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
                        "Loss": loss,
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
    node_paths = glob.glob(os.path.join(instance_path, "*.conf_ibrdtn.log"))

    parsed_nodes = [
        parse_node(
            node_path=p,
            software=params["software"],
            bps=params["bps"],
            cla=params["cla"],
            loss=params["loss"],
            node_count=params["node_count"],
            num_payloads=params["num_payloads"],
            payload_size=params["payload_size"],
            sim_instance_id=params["simInstanceId"],
        )
        for p in node_paths
    ]
    return parsed_nodes

