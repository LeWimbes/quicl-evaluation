import json
import time

from core.nodes.base import CoreNode

from software import Software

class DTN7Go(Software):

    def init_software(self, node_id):
        node = self.session.get_node(node_id, CoreNode)
        node.cmd(f"dtnclient register -r /registration.json dtn://n{node_id}/")

    def send_file(self, sender_node, payload_path, dst_name):
        sender_node.cmd(f"dtnclient send -r /registration.json -p {payload_path} dtn://{dst_name}/")

    def wait_for_arrivals(self, node_id, payload_count):
        node = self.session.get_node(node_id, CoreNode)

        with open(f"{node.directory}/dtngod.log") as log_file:

            arrived_payloads = 0
            while True:

                if self._timeout_reached():
                    print("Timeout reached. Stopping experiment.")
                    break

                line = log_file.readline()

                if not line:
                    time.sleep(0.1)
                    continue

                try:
                    json_obj = json.loads(line)
                    if json_obj["msg"] == "Received bundle for local delivery":
                        arrived_payloads += 1
                        if arrived_payloads == payload_count:
                            break
                except Exception as e:
                    print(e)
                    continue
