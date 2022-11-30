import json
import os
import re

import typer

from connect_core import ConnectConfig, Connection
from console import console
from sync_core import SyncConfig, SyncMode, SyncTask

app = typer.Typer()


@app.command(name='push')
def push(config_path: str = typer.Option('./l2r_config.json', help='config file path, default to ./l2r_config.json'),
         sync_mode: int = typer.Option(2, help='sync mode 1:force(del then upload) 2:normal 3:soft(upload only new files)')):
    if not os.path.exists(config_path):
        console.print(
            f'[red bold]config file [blue]({config_path})[/] not find.\n[green]please check whether [blue]{config_path}[/] exists')
        return
    connect_config = ConnectConfig(config_path)
    connection = Connection(connect_config)
    sync_config = SyncConfig(config_path)
    sync_config.sync_mode = SyncMode.force
    sftp_client = connection.ssh_client.open_sftp()
    sync_task = SyncTask(connection.ssh_client, sftp_client, sync_config)
    sync_task.start()
    sftp_client.close()


@app.command()
def pull(files: list[str], config_path: str = typer.Option('./l2r_config.json', help='config file path, default to ./l2r_config.json')):
    print(files)

    pass


@ app.command(name='init')
def init(sync_dir: str,
         remote_url: str = typer.Option(
             default='', help='the link to the remote ssh host. like => username:password@ip or username:password@ip:port'),
         remote_path: str = typer.Option(
             default='', help='remote path to sync'),
         config_file_name: str = typer.Option(default='l2r_config', help='file name to the config name => config_file_name.json')):
    if not os.path.exists(sync_dir):
        console.print(f'[red]{sync_dir} does not exist')
        return
    sync_dir = os.path.abspath(sync_dir)

    init_data = {
        "connect_config": {
            "ip": "",
            "port": 22,
            "username": "",
            "password": ""
        },
        "file_sync_config": {
            "root_path": sync_dir,
            "remote_root_path": remote_path,
            "exclude": []
        }
    }
    conifg_file = f'./{config_file_name}.json'
    if os.path.exists(conifg_file):
        console.print(f'[red]{conifg_file} already exist!')
        return
    with open(conifg_file, 'w+', encoding='utf-8') as file:
        json.dump(init_data, file, indent=4)


@ app.command(name='test')
def test_func():
    pass


if __name__ == '__main__':
    app()
