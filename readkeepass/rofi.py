import subprocess as sp
import re
from collections import OrderedDict
from readkeepass import utils as _utils
from tabulate import tabulate

_logger = _utils.get_logger(__name__)

def _get_rofi_cmd(n_lines_per_key, entry_sep):
    if n_lines_per_key > 1:
        cmd = ('rofi', '-fullscreen', '-dmenu', '-i', '-eh', str(n_lines_per_key),
               '-sep', entry_sep)
    else:
        cmd = ('rofi', '-fullscreen', '-dmenu', '-i')
    return cmd


def _prepare_stdin_dict(stdin_dict, n_lines_per_key):
    stdin_dict = OrderedDict((k.strip(), v) for k, v in stdin_dict.items())
    if n_lines_per_key == -1:
        n_lines_per_key = max(key.count('\n') for key in stdin_dict) + 1
        msg = 'n_lines_per_key was not specified: found to be {}'
        _logger.debug(msg.format(n_lines_per_key))
    return stdin_dict, n_lines_per_key


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
    stdin_dict, n_lines_per_key = _prepare_stdin_dict(stdin_dict, n_lines_per_key)

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


def build_rofi_input(keepass_db):
    """Create a rofi-usable dict from a KeePassDB object.

    keepass_db is just a namedtuple with fields 'filename' and 'entries'

    The keys are display strings for each entry in the keepass database
    The values are a namedtuple containing all of an entry's info.
    """
    entry_sentinel = '@@!$#@@'
    def tabulate_list(entries, entry_layout):
        to_format = []
        for e in entries:
            d = e.as_formatted_dict
            for row in entry_layout:
                vals = [d.get(key, ' ') for key in row]
                vals = [x if x else ' ' for x in vals]
                to_format.append(tuple(vals))
            to_format.append([entry_sentinel] + [''] * (len(row)-1))
        return to_format

    entries = keepass_db.entries
    entry_layout = (('title', 'url'), ('username', 'groupname'), ('notes', None))

    to_format = tabulate_list(entries, entry_layout)
    table_str = tabulate(to_format, tablefmt='plain')
    
    table = table_str.split(entry_sentinel)
    table = [x.lstrip() for x in table]
    table = [x for x in table if x]
    return OrderedDict(zip(table, [x.as_ntuple for x in entries]))


@_utils.root.register(name='rofi')
def launch_rofi(*keepass_dbs):
    # TODO Docstrings & rename
    keepass_db = type(keepass_dbs[0])()
    for d in keepass_dbs:
        keepass_db.update(d)

    totald = build_rofi_input(keepass_db)
    return run(totald)
