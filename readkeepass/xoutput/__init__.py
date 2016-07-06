import sys as _sys
from . import copy as _copy
from . import autotype as _autotype
_simulate = _autotype.simulate

copy = _copy.run

def autotype(username, password, *pargs, **kwargs):
    "Click on username and password, and then it autotypes."
    _autotype.type_at_clicks(username, password)
    _simulate.enter_key()

def autotype_tab(username, password, *pargs, **kwargs):
    "Click on username, and then it will autotype using tab to switch fields."
    tab = _simulate.tab_key
    enter = _simulate.enter_key
    _autotype.click_and_type(username, password, sep=tab, end=enter)

def stdout(username, password, *pargs, **kwargs):
    "Write username and password to stdout"
    lines = [
        '@username: {}\n'.format(username),
        '@password: {}\n'.format(password),
    ]
    for k,v in kwargs.items():
        lines.append('@{}: {}\n'.format(k, v))
    _sys.stdout.writelines(lines)

backends = ['stdout', 'copy', 'autotype', 'autotype_tab']
__all__ = backends
