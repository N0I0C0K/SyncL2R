from pathlib import PurePath
import paramiko
import enum
from paramiko import SSHClient, SFTPClient


class FileType(enum.IntFlag):
    DIR = 4
    NORMAL_FILE = 8


def path_to_absolute(path: PurePath) -> PurePath:
    if not path.is_absolute():
        from syncl2r.config import get_global_config

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


class SFTPFunction:
    def __init__(self, sftp_client: SFTPClient, ssh_client: SSHClient) -> None:
        self.sftp_client = sftp_client
        self.ssh_client = ssh_client

        self.stat = self.sftp_client.stat

    def get_file_type(self, file_stat: paramiko.SFTPAttributes) -> FileType | None:
        file_mode = file_stat.st_mode >> 12  # type: ignore
        for name in FileType:
            if (file_mode ^ name.value) == 0:
                return name
        return

    def get_remote_file_md5(self, file_path: str) -> str:
        from shlex import quote

        stdin, stdout, stderr = self.ssh_client.exec_command(
            f"md5sum {quote(file_path)}"
        )
        res = stdout.read().decode().split()
        if len(res) > 0:
            return res[0]
        else:
            return ""

    def get_file_type_from_path(self, file_path: str) -> FileType | None:
        try:
            stat = self.sftp_client.stat(file_path)
            return self.get_file_type(stat)
        except:
            return None

    def rfile_equal_lfile(self, remote_file_path: str, local_file_path: str) -> bool:
        from syncl2r.utils.utils import get_file_md5

        return get_file_md5(local_file_path) == self.get_remote_file_md5(
            remote_file_path
        )

    def exist_remote(self, file_path: str) -> bool:
        try:
            self.sftp_client.stat(file_path)
        except FileNotFoundError:
            return False
        else:
            return True

    def mkdir(self, dir_path: str):
        self.sftp_client.mkdir(dir_path)
