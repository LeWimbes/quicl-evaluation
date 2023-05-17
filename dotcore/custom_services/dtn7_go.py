from core.nodes.base import CoreNode
from core.services.coreservices import CoreService, ServiceMode

class DTN7GoService(CoreService):
    name: str = "DTN7Go"
    group: str = "DTN"
    executables: tuple[str, ...] = ("dtngod", )
    dependencies: tuple[str, ...] = ("bwm-ng", "pidstat")
    dirs: tuple[str, ...] = ()
    configs: tuple[str, ...] = ("dtngod.toml", )
    startup: tuple[str, ...] = (f'bash -c "nohup dtngod {configs[0]} &> dtngod.log &"', )
    validate: tuple[str, ...] = ("pgrep dtngod", )
    validation_mode: ServiceMode = ServiceMode.NON_BLOCKING
    validation_timer: int = 1
    validation_period: float = 0.5
    shutdown: tuple[str, ...] = ("pkill dtngod", )
    config_data: dict[str, str] = {"cla": "mtcp", "ip": {}}

    @classmethod
    def generate_config(cls, node: CoreNode, filename: str) -> str:
        cfg = f"""
[core]
store = "store_{node.name}"
node-id = "dtn://{node.name}/"
inspect-all-bundles = true

[logging]
level = "info"
report-caller = false
format = "text"

[discovery]
ipv4 = {"false" if cls.config_data['cla'] == "quicl" and "mobile" not in cls.config_data['ip'] else "true"}
ipv6 = false
interval = 2

[agents]
[agents.webserver]
address = "localhost:8080"
websocket = true
rest = true

[cron]
check-bundles = "10s"
clean-store = "10m"
clean-id = "1h"

[[listen]]
protocol = "{cls.config_data['cla']}"
endpoint = ":4556"

[routing]
algorithm = "epidemic"

"""

        if "mobile" not in cls.config_data['ip'] and cls.config_data['cla'] == "quicl" and cls.config_data['ip'][node.id] is not None:
            cfg = cfg + f"""[[peer]]
protocol = "{cls.config_data['cla']}"
endpoint = "{cls.config_data['ip'][node.id]}:4556"
"""

        return cfg
