from pathlib import PurePath
from paramiko import SSHClient


class ConnectionFunction:
    def __init__(self, conn: SSHClient) -> None:
        self.conn = conn

    def read_file(self, path: PurePath) -> str:
        if not path.is_absolute():
            from ..config import get_global_config

            config = get_global_config()
            path = PurePath(config.file_sync_config.remote_root_path) / path

        _, out, _ = self.conn.exec_command(f"cat {path.as_posix()}")
        return out.read().decode()
