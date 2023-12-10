import typer
from .app import app
from ..console import pprint
from ..connect_core import Connection
from ..sync_core import RemoteFileManager


@app.command(name="pull", help="pull files from remote")
def pull(
    files: list[str] = typer.Argument(
        default=None, help="files to pull, default to hole file"
    ),
):
    try:
        connection = Connection()
        sync_task = RemoteFileManager(connection)
        files = ["."] if files is None or len(files) == 0 else files
        for file in files:
            sync_task.pull(file)
    except Exception as e:
        pprint(f"\n[danger]err happen in command pull, error info: {e}")
