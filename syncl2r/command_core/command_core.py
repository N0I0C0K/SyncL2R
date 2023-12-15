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
        from syncl2r.config.constant import (
            Temp_Output_Path,
            Temp_Pids_Path,
            Remote_Root_Abs_Path,
        )

        # to let all command exec in the program root path, we zip all command in to a single command combian by &
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

                    # for the first background task, refresh the log file and write some info at the beginning of the file
                    if self.background_tasks_num == 0:
                        cmd_encode_list.append(
                            f'echo {quote(time.strftime(r"%Y-%m-%d %H:%M:%S"))} > {(Remote_Root_Abs_Path/Temp_Output_Path).as_posix()}'
                        )

                    # if there are more than one background process, then put their output in one log file
                    cmd_encode_list.append(
                        f"nohup {cmd.cmd} >> {(Remote_Root_Abs_Path/Temp_Output_Path).as_posix()} 2>&1 & echo $! >> {(Remote_Root_Abs_Path/Temp_Pids_Path).as_posix()}"
                    )
                    self.background_tasks_num += 1

        # use separator to record process
        s_key = token_hex(8)
        cmd_encode_list.append(f"echo {s_key}")
        cmd_res = "&&".join(cmd_encode_list)

        start_time = time.time()
        stdin, stdout, stderr = self.ssh_client.exec_command(cmd_res)

        # count zero len size
        zero_count = 0
        while stdout.readable():
            line: str = stdout.readline()

            # 1000 is a save count
            if zero_count >= 1000:
                break

            if len(line) == 0:
                # Under my tests, if there are too many white space read from "readline" function, it means command execute failed
                zero_count += 1
                continue

            if line.startswith(s_key):
                break
            pprint(line, end="")

        if zero_count >= 1000:
            error_info = stderr.read().decode()
            pprint(f"[red]{error_info}")

        pprint(f"all command exec finished, use {time.time() - start_time:.2f} seconds")
