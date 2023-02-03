from core.nodes.base import CoreNode
from core.services.coreservices import CoreService, ServiceMode

class DTN7rsService(CoreService):
    name: str = "DTN7Rs"
    group: str = "DTN"
    executables: tuple[str, ...] = ("dtnrs", )
    dependencies: tuple[str, ...] = ("DefaultRoute", "bwm-ng", "pidstat")
    dirs: tuple[str, ...] = ()
    configs: tuple[str, ...] = ("dtnrs.toml", )
    startup: tuple[str, ...] = (f'bash -c "RUST_BACKTRACE=full nohup dtnrs -c {configs[0]} &> dtnrs.log &"', )
    validate: tuple[str, ...] = ("pgrep dtnrs", )
    validation_mode: ServiceMode = ServiceMode.NON_BLOCKING
    validation_timer: int = 1
    validation_period: float = 0.5
    shutdown: tuple[str, ...] = ("pkill -9 dtnrs", )
    config_data: dict[str, str] = {"cla": "mtcp"}

    @classmethod
    def generate_config(cls, node: CoreNode, filename: str) -> str:
        cfg =  f"""
nodeid = "{node.name}"
beacon-period = true
generate-status-reports = false
parallel-bundle-processing = false
webport = 3000
workdir = "store_{node.name}"
db = "mem"

[routing]
strategy = "epidemic"

[core]
janitor = "10s"

[convergencylayers]
cla.0.id = "{cls.config_data['cla']}"
cla.0.port = 16163

[endpoints]
local.0 = "incoming"
local.1 = "null"

[discovery]
interval = "2s"
peer-timeout = "20s"

[discovery_destinations]
"""

        discovery_config_template = '''
target.{iface_id}.destination = "{bcast}"
'''

        for iface_id, netif in node.ifaces.items():
            bcast = str(netif.get_ip4().broadcast)

            cfg += discovery_config_template.format(iface_id=iface_id, bcast=bcast)

        return cfg
