import sys as _sys
from getpass import getpass as _getpass
from . import xquery as _xquery

def stdin(db_name='', *pargs, **kwargs):
    "Return password from terminal or stdin"
    if _sys.stdin.isatty():
        p = _getpass('Enter password for {}: '.format(db_name))
    else:
        p = _sys.stdin.readline().rstrip()
    return p

def xquery(db_name='', *pargs, **kwargs):
    "Return password from a popup TK window (xquery)"
    prompt='Enter password for {}:'.format(db_name)
    button='OK'
    password=True
    return _xquery.run(prompt, button, password)

def pyautogui(db_name='', *pargs, **kwargs):
    import pyautogui
    prompt='Enter password for {}:'.format(db_name)
    return pyautogui.password(text=prompt, title='keepass-menu', mask='•')



