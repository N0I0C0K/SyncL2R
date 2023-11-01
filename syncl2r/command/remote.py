import typer
from .app import app
from ..utils import pprint
from ..config import get_global_config
from ..connect_core import Connection
from syncl2r.sync_core.deploy_core import stop_last_pids, get_entire_log

remote_cmd = typer.Typer(name="remote", help="remote cmds")

app.add_typer(remote_cmd)


@remote_cmd.command(name="stop", help="stop remote running process")
def stop_remote():
    conn = Connection()
    stop_last_pids(conn)

    cfg = get_global_config()
    if cfg.events is not None and cfg.events.stop is not None:
        conn.exec_cmd_list(cfg.events.stop)


@remote_cmd.command(name="start", help="start remote production process")
def start_remote():
    cfg = get_global_config()
    if cfg.events is not None and cfg.events.start is not None:
        conn = Connection()
        conn.exec_cmd_list(cfg.events.start, cfg.file_sync_config.remote_root_path)


@remote_cmd.command(name="relaod", help="restart remote task")
def restart_remote():
    # TODO
    pass


@remote_cmd.command(name="log", help="show remote task log")
def log_remote():
    conn = Connection()
    log = get_entire_log(conn)
    pprint(log)
