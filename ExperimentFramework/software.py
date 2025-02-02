import time
import pathlib
import multiprocessing as mp

from core.nodes.base import CoreNode

class Software:

    def __init__(self, session):
        self.session = session

        # We have a 54 Mbit/s (6.75 MB/s) network, means it takes about
        # 15 seconds to transmit 100 MB over one hop in the best case.
        # Smaller tests show, that DTN7 takes about 25 seconds to transmit
        # 100 MB over one hop, which means 27 minutes for 64 hops.
        # To be on the safe site, we give the experiments 30 minutes.
        self.timeout = time.time() + 60 * 30
        self.processes = []

    def _timeout_reached(self):
        if time.time() >= self.timeout:
            return True

        return False

    def terminate_processes(self):
        for process in self.processes:
            if process:
                process.terminate()
                process.join()
            else:
                print("Process is none!")

    def init_software(self, node_name):
        pass

    def send_files_process(self, sender_id, payload_folder_path, dst_name, num_payloads, burst_time):
        sender_node = self.session.get_node(sender_id, CoreNode)

        payload_paths = pathlib.Path(payload_folder_path).glob('*.file')

        wait_time = burst_time / num_payloads
        for payload_path in payload_paths:
            print("Sending payload")
            p = mp.Process(
                    target=self.send_file,
                    args=(sender_node, payload_path, dst_name)
                )

            self.processes.append(p)
            p.start()

            time.sleep(wait_time)

    def send_files(self, sender_id, payload_folder_path, dst_name, num_payloads, burst_time=10):
        p = mp.Process(
                target=self.send_files_process,
                args=(sender_id, payload_folder_path, dst_name, num_payloads, burst_time)
            )

        self.processes.append(p)
        p.start()

    def send_file(self, sender_node, payload_path, dst_name):
        pass

    def wait_for_arrival(self, node_name):
        pass
