import time

from core.nodes.base import CoreNode

from software import Software

class Serval(Software):

    def send_file(self, sender_node, payload_path, dst_name):
        sender_node.cmd(f"bash -c 'servald rhizome add file `cat serval.sid` {payload_path}'")

    def wait_for_arrivals(self, node_id, payload_count):
        node = self.session.get_node(node_id, CoreNode)

        with open(f"{node.directory}/serval.log") as log_file:

            arrived_payloads = 0
            while True:

                if self._timeout_reached():
                    print("Timeout reached. Stopping experiment.")
                    break

                line = log_file.readline()

                if not line:
                    time.sleep(0.1)
                    continue

                if "rhizome_database.c:1559:rhizome_add_manifest_to_store()  RHIZOME ADD MANIFEST service=file bid=" in line:
                    arrived_payloads += 1
                    if arrived_payloads == payload_count:
                        break
