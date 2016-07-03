#!/usr/bin/env python
"""Open KeePass database with rofi.

Select an entry using rofi,
and then paste password with primary selection
and username with clipboard selection.
"""
import argparse
import re
from collections import OrderedDict
# import getpass
# import sys

import readkeepass as rk
from tabulate import tabulate

# def get_password():
#     if sys.stdin.isatty():
#         p = getpass.getpass('Using getpass: ')
#     else:
#         print('Using readline')
#         p = sys.stdin.readline().rstrip()
#     return p

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

def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--filename', type=str, required=True)
    parser.add_argument('--keyfile', type=str)
    return parser.parse_args()

def main():
    args = parse_args()
    db_name = args.filename.split('/')[-1]
    pw = rk.xquery.run(prompt='Password for {}:'.format(db_name),
                       button='OK', password=True)
    if not pw:
        print('No password given!')
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
        rk.xoutput.autotype(res.username, res.password)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
