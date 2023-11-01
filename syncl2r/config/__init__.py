import pathlib
import json
import os
import typing

from ..console import pprint
from pydantic import BaseModel


class ConnectConfig(BaseModel):
    ip: str
    port: int = 22
    username: str | None
    password: str | None
    key_name: str | None


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
        if not path.is_dir() and path.stat().st_size == 0:
            return True
        return False

    def __init__(self, **data):
        super().__init__(**data)
        self.root_path = os.path.abspath(self.root_path)
        # self.exclude.append("./.l2r")


class AdvancedCommand(BaseModel):
    cmd: str
    mode: typing.Literal["nohup", "once"] = "once"


class EventConfig(BaseModel):
    push_complete_exec: list[str | AdvancedCommand] | None = None
    push_start_exec: list[str | AdvancedCommand] | None = None
    start: list[str | AdvancedCommand] | None = None
    stop: list[str | AdvancedCommand] | None = None


class ActionConfig(BaseModel):
    cmd: list[str] | None
    description: str = ""


class GlobalConfig(BaseModel):
    connect_config: ConnectConfig
    file_sync_config: FileSyncConfig
    events: EventConfig | None = None
    actions: dict[str, ActionConfig] | None = None


global_config: GlobalConfig | None = None
l2r_path: pathlib.PurePath = pathlib.PurePath("./.l2r")


def load_config(
    config_path_or_obj: pathlib.Path | dict | str | None = None,
) -> GlobalConfig:
    if isinstance(config_path_or_obj, dict):
        modal = GlobalConfig.parse_obj(config_path_or_obj)
        set_global_config(modal)
        return modal
    if config_path_or_obj is None:
        if not os.path.exists("./.l2r"):
            raise FileNotFoundError(
                ".l2r dir is not find, Probably not initialized yet"
            )
        config_path_or_obj = (
            pathlib.Path(os.path.abspath(".")) / ".l2r" / "config.l2r.yaml"
        )
        # pprint(f"[info]use config file [red]{config_path_or_obj.as_posix()}")
        # for file_name in os.listdir("./.l2r"):
        #     if file_name.count(".l2r"):
        #         break

    if isinstance(config_path_or_obj, str):
        config_path_or_obj = pathlib.Path(os.path.abspath(config_path_or_obj))
    if isinstance(config_path_or_obj, pathlib.Path):
        if not config_path_or_obj.exists():
            raise FileNotFoundError("config not find!")

        if config_path_or_obj.suffix == ".yaml":
            import yaml

            try:
                from yaml import CLoader as Loader
            except ImportError:
                from yaml import Loader
            obj = yaml.load(config_path_or_obj.read_text(encoding="utf-8"), Loader)
            return set_global_config(GlobalConfig.parse_obj(obj))
        elif config_path_or_obj.suffix == ".json":
            obj = json.loads(config_path_or_obj.read_text(encoding="utf-8"))
            modal = GlobalConfig.parse_obj(obj)
            set_global_config(modal)
            return modal
    raise ValueError("config is not find")


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
