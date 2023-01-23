from core.nodes.base import CoreNode
from core.services.coreservices import CoreService, ServiceMode

class Dtn7GoService(CoreService):
    name: str = "dtn7-rs"
    group: str = "DTN"
    executables: tuple[str, ...] = ("dtnrs", )
    dependencies: tuple[str, ...] = ("DefaultRoute", )
    dirs: tuple[str, ...] = ()
    configs: tuple[str, ...] = ("dtnrs.toml", )
    startup: tuple[str, ...] = (f'bash -c "RUST_BACKTRACE=full nohup dtnrs -c {configs[0]} &> dtnrs.log &"', )
    validate: tuple[str, ...] = ("pgrep dtnrs", )
    validation_mode: ServiceMode = ServiceMode.NON_BLOCKING
    validation_timer: int = 1
    validation_period: float = 0.5
    shutdown: tuple[str, ...] = ("pkill -9 dtnrs", )

    @classmethod
    def generate_config(cls, node: CoreNode, filename: str) -> str:
        return f"""
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
[discovery]
interval = "2s"
peer-timeout = "20s"
[convergencylayers]
cla.0.id = "mtcp"
cla.0.port = 16163
[endpoints]
local.0 = "incoming"
local.1 = "null"
"""
