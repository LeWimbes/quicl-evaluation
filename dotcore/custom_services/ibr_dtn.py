from core.nodes.base import CoreNode
from core.services.coreservices import CoreService, ServiceMode

class IbrDtnService(CoreService):
    name: str = "IBRDTN"
    group: str = "DTN"
    executables: tuple[str, ...] = ("dtnd", "dtnsend")
    dependencies: tuple[str, ...] = ()
    dirs: tuple[str, ...] = ("/ibrdtn_inbox", )
    configs: tuple[str, ...] = ('ibrdtn.conf', )
    startup: tuple[str, ...] = ("bash -c 'dtnd -c ibrdtn.conf -D; sleep 2; pkill -INT dtnd; nohup dtnd -v --timestamp -c ibrdtn.conf > ibrdtn_run.log 2>&1 &'", )
    validate: tuple[str, ...] = ("pgrep dtnd" ,)
    validation_mode: ServiceMode = ServiceMode.NON_BLOCKING
    validation_timer: int = 1
    validation_period: float = 0.5
    shutdown: tuple[str, ...] = ("pkill dtnd", )

    @classmethod
    def generate_config(cls, node: CoreNode, filename: str) -> str:
        cfg = '''storage_path = /ibrdtn_inbox
discovery_address = 224.0.0.142
discovery_interval = 2
routing = epidemic
routing_forwarding = yes
net_autoconnect = 10
net_interfaces = '''

        iface_config_template = '''
net_lan{iface_id}_type = tcp
net_lan{iface_id}_interface = {netif.name}
net_lan{iface_id}_port = 4556
'''

        for iface_id in node.ifaces:
            cfg += "lan{} ".format(iface_id)

        for iface_id, netif in node.ifaces.items():
            cfg += iface_config_template.format(**locals())

        return cfg
