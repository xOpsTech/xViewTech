import time
import socket

hostname = socket.gethostname()


def get_timestamp():
    return int(time.time() * 1000)


def get_hostname():
    return hostname
