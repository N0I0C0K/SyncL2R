import paramiko
import pathlib
import os

ssh_key = pathlib.Path(os.path.abspath("~/.ssh/id_rsa"))

ssh_client = paramiko.SSHClient()

with ssh_key.open() as f:
    pkey = paramiko.RSAKey.from_private_key(f)

ssh_client.load_system_host_keys()
ssh_client.connect("*", username="root", pkey=pkey)
stdin, stdout, stderr = ssh_client.exec_command("ls -l")

print(stdout.read().decode())
ssh_client.close()
