import paramiko
import pathlib
from .sync_config import SyncConfig, SyncMode
from utils import sftp_utils, utils
from console import pprint
from rich import panel, padding, progress


class SyncTask:
    def __init__(self, ssh_client: paramiko.SSHClient, sftp_client: paramiko.SFTPClient, config: SyncConfig) -> None:
        # TODO 这个地方应该是可以选择传入 config_file 或者直接传入配置信息
        self.ssh_client = ssh_client
        self.sftp_client = sftp_client
        self.config = config

    def start(self):
        self.show_sync_file_tree()
        upload_file_nums, make_dir_nums = self.upload(
            self.config.root_path, self.config.remote_root_path)
        pprint(
            f'[green]upload complete [red]{upload_file_nums}[/] file upload')

    def show_sync_file_tree(self):
        pprint('[red bold]find file prepare to sync: ')
        pprint(padding.Padding(
            utils.get_dir_tree(self.config.root_path, self.config.escape_file), (0, 0, 0, 0)))

    def upload(self, path: str, remote_path: str, *, use_exclude=True) -> tuple[int, int]:
        _path = pathlib.Path(path)
        _remote_path = pathlib.PurePath(remote_path)
        file_upload, dir_maked = 0, 0

        def upload_dir(dir_path: pathlib.Path, r_path: pathlib.PurePath):
            r_path = r_path/dir_path.name
            if not sftp_utils.exist_remote(r_path.as_posix(), self.sftp_client):
                self.sftp_client.mkdir(r_path.as_posix())
                pprint(
                    f'[info]create folder {dir_path.relative_to(_path)}')
            for child_file in dir_path.iterdir():
                upload_file_or_dir(child_file, r_path)

        def upload_file(file_path: pathlib.Path, r_path: pathlib.PurePath):
            nonlocal file_upload
            if not file_path.exists():
                pprint(f'[danger]{file_path} not exist')
                return
            r_path = r_path/file_path.name
            with progress.Progress() as pross:
                task = pross.add_task(
                    f'[green]uploading [yellow]{file_path.relative_to(_path)}')

                def task_pross(nowhave: int, allbyte: int):
                    pross.update(task, completed=nowhave/allbyte*100)
                self.sftp_client.put(file_path.as_posix(),
                                     r_path.as_posix(), task_pross)
            file_upload += 1

        def upload_file_or_dir(file_or_dir: pathlib.Path, r_path: pathlib.PurePath):
            if use_exclude and self.config.escape_file(file_or_dir):
                return
            if file_or_dir.is_dir():
                upload_dir(file_or_dir, r_path)
            else:
                upload_file(file_or_dir, r_path)

        if self.config.sync_mode == SyncMode.force:
            del_p = (_remote_path/_path.name).as_posix()
            if sftp_utils.exist_remote(del_p, self.sftp_client):
                pprint(
                    '[danger.high]!!!upload [bright_red]force[/] mode')
                self.ssh_client.exec_command(f'rm -r {del_p}')

        upload_file_or_dir(_path, _remote_path)
        return file_upload, dir_maked

    def pull(self, remote_file: str):
        remote_path = pathlib.PurePath(
            self.config.remote_root_path, remote_file)
        stat = self.sftp_client.stat(remote_path.as_posix())
        match sftp_utils.get_file_type(stat):
            case sftp_utils.FileType.DIR:
                pass
            case sftp_utils.FileType.NORMAL_FILE:
                pass
