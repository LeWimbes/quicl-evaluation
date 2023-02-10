import json
import time

from core.nodes.base import CoreNode

from software import Software


class Forban(Software):

    def send_file(self, sender_node, payload_path, dst_name):
        with open(f"{sender_node.directory}/forban_insert.log", "a") as insert_log:
            timestamp = time.time()
            insert_log.write(f"{sender_node.name},{timestamp},{payload_path},{dst_name}\n")

        sender_node.cmd(f"bash -c 'cp {payload_path} forban/var/share/'")

    def wait_for_arrivals(self, node_id, payload_count):
        node = self.session.get_node(node_id, CoreNode)

        with open(f"{node.directory}/forban/var/log/forban_opportunistic.log") as log_file:

            arrived_payloads = 0
            while True:

                if self._timeout_reached():
                    print("Timeout reached. Stopping experiment.")
                    break

                line = log_file.readline()

                if not line:
                    time.sleep(0.1)
                    continue

                if "saved local file" in line:
                    arrived_payloads += 1
                    if arrived_payloads == payload_count:
                        break
