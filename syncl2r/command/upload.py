import typer
from .app import app
from syncl2r.console import pprint
from syncl2r.connect_core import Connection
from syncl2r.sync_core import RemoteFileManager, SyncMode
from pathlib import Path


@app.command(
    name="upload",
    help="upload file(s) to remote, if you want push hole project to remote, please use <push> command",
)
def upload(
    files: list[str] = typer.Argument(help="files to push, must to be not none"),
):
    # config = get_global_config()
    from syncl2r.config.constant import Local_Root_Abs_Path

    try:
        conn = Connection.default_connection()
        sync_task = RemoteFileManager(conn)

        file_path = list(map(lambda x: Path(Local_Root_Abs_Path / x), files))
        pprint(f"files to upload")
        for file in file_path:
            pprint(f"[red]{file.as_posix()}[/]")
        if typer.confirm("continue?", abort=True):
            sync_task.push_files(file_path, mode=SyncMode.normal, use_exclude=False)
    except Exception as e:
        pprint(f"[danger]error happen in upload, err:{e}")
