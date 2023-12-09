from paramiko import SSHClient
from syncl2r.config.local import AdvancedCommand

from ..console import pprint


class CommandExector:
    def __init__(self, conn: SSHClient) -> None:
        self.ssh_client = conn
        self.background_tasks_num = 0

    def exec_cmd_list(
        self,
        cmd_list: list[str | AdvancedCommand] | list[str],
        pwd: str | None = None,
    ):
        import time
        from secrets import token_hex
        from shlex import quote
        from syncl2r.config.constant import Temp_Output_Path, Temp_Pids_Path

        cmd_encode_list: list[str] = []
        if pwd:
            cmd_encode_list.append(f"cd {quote(pwd)}")

        cmd_encode_list.append('echo "Your current remote path:"')
        cmd_encode_list.append("pwd")

        # if there are more than one background process, then put their output in one log file
        append_or_new = ">" if self.background_tasks_num == 0 else ">>"

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
                    if self.background_tasks_num == 0:
                        cmd_encode_list.append(
                            f'echo {quote(time.strftime(r"%Y-%m-%d %H:%M:%S"))}'
                        )
                    cmd_encode_list.append(
                        f"nohup {cmd.cmd} {append_or_new} {Temp_Output_Path.as_posix()} 2{append_or_new}&1 & echo $! >> {Temp_Pids_Path.as_posix()}"
                    )
                    self.background_tasks_num += 1

        # use separator to record process
        s_key = token_hex(8)
        cmd_encode_list.append(f"echo {s_key}")
        cmd_res = ";".join(cmd_encode_list)

        start_time = time.time()
        stdin, stdout, stderr = self.ssh_client.exec_command(cmd_res)
        while stdout.readable():
            line: str = stdout.readline()
            if len(line) == 0:
                continue
            if line.startswith(s_key):
                break
            pprint(line, end="")
        pprint(f"all command exec finished, use {time.time() - start_time:.2f} seconds")
