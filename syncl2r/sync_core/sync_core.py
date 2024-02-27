import paramiko
import pathlib
import enum

from io import BufferedWriter

from ..connect_core import Connection
from ..utils import sftp_utils, utils
from ..console import pprint
from rich import padding, progress
from ..config import get_global_config, FileSyncConfig


class SyncMode(enum.IntEnum):
    force = 1  # 先删除掉原来的文件再上传新的文件
    normal = 2  # 直接上传新的文件进行覆盖
    soft = 3  # 只上传新添加的文件


class RemoteFileManager:
    def __init__(
        self,
        connection: Connection,
        *,
        config: FileSyncConfig | None = None,
    ) -> None:
        self.ssh_client = connection.ssh_client
        self.sftp_client = connection.sftp_client
        self.config = get_global_config().file_sync_config if config is None else config
        self.total_upload_file = 0
        self.total_pull_file = 0

    def push_root_path(self, mode: SyncMode):
        self.total_upload_file = 0
        self.upload(self.config.root_path, self.config.remote_root_path, mode=mode)
        pprint(f"[green]upload complete [red]{self.total_upload_file}[/] file upload")

    def push_files(
        self,
        files: list[pathlib.Path],
        *,
        mode: SyncMode = SyncMode.normal,
        use_exclude=True,
    ):
        self.total_upload_file = 0
        r_path = pathlib.PurePath(self.config.remote_root_path)
        for file in files:
            self.upload_file_or_dir(
                file,
                r_path / (file.relative_to(self.config.root_path)),
                mode=mode,
                use_exclude=use_exclude,
            )

    def show_sync_file_tree(self):
        pprint("[red bold]file tree prepare to sync: ")
        pprint(
            padding.Padding(
                utils.get_dir_tree(self.config.root_path, self.config.escape_file),
                (0, 0, 0, 0),
            )
        )

    def upload_file(
        self,
        file_path: pathlib.Path,
        r_path: pathlib.PurePath,
    ):
        if not file_path.exists():
            pprint(f"[danger]{file_path} not exist")
            return
        if sftp_utils.exist_remote(
            r_path.as_posix(), self.sftp_client
        ) and sftp_utils.rfile_equal_lfile(
            r_path.as_posix(), file_path.as_posix(), self.ssh_client
        ):
            pprint(f"[warning]{file_path.name} has no change, skip")
            return
        with progress.Progress() as pross:
            task = pross.add_task(
                f"[green]uploading [yellow]{file_path.relative_to(self.config.root_path)}"
            )

            def task_pross(nowhave: int, allbyte: int):
                pross.update(task, completed=nowhave / allbyte * 100)

            self.sftp_client.put(
                file_path.as_posix(), r_path.as_posix(), task_pross, confirm=True
            )
        self.total_upload_file += 1

    def upload_dir(self, dir_path: pathlib.Path, r_path: pathlib.PurePath):
        if not sftp_utils.exist_remote(r_path.as_posix(), self.sftp_client):
            self.sftp_client.mkdir(r_path.as_posix())
            pprint(f"[info]create folder {r_path.as_posix()}")
        for child_file in dir_path.iterdir():
            self.upload_file_or_dir(child_file, r_path / child_file.name)

    def upload_file_or_dir(
        self,
        file_or_dir: pathlib.Path,
        r_path: pathlib.PurePath,
        *,
        mode=SyncMode.normal,
        use_exclude=True,
    ):
        if use_exclude and self.config.escape_file(file_or_dir):
            return
        if file_or_dir.is_dir():
            self.upload_dir(file_or_dir, r_path)
        else:
            if mode == SyncMode.soft and sftp_utils.exist_remote(
                r_path.as_posix(), self.sftp_client
            ):
                pprint(
                    f"[info.low]skip [yellow]{file_or_dir.relative_to(self.config.root_path)}[/] (already exist)"
                )
                return
            self.upload_file(file_or_dir, r_path)

    def upload(
        self,
        path: str,
        remote_path: str,
        *,
        use_exclude=True,
        mode: SyncMode = SyncMode.normal,
    ):
        pprint(f"[danger.high]upload [yellow2]{mode.name}[/] mode")

        if self.sftp_client is None:
            pprint("[danger.high]connection failed")
        _path = pathlib.Path(path)
        _remote_path = pathlib.PurePath(remote_path)

        if not sftp_utils.exist_remote(_remote_path.as_posix(), self.sftp_client):
            pprint(
                f"[warning]remote does not exist {_remote_path.as_posix()}, now created"
            )
            self.sftp_client.mkdir(_remote_path.as_posix())

        if mode == SyncMode.force:
            del_p = (_remote_path / "*").as_posix()
            if sftp_utils.exist_remote(_remote_path.as_posix(), self.sftp_client):
                self.ssh_client.exec_command(f"rm -r {del_p}")
                pprint(f"[danger.high]del remote folder [yellow2]({del_p})")
        if _path.is_dir():
            for child_file in _path.iterdir():
                self.upload_file_or_dir(
                    child_file, _remote_path, use_exclude=use_exclude, mode=mode
                )
        else:
            self.upload_file_or_dir(
                _path, _remote_path, use_exclude=use_exclude, mode=mode
            )

    def pull_file(
        self,
        relative_loc_file: pathlib.PurePath,
        target_path: pathlib.PurePath | BufferedWriter | None = None,
    ):
        remote_path = pathlib.PurePath(self.config.remote_root_path, relative_loc_file)

        if not sftp_utils.exist_remote(remote_path.as_posix(), self.sftp_client):
            pprint(
                f"[warning]{relative_loc_file.as_posix()} does not exist on remote server"
            )
            return

        with progress.Progress() as pross:
            task = pross.add_task(f"[green]pulling [yellow]{relative_loc_file}")

            def task_pross(nowhave: int, allbyte: int):
                pross.update(task, completed=nowhave / allbyte * 100)

            if target_path is None:
                target_path = relative_loc_file
                self.sftp_client.get(
                    remote_path.as_posix(), target_path.as_posix(), task_pross
                )
            elif isinstance(target_path, pathlib.PurePath):
                self.sftp_client.get(
                    remote_path.as_posix(), target_path.as_posix(), task_pross
                )
            elif isinstance(target_path, BufferedWriter):
                self.sftp_client.getfo(remote_path.as_posix(), target_path, task_pross)

    def pull(self, relative_path: str):
        _loc_path = pathlib.PurePath(relative_path)
        loc_root_path = pathlib.Path(self.config.root_path)
        remote_root_path = pathlib.PurePath(self.config.remote_root_path)

        def pull_dir(relative_loc_dir: pathlib.PurePath):
            _p = loc_root_path / relative_loc_dir
            if not _p.exists():
                pprint(f"[info]mkdir {relative_loc_dir.as_posix()}")
                _p.mkdir()
            remote_path = pathlib.PurePath(remote_root_path, relative_loc_dir)
            files = self.sftp_client.listdir(remote_path.as_posix())
            for file in files:
                f_p = pathlib.PurePath(file)
                pull_file_or_dir(relative_loc_dir / f_p)

        def pull_file(relative_loc_file: pathlib.PurePath):
            remote_path = pathlib.PurePath(remote_root_path, relative_loc_file)
            loc_path = loc_root_path / relative_loc_file
            if not sftp_utils.exist_remote(remote_path.as_posix(), self.sftp_client):
                pprint(
                    f"[warning]{relative_loc_file.as_posix()} does not exist on remote server"
                )
                return

            if sftp_utils.rfile_equal_lfile(
                remote_path.as_posix(), loc_path.as_posix(), self.ssh_client
            ):
                pprint(f"[warning]{relative_loc_file.as_posix()} has no change, skip")
                return
            with progress.Progress() as pross:
                task = pross.add_task(f"[green]pulling [yellow]{relative_loc_file}")

                def task_pross(nowhave: int, allbyte: int):
                    pross.update(task, completed=nowhave / allbyte * 100)

                self.sftp_client.get(
                    remote_path.as_posix(), loc_path.as_posix(), task_pross
                )

        def pull_file_or_dir(relative_path: pathlib.PurePath):
            remote_path = pathlib.PurePath(remote_root_path, relative_path)
            try:
                stat = self.sftp_client.stat(remote_path.as_posix())
            except FileNotFoundError:
                pprint(f"[warning]{relative_path} does not exist on remote server")
                return
            match sftp_utils.get_file_type(stat):
                case sftp_utils.FileType.DIR:
                    pull_dir(relative_path)
                case sftp_utils.FileType.NORMAL_FILE:
                    pull_file(relative_path)

        pull_file_or_dir(_loc_path)
