import pathlib
from ..connect_core import Connection
from ..config import get_global_config

from ..console import pprint

from ..config.constant import Temp_Pids_Path, Temp_Output_Path, Remote_Root_Abs_Path


def clear_last_pids(conn: Connection):
    config = get_global_config()
    pid_file = (
        pathlib.PurePath(config.file_sync_config.remote_root_path) / Temp_Pids_Path
    )
    conn.exec_command(f"> {pid_file.as_posix()}")


def get_pids(conn: Connection) -> list[str]:
    config = get_global_config()
    pid_file = (
        pathlib.PurePath(config.file_sync_config.remote_root_path) / Temp_Pids_Path
    )
    _, out, _ = conn.exec_command(f"cat {pid_file.as_posix()}")
    raw_pids = out.read().decode().removesuffix("\n").split("\n")
    pids = list(filter(lambda x: len(x) > 0, raw_pids))

    return pids


def get_remote_log(conn: Connection, additional_cmds: list[str] | None = None) -> str:
    config = get_global_config()
    log_file = (
        pathlib.PurePath(config.file_sync_config.remote_root_path) / Temp_Output_Path
    )
    cmd = f"cat {log_file.as_posix()}"
    if additional_cmds is not None and len(additional_cmds) > 0:
        cmd = cmd + "|" + "|".join(additional_cmds)

    _, out, _ = conn.exec_command(cmd)
    raw = out.read().decode()
    return raw


def check_still_running(conn: Connection) -> bool:
    pids = get_pids(conn)

    if len(pids) == 0:
        return False
    _, out, _ = conn.exec_command(f'ps -p {" ".join(pids)}')
    lines = out.read().decode().splitlines()
    return len(lines) > 1


def stop_last_pids(conn: Connection):
    pids = get_pids(conn)
    if len(pids) == 0:
        return

    from ..bash import kill_pid_and_child

    pprint(f"Will terminate the process and its child processes: {pids}")

    # # cmds = list(map(lambda v: f"kill -s 9 {v}", filter(lambda x: len(x) > 0, pids)))
    # cmds = [f'kill -s 9 {" ".join(pids)}']
    # # print(cmds)
    # conn.exec_cmd_list(cmds, config.file_sync_config.remote_root_path)
    pprint(kill_pid_and_child(pids))
    clear_last_pids(conn)


def store_log(conn: Connection):
    from ..config.constant import History_Log_Path

    his = Remote_Root_Abs_Path / History_Log_Path
    t = conn.exec_command_sample(f"head {his.as_posix()} -c 1").removesuffix("\n")
    conn.exec_command("cp ")
    pass
