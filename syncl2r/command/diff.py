import os
import typer
import pathlib
import subprocess
import tempfile

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
    [tmp_file, file_name] = tempfile.mkstemp()
    temp_file_open = os.fdopen(tmp_file, "wb")
    # tp = pathlib.PurePath(file_name)
    sync.pull_file(lf, temp_file_open)
    subprocess.call(["code", "--diff", lf.as_posix(), file_name], shell=True)
