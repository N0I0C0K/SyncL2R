import typer
from .app import app
from ..config import get_global_config
from ..utils.utils import show_sync_file_tree
from ..connect_core import Connection
from ..utils.sftp_utils import show_remote_file_tree, remote_file_list_to_tree
from ..bash import get_remote_tree


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
        from ..console import pprint
        from rich.padding import Padding

        tree = remote_file_list_to_tree(
            get_remote_tree(
                global_config.file_sync_config.exclude,
            ),
            global_config.file_sync_config.remote_root_path,
        )
        pprint(
            Padding(
                tree,
                (0, 0, 0, 0),
            )
        )
        # show_remote_file_tree(
        #     global_config.file_sync_config.remote_root_path, conn.sftp_client
        # )
