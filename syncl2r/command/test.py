from .app import app
from .app import app
from syncl2r.connect_core import Connection
from syncl2r.bash import get_remote_tree
from syncl2r.command_core.deploy_core import check_still_running
from syncl2r.config import get_global_config
from syncl2r.console import pprint

import typer


@app.command()
def test(st: list[str], ctx: typer.Context):
    # config = load_config()
    pprint(st)
    # pprint(ctx)
