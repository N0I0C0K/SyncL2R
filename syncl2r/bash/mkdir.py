from paramiko import SSHClient


def mkdir(path: str, parents: bool = False, *, ssh_client: SSHClient):
    ssh_client.exec_command(f'mkdir {path}{" -p" if parents else ""}')
