import subprocess as _subprocess
from . import copy as _copy
from . import autotype as _autotype

copy = _copy.run
autotype = _autotype.run

def notify_send(message):
    _subprocess.run(['notify-send', message])

