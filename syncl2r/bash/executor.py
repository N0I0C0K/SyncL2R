import shlex
from secrets import token_hex
from syncl2r.console import pprint
from syncl2r.config import get_global_config
from syncl2r.connect_core import Connection


def execute_bash(
    sh: str, *args, pwd: str | None = None, conn: Connection | None = None
) -> str:
    if pwd is None:
        config = get_global_config()
        pwd = config.file_sync_config.remote_root_path
    conn = Connection.default_connection()
    sh_file = f".syncl2r_bash_{token_hex(8)}.sh"
    sh = shlex.quote(sh % args)
    conn.ssh_client.exec_command(f"cd {pwd}; echo {sh} > {sh_file}")
    _, out_r, err_r = conn.ssh_client.exec_command(
        f"cd {pwd}; bash {sh_file}; rm {sh_file}"
    )
    out = out_r.read().decode().removesuffix("\n")
    err = err_r.read()
    if len(err) > 0:
        pprint(f"[red]cmd exec err: {err.decode()}")
    # conn.ssh_client.exec_command(f"cd {pwd}; rm {sh_file}")
    return out


def execute_cmd(cmd: str, pwd: str | None = None) -> str:
    if pwd is None:
        config = get_global_config()
        pwd = config.file_sync_config.remote_root_path
    conn = Connection.default_connection()
    return (
        conn.ssh_client.exec_command(f"cd {pwd} ; {cmd}")[1]
        .read()
        .decode()
        .removesuffix("\n")
    )
