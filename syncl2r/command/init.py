import os
import re
import pathlib
import typer

from typing import Literal

from .app import app
from syncl2r.config import load_config, save_config, Config_Path
from syncl2r.console import pprint
from syncl2r.connect_core import Connection


@app.command(name="init", help="init config file for current path")
def init(
    host: str = typer.Option(prompt="host to connect"),
    port: str = typer.Option("22", prompt="enter port, default to 22"),
    username: str = typer.Option(prompt="user name for ssh connect"),
    sync_path: str = typer.Option(
        ".", "--local-path", "-lp", help="local path to sync"
    ),
    test_connect: bool = typer.Option(
        default=False,
        help="test connection before write config file, Used to check whether the connection configuration is correct",
    ),
):
    mode: Literal["password", "key"] = typer.prompt(
        "which mode do you want use? [password]/[key]", default="password"
    )
    key_name: str = ""
    password: str = ""
    if mode == "key":
        key_name = typer.prompt("ssh private key to connect, link to ~/.ssh/[key_name]")
    elif mode == "password":
        password = typer.prompt("enter password", hide_input=True)
    else:
        raise typer.Abort
    if not os.path.exists("./.l2r"):
        os.makedirs(".l2r")
    if os.path.exists(Config_Path):
        replace = typer.confirm(f"{Config_Path} already exist, do you want to replace?")
        if not replace:
            raise typer.Abort()

    # check weather sync dir is right config
    sync_dir = sync_path
    sync_dir_name = os.path.split(os.path.abspath(sync_dir))[-1]
    if not os.path.exists(sync_dir):
        pprint(f"[red]{sync_dir} does not exist")
        return

    if key_name:
        key_file = pathlib.Path.home() / ".ssh" / key_name
        if not key_file.exists():
            raise ValueError(f"key file({key_file.as_posix()}) is not exist")

    remote_path = f"{sync_dir_name}"

    init_data = {
        "connect_config": {
            "host": host,
            "username": username,
            "password": password,
            "port": port,
            "key_name": key_name,
        },
        "file_sync_config": {
            "root_path": sync_dir,
            "remote_root_path": remote_path,
        },
        "events": {"push_complete_exec": [], "push_start_exec": []},
    }
    config = load_config(init_data)

    if test_connect:
        try:
            conn = Connection.default_connection()
        except Exception as e:
            pprint(
                f"[danger.high]exception happend during connecting to the host, error info: {e}"
            )
            return
        else:
            conn.close()

    save_config(config)
