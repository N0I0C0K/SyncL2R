import os
import time
import paramiko
import json
import typing
import functools
import utils


def clock(func: typing.Callable):
    @functools.wraps(func)
    def dec(*args, **kwargs):
        s_t = time.time()
        res = func(*args, **kwargs)
        s_e = time.time()
        print(f'{func.__name__} end=> {s_e-s_t}')
        return res
    return dec


def test_connect(ssh_client: paramiko.SSHClient):
    stdin, stdout, stderr = ssh_client.exec_command('ls -al')
    print(stdout.read().decode())
    ssh_client.close()


def exec_command(ssh_client: paramiko.SSHClient, command):
    res = ssh_client.exec_command(command)
    print(res[1].read().decode())


def upload_file_or_dir(sftp_client: paramiko.SFTPClient, localfile: str, remotefile: str):
    if os.path.isdir(localfile):
        upload_dir(sftp_client, localfile, remotefile)
        return
    else:
        upload_file(sftp_client, localfile, remotefile)


def upload_dir(sftp_client: paramiko.SFTPClient, localdir: str, remotedir: str):
    if not os.path.isdir(localdir):
        return
    dir_name = os.path.basename(localdir)
    remotedir = f'{remotedir}/{dir_name}'
    sftp_client.mkdir(remotedir)

    for i in os.listdir(localdir):
        upload_file_or_dir(sftp_client, f'{localdir}/{i}', remotedir)


def upload_file(sftp_client: paramiko.SFTPClient, localfile: str, remotedir: str):
    if os.path.isdir(localfile):
        return
    sftp_client.put(localfile, f'{remotedir}/{os.path.basename(localfile)}')


def test_upload_file(ssh_client: paramiko.SSHClient):
    sftp_client = ssh_client.open_sftp()
    upload_file_or_dir(sftp_client, './test_upload_dir', '/home')


def get_ssh_client():
    with open('./l2r_config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
    ip = config['connect_config']['ip']
    port = config['connect_config']['port']
    username = config['connect_config']['username']
    pwd = config['connect_config']['password']
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(ip, port, username, pwd)
    return ssh_client


def get_type(file_mode):
    file_mode = file_mode >> 12
    if (file_mode ^ 8) == 0:
        return 1  # nomal file
    elif (file_mode ^ 4) == 0:
        return 2  # dir
    return 0


def test_command(ssh_client: paramiko.SSHClient):
    try:
        sftp = ssh_client.open_sftp()
        sftp.stat('/home/asasda/aaa.txt')
    except FileNotFoundError:
        print('文件不存在')
    #atts = sftp.listdir_attr('/home')
    #print('\n'.join(map(lambda x: str(x.longname), atts)))


if __name__ == '__main__':
    assh_client = get_ssh_client()
    print(utils.ssh_utils.get_file_md5('/home/a.txt', assh_client))
    assh_client.close()
    # for i in os.walk('./test_upload_dir'):
    #     print(i)
    # print(os.listdir('./test_upload_dir'))
