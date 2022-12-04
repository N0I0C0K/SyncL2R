import os
import paramiko
import pathlib
from .sync_config import SyncConfig, SyncMode
from utils import sftp_utils, utils
from console import pprint
from rich import panel, padding, progress


class SyncTask:
    def __init__(self, ssh_client: paramiko.SSHClient, sftp_client: paramiko.SFTPClient, config: SyncConfig) -> None:
        self.ssh_client = ssh_client
        self.sftp_client = sftp_client
        self.config = config

    def push(self):
        self.show_sync_file_tree()
        upload_file_nums, make_dir_nums = self.upload(
            self.config.root_path, self.config.remote_root_path)
        pprint(
            f'[green]upload complete [red]{upload_file_nums}[/] file upload')

    def show_sync_file_tree(self):
        pprint('[red bold]file tree prepare to sync: ')
        # TODO 此处应该对比本地和远程文件,将不同的文件进行标注
        pprint(padding.Padding(
            utils.get_dir_tree(self.config.root_path, self.config.escape_file), (0, 0, 0, 0)))

    def upload(self, path: str, remote_path: str, *, use_exclude=True) -> tuple[int, int]:
        pprint(
            f'[danger.high]upload [yellow2]{self.config.sync_mode.name}[/] mode')

        if self.sftp_client is None:
            pprint('[danger.high]connection failed')
        _path = pathlib.Path(path)
        _remote_path = pathlib.PurePath(remote_path)
        file_upload, dir_maked = 0, 0

        if not sftp_utils.exist_remote(_remote_path.as_posix(), self.sftp_client):
            pprint(
                f'[warning]remote does not exist {_remote_path.as_posix()}, now created')
            self.sftp_client.mkdir(_remote_path.as_posix())

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
            if self.config.sync_mode == SyncMode.soft and sftp_utils.exist_remote(r_path.as_posix(), self.sftp_client):
                pprint(
                    f'[info.low]skip [yellow]{file_path.relative_to(path)}[/] (already exist)')
                return
            with progress.Progress() as pross:
                task = pross.add_task(
                    f'[green]uploading [yellow]{file_path.relative_to(_path)}')

                def task_pross(nowhave: int, allbyte: int):
                    pross.update(task, completed=nowhave/allbyte*100)
                self.sftp_client.put(file_path.as_posix(),
                                     r_path.as_posix(), task_pross, confirm=True)
            file_upload += 1

        def upload_file_or_dir(file_or_dir: pathlib.Path, r_path: pathlib.PurePath):
            if use_exclude and self.config.escape_file(file_or_dir):
                return
            if file_or_dir.is_dir():
                upload_dir(file_or_dir, r_path)
            else:
                upload_file(file_or_dir, r_path)

        if self.config.sync_mode == SyncMode.force:
            del_p = (_remote_path/'*').as_posix()
            if sftp_utils.exist_remote(del_p, self.sftp_client):
                self.ssh_client.exec_command(f'rm -r {del_p}')
                pprint(f'[danger.high]del remote folder [yellow2]({del_p})')
        if _path.is_dir():
            for child_file in _path.iterdir():
                upload_file_or_dir(child_file, _remote_path)
        else:
            upload_file_or_dir(_path, _remote_path)
        return file_upload, dir_maked

    def pull(self, relative_path: str):
        _loc_path = pathlib.PurePath(relative_path)
        loc_root_path = pathlib.Path(self.config.root_path)
        remote_roott_path = pathlib.PurePath(self.config.remote_root_path)

        def pull_dir(relative_loc_dir: pathlib.PurePath):
            _p = (loc_root_path/relative_loc_dir)
            if not _p.exists():
                pprint(f'[info]mkdir {relative_loc_dir.as_posix()}')
                _p.mkdir()
            for file in _p.iterdir():
                pull_file_or_dir(file.relative_to(loc_root_path))

        def pull_file(relative_loc_file: pathlib.PurePath):
            remote_path = pathlib.PurePath(
                remote_roott_path, relative_loc_file)
            if not sftp_utils.exist_remote(remote_path.as_posix(), self.sftp_client):
                pprint(
                    f'[warning]{relative_loc_file.as_posix()} does not exist on remote server')
                return
            pprint(f'[info]pulling {relative_loc_file.as_posix()}')
            self.sftp_client.get(remote_path.as_posix(),
                                 (loc_root_path/relative_loc_file).as_posix())

        def pull_file_or_dir(relative_path: pathlib.PurePath):
            remote_path = pathlib.PurePath(
                remote_roott_path, relative_path)
            try:
                stat = self.sftp_client.stat(remote_path.as_posix())
            except FileNotFoundError:
                pprint(
                    f'[warning]{relative_path} does not exist on remote server')
                return
            match sftp_utils.get_file_type(stat):
                case sftp_utils.FileType.DIR:
                    pull_dir(relative_path)
                case sftp_utils.FileType.NORMAL_FILE:
                    pull_file(relative_path)

        pull_file_or_dir(_loc_path)
