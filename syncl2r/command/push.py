import typer
from .app import app
from ..config import load_config
from ..console import pprint
from ..connect_core import Connection
from ..sync_core import SyncTask, SyncMode


@app.command(name="push", help="push file to remote")
def push(
    config: str = typer.Option(
        None, help="config file path, default find one match ./*.l2r.yaml"
    ),
    mode: int = typer.Option(
        2,
        "--mode",
        "-m",
        help="sync mode 1:force(del then upload) 2:normal 3:soft(upload only new files)",
    ),
    invoke_event: bool = typer.Option(True, help="weather invoke events"),
):
    try:
        config_modal = load_config(config)
        connection = Connection()
        sync_task = SyncTask(connection)

        if (
            invoke_event
            and config_modal.events is not None
            and config_modal.events.push_start_exec is not None
        ):
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
