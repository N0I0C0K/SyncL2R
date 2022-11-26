import paramiko
from .sync_task import SyncTask


class SyncCore:
    def __init__(self, ssh_client: paramiko.SSHClient, sftp_client: paramiko.SFTPClient = None) -> None:
        self.ssh_client = ssh_client
        self.sftp_client = sftp_client if sftp_client else ssh_client.open_sftp()

    def sync_dir(self, root_path: str) -> SyncTask:
        sync_task = SyncTask(self.ssh_client, self.sftp_client, root_path)
        return sync_task
