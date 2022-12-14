import json
import paramiko


class ConnectConfig:
    def __init__(self, *,
                 config_path: str = ...,
                 ip: str = ...,
                 port: int = ...,
                 username: str = ...,
                 password: str = ...) -> None:
        if config_path != ...:
            with open(config_path, 'r', encoding='utf-8') as file:
                self.raw_data = json.load(file)['connect_config']
            self.ip: str = self.raw_data['ip']
            self.port: int = self.raw_data['port']
            self.username: str = self.raw_data['username']
            self.password: str = self.raw_data['password']
        else:
            self.ip = ip
            self.port = port
            self.username = username
            self.password = password
