import os
import typer
import pathlib
import subprocess

from ..connect_core import Connection
from ..console import pprint
from ..sync_core import SyncTask
from .app import app


@app.command(
    "diff", help="Show the difference between local and remote files, based on vscode"
)
def show_diff(file: str = typer.Argument(help="Local file path (relative path)")):
    if not os.path.exists(file):
        pprint(f"[warn]{file} do not exist")
        return
    conn = Connection()
    sync = SyncTask(conn)
    lf = pathlib.PurePath(file)
    tp = pathlib.PurePath("./.l2r/tmp")
    sync.pull_file(lf, tp)
    subprocess.call(["code", "--diff", lf.as_posix(), tp.as_posix()], shell=True)
