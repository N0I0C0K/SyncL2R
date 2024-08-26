import typer
from .app import app
from syncl2r.config import get_global_config
from syncl2r.utils.utils import show_sync_file_tree
from syncl2r.connect_core import Connection
from syncl2r.utils.sftp_utils import (
    show_remote_file_tree,
    remote_file_list_to_tree,
)
from syncl2r.bash import get_remote_files_with_md5


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
        from syncl2r.console import pprint
        from rich.padding import Padding

        remote_files = get_remote_files_with_md5(
            global_config.file_sync_config.exclude,
        )
        tree = remote_file_list_to_tree(
            list(remote_files),
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
