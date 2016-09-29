import sys as _sys
from subprocess import Popen as _Popen, PIPE as _PIPE
from readkeepass import utils as _utils
from . import autotype as _autotype
_simulate = _autotype.simulate


output = _utils.root('output')

@output.register
def menu_select(username, password, *pargs, **kwargs):
    "Select one of the other output methods"
    from readkeepass import rofi
    leaves = output.node_leaves.copy()
    leaves.pop('menu_select', None)
    res = rofi.run(leaves)[1]
    return res(username, password, *pargs, **kwargs)

@output.register
def copy(username, password, *pargs, **kwargs):
    """Copy username and password to the clipboards.

    usename is copied to the clipboard (Ctrl-v)
    password is copied to the primary selection (Middle mouse)

    Copying is performed using the xsel program.
    """
    def _xsel(txt, selection):
        cmd = ['xsel', '--logfile', '/dev/null',
               '--{}'.format(selection), '--input']
        p = _Popen(cmd, stdout=_PIPE, stderr=_PIPE, stdin=_PIPE)
        return p.communicate(txt.encode())

    _xsel(username, selection='clipboard')
    _xsel(password, selection='primary')


@output.register
def autotype(username, password, *pargs, **kwargs):
    "Click on username and password, and then it autotypes."
    _autotype.type_at_clicks(username, password)
    # _simulate.enter_key()


@output.register
def autotype_tab(username, password, *pargs, **kwargs):
    "Click on username, and then it will autotype using tab to switch fields."
    tab = _simulate.tab_key
    _autotype.click_and_type(username, password, sep=tab)


@output.register
def stdout(username, password, *pargs, **kwargs):
    "Write username and password to stdout"
    lines = [
        '@username: {}\n'.format(username),
        '@password: {}\n'.format(password),
    ]
    for k, v in kwargs.items():
        lines.append('@{}: {}\n'.format(k, v))
    _sys.stdout.writelines(lines)
