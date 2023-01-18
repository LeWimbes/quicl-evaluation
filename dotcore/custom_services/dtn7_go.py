from core.nodes.base import CoreNode
from core.services.coreservices import CoreService, ServiceMode


class Dtn7GoService(CoreService):
    name: str = "dtn7-go"
    group: str = "DTN"
    executables: tuple[str, ...] = (
        "dtngod",
    )
    dependencies: tuple[str, ...] = ()
    dirs: tuple[str, ...] = ()
    configs: tuple[str, ...] = ("dtngod.toml",)
    startup: tuple[str, ...] = (f'bash -c "nohup dtngod {configs[0]} &> dtngod.log &"',)
    validate: tuple[str, ...] = ("pgrep dtngod",)
    validation_mode: ServiceMode = ServiceMode.NON_BLOCKING
    validation_timer: int = 1
    validation_period: float = 0.5
    shutdown: tuple[str, ...] = ("pkill dtngod",)

    @classmethod
    def generate_config(cls, node: CoreNode, filename: str) -> str:
        return f"""
[core]
store = "store_{node.name}"
node-id = "dtn://{node.name}/"
inspect-all-bundles = true

[logging]
level = "debug"
report-caller = false
format = "json"

[discovery]
ipv4 = true
ipv6 = false
interval = 2

[agents]
[agents.webserver]
address = "localhost:8080"
websocket = true
rest = true

[[listen]]
protocol = "quicl"
endpoint = ":4556"
[routing]
algorithm = "epidemic"
"""
