import pathlib
import typing
from shlex import quote

import paramiko
from ..config.constant import Temp_Output_Path, Temp_Pids_Path

from ..config import ConnectConfig, get_global_config
from ..console import pprint
from .utils import ConnectionFunction
from ..command_core import CommandExector


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
        self.__cmd: CommandExector | None = None

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

    def exec_command_sample(self, command: str) -> str:
        """sample exec a command, without advanced function

        Args:
            command (str): cmd

        Returns:
            str: output
        """
        _, out, err = self.exec_command(command)
        res = out.read().decode()
        return res

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

    @property
    def cmd(self) -> CommandExector:
        if self.__cmd is None:
            self.__cmd = CommandExector(self.ssh_client)
        return self.__cmd

    def __del__(self):
        self.ssh_client.close()
        if self.__sftp_client is not None:
            self.__sftp_client.close()
        print(
            f"connection({self.config.ip}:{self.config.port}@{self.config.username}) close"
        )


global_connection: Connection | None = None


def set_global_connection(connection: Connection):
    global global_connection
    global_connection = connection


def get_global_connection() -> Connection:
    if global_connection is None:
        raise ValueError("global connection is not init")
    return global_connection
