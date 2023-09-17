import typer
from .app import app
from ..config import load_config
from ..console import pprint
from ..connect_core import Connection
from ..sync_core import SyncTask


@app.command(name="pull", help="pull files from remote")
def pull(
    files: list[str] = typer.Argument(
        default=None, help="files to pull, default to hole file"
    ),
    config: str = typer.Option(
        None, help="config file path, default find one match ./*.l2r.yaml"
    ),
):
    try:
        load_config(config)
        connection = Connection()
        sync_task = SyncTask(connection)
        files = ["."] if files is None or len(files) == 0 else files
        for file in files:
            sync_task.pull(file)
    except Exception as e:
        pprint(f"\n[danger]err happen in command pull, error info: {e}")
