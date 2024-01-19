from core.nodes.base import CoreNode
from core.services.coreservices import CoreService, ServiceMode

class DTN7NGService(CoreService):
    name: str = "DTN7NG"
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
    config_data: dict[str, str] = {"cla": "mtcp"}

    @classmethod
    def generate_config(cls, node: CoreNode, filename: str) -> str:
        cfg = f"""
node_id = "dtn://{node.name}/"

[Store]
path = "store_{node.name}"

# Specify routing algorithm
[Routing]
algorithm = "epidemic"

[Agents]
[Agents.REST]
# Address to bind the server to.
address = ":8080"

[[Listener]]
type = "{cls.config_data['cla']}"
address = ":35037"
"""

        return cfg
