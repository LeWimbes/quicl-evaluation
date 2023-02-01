### ENV int node_num "How many nodes should be emulated"
### ENV int size "Size of payload to be sent in bytes"
### ENV int num_payloads "How many payloads should be sent"
### ENV string software "Which DTN software should be used"

import os
import sys
import traceback
import time
import tempfile
import uuid
import pathlib
import shutil
import logging

import framework

from core.emulator.coreemu import CoreEmu
from core.nodes.base import CoreNode
from core.emulator.enumerations import EventTypes
from core.services.coreservices import ServiceManager
from core.xml.corexml import CoreXmlReader

from dtngod import DTN7Go
from forban import Forban
from ibr_dtn import IBRDTN
from log_files import collect_logs


def create_payloads(size, num):
    payload_base_path = tempfile.mkdtemp(dir="/tmp")

    for _ in range(num):
        path = f"{payload_base_path}/{uuid.uuid4()}.file"
        with open(path, "wb") as f:
            f.write(os.urandom(size))

    return payload_base_path


def cleanup_payloads(payload_path):
    shutil.rmtree(payload_path, ignore_errors=True)


def create_session(topo_path, _id, dtn_software):
    coreemu = CoreEmu()
    session = coreemu.create_session(_id=_id)
    session.set_state(EventTypes.DEFINITION_STATE)

    errors = ServiceManager.add_services(pathlib.Path('/root/.coregui/custom_services'))
    if errors:
        print(f"Could not add services: {errors}")
        session.shutdown()
        return None

    file_path = pathlib.Path(topo_path)
    session.clear()
    session.set_state(EventTypes.CONFIGURATION_STATE)
    session.name = file_path.name
    session.file_path = file_path
    CoreXmlReader(session).read(file_path)

    for node in session.nodes.values():
        if type(node) is CoreNode:
            session.services.add_services(node, node.model, ["DefaultRoute", "bwm-ng", "pidstat", dtn_software])

    session.set_state(EventTypes.INSTANTIATION_STATE)
    errors = session.instantiate()
    if errors:
        traceback.print_exception(errors[0])
        session.shutdown()
        return None

    return session


def cleanup_experiment(session, payload_path, should_collect_logs=False):
    # When the experiment is finished, we set the session to
    # DATACOLLECT_STATE and collect the logs.
    # After that, we shutdown the session, cleanup the generated payloads
    # and manually make sure, that all remaining files of the experiments
    # are gone.
    # Finally, we wait another 10 seconds to make sure everyhing is clean.
    if session is not None:
        session.set_state(EventTypes.DATACOLLECT_STATE)
    time.sleep(2)
    if should_collect_logs:
        collect_logs(session.directory)
    if session is not None:
        session.shutdown()
    cleanup_payloads(payload_path)
    os.system("core-cleanup")
    time.sleep(10)

    framework.stop()



if __name__ in ["__main__", "__builtin__"]:
    framework.start()

    # Prepare experiment
    payload_path = create_payloads({{size}}, {{num_payloads}})

    _ch = logging.StreamHandler(sys.stdout)
    # _ch = logging.FileHandler('core_session.log')
    _ch.setLevel(logging.DEBUG)
    _ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger = logging.getLogger()
    logger.addHandler(_ch)
    logger.setLevel(logging.DEBUG)

    session = create_session("/root/.coregui/xmls/quicl_debug.xml", {{simInstanceId}}, "{{software}}")
    if session is None:
        cleanup_experiment(session, payload_path)
        sys.exit(1)

    time.sleep(10)

    # Run the experiment
    software = {{software}}(session)
    software.init_software(1)
    software.send_files(1, payload_path, "n{{node_num}}")
    software.wait_for_arrivals({{node_num}}, {{num_payloads}})
    time.sleep(10)

    cleanup_experiment(session, payload_path, should_collect_logs=True)
