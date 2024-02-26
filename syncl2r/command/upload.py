import typer
from .app import app
from ..console import pprint
from ..connect_core import Connection
from ..sync_core import RemoteFileManager
from pathlib import Path


@app.command(
    name="upload",
    help="upload file(s) to remote, if you want push hole project to remote, please use <push> command",
)
def upload(
    files: list[str] = typer.Argument(help="files to push, must to be not none"),
):
    # config = get_global_config()
    from ..config.constant import Local_Root_Abs_Path

    conn = Connection()
    sync_task = RemoteFileManager(conn)

    file_path = list(map(lambda x: Path(Local_Root_Abs_Path / x), files))
    pprint(f"files to upload")
    for file in file_path:
        pprint(f"[red]{file.as_posix()}[/]")
    if typer.confirm("continue?"):
        sync_task.push_files(file_path)
