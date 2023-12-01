from pathlib import PurePath
from paramiko import SSHClient


def path_to_absolute(path: PurePath) -> PurePath:
    if not path.is_absolute():
        from ..config import get_global_config

        config = get_global_config()
        path = PurePath(config.file_sync_config.remote_root_path) / path
    return path


class ConnectionFunction:
    def __init__(self, conn: SSHClient) -> None:
        self.conn = conn

    def read_file(self, path: PurePath) -> str:
        path = path_to_absolute(path)

        _, out, _ = self.conn.exec_command(f"cat {path.as_posix()}")
        return out.read().decode()

    def write_file(self, path: PurePath, data: str):
        from shlex import quote

        path = path_to_absolute(path)
        self.conn.exec_command(f'echo "{quote(data)}" > {path.as_posix}')
