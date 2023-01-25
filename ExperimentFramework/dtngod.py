import json
import time
from software import Software


class DTNGod(Software):

    def init_software(self, node_name):
        node = self.session.get_object_by_name(node_name)
        node.cmd(f"dtnclient register -r /registration.json dtn://{node_name}/")

    def send_file(self, sender_node, payload_path, dst_name):
        sender_node.cmd(f"dtnclient send -r /registration.json -p {payload_path} -p {dst_name}")

    def wait_for_arrivals(self, node_name, payload_count):
        node = self.session.get_object_by_name(node_name)

        with open(f"{node.nodedir}/dtn7d_run.log") as log_file:

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
