import os
import tempfile
import uuid


def create_payloads(size, num):
    payload_base_path = tempfile.mkdtemp(dir="/tmp")

    for _ in range(num):
        path = f"{payload_base_path}/{uuid.uuid4()}.file"
        with open(path, "wb") as f:
            f.write(os.urandom(size))

    return payload_base_path
