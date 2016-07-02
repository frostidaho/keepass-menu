import subprocess as sp

def run(somedict, n_lines_per_entry=1, entry_sep='+'):
    if n_lines_per_entry > 1:
        cmd = ('rofi', '-dmenu', '-i', '-eh', str(n_lines_per_entry),
               '-sep', entry_sep)
    else:
        cmd = ('rofi', '-dmenu', '-i')
        entry_sep = ''

    def _common(cmd, somedict, entry_sep):
        entries = ('\n' + entry_sep).join(somedict)
        entries = entries.encode()
        p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE)
        stdout, stderr = p.communicate(entries)
        p.terminate()
        p.kill()
        key = stdout.decode().rstrip()
        return key, somedict[key]
    return _common(cmd, somedict, entry_sep)
