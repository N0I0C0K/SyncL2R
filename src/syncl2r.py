import typer
from connect_core import ConnectConfig, Connection
from sync_core import SyncTask, SyncConfig
from console import console

app = typer.Typer()


@app.command(name='push')
def push(config_path: str = typer.Option('./l2r_config.json', help='config file path, default to ./l2r_config.json')):
    connect_config = ConnectConfig(config_path)
    connection = Connection(connect_config)
    sync_config = SyncConfig(config_path)
    sftp_client = connection.ssh_client.open_sftp()
    sync_task = SyncTask(connection.ssh_client, sftp_client, sync_config)
    sync_task.show_sync_file_tree()
    sftp_client.close()


@app.command()
def pull():
    pass


if __name__ == '__main__':
    app()
