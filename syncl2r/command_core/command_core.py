from shlex import quote

from paramiko import SSHClient

from syncl2r.config.constant import Temp_Output_Path, Temp_Pids_Path
from syncl2r.config.local import AdvancedCommand

from ..console import pprint


class CommandExector:
    def __init__(self, conn: SSHClient) -> None:
        self.ssh_client = conn

    def exec_cmd_list(
        self, cmd_list: list[str | AdvancedCommand] | list[str], pwd: str | None = None
    ):
        import time

        cmd_encode_list: list[str] = []
        if pwd:
            cmd_encode_list.append(f"cd {quote(pwd)}")

        cmd_encode_list.append('echo "Your current remote path:"')
        cmd_encode_list.append("pwd")
        for cmd in cmd_list:
            if isinstance(cmd, str):
                cmd_encode_list.append(
                    f"echo '[green][*]\"{quote(cmd)}\" start execute'"
                )
                cmd_encode_list.append(cmd)
            elif isinstance(cmd, AdvancedCommand):
                if cmd.mode == "once":
                    cmd_encode_list.append(
                        f"echo '[green][*]\"{quote(cmd.cmd)}\" start execute'"
                    )
                    cmd_encode_list.append(cmd.cmd)
                elif cmd.mode == "nohup":
                    cmd_encode_list.append(
                        f"echo '[red][*]\"{quote(cmd.cmd)}\" (forever task) start execute'"
                    )
                    cmd_encode_list.append(
                        f"nohup {cmd.cmd} > {Temp_Output_Path.as_posix()} 2>&1 & echo $! >> {Temp_Pids_Path.as_posix()}"
                    )
        cmd_encode_list.append("echo sdif92ja0lfas")
        cmd_res = ";".join(cmd_encode_list)

        start_time = time.time()
        stdin, stdout, stderr = self.ssh_client.exec_command(cmd_res)
        while stdout.readable():
            line: str = stdout.readline()
            if len(line) == 0:
                continue
            if line.startswith("sdif92ja0lfas"):
                break
            pprint(line, end="")
        pprint(f"all command exec finished, use {time.time() - start_time:.2f} seconds")
