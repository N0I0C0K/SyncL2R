import os
import re

import typer
import pathlib

from config import load_config
from console import pprint
from connect_core import Connection
from sync_core import SyncTask, SyncMode

app = typer.Typer()


@app.command(name="push", help="push file to remote")
def push(
    config: str = typer.Option(
        "./l2r_config.yaml", help="config file path, default to ./l2r_config.yaml"
    ),
    mode: int = typer.Option(
        2,
        help="sync mode 1:force(del then upload) 2:normal 3:soft(upload only new files)",
    ),
):
    try:
        load_config(pathlib.Path(config))
        connection = Connection()
        sftp_client = connection.ssh_client.open_sftp()
        sync_task = SyncTask(connection.ssh_client, sftp_client)
        sync_task.push(mode=SyncMode(mode))
        sftp_client.close()
    except Exception as e:
        pprint(f"\n[danger]err happen in command push, error info: {e}")


@app.command(name="pull", help="pull files from remote")
def pull(
    files: list[str] = typer.Argument(
        default=None, help="files to pull, default to hole file"
    ),
    config: str = typer.Option(
        "./l2r_config.yaml", help="config file path, default to ./l2r_config.yaml"
    ),
):
    try:
        load_config(pathlib.Path(config))
        connection = Connection()
        sftp_client = connection.ssh_client.open_sftp()
        sync_task = SyncTask(connection.ssh_client, sftp_client)
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
        help="custom file name for the config name => l2r_config_name.yaml",
    ),
    test_connect: bool = typer.Option(
        default=False,
        help="test connection before write config file, Used to check whether the connection configuration is correct",
    ),
):
    conifg_file = os.path.abspath(f"./l2r_{config_name}.yaml")
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
def show_files(
    config: str = typer.Option(
        "./l2r_config.yaml", help="config file path, default to ./l2r_config.yaml"
    )
):
    load_config(pathlib.Path(config))
    sync_task = SyncTask(None, None)  # type: ignore #ignore
    sync_task.show_sync_file_tree()


@app.command(name="shell", help="open shell to remote")
def link_shell(
    config: str = typer.Option(
        "./l2r_config.yaml", help="config file path, default to ./l2r_config.yaml"
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
        while channel.recv_ready():
            channel.recv(1024)
        user_cmd = input(start)
        user_cmd = user_cmd + "\n"
        channel.send(user_cmd.encode())
        stdout = bytes()
        time.sleep(0.05)
        while channel.recv_ready():
            stdout += channel.recv(1024)
        stdout_decoded = stdout.decode()
        stdouts = stdout_decoded.split("\n")
        pprint("\n".join(stdouts[1:-1]))
        start = stdouts[-1]


__all__ = ["main"]


def main():
    app()


if __name__ == "__main__":
    main()
