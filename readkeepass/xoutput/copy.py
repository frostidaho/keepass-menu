from subprocess import Popen, PIPE

class _copy:
    @staticmethod
    def _xsel(txt, selection='primary'):
        cmd = ['xsel', '--logfile', '/dev/null',
               '--{}'.format(selection), '--input']
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        return p.communicate(txt.encode())

    @staticmethod
    def clipboard(txt):
        return _copy._xsel(txt, 'clipboard')

    @staticmethod
    def primary(txt):
        return _copy._xsel(txt, 'primary')

def run(username, password):
    """Copy username and password to the clipboards.

    usename is copied to the clipboard (Ctrl-v)
    password is copied to the primary selection (Middle mouse)
    """
    _copy.clipboard(username)
    _copy.primary(password)
