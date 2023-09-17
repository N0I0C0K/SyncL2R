import typer
from .app import app
from ..config import load_config
from ..utils.utils import show_sync_file_tree


@app.command(name="show", help="show file struct for the current sync file")
def show_files(config: str = typer.Option(None, help="c")):
    global_config = load_config(config)
    show_sync_file_tree(global_config.file_sync_config)
