import json
import os
import re

import typer

from connect_core import ConnectConfig, Connection
from console import pprint
from sync_core import SyncConfig, SyncMode, SyncTask

app = typer.Typer()


@app.command(name='push')
def push(config: str = typer.Option('./l2r_config.json', help='config file path, default to ./l2r_config.json'),
         mode: int = typer.Option(2, help='sync mode 1:force(del then upload) 2:normal 3:soft(upload only new files)')):
    if not os.path.exists(config):
        pprint(
            f'[danger]config file [blue]({config})[/] not find.\n[info]please check whether [blue]{config}[/] exists')
        return
    connect_config = ConnectConfig(config_path=config)
    connection = Connection(connect_config)
    sync_config = SyncConfig(config)
    sync_config.sync_mode = SyncMode(mode)
    sftp_client = connection.ssh_client.open_sftp()
    sync_task = SyncTask(connection.ssh_client, sftp_client, sync_config)
    sync_task.push()
    sftp_client.close()


@app.command(name='pull')
def pull(files: list[str] = typer.Argument(default=None, help='files to pull, default to hole file'),
         config: str = typer.Option('./l2r_config.json', help='config file path, default to ./l2r_config.json')):
    connect_config = ConnectConfig(config_path=config)
    connection = Connection(connect_config)
    sync_config = SyncConfig(config)
    sftp_client = connection.ssh_client.open_sftp()
    sync_task = SyncTask(connection.ssh_client, sftp_client, sync_config)
    files = ['.'] if files is None or len(files) == 0 else files
    for file in files:
        sync_task.pull(file)


@app.command(name='init')
def init(remote_url: str = typer.Argument(
        ..., help='the link to the remote ssh host. like => username:password@ip or username:password@ip:port'),
        remote_path: str = typer.Option(
        default='', help='remote path to sync'),
        config_name: str = typer.Option(
        default='config', help='file name to the config name => l2r_config_name.json'),
        test_connect: bool = typer.Option(default=False, help='test connect to the host')):
    sync_dir = '.'
    if not os.path.exists(sync_dir):
        pprint(f'[red]{sync_dir} does not exist')
        return

    res = re.match(r"(.*?):(.*?)@([0-9,\.]*):?([0-9]*)?",
                   remote_url)
    if res is None:
        pprint(f'[danger]{remote_url} is invalid')
        return
    username, pwd, ip, port = res.groups()
    port = 22 if port == '' else int(port)
    if test_connect:
        try:
            conn = Connection(ConnectConfig(username=username,
                                            password=pwd, port=port, ip=ip))
        except:
            pprint(
                f'[danger.high]exception happend during connecting to the host {remote_url}')
            return

    init_data = {
        "connect_config": {
            "ip": ip,
            "port": port,
            "username": username,
            "password": pwd
        },
        "file_sync_config": {
            "root_path": sync_dir,
            "remote_root_path": remote_path,
            "exclude": []
        }
    }
    conifg_file = f'./l2r_{config_name}.json'
    if os.path.exists(conifg_file):
        pprint(f'[red]{conifg_file} already exist! now relpace')
    with open(conifg_file, 'w+', encoding='utf-8') as file:
        json.dump(init_data, file, indent=4)


@app.command(name='show')
def show_files(config_path: str = typer.Option('./l2r_config.json', help='config file path, default to ./l2r_config.json')):
    sync_config = SyncConfig(config_path)
    sync_task = SyncTask(None, None, sync_config)  # type: ignore #ignore
    sync_task.show_sync_file_tree()


@ app.command(name='test')
def test_func():
    connect_config = ConnectConfig(config_path='./l2r_config.json')
    connection = Connection(connect_config)
    sftp = connection.ssh_client.open_sftp()
    pprint(sftp.listdir('/home/test'))
    pass


def main():
    app()


if __name__ == '__main__':
    main()
