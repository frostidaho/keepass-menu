#!/usr/bin/env python
"""Open KeePass database with rofi.

Select an entry using rofi,
and then paste password with primary selection
and username with clipboard selection.
"""
import argparse
import re
from collections import OrderedDict

import readkeepass as rk
from tabulate import tabulate


def build_rofi_input(filename, password='', keyfile=''):
    """Create a dictionary from a keepass database file.

    The keys are display strings for each entry in the keepass database 
    The values are a namedtuple containing all of an entry's info.
    """
    def tabulate_list(entries, entry_layout):
        to_format = []
        for e in entries:
            d = e.as_formatted_dict
            for row in entry_layout:
                vals = [d.get(key, ' ') for key in row]
                vals = [x if x else ' ' for x in vals]
                to_format.append(tuple(vals))
        return to_format

    entries = rk.load(filename, password, keyfile)
    entry_layout = (('title', 'url'), ('username', 'groupname'), ('notes', None))

    to_format = tabulate_list(entries, entry_layout)
    table_str = tabulate(to_format, tablefmt='plain')

    table = re.findall(len(entry_layout) * r'.*\n', table_str)
    return OrderedDict(zip(table, [x.as_ntuple for x in entries]))

def launch_rofi(kdb_path, password='', keyfile=''):
    d = build_rofi_input(kdb_path, password, keyfile)
    key, res = rk.rofi.run(d)
    return key, res

def parse_args(default_output='autotype', default_input='xquery'):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '-f', '--filename',
        type = str,
        required = True,
        help = 'The keepass database file',
    )
    parser.add_argument(
        '-k', '--keyfile',
        type = str,
        help = 'The keyfile corresponding to the keepass database'
    )
    parser.add_argument(
        '-o', '--output',
        type = str,
        choices = ('copy', 'autotype', 'stdout'),
        default = default_output,
        help = ('Output username & password with this method.'
                "\nDefaults to '{}'".format(default_output))
    )
    parser.add_argument(
        '-pw', '--pw-query',
        type = str,
        choices = ('xquery', 'stdin', 'pyautogui'),
        default = default_input,
        help = ('Output username & password with this method.'
                "\nDefaults to '{}'".format(default_input))
    )

    return parser.parse_args()

def pw_query(db_path, query_fn_name):
    "Query for a password"
    db_name = db_path.split('/')[-1]
    fn = getattr(rk.userinput, query_fn_name)
    pw = fn(db_name)
    if pw:
        return pw
    raise ValueError('No password given!')

def main():
    args = parse_args()
    
    try:
        pw = pw_query(args.filename, args.pw_query)
    except ValueError as e:
        print(e)
        return

    try:
        key, res = launch_rofi(args.filename, pw, args.keyfile)
        msg = 'Selected: {} ({}) - {}'.format(res.title, res.url, res.username)
        print(msg)
        rk.xoutput.notify_send(msg)
    except AttributeError:
        print('Rofi did not return a key.')
        return

    try:
        getattr(rk.xoutput, args.output)(res.username, res.password)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
