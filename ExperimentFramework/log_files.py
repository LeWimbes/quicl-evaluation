
import os
import shutil

import framework


excluded_files = [
    #DTN7
    "store_n",
    # Serval
    "blob",
    "serval.log",
    "keyring.dump",
    "proc/",
    "rhizome.db",
    "serval.keyring",
    ".git",
    "AUTHORS",
    "FAQ",
    "README",
    # IBRDTN
    "inbox"
]


def get_chunk(file_object, chunk_size=20000000):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def prepare_log_file(input_file):
    total_file_size = os.path.getsize(input_file)

    if total_file_size > 20000000:

        with open(input_file, "rb") as f:
            chunk_count = 0
            for chunk in get_chunk(f):
                chunk_path = '{}_chunk{}'.format(input_file, chunk_count)
                with open(chunk_path, 'wb') as chunk_file:
                    chunk_file.write(chunk)
                    framework.addBinaryFile(chunk_path)
                chunk_count = chunk_count + 1

    else:
        framework.addBinaryFile(input_file)


def _is_blacklisted(name):
    for elem in excluded_files:
        if elem in name:
            return True

    return False


def collect_logs(session_dir):
    for root, _, files in os.walk(session_dir):
        for f in files:
            src_file_path = os.path.join(root, f)

            # Ignore all files outside the <nodename>.conf folder
            if '.conf' not in src_file_path:
                continue

            if _is_blacklisted(src_file_path):
                continue

            session_dir_trailing = '{}/'.format(session_dir)
            new_file_name = src_file_path.replace(session_dir_trailing,
                                                  '').replace('/', '_')
            dst_file_path = '{}/{}'.format(os.getcwd(), new_file_name)

            try:
                shutil.move(src_file_path, dst_file_path)
                prepare_log_file(new_file_name)
            except IOError as e:
                print(f"Could not add binary file: {e}")

    prepare_log_file('parameters.py')
