from .app import app
from .app import app
from ..connect_core import Connection
from ..bash import get_remote_tree
from ..command_core import check_still_running
from ..config import get_global_config
from ..console import pprint

import typer


@app.command()
def test(st: list[str], ctx: typer.Context):
    # config = load_config()
    pprint(st)
    # pprint(ctx)
