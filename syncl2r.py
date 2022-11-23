import paramiko
import json


def test():
    with open('./l2r-config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
    ip = config['connect_config']['ip']
    port = config['connect_config']['port']
    username = config['connect_config']['username']
    pwd = config['connect_config']['password']
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(ip, port, username, pwd)
    stdin, stdout, stderr = ssh_client.exec_command('ls -al')
    print(stdout.read().decode())
    ssh_client.close()


if __name__ == '__main__':
    test()
