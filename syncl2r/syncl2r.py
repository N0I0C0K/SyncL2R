import os
import re

import typer
import pathlib

from .utils.utils import show_sync_file_tree
from .config import load_config
from .console import pprint
from .connect_core import Connection
from .sync_core import SyncTask, SyncMode

app = typer.Typer()


@app.command(name="push", help="push file to remote")
def push(
    config: str = typer.Option(
        None, help="config file path, default find one match ./*.l2r.yaml"
    ),
    mode: int = typer.Option(
        2,
        help="sync mode 1:force(del then upload) 2:normal 3:soft(upload only new files)",
    ),
    invoke_event: bool = typer.Option(True, help="weather invoke events"),
):
    try:
        config_modal = load_config(config)
        connection = Connection()
        sync_task = SyncTask(connection)

        if (
            invoke_event
            and config_modal.events is not None
            and config_modal.events.push_start_exec is not None
        ):
            # invoke push start events
            pprint("[yellow]start exec start events")
            connection.exec_cmd_list(
                config_modal.events.push_start_exec,
                config_modal.file_sync_config.remote_root_path,
            )

        sync_task.push(mode=SyncMode(mode))

        if (
            invoke_event
            and config_modal.events is not None
            and config_modal.events.push_complete_exec is not None
        ):
            # invoke push finissh events
            pprint("[yellow]start exec finish events")
            connection.exec_cmd_list(
                config_modal.events.push_complete_exec,
                config_modal.file_sync_config.remote_root_path,
            )

    except Exception as e:
        pprint(f"\n[danger]err happen in command push, error info: {e}")


@app.command(name="pull", help="pull files from remote")
def pull(
    files: list[str] = typer.Argument(
        default=None, help="files to pull, default to hole file"
    ),
    config: str = typer.Option(
        None, help="config file path, default find one match ./*.l2r.yaml"
    ),
):
    try:
        load_config(config)
        connection = Connection()
        sync_task = SyncTask(connection)
        files = ["."] if files is None or len(files) == 0 else files
        for file in files:
            sync_task.pull(file)
    except Exception as e:
        pprint(f"\n[danger]err happen in command pull, error info: {e}")


@app.command(name="init", help="init config file for current path")
def init(
    remote_url: str = typer.Argument(
        ...,
        help="the link to the remote ssh host. like => username:password@ip or username:password@ip:port",
    ),
    remote_path: str = typer.Option(default="", help="remote path to sync"),
    config_name: str = typer.Option(
        default="config",
        help="custom file name for the config name => config.l2r.yaml",
    ),
    test_connect: bool = typer.Option(
        default=False,
        help="test connection before write config file, Used to check whether the connection configuration is correct",
    ),
):
    conifg_file = os.path.abspath(f"./{config_name}.l2r.yaml")
    if os.path.exists(conifg_file):
        replace = typer.confirm(f"{conifg_file} already exist, do you want to replace?")
        if not replace:
            raise typer.Abort()

    sync_dir = "."
    if not os.path.exists(sync_dir):
        pprint(f"[red]{sync_dir} does not exist")
        return

    res = re.match(r"(.*?):(.*?)@([0-9,\.]*):?([0-9]*)?", remote_url)
    if res is None:
        pprint(f"[danger]{remote_url} is invalid")
        return
    username, pwd, ip, port = res.groups()
    port = 22 if port == "" else int(port)

    init_data = {
        "connect_config": {
            "ip": ip,
            "port": port,
            "username": username,
            "password": pwd,
        },
        "file_sync_config": {
            "root_path": sync_dir,
            "remote_root_path": remote_path,
            "exclude": [],
        },
    }

    load_config(init_data)

    if test_connect:
        try:
            conn = Connection()
        except Exception as e:
            pprint(
                f"[danger.high]exception happend during connecting to the host {remote_url}, error info: {e}"
            )
            return
        else:
            conn.close()

    if os.path.exists(conifg_file):
        pprint(f"[red]{conifg_file} already exist! now relpace")
    with open(conifg_file, "w+", encoding="utf-8") as file:
        import yaml

        try:
            from yaml import CDumper as Dumper
        except:
            from yaml import Dumper

        yaml.dump(init_data, file, Dumper)


@app.command(name="show", help="show file struct for the current sync file")
def show_files(config: str = typer.Option(None, help="c")):
    global_config = load_config(pathlib.Path(config))
    show_sync_file_tree(global_config.file_sync_config)


@app.command(name="shell", help="open shell to remote")
def link_shell(
    config: str = typer.Option(
        None, help="config file path, default find one match ./*.l2r.yaml"
    )
):
    import time

    load_config(pathlib.Path(config))
    try:
        connection = Connection()
        ssh_client = connection.ssh_client
    except Exception as e:
        pprint(f"[danger]connect to remote failed, error info: {e}")
        return

    user_cmd = ""
    channel = ssh_client.invoke_shell()
    time.sleep(0.1)
    while not channel.recv_ready():
        pass
    pprint(channel.recv(1000).decode())
    start = ">"
    while user_cmd != "exit\n":
        user_cmd = input(start)
        user_cmd = user_cmd + "\n"
        channel.send(user_cmd.encode())
        stdout = bytes()
        while not channel.recv_ready():
            time.sleep(0.1)
        while channel.recv_ready():
            stdout += channel.recv(1024)
        stdout_decoded = stdout.decode()
        stdouts = stdout_decoded.split("\n")
        pprint("\n".join(stdouts[1:-1]))
        start = stdouts[-1]


@app.command()
def test():
    config = load_config()
    conn = Connection()
    conn.exec_cmd_list(
        config.events.push_start_exec, config.file_sync_config.remote_root_path  # type: ignore
    )


__all__ = ["main"]


def main():
    app()


if __name__ == "__main__":
    main()
