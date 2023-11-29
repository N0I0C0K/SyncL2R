class RemoteConfig:
    pids: list[str]
    log_file_name: str


def load_remote_config() -> RemoteConfig:
    from ..connect_core import get_global_connection
    from .local import get_global_config

    conn = get_global_connection()


def save_remote_config(config: RemoteConfig):
    pass
