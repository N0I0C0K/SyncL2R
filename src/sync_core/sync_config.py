import os
import re
import json
import pathlib
from console import console

import enum


class SyncMode(enum.IntEnum):
    force = 1       # 先删除掉原来的文件再上传新的文件
    normal = 2      # 直接上传新的文件进行覆盖
    soft = 3        # 只上传新添加的文件


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
        if not os.path.exists(self.root_path):
            raise FileNotFoundError
        self.sync_mode: SyncMode = SyncMode.normal

    def escape_file(self, path: pathlib.Path) -> bool:
        for par in self.exclude:
            # if re.match(par, path):
            #     console.log(f'{path} [red bold]ignore')
            #     return True
            if path.match(par):
                return True
        return False
