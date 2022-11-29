import os
import re
import json
import pathlib
from console import console


class SyncConfig:
    def __init__(self, config_file_path: str) -> None:
        if not os.path.exists(config_file_path):
            raise FileNotFoundError
        with open(config_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        self.file_sync_config: dict = data['file_sync_config']
        self.exclude: list[str] = self.file_sync_config['exclude']
        self.remote_root_path = self.file_sync_config['remote_root_path']
        self.root_path = os.path.abspath(self.file_sync_config['root_path'])

    def escape_file(self, path: pathlib.Path) -> bool:
        for par in self.exclude:
            # if re.match(par, path):
            #     console.log(f'{path} [red bold]ignore')
            #     return True
            if path.match(par):
                console.log(f'{path.name} [red bold]ignore')
                return True
        return False
