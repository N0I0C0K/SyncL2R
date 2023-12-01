from .constant import Remote_Config_Data_Path
from pydantic import BaseModel


class RemoteConfig(BaseModel):
    pids: list[str]

    @classmethod
    def default(cls) -> "RemoteConfig":
        return RemoteConfig(pids=[])


__config: RemoteConfig | None = None


def get_remote_config() -> RemoteConfig:
    if __config is None:
        global __config
        __config = load_remote_config()
    return __config


def load_remote_config() -> RemoteConfig:
    from ..connect_core import get_global_connection
    from .local import get_global_config

    conn = get_global_connection()
    data = conn.utils.read_file(Remote_Config_Data_Path)
    if len(data) < 4:
        return RemoteConfig.default()
    import yaml

    try:
        from yaml import CLoader as Loader
    except ImportError:
        from yaml import Loader
    obj = yaml.load(data, Loader)
    return RemoteConfig.parse_obj(obj)


def save_remote_config():
    import yaml

    yaml.dump(get_remote_config())
    pass
