import sys as _sys
from getpass import getpass as _getpass
from readkeepass import utils as _utils
from . import xquery as _xquery


userinput = _utils.root('userinput')

@userinput.register
def stdin(db_name='', *pargs, **kwargs):
    """Read password from stdin.

    If stdin is a tty a prompt will be displayed.
    It returns the entered password as a string.
    """
    if _sys.stdin.isatty():
        p = _getpass('Enter password for {}: '.format(db_name))
    else:
        p = _sys.stdin.readline().rstrip()
    return p


@userinput.register
def tk(db_name='', *pargs, **kwargs):
    """Query user for a password using a tk window.

    It returns the entered password as a string.
    """
    prompt = 'Enter password for {}:'.format(db_name)
    button = 'OK'
    password = True
    return _xquery.run(prompt, button, password)


@userinput.register
def pymsgbox(db_name='', *pargs, **kwargs):
    """Query user for a password using the graphical pymsgbox.

    It returns the entered password as a string.
    """
    import pyautogui
    prompt = 'Enter password for {}:'.format(db_name)
    return pyautogui.password(text=prompt, title='keepass-menu', mask='•')
