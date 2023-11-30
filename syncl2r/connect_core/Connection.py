import typing
import paramiko
import pathlib
from shlex import quote
from ..console import pprint
from .utils import ConnectionFunction
from ..config import get_global_config, ConnectConfig, AdvancedCommand
from config.constant import Temp_Output_Path, Temp_Pids_Path


class Connection:
    def __init__(self, config: ConnectConfig | None = None) -> None:
        self.config = (
            config if config is not None else get_global_config().connect_config
        )
        self.ssh_client = paramiko.SSHClient()
        self.close = self.ssh_client.close

        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.load_system_host_keys()
        self.__sftp_client: paramiko.SFTPClient | None = None
        self.__utils: ConnectionFunction | None = None

        pprint(
            f"[info]start link to [underline red]{self.config.ip}:{self.config.port}@{self.config.username}",
            end=" ",
        )
        try:
            if self.config.password is not None:
                self.ssh_client.connect(
                    self.config.ip,
                    self.config.port,
                    self.config.username,
                    self.config.password,
                    timeout=5,
                )
            elif self.config.key_name is not None:
                key_file = pathlib.Path.home() / ".ssh" / self.config.key_name
                if not key_file.exists():
                    raise FileNotFoundError(f"{key_file.as_posix()} can not be found")
                with key_file.open() as f:
                    pkey = paramiko.RSAKey.from_private_key(f)
                self.ssh_client.connect(
                    self.config.ip, self.config.port, self.config.username, pkey=pkey
                )
            else:
                raise ValueError("connection config is invaild")
        except TimeoutError:
            pprint(
                f"[danger.high]can not connect to the {self.config.ip}:{self.config.port}!"
            )
            raise
        else:
            pprint("[green]success")
        self.exec_command = self.ssh_client.exec_command
        set_global_connection(self)

    @property
    def sftp_client(self) -> paramiko.SFTPClient:
        if self.__sftp_client is None:
            self.__sftp_client = self.ssh_client.open_sftp()
        return self.__sftp_client

    @property
    def utils(self) -> ConnectionFunction:
        if self.__utils is None:
            self.__utils = ConnectionFunction(self.ssh_client)
        return self.__utils

    def __del__(self):
        self.ssh_client.close()
        if self.__sftp_client is not None:
            self.__sftp_client.close()
        print(
            f"connection({self.config.ip}:{self.config.port}@{self.config.username}) close"
        )

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


global_connection: Connection | None = None


def set_global_connection(connection: Connection):
    global global_connection
    global_connection = connection


def get_global_connection() -> Connection:
    if global_connection is None:
        raise ValueError("global connection is not init")
    return global_connection
