import typer
from .app import app
from ..connect_core import Connection
from syncl2r.sync_core.deploy_core import stop_last_pids


@app.command(name="stop", help="stop remote running process")
def stop_remote():
    conn = Connection()
    stop_last_pids(conn)
