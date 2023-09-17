import typer
from .app import app
from ..config import load_config
from ..console import pprint
from ..connect_core import Connection


@app.command(name="shell", help="open shell to remote")
def link_shell(
    config: str = typer.Option(
        None, help="config file path, default find one match ./*.l2r.yaml"
    )
):
    import time
    from ..utils.ssh_utils import channel_recv

    load_config(config)
    try:
        connection = Connection()
        ssh_client = connection.ssh_client
    except Exception as e:
        pprint(f"[danger]connect to remote failed, error info: {e}")
        return
    channel = ssh_client.invoke_shell()
    time.sleep(0.1)
    while not channel.recv_ready():
        pass

    while True:
        t = channel_recv(channel).decode()
        print(t, end="")
        cmd = input()
        cmd += "\n"
        channel.send(cmd.encode())
        time.sleep(0.1)
