import pathlib
import traceback
import time
import os
import shutil

import framework

from core.emulator.coreemu import CoreEmu
from core.emulator.data import IpPrefixes
from core.emulator.enumerations import EventTypes
from core.nodes.base import CoreNode, Position, CoreNodeOptions
from core.services.coreservices import ServiceManager
from core.xml.corexml import CoreXmlReader

from log_files import collect_logs


def create_session(_id, dtn_software, node_count):
    ip_prefixes = IpPrefixes(ip4_prefix="10.0.0.0/24")

    coreemu = CoreEmu()
    session = coreemu.create_session(_id=_id)

    session.set_state(EventTypes.DEFINITION_STATE)

    errors = ServiceManager.add_services(pathlib.Path('/root/.coregui/custom_services'))
    if errors:
        print(f"Could not add services: {errors}")
        session.shutdown()
        return None

    session.set_state(EventTypes.CONFIGURATION_STATE)

    nodes = []
    for node_num in range(1, node_count + 1):
        position = Position(x=node_num*10, y=node_num*10)

        node = session.add_node(CoreNode, position=position, name=f"n{node_num}", options=CoreNodeOptions(model="prouter"))

        iface1 = ip_prefixes.create_iface(node)
        iface2 = ip_prefixes.create_iface(node)

        session.services.add_services(node, node.model, ["DefaultRoute", "bwm-ng", "pidstat", dtn_software])

        nodes.append((node, iface1, iface2))

    for node_a, node_b in zip(nodes[:-1], nodes[1:]):
        session.add_link(node_a[0].id, node_b[0].id, node_a[2], node_b[1])

    session.set_state(EventTypes.INSTANTIATION_STATE)
    errors = session.instantiate()
    if errors:
        traceback.print_exception(errors[0])
        session.shutdown()
        return None

    return session


def create_session_xml(topo_path, _id, dtn_software):
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
    shutil.rmtree(payload_path, ignore_errors=True)
    os.system("core-cleanup")
    time.sleep(10)

    framework.stop()
