import paramiko
import pathlib
from .sync_config import SyncConfig
from utils import sftp_utils, utils
from console import console
from rich import panel, padding


class SyncTask:
    def __init__(self, ssh_client: paramiko.SSHClient, sftp_client: paramiko.SFTPClient, config: SyncConfig) -> None:
        # TODO 这个地方应该是可以选择传入 config_file 或者直接传入配置信息
        self.ssh_client = ssh_client
        self.sftp_client = sftp_client
        self.config = config

    def start(self):
        remote_root_path = self.config.remote_root_path
        self.show_sync_file_tree()
        sftp_utils.upload_file_or_dir(
            self.sftp_client, self.config.root_path, remote_root_path)

    def show_sync_file_tree(self):
        console.print('[red bold]find file prepare to sync: ')
        console.print(padding.Padding(
            utils.get_dir_tree(self.config.root_path, self.config.escape_file), (0, 0, 0, 0)))
        self.upload(self.config.root_path, self.config.remote_root_path)

    def upload(self, path: str, remote_path: str, *, use_exclude=True):
        _path = pathlib.Path(path)
        _remote_path = pathlib.PurePath(remote_path)

        def upload_dir(dir_path: pathlib.Path, r_path: pathlib.PurePath):
            r_path = r_path/dir_path.name
            if not sftp_utils.exist_remote(r_path.as_posix(), self.sftp_client):
                self.sftp_client.mkdir(r_path.as_posix())
                console.log(f'[blue]make dir {dir_path.relative_to(_path)}')
            for child_file in dir_path.iterdir():
                upload_file_or_dir(child_file, r_path)

        def upload_file(file_path: pathlib.Path, r_path: pathlib.PurePath):
            if not file_path.exists():
                console.log(f'[red bold]{file_path} not exist')
                return
            r_path = r_path/file_path.name
            console.log(f'[green]upload {file_path.relative_to(_path)}')
            self.sftp_client.put(file_path.as_posix(), r_path.as_posix())

        def upload_file_or_dir(file_or_dir: pathlib.Path, r_path: pathlib.PurePath):
            if file_or_dir.is_dir():
                upload_dir(file_or_dir, r_path)
            else:
                upload_file(file_or_dir, r_path)

        upload_file_or_dir(_path, _remote_path)
