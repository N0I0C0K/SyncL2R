import os
import paramiko
from .sync_config import SyncConfig
from utils import sftp_utils, utils
from console import console


class SyncTask:
    def __init__(self, ssh_client: paramiko.SSHClient, sftp_client: paramiko.SFTPClient, root_path: str, config_file_name: str = None) -> None:
        # TODO 这个地方应该是可以选择传入 config_file 或者直接传入配置信息
        self.ssh_client = ssh_client
        self.sftp_client = sftp_client
        self.root_path = root_path
        self.config_path = f'{self.root_path}/{config_file_name if config_file_name else "l2r_config.json"}'
        self.sync_config = SyncConfig(self.config_path)

    def start(self):
        remote_root_path = self.sync_config.remote_root_path
        self.show_sync_file_tree()
        sftp_utils.upload_file_or_dir(
            self.sftp_client, self.root_path, remote_root_path)

    def show_sync_file_tree(self):
        console.print(utils.get_dir_tree(self.root_path))
        pass
