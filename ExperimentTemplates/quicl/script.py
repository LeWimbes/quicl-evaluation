### ENV int node_count "How many nodes should be emulated"
### ENV int payload_size "Size of payload to be sent in bytes"
### ENV int num_payloads "How many payloads should be sent"
### ENV string software "Which DTN software should be used"
### ENV string cla "Which CLA to use (if applicalbe)"

import os
import sys
import time
import tempfile
import uuid
import logging

import framework
from core_helper import *

from dtngod import DTN7Go
from forban import Forban
from ibr_dtn import IBRDTN
from serval import Serval
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

    # Prepare experiment
    payload_path = create_payloads({{payload_size}}, {{num_payloads}})

    _ch = logging.StreamHandler(sys.stdout)
    # _ch = logging.FileHandler('core_session.log')
    _ch.setLevel(logging.DEBUG)
    _ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger = logging.getLogger()
    logger.addHandler(_ch)
    logger.setLevel(logging.DEBUG)

    session = create_session({{simInstanceId}}, "{{software}}", {{node_count}}, "{{cla}}")
    if session is None:
        cleanup_experiment(session, payload_path)
        sys.exit(1)

    time.sleep(10)

    # Run the experiment
    software = {{software}}(session)
    software.init_software(1)
    software.send_files(1, payload_path, "n{{node_count}}")
    software.wait_for_arrivals({{node_count}}, {{num_payloads}})
    time.sleep(10)

    cleanup_experiment(session, payload_path, should_collect_logs=True)
