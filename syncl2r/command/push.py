import typer
import pathlib
from .app import app
from ..config import get_global_config
from ..console import pprint
from ..connect_core import Connection
from ..sync_core import SyncTask, SyncMode
from ..utils.utils import show_sync_file_tree, get_file_md5
from ..utils.sftp_utils import rfile_equal_lfile
from ..sync_core.deploy_core import stop_last_pids
from ..bash import get_remote_tree


@app.command(name="push", help="push file to remote")
def push(
    mode: int = typer.Option(
        2,
        "--mode",
        "-m",
        help="sync mode 1:force(del then upload) 2:normal 3:soft(upload only new files)",
    ),
    invoke_event: bool = typer.Option(True, help="weather invoke events"),
    show_diff: bool = typer.Option(
        False, "--show-diff", "-s", help="Whether to display file changes"
    ),
):
    try:
        config_modal = get_global_config()
        connection = Connection()
        sync_task = SyncTask(connection)
        if show_diff:
            remote_path = pathlib.PurePath(
                config_modal.file_sync_config.remote_root_path
            )

            remote_files = get_remote_tree(
                config_modal.file_sync_config.exclude,
            )

            remote_md5_map: dict[str, str] = dict()
            for file in remote_files:
                t = file.find("||")
                if t != -1:
                    remote_md5_map[file[:t]] = file[t + 2 :]

            def esc_equal_file(path: pathlib.PurePath):
                rp = path.relative_to(
                    config_modal.file_sync_config.root_path
                ).as_posix()

                return (
                    rp in remote_md5_map
                    and get_file_md5(path.as_posix()) == remote_md5_map[rp]
                )

            show_sync_file_tree(config_modal.file_sync_config, esc_equal_file)

            if not typer.confirm("Do you want to continue?"):
                return

        if (
            invoke_event
            and config_modal.events is not None
            and config_modal.events.push_start_exec is not None
        ):
            # Stop running task
            stop_last_pids(connection)

            # invoke push start events
            pprint("[yellow]start exec start events")
            connection.exec_cmd_list(
                config_modal.events.push_start_exec,
                config_modal.file_sync_config.remote_root_path,
            )

        sync_task.push(mode=SyncMode(mode))

        if (
            invoke_event
            and config_modal.events is not None
            and config_modal.events.push_complete_exec is not None
        ):
            # invoke push finissh events
            pprint("[yellow]start exec finish events")
            connection.exec_cmd_list(
                config_modal.events.push_complete_exec,
                config_modal.file_sync_config.remote_root_path,
            )

    except Exception as e:
        pprint(f"\n[danger]err happen in command push, error info: {e}")
