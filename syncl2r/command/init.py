import os
import re
import typer
from .app import app
from ..config import load_config
from ..console import pprint
from ..connect_core import Connection


@app.command(name="init", help="init config file for current path")
def init(
    remote_url: str = typer.Argument(
        ...,
        help="the link to the remote ssh host. like => username:password@ip or username:password@ip:port",
    ),
    remote_path: str = typer.Option(
        default=None, help="remote path to sync, default same as local dir name"
    ),
    sync_path: str = typer.Option(default=".", help="local path to sync"),
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

    sync_dir = sync_path
    sync_dir_name = os.path.split(os.path.abspath(sync_dir))[-1]
    if not os.path.exists(sync_dir):
        pprint(f"[red]{sync_dir} does not exist")
        return

    if remote_path is None:
        remote_path = f"{sync_dir_name}"

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
