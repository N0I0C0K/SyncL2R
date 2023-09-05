import paramiko
from console import console, pprint
from config import get_global_config, ConnectConfig


class Connection:
    def __init__(self, config: ConnectConfig | None = None) -> None:
        self.config = (
            config if config is not None else get_global_config().connect_config
        )
        self.ssh_client = paramiko.SSHClient()
        self.close = self.ssh_client.close
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        console.print(
            f"[info]start link to [underline red]{self.config.ip}:{self.config.port}@{self.config.username}",
            end=" ",
        )
        try:
            self.ssh_client.connect(
                self.config.ip,
                self.config.port,
                self.config.username,
                self.config.password,
                timeout=5,
            )
        except TimeoutError:
            pprint(
                f"[danger.high]can not connect to the {self.config.ip}:{self.config.port}!"
            )
            raise
        else:
            console.print("[green]success")
        self.exec_command = self.ssh_client.exec_command
        self.__sftp_client: paramiko.SFTPClient | None = None

    @property
    def sftp_client(self) -> paramiko.SFTPClient:
        if self.__sftp_client is None:
            self.__sftp_client = self.ssh_client.open_sftp()
        return self.__sftp_client

    def __del__(self):
        self.ssh_client.close()
        if self.__sftp_client is not None:
            self.__sftp_client.close()
        console.print(
            f"[green bold]connection[red]({self.config.ip}:{self.config.port}@{self.config.username})[/] close[/] "
        )

    def invoke_cmd_list(self, cmd_list: list[str]):
        cmd_encode_list = []
        for cmd in cmd_list:
            cmd_encode_list.append(f'echo "[*]{cmd} start execute"')
            cmd_encode_list.append(cmd)
        cmd_res = ";".join(cmd_encode_list)
        stdin, stdout, stderr = self.ssh_client.exec_command(cmd_res)
        pprint(stdout.read())


# global_connection: Connection | None = None


# def set_global_connection(connection: Connection):
#     global global_connection
#     global_connection = connection


# def get_connection() -> Connection:
#     if global_connection is None:
#         raise ValueError("global connection is not init")
#     return global_connection
