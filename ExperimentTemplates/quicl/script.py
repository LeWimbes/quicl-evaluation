### ENV int node_num "How many nodes should be emulated"
### ENV int size "Size of payload to be sent in bytes"
### ENV int num_payloads "How many payloads should be sent"
### ENV string software "Which DTN software should be used"

import os
import time
import tempfile
import uuid

import framework

from core.emulator.coreemu import CoreEmu
from core.netns.nodes import CoreNode
from core.enumerations import EventTypes
from core.service import ServiceManager

from dtngod import DTNGod
from log_files import collect_logs


def create_payloads(size, num):
    payload_base_path = tempfile.mkdtemp(dir="/tmp")

    for _ in range(num):
        path = f"{payload_base_path}/{uuid.uuid4()}.file"
        with open(path, "wb") as f:
            f.write(os.urandom(size))

    return payload_base_path


def cleanup_payloads(payload_path):
    os.rmdir(payload_path)


def create_session(topo_path, _id, dtn_software):
    coreemu = CoreEmu()
    session = coreemu.create_session(_id=_id)
    session.set_state(EventTypes.CONFIGURATION_STATE)

    ServiceManager.add_services('/root/.coregui/custom_services')

    session.open_xml(topo_path)

    for obj in session.objects.itervalues():
        if type(obj) is CoreNode:
            session.services.add_services(obj, obj.type, [dtn_software])

    session.instantiate()

    return session


if __name__ in ["__main__", "__builtin__"]:
    framework.start()

    # Prepare experiment
    payload_path = create_payloads({{size}}, {{num_payloads}})
    session = create_session(
        "/topologies/chain/{}.xml".format({{node_num}}), {{simInstanceId}}, "{{software}}")
    time.sleep(10)

    # Run the experiment
    software = {{software}}(session)
    software.send_files("n1", payload_path, "n{{node_num}}")
    software.wait_for_arrivals("n{{node_num}}", {{num_payloads}})
    time.sleep(10)

    # When the experiment is finished, we set the session to
    # DATACOLLECT_STATE and collect the logs.
    # After that, we shutdown the session, cleanup the generated payloads
    # and manually make sure, that all remaining files of the experiments
    # are gone.
    # Finally, we wait another 10 seconds to make sure everyhing is clean.
    session.set_state(EventTypes.DATACOLLECT_STATE)
    time.sleep(2)
    collect_logs(session.session_dir)
    session.shutdown()
    cleanup_payloads()
    os.system("core-cleanup")
    time.sleep(10)

    framework.stop()
