from .constant import Remote_Config_Data_Path
from ..sync_core import RemoteFileManager
from pydantic import BaseModel


class RemoteConfig(BaseModel):
    pids: list[str]

    def default():
        return RemoteConfig(pids=[])


def load_remote_config(rfile: RemoteFileManager) -> RemoteConfig:
    from ..connect_core import get_global_connection
    from .local import get_global_config

    conn = get_global_connection()
    data = conn.utils.read_file(Remote_Config_Data_Path)
    if len(data) < 4:
        return


def save_remote_config(config: RemoteConfig):
    pass
