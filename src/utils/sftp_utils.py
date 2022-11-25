import enum
import paramiko


class FileType(enum.IntFlag):
    DIR = 4
    NORMAL_FILE = 8


def get_file_type(file_stat: paramiko.SFTPAttributes) -> FileType:
    file_mode = file_stat.st_mode >> 12
    for name in FileType:
        if (file_mode ^ name.value) == 0:
            return name
    return


def get_file_type_from_path(file_path: str, sftp_client: paramiko.SFTPClient) -> FileType | None:
    try:
        stat = sftp_client.stat(file_path)
        return get_file_type(stat)
    except:
        return None


def get_file_md5(file_path: str, ssh_client: paramiko.SSHClient) -> str:
    stdin, stdout, stderr = ssh_client.exec_command(f'md5sum {file_path}')
    res = stdout.read().decode()
    return res.split()[0]


def exist(file_path: str, sftp_client: paramiko.SFTPClient) -> bool:
    try:
        sftp_client.stat(file_path)
    except FileNotFoundError:
        return False
    else:
        return True
