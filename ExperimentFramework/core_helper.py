import pathlib
import traceback
import time
import os
import shutil

import netaddr

import framework

from core.emulator.coreemu import CoreEmu
from core.emulator.data import InterfaceData, LinkOptions
from core.emulator.enumerations import EventTypes
from core.nodes.base import CoreNode, CoreNodeOptions
from core.services.coreservices import ServiceManager
from core.xml.corexml import CoreXmlReader

from log_files import collect_logs


def create_session(_id, dtn_software, node_count, cla):

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
        node = session.add_node(CoreNode, name=f"n{node_num}", options=CoreNodeOptions(model="prouter"))

        session.services.add_services(node, node.model, ["DefaultRoute", "bwm-ng", "pidstat", dtn_software])
        service = session.services.get_service(node.id, dtn_software, default_service=True)
        service.config_data['cla'] = cla

        nodes.append(node)

    ip_netmask = "24"
    link_options = LinkOptions(bandwidth=54_000_000, delay=800, jitter=200, loss=10)
    for node_a, node_b in zip(nodes[:-1], nodes[1:]):
        ip1 = f"10.0.{node_a.id}.1"
        ip2 = f"10.0.{node_a.id}.2"

        iface1 = InterfaceData(ip4=ip1, ip4_mask=ip_netmask)
        iface2 = InterfaceData(ip4=ip2, ip4_mask=ip_netmask)

        session.add_link(node_a.id, node_b.id, iface1, iface2, link_options)

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
