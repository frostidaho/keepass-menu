import subprocess as sp
from collections import OrderedDict

def _get_rofi_cmd(n_lines_per_key, entry_sep):
    if n_lines_per_key > 1:
        cmd = ('rofi', '-dmenu', '-i', '-eh', str(n_lines_per_key),
               '-sep', entry_sep)
    else:
        cmd = ('rofi', '-dmenu', '-i')
    return cmd

def run(stdin_dict, n_lines_per_key=-1, entry_sep='+'):
    """Launch rofi and return its output.

    run() concatenates the keys of stdin_dict and sends it to rofi's stdin.
    rofi returns one of the keys.
    Finally, the corresponding value (stdin_dict[key]) is returned.

    Each key in stdin_dict is expected to be a string, and they should
    all have the same number of newlines.

    n_lines_per_key can be set explicitly. It is the number of expected
    newlines in each key.

    entry_sep is the separator that will be used by rofi.
    Choose something that will not likely appear in any of the keys.
    #TODO Replace any instance of entry_sep in keys with some other character.
    """
    stdin_dict = OrderedDict((k.rstrip(),v) for k,v in stdin_dict.items())
    if n_lines_per_key == -1:
        n_lines_per_key = next(iter(stdin_dict)).count('\n') + 1

    cmd = _get_rofi_cmd(n_lines_per_key, entry_sep)
    if n_lines_per_key == 1:
        entry_sep = ''
        # no additional separator if each entry is only one line

    def _run_process(cmd, stdin_dict, entry_sep):
        entries = ('\n' + entry_sep).join(stdin_dict)
        entries = entries.encode()
        p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE)
        stdout, stderr = p.communicate(entries)
        p.terminate()
        return stdout.decode().rstrip()

    key = _run_process(cmd, stdin_dict, entry_sep)
    return key, stdin_dict.get(key)

