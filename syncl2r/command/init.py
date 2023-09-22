import os
import re
import typer
import pathlib
from .app import app
from ..config import load_config
from ..console import pprint
from ..connect_core import Connection


@app.command(name="init", help="init config file for current path")
def init(
    remote_url: str = typer.Option(
        None,
        "--remote-url",
        "-u",
        help="the link to the remote ssh host. like => username:password@ip / username:password@ip:port / username@ip:port /username@ip",
    ),
    key_name: str = typer.Option(
        None,
        help="Set this item to enable key login, private key link to ~/.ssh/[key_name]",
    ),
    remote_path: str = typer.Option(
        None,
        "--remote-path",
        "-rp",
        help="remote path to sync, default same as local dir name",
    ),
    sync_path: str = typer.Option(
        ".", "--local-path", "-lp", help="local path to sync"
    ),
    test_connect: bool = typer.Option(
        default=False,
        help="test connection before write config file, Used to check whether the connection configuration is correct",
    ),
):
    if not os.path.exists("./.l2r"):
        os.makedirs(".l2r")
    conifg_file = os.path.abspath("./.l2r/config.l2r.yaml")
    if os.path.exists(conifg_file):
        replace = typer.confirm(f"{conifg_file} already exist, do you want to replace?")
        if not replace:
            raise typer.Abort()

    # check weather sync dir is right config
    sync_dir = sync_path
    sync_dir_name = os.path.split(os.path.abspath(sync_dir))[-1]
    if not os.path.exists(sync_dir):
        pprint(f"[red]{sync_dir} does not exist")
        return

    if remote_path is None:
        remote_path = f"{sync_dir_name}"

    init_data = {
        "connect_config": {},
        "file_sync_config": {
            "root_path": sync_dir,
            "remote_root_path": remote_path,
            "exclude": [],
        },
        "events": {"push_complete_exec": [], "push_start_exec": []},
        "actions": [],
    }

    # check remote connection config is alright
    ip: str | None = None
    port: str | None = None
    if remote_url is not None:
        res = re.match(r"(.*?)(:(.*?))?@([0-9,\.]*):?([0-9]*)?", remote_url)
        if res is None:
            pprint(f"[danger]remote url({remote_url}) is invalid")
            return
        username, _, pwd, ip, port = res.groups()
        init_data["connect_config"] |= {"username": username}
        if pwd and pwd != "":
            init_data["connect_config"] |= {"password": pwd}

    if key_name is not None:
        key_file = pathlib.Path.home() / ".ssh" / key_name
        if not key_file.exists():
            raise ValueError(f"key file({key_file.as_posix()}) is not exist")
        init_data["connect_config"] |= {"key_name": key_name}

    if ip is None:
        raise ValueError("ip address is none, please check your config is alright")

    if port is None or port == "":
        port = "22"

    init_data["connect_config"] |= {"ip": ip, "port": int(port)}

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
