import sys as _sys
import subprocess as _subprocess

from . import copy as _copy
from . import autotype as _autotype

copy = _copy.run

def autotype(username, password, *pargs, **kwargs):
    return _autotype.run(username, password)

def stdout(username, password, *pargs, **kwargs):
    lines = [
        '@username: {}\n'.format(username),
        '@password: {}\n'.format(password),
    ]
    for k,v in kwargs.items():
        lines.append('@{}: {}\n'.format(k, v))
    _sys.stdout.writelines(lines)

def notify_send(message):
    _subprocess.run(['notify-send', message])

