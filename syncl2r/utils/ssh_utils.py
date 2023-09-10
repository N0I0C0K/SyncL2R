import paramiko


def channel_recv(channel: paramiko.Channel) -> bytes:
    read = bytearray()
    bath_size = 128
    while True:
        t = channel.recv(bath_size)
        read.extend(t)
        if len(t) < bath_size:
            break
    return read
