import typer
from .app import app
from syncl2r.utils import pprint
from syncl2r.config import get_global_config
from syncl2r.connect_core import Connection
from syncl2r.command_core.deploy_core import (
    stop_last_pids,
    get_remote_log,
    check_still_running,
    store_log,
)

remote_cmd = typer.Typer(name="remote", help="remote cmds")

app.add_typer(remote_cmd)


@remote_cmd.command(name="stop", help="stop remote running process")
def stop_remote():
    conn = Connection.default_connection()
    stop_last_pids(conn)

    cfg = get_global_config()
    if cfg.events is not None and cfg.events.stop is not None:
        conn.cmd.exec_cmd_list(cfg.events.stop)


@remote_cmd.command(name="start", help="start remote production process")
def start_remote():
    cfg = get_global_config()
    if cfg.events is not None and cfg.events.start is not None:
        conn = Connection.default_connection()
        if check_still_running(conn):
            return pprint("[red]last process is still running")
        store_log(conn)
        conn.cmd.exec_cmd_list(cfg.events.start, cfg.file_sync_config.remote_root_path)


@remote_cmd.command(name="relaod", help="restart remote task")
def restart_remote():
    cfg = get_global_config()
    if cfg.events is not None and cfg.events.start is not None:
        conn = Connection.default_connection()
        stop_last_pids(conn)
        conn.cmd.exec_cmd_list(cfg.events.start, cfg.file_sync_config.remote_root_path)


@remote_cmd.command(name="log", help="show remote task log")
def log_remote(
    additional_cmds: list[str] = typer.Option(
        None,
        "-c",
        "--additional-commands",
        help="add additional command to cat remote log file, Use the | pipe splicing command",
    )
):
    conn = Connection.default_connection()
    log = get_remote_log(conn, additional_cmds)
    pprint(log)


@remote_cmd.command(name="state", help="get remote running state")
def get_state():
    conn = Connection.default_connection()
    state = check_still_running(conn)
    if state:
        pprint("Remote running state: [green]running")
    else:
        pprint("Remote running state: [red]stopped")
