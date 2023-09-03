from pydantic import BaseModel
import pathlib
import json
import os


class ConnectConfig(BaseModel):
    ip: str
    port: int = 22
    username: str | None
    password: str | None


class FileSyncConfig(BaseModel):
    root_path: str
    remote_root_path: str
    exclude: list[str]

    def escape_file(self, path: pathlib.Path) -> bool:
        for par in self.exclude:
            # if re.match(par, path):
            #     console.log(f'{path} [red bold]ignore')
            #     return True
            if path.match(par):
                return True
        return False

    def __init__(self, **data):
        super().__init__(**data)
        self.root_path = os.path.abspath(self.root_path)


class EventConfig(BaseModel):
    push_complete_exec: list[str] | None = None
    push_start_exec: list[str] | None = None


class GlobalConfig(BaseModel):
    connect_config: ConnectConfig
    file_sync_config: FileSyncConfig
    events: EventConfig | None = None


global_config: GlobalConfig | None = None


def load_config(config_path_or_obj: pathlib.Path | dict) -> GlobalConfig:
    if isinstance(config_path_or_obj, dict):
        modal = GlobalConfig.parse_obj(config_path_or_obj)
        set_global_config(modal)
        return modal
    if config_path_or_obj.suffix == ".yaml":
        import yaml

        try:
            from yaml import CLoader as Loader
        except ImportError:
            from yaml import Loader
        obj = yaml.load(config_path_or_obj.read_text(), Loader)
        return set_global_config(GlobalConfig.parse_obj(obj))
    elif config_path_or_obj.suffix == ".json":
        obj = json.loads(config_path_or_obj.read_text())
        modal = GlobalConfig.parse_obj(obj)
        set_global_config(modal)
        return modal
    raise ValueError("config file type is not support")


def set_global_config(config: GlobalConfig) -> GlobalConfig:
    global global_config
    global_config = config
    return global_config


def get_global_config() -> GlobalConfig:
    if global_config is None:
        raise ValueError("config is not initd")
    return global_config


if __name__ == "__main__":
    print(load_config(pathlib.Path("./test/config.local.yaml")))
