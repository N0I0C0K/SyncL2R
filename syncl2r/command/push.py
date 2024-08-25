import typer
import pathlib
from .app import app
from syncl2r.config import get_global_config
from syncl2r.console import pprint
from syncl2r.connect_core import Connection
from syncl2r.sync_core import RemoteFileManager, SyncMode
from syncl2r.utils.utils import show_sync_file_tree, get_file_md5
from syncl2r.utils.sftp_utils import rfile_equal_lfile
from syncl2r.command_core.deploy_core import stop_last_pids
from syncl2r.bash import get_remote_tree


@app.command(
    name="push",
    help="push files(which defined in .l2r config) to remote, if you want upload only few file, please use <upload> command",
)
def push(
    mode: int = typer.Option(
        2,
        "--mode",
        "-m",
        help="sync mode 1:force(del then upload) 2:normal 3:soft(upload only new files)",
    ),
    invoke_event: bool = typer.Option(True, help="weather invoke events"),
):
    try:
        config_modal = get_global_config()
        connection = Connection.default_connection()
        sync_task = RemoteFileManager(connection)

        # store diffrent file's Path obj
        diff_files: list[pathlib.Path] = []

        if mode == 1:
            pprint(
                "[danger]Pattern 1 will delete all the files in remote directory brfore upload"
            )
            if not typer.confirm("sure you want to continue?"):
                return
        else:
            remote_files = get_remote_tree(
                config_modal.file_sync_config.exclude,
            )

            remote_md5_map: dict[str, str] = dict()
            dir_set: set[str] = set()

            for file in remote_files:
                t = file.find("||")
                if t != -1:
                    remote_md5_map[file[:t]] = file[t + 2 :]
                else:
                    dir_set.add(file)

            def esc_equal_file(path: pathlib.Path):
                rp = path.relative_to(
                    config_modal.file_sync_config.root_path
                ).as_posix()
                if (
                    rp in remote_md5_map
                    and get_file_md5(path.as_posix()) == remote_md5_map[rp]
                ):
                    return True
                if not path.is_dir():
                    diff_files.append(path)
                # else:
                #     if rp not in dir_set:
                #         diff_files.append(path)
                return False

            show_sync_file_tree(config_modal.file_sync_config, esc_equal_file)

            if not typer.confirm("Do you want to continue?", default=False):
                return

        if invoke_event:
            # Stop running task
            stop_last_pids(connection)

        if (
            invoke_event
            and config_modal.events is not None
            and config_modal.events.push_start_exec is not None
        ):
            # invoke push start events
            pprint("[yellow]start exec start events")
            connection.cmd.exec_cmd_list(
                config_modal.events.push_start_exec,
                config_modal.file_sync_config.remote_root_path,
            )

        if mode == 1:
            sync_task.push_root_path(mode=SyncMode(mode))
        else:
            if len(diff_files) == 0:
                pprint("[green]There is no different between local and remote.")
            else:
                sync_task.push_files(diff_files, mode=SyncMode(mode))

        if (
            invoke_event
            and config_modal.events is not None
            and config_modal.events.push_complete_exec is not None
        ):
            # invoke push finissh events
            pprint("[yellow]start exec [on_push_complete] events")
            connection.cmd.exec_cmd_list(
                config_modal.events.push_complete_exec,
                config_modal.file_sync_config.remote_root_path,
            )

        # start deployment tasks
        if (
            invoke_event
            and config_modal.events is not None
            and config_modal.events.start is not None
        ):
            pprint("[yellow]start exec [start] events")
            connection.cmd.exec_cmd_list(
                config_modal.events.start,
                config_modal.file_sync_config.remote_root_path,
            )
    except Exception as e:
        pprint(f"\n[danger]err happen in command push, error info: {e}")
