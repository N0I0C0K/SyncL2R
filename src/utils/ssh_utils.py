import paramiko


def get_file_md5(file_path: str, ssh_client: paramiko.SSHClient) -> str:
    stdin, stdout, stderr = ssh_client.exec_command(f'md5sum {file_path}')
    res = stdout.read().decode()
    return res.split()[0]
