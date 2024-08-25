import pathlib
import json
import os
import typing

from typing import Annotated, Optional
from pydantic import BaseModel, Field


from .constant import Config_Path
from syncl2r.console import pprint


class ConnectConfig(BaseModel):
    host: str
    username: str
    port: int = 22
    password: str | None
    key_name: str | None


class FileSyncConfig(BaseModel):
    root_path: str
    remote_root_path: str
    exclude: Annotated[list[str], Field(default_factory=list)]
    use_git: Annotated[bool, Field(default=True)]

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

    def __post__init__(self):
        from .constant import update_local_root_path, update_remote_root_path

        self.root_path = os.path.abspath(self.root_path)

        update_local_root_path(self.root_path)
        update_remote_root_path(self.remote_root_path)

        if not os.path.exists("./git"):
            self.use_git = False


class AdvancedCommand(BaseModel):
    cmd: str
    mode: typing.Literal["nohup", "once"] = "once"
    location: typing.Literal["local", "remote"] = "remote"


class EventConfig(BaseModel):
    push_complete_exec: list[str | AdvancedCommand] | None = None
    push_start_exec: list[str | AdvancedCommand] | None = None
    start: list[str | AdvancedCommand] | None = None
    stop: list[str | AdvancedCommand] | None = None


class ActionConfig(BaseModel):
    cmd: list[str] | None
    description: str = ""


class ConfigModel(BaseModel):
    connect_config: ConnectConfig
    file_sync_config: FileSyncConfig
    events: EventConfig | None = None
    actions: dict[str, ActionConfig] | None = None


global_config: ConfigModel | None = None


def load_config(
    config_path_or_obj: pathlib.Path | dict | str | None = None,
) -> ConfigModel:
    if isinstance(config_path_or_obj, dict):
        modal = ConfigModel.model_validate(config_path_or_obj)
        set_global_config(modal)
        return modal
    if config_path_or_obj is None:
        config_path_or_obj = pathlib.Path(Config_Path)
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
            return set_global_config(ConfigModel.model_validate(obj))
        elif config_path_or_obj.suffix == ".json":
            obj = json.loads(config_path_or_obj.read_text(encoding="utf-8"))
            modal = ConfigModel.model_validate(obj)
            set_global_config(modal)
            return modal
    raise ValueError("config is not find")


def save_config(config: Optional[ConfigModel] = None):
    if config is None:
        config = get_global_config()
    with open(Config_Path, "w+", encoding="utf-8") as file:
        import yaml

        try:
            from yaml import CDumper as Dumper
        except:
            from yaml import Dumper

        yaml.dump(config.model_dump(), file, Dumper)


def set_global_config(config: ConfigModel) -> ConfigModel:
    global global_config
    global_config = config
    return global_config


def get_global_config() -> ConfigModel:
    if global_config is None:
        raise ValueError("config is not initd")
    return global_config


if __name__ == "__main__":
    print(load_config(pathlib.Path("./test/config.local.yaml")))
