import paramiko
from console import console, pprint
from config import GlobalConfig, get_global_config, ConnectConfig


class Connection:
    def __init__(self, config: ConnectConfig | None = None) -> None:
        self.config = (
            config if config is not None else get_global_config().connect_config
        )
        self.ssh_client = paramiko.SSHClient()
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

    def __del__(self):
        self.ssh_client.close()
        console.print(
            f"[green bold]connection[red]({self.config.ip}:{self.config.port}@{self.config.username})[/] close[/] "
        )
