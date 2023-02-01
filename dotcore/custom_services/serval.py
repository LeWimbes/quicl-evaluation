from core.nodes.base import CoreNode
from core.services.coreservices import CoreService, ServiceMode

import nacl.hash
from nacl.encoding import HexEncoder
from nacl.bindings import crypto_sign_seed_keypair, crypto_sign_ed25519_sk_to_curve25519, crypto_scalarmult_base

sevald_keyring_dump_format_legacy = '''0: type=4(DID)  DID="{did}" Name="{name}"
0: type=1(CRYPTOBOX)  pub={box_pk} sec={box_sk}
0: type=2(CRYPTOSIGN)  pub={sign_pk} sec={sign_sk}
0: type=3(RHIZOME)  sec={rhiz_pk}
'''

servald_keyring_dump_format = '''0: type=0x04(DID)  DID="{did}" Name="{name}"
0: type=0x06 (CRYPTOCOMBINED)  pub={sign_pk}{box_pk} sec={sign_sk}{box_sk}
0: type=0x03(RHIZOME)  sec={rhiz_pk}
'''


def generate_serval_keys(name):
    node_hash = HexEncoder.decode(nacl.hash.sha256(name.encode("utf-8")))
    sign_pk, sign_sk = crypto_sign_seed_keypair(node_hash)
    box_sk = crypto_sign_ed25519_sk_to_curve25519(sign_sk)
    box_pk = crypto_scalarmult_base(box_sk)

    rhiz_pk = HexEncoder.decode(
        nacl.hash.sha256(("rhizome"+name).encode("utf-8")))

    keys = {
        "sign_pk": HexEncoder.encode(sign_pk).decode("ascii").upper(),
        "box_sk":  HexEncoder.encode(box_sk).decode("ascii").upper(),
        "sign_sk": HexEncoder.encode(sign_sk).decode("ascii").upper(),
        "box_pk":  HexEncoder.encode(box_pk).decode("ascii").upper(),
        "sid":     HexEncoder.encode(box_pk).decode("ascii").upper(),
        "rhiz_pk": HexEncoder.encode(rhiz_pk).decode("ascii").upper(),
    }
    return keys


def generate_serval_keyring_dump(name):
    keys = generate_serval_keys(name)
    keys["did"] = "".join(c for c in name if c.isdigit()).rjust(5, "0")
    keys["name"] = name

    return servald_keyring_dump_format.format(**keys)


class ServalService(CoreService):
    name: str = "Serval"
    group: str = "DTN"
    executables: tuple[str, ...] = ('servald', )
    dependencies: tuple[str, ...] = ("bwm-ng", "pidstat")
    configs: tuple[str, ...] = ('serval.conf', 'keyring.dump', 'serval.sid')
    validate: tuple[str, ...] = ('bash -c "servald status"', )   # ps -C returns 0 if the process is found, 1 if not.
    validation_mode: ServiceMode = ServiceMode.NON_BLOCKING  # NON_BLOCKING uses the validate commands for validation.
    validation_timer: int = 1                        # Wait 1 second before validating service.
    validation_period: float = 0.5                     # Retry after 1 second if validation was not successful.
    shutdown: tuple[str, ...] = ('bash -c "servald stop"', )

    @classmethod
    def get_startup(cls, node: CoreNode) -> tuple[str, ...]:
        startup_commands = []
        start_serval = 'bash -c "servald keyring load keyring.dump; nohup servald start foreground > servallog 2>&1 &"'

        for _, netif in node.ifaces.items():
            dev = netif.name
            ip_addr = netif.get_ip4()

            startup_commands.append(f'bash -c "ip address del {ip_addr} dev {dev}; ip address add {ip_addr} broadcast + dev {dev}"')

        startup_commands.append(start_serval)
        return tuple(startup_commands)

    @classmethod
    def generate_config(cls, node: CoreNode, filename: str) -> str:
        if filename == "serval.conf":
            return '''interfaces.0.match=*
interfaces.0.type=ethernet
server.motd="{}"
api.restful.users.pyserval.password=pyserval
'''.format(node.name)

        if filename == "keyring.dump":
            return generate_serval_keyring_dump(node.name)

        if filename == "serval.sid":
            return generate_serval_keys(node.name)["sid"]
