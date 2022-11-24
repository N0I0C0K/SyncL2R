import os
import paramiko
import json


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
        pass


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
    with open('./l2r-config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
    ip = config['connect_config']['ip']
    port = config['connect_config']['port']
    username = config['connect_config']['username']
    pwd = config['connect_config']['password']
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(ip, port, username, pwd)
    return ssh_client


if __name__ == '__main__':
    assh_client = get_ssh_client()
    test_upload_file(assh_client)
    # for i in os.walk('./test_upload_dir'):
    #     print(i)
    # print(os.listdir('./test_upload_dir'))
