import os
import typer
import pathlib
import subprocess
import tempfile

from .app import app
from syncl2r.connect_core import Connection
from syncl2r.console import pprint
from syncl2r.sync_core import RemoteFileManager


@app.command(
    "diff", help="Show the difference between local and remote files, based on vscode"
)
def show_diff(file: str = typer.Argument(help="Local file path (relative path)")):
    if not os.path.exists(file):
        pprint(f"[warn]{file} do not exist")
        return
    conn = Connection()
    sync = RemoteFileManager(conn)
    show_diff_inter(file, sync, conn)


def show_diff_inter(file: str, sync: RemoteFileManager, conn: Connection):
    from syncl2r.config.constant import Remote_Root_Abs_Path

    lf = pathlib.PurePath(file)
    rf = Remote_Root_Abs_Path / lf

    try:
        info = conn.sftp_client.stat(rf.as_posix())
    except FileNotFoundError:
        pprint("[red]%s does not exist", rf.as_posix())
    else:
        # if remote file size bigger than 2Mb, ask to continue
        if info.st_size and info.st_size >= 1024 * 1024 * 2:
            typer.confirm(
                f"remote file: {rf} is larger than 2Mb, continue to download?",
                False,
                True,
            )

    [tmp_file, file_name] = tempfile.mkstemp()
    temp_file_open = os.fdopen(tmp_file, "wb")
    # tp = pathlib.PurePath(file_name)
    sync.pull_file(lf, temp_file_open)
    subprocess.call(["code", "--diff", file_name, lf.as_posix()], shell=True)
