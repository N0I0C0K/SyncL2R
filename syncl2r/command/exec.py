import typer
from .app import app
from ..config import get_global_config
from ..console import pprint
from ..connect_core import Connection


@app.command(name="exec", help="exec action")
def exec_action(
    action: str = typer.Argument(""),
    show_list: bool = typer.Option(False, "--all", "-a", help="show the actions list"),
):
    config_modal = get_global_config()
    if config_modal.actions is None:
        pprint("[warn]config has no action")
        return
    if show_list:
        pprint("[blue]actions: ")
        for k, val in config_modal.actions.items():
            pprint(f"[yellow]* {k} [grey50]{val.description}")
        return

    if config_modal.actions is None or action not in config_modal.actions:
        pprint(f"[warn]can not find '{action}' in config.actions")
        return
    cmd_list = config_modal.actions[action].cmd
    if cmd_list is None:
        pprint("[warn]no cmd need to exec, now quit")
        return
    conn = Connection(config_modal.connect_config)
    conn.cmd.exec_cmd_list(cmd_list)
