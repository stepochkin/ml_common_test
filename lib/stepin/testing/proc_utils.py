# coding=utf-8

from datetime import datetime
from time import sleep


def wait_process(p, timeout):
    if timeout is None:
        until = None
    else:
        until = datetime.now() + timeout
    while p.poll() is None:
        if until is not None and datetime.now() > until:
            return p.poll()
        sleep(0.1)
    return p.returncode
