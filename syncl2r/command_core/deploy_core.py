import pathlib
from syncl2r.connect_core import Connection
from syncl2r.config import get_global_config

from syncl2r.console import pprint

from syncl2r.config.constant import Temp_Pids_Path, Temp_Output_Path


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

    from syncl2r.bash import kill_pid_and_child

    pprint(f"Will terminate the process and its child processes: {pids}")

    # # cmds = list(map(lambda v: f"kill -s 9 {v}", filter(lambda x: len(x) > 0, pids)))
    # cmds = [f'kill -s 9 {" ".join(pids)}']
    # # print(cmds)
    # conn.exec_cmd_list(cmds, config.file_sync_config.remote_root_path)
    pprint(kill_pid_and_child(pids))
    clear_last_pids(conn)
    store_log(conn)


def store_log(conn: Connection):
    import time
    from syncl2r.config.constant import (
        History_Log_Path,
        Temp_Output_Path,
        Remote_Root_Abs_Path,
    )

    out = Remote_Root_Abs_Path / Temp_Output_Path
    t = conn.exec_command_sample(f"head {out.as_posix()} -n 1").removesuffix("\n")
    s_t = time.localtime()
    try:
        s_t = time.strptime(t, r"%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass

    his = (
        Remote_Root_Abs_Path
        / History_Log_Path
        / f'{time.strftime(r"%Y%m%d%H%M%S", s_t)}.log'
    )

    his_dir = (Remote_Root_Abs_Path / History_Log_Path).as_posix()

    if not conn.sftp_utils.exist_remote(his_dir):
        conn.sftp_utils.mkdir(his_dir)

    conn.exec_command(f"cp {out.as_posix()} {his.as_posix()}")
    pprint(f"[green] store last output log to {his.as_posix()}")
