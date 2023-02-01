from core.nodes.base import CoreNode
from core.services.coreservices import CoreService, ServiceMode

class ForbanService(CoreService):
    name: str = "Forban"
    group: str = "DTN"
    executables: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ("bwm-ng", "pidstat")
    configs: tuple[str, ...] = ("forban.cfg", )
    validate = ("bash -c 'if [ \"$(forban/bin/forbanctl status | tail -1 | cut -d\" \" -f2)\" == \"PID:False\" ]; then exit 1; else exit 0; fi'", ) # forbanctl prints  the PIDs of the procceses, if they are running. But PID:False is printed, then it is not running.
    validation_mode: ServiceMode = ServiceMode.NON_BLOCKING
    validation_timer: int = 1
    validation_period: float = 0.5
    shutdown = ("bash -c 'forban/bin/forbanctl stop >> forban/forban.log 2>&1'", )

    @classmethod
    def generate_config(cls, node: CoreNode, filename: str) -> str:
        destinations = []
        for iface in node.ifaces.values():
            for addr in iface.ip4s:
                destinations.append(addr.broadcast)

        destinations_str = ", ".join(
                ["\"{}\"".format(dest) for dest in destinations])

        return '''
[global]
name = {node_name}
version = 0.0.34

logging = INFO
loggingsizemax = 20000000

disabled_ipv6 = 1

destination = [ {destinations_str} ]

mode = opportunistic
announceinterval = 2

[forban]

[opportunistic]
filter =
maxsize = 0

[opportunistic_fs]
directory = /media
checkforban = 1
mode = out
    '''.format(node_name=node.name, destinations_str=destinations_str)

    @classmethod
    def get_startup(cls, node):
        cmds = ["cp -r /forban {nd}",
                "cp {nd}/forban.cfg {nd}/forban/cfg/",
                "{nd}/forban/bin/forbanctl start >> {nd}/forban.log 2>&1"]
        cmd_line = " && ".join([c.format(nd=node.directory) for c in cmds])
        return ("bash -c '{cmd_line}'".format(cmd_line=cmd_line), )
