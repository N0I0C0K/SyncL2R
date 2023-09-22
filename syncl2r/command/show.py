import typer
from .app import app
from ..config import get_global_config
from ..utils.utils import show_sync_file_tree
from ..connect_core import Connection
from ..utils.sftp_utils import show_remote_file_tree


@app.command(name="show", help="show file struct for the current sync file")
def show_files(
    show_remote: bool = typer.Option(
        False, "--remote", "-r", help="show remote path tree"
    ),
):
    global_config = get_global_config()
    if not show_remote:
        show_sync_file_tree(global_config.file_sync_config)
    else:
        conn = Connection()
        show_remote_file_tree(
            global_config.file_sync_config.remote_root_path, conn.sftp_client
        )
