### ENV int payload_size "Size of payload to be sent in bytes"
### ENV int num_payloads "How many payloads should be sent"
### ENV string software "Which DTN software should be used"
### ENV string cla "Which CLA to use (if applicalbe)"
### ENV int movement "Mobility model of the nodes"

import os
import sys
import time
import tempfile
import uuid
import logging

import framework
from core_helper import *

from dtngod import DTN7NG
from dtnrs import DTN7Rs
from log_files import collect_logs


def create_payloads(size, num):
    payload_base_path = tempfile.mkdtemp(dir="/tmp")

    for _ in range(num):
        path = f"{payload_base_path}/{uuid.uuid4()}.file"
        with open(path, "wb") as f:
            f.write(os.urandom(size))

    return payload_base_path


if __name__ in ["__main__", "__builtin__"]:
    framework.start()

    _ch = logging.StreamHandler(sys.stdout)
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger = logging.getLogger()
    logger.addHandler(_ch)
    logger.setLevel(logging.INFO)

    # Prepare experiment
    payload_path = create_payloads({{payload_size}}, {{num_payloads}})
    link_movement({{movement}})

    session = create_session_xml({{simInstanceId}}, "/root/.coregui//xmls/quicl_mobile.xml", "{{software}}", "{{cla}}")

    if session is None:
        cleanup_experiment(session, payload_path)
        sys.exit(1)

    time.sleep(20)

    # Run the experiment
    software = {{software}}(session)
    software.init_software(1)
    software.init_software(30)
    software.send_files(1, payload_path, f"n30", {{num_payloads}}, burst_time=60*10)
    software.wait_for_arrivals(30, {{num_payloads}})

    time.sleep(10)

    cleanup_experiment(session, payload_path, should_collect_logs=True, software=software)
