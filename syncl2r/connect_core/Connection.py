import paramiko
from .connect_config import ConnectConfig
from console import console, pprint


class Connection:
    def __init__(self, connect_config: ConnectConfig) -> None:
        self.config = connect_config
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        console.print(
            f'[info]start link to [underline red]{self.config.ip}:{self.config.port}@{self.config.username}', end=' ')
        try:
            self.ssh_client.connect(connect_config.ip,
                                    connect_config.port,
                                    connect_config. username,
                                    connect_config. password,
                                    timeout=5)
        except TimeoutError:
            pprint(
                f'[danger.high]can not connect to the {connect_config.ip}:{connect_config.port}!')
            raise
        else:
            console.print('[green]success')
        self.exec_command = self.ssh_client.exec_command

    def __del__(self):
        self.ssh_client.close()
        console.print(
            f'[green bold]connection[red]({self.config.ip}:{self.config.port}@{self.config.username})[/] close[/] ')
