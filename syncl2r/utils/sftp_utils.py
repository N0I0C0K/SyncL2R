import os
import enum
import paramiko
import typing
import pathlib
from .utils import get_file_md5


class FileType(enum.IntFlag):
    DIR = 4
    NORMAL_FILE = 8


def upload_file_or_dir(sftp_client: paramiko.SFTPClient,
                       localfile: str, remote_path: str,
                       call_back: typing.Callable[[str], None] | None = None,
                       *,
                       escape_func: typing.Callable[[pathlib.Path], bool] | None = None):
    if escape_func and escape_func(pathlib.Path(localfile)):
        return
    if os.path.isdir(localfile):
        upload_dir(sftp_client, localfile, remote_path)
    else:
        upload_file(sftp_client, localfile, remote_path)
        if call_back:
            call_back(localfile)


def upload_dir(sftp_client: paramiko.SFTPClient,
               localdir: str,
               remotedir: str):
    if not os.path.isdir(localdir):
        return
    dir_name = os.path.basename(localdir)
    remotedir = f'{remotedir}/{dir_name}'
    if not exist_remote(remotedir, sftp_client):
        sftp_client.mkdir(remotedir)
    for i in os.listdir(localdir):
        upload_file_or_dir(sftp_client, f'{localdir}/{i}', remotedir)


def upload_file(sftp_client: paramiko.SFTPClient, localfile: str, remotedir: str):
    if os.path.isdir(localfile):
        return
    sftp_client.put(localfile, f'{remotedir}/{os.path.basename(localfile)}')


def get_file_type(file_stat: paramiko.SFTPAttributes) -> FileType | None:
    file_mode = file_stat.st_mode >> 12  # type: ignore
    for name in FileType:
        if (file_mode ^ name.value) == 0:
            return name
    return


def get_remote_file_md5(file_path: str, ssh_client: paramiko.SSHClient) -> str:
    stdin, stdout, stderr = ssh_client.exec_command(f'md5sum {file_path}')
    res = stdout.read().decode()
    return res.split()[0]


def get_file_type_from_path(file_path: str, sftp_client: paramiko.SFTPClient) -> FileType | None:
    try:
        stat = sftp_client.stat(file_path)
        return get_file_type(stat)
    except:
        return None


def rfile_equal_lfile(remote_file_path: str, local_file_path: str, ssh_client: paramiko.SSHClient) -> bool:
    return get_file_md5(local_file_path) == get_remote_file_md5(remote_file_path, ssh_client)


def exist_remote(file_path: str, sftp_client: paramiko.SFTPClient) -> bool:
    try:
        sftp_client.stat(file_path)
    except FileNotFoundError:
        return False
    else:
        return True
