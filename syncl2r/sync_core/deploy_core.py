import pathlib
from ..connect_core import Connection
from ..config import get_global_config
from ..bash import kill_pid_and_child


def clear_last_pids():
    pass


def stop_last_pids(conn: Connection):
    config = get_global_config()
    pid_file = (
        pathlib.PurePath(config.file_sync_config.remote_root_path) / ".l2r" / "pids.txt"
    )
    _, out, _ = conn.exec_command(f"cat {pid_file.as_posix()}")
    pids = out.read().decode().split("\n")

    # # cmds = list(map(lambda v: f"kill -s 9 {v}", filter(lambda x: len(x) > 0, pids)))
    # cmds = [f'kill -s 9 {" ".join(pids)}']
    # # print(cmds)
    # conn.exec_cmd_list(cmds, config.file_sync_config.remote_root_path)
    kill_pid_and_child(pids)

    conn.exec_command(f"> {pid_file.as_posix()}")
