import glob
import os

from datetime import datetime
from typing import Dict, List, Union


def log_entry_time(line):
    time_string = line.split('Z')[0].strip()
    return datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%f")


def log_entry_bundle_id(line):
    return line.split(" ")[-1]


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
                if 'INFO  dtn7::core::processing          > Transmission of bundle requested: dtn://n1/' in line:  # A bundle is created
                    event = "creation"

                elif 'INFO  dtn7::core::processing          > Dispatching bundle: dtn://n1/' in line: # A bundle is about to be sent
                    event = "sending"

                elif 'INFO  dtn7::core::processing          > Received new bundle: dtn://n1/' in line:  # Received bundle
                    event = "reception"

                elif 'INFO  dtn7::core::processing          > Received bundle for local delivery: dtn://n1/' in line: # Bundle reached destination
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
    node_paths = glob.glob(os.path.join(instance_path, "*.conf_dtnrs.log"))

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

