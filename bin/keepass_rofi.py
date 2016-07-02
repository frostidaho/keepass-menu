#!/usr/bin/env python

import argparse
import subprocess as sp
import re
# import getpass
# import sys

import readkeepass as rk
from collections import OrderedDict
from tabulate import tabulate
# def get_password():
#     if sys.stdin.isatty():
#         p = getpass.getpass('Using getpass: ')
#     else:
#         print('Using readline')
#         p = sys.stdin.readline().rstrip()
#     return p

def load_keepass_db(filename, password='', keyfile=''):
    """Get the rofi display strings and their username/pw.

    load_keepass_db returns a dict where
                    keys   = rofi display strings
                    values = namedtuple with attributes 'username', 'password', and more
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

    table = [x.rstrip() for x in re.findall(len(entry_layout) * r'.*\n', table_str)]
    od = OrderedDict()
    for k,entry in zip(table, entries):
        od[k] = entry.as_ntuple
    return od

class copy:
    @staticmethod
    def _xsel(txt, selection='primary'):
        cmd = ['xsel', '--logfile', '/dev/null',
               '--{}'.format(selection), '--input']
        p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE)
        return p.communicate(txt.encode())

    @staticmethod
    def clipboard(txt):
        return copy._xsel(txt, 'clipboard')

    @staticmethod
    def primary(txt):
        return copy._xsel(txt, 'primary')

def rofi_db(kdb_path, password='', keyfile=''):
    d = load_keepass_db(kdb_path, password, keyfile)
    key, res = rk.rofi.run(d, n_lines_per_entry=3)
    copy.clipboard(res.username)
    copy.primary(res.password)
    return key, res

def parse_args():
    parser = argparse.ArgumentParser(description='Open KeePass database with rofi. Then select an entry, and paste password with primary selection and username with clipboard selection.')
    parser.add_argument('--filename', type=str, required=True)
    parser.add_argument('--keyfile', type=str)
    # TODO add & test option to read password from terminal
    # parser.add_argument(
    #     "--xpassword",
    #     help="ask for password with a graphical window",
    #     action="store_true",
    # )
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    db_name = args.filename.split('/')[-1]
    pw = rk.xquery.run(prompt='Password for {}:'.format(db_name),
                       button='OK', password=True)
    if pw:
        key, res = rofi_db(args.filename, pw, args.keyfile)
        sp.run(['notify-send', '{} has been copied!'.format(res.title, res.url)])
    else:
        print('No password given!')

