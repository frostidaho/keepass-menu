#!/usr/bin/env python
# import sys
import argparse
# import getpass
import subprocess as sp

import readkeepass as rk
from collections import OrderedDict

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
    entries = rk.load(filename, password, keyfile)
    key_vals = ((x.as_string, x.as_ntuple) for x in entries)
    return OrderedDict(key_vals)

def run_rofi(somedict, n_lines_per_entry=1, entry_sep='+'):
    if n_lines_per_entry > 1:
        cmd = ('rofi', '-dmenu', '-eh', str(n_lines_per_entry),
               '-sep', entry_sep)
    else:
        cmd = ('rofi', '-dmenu')
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
    key, res = run_rofi(d, n_lines_per_entry=2)
    # print('\n', key)
    # print(40*'-')
    # print(res)
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
    # ./keepass_rofi.py --filename ~/htmp/rofi_keepass/tests/data/exampledatabase.kdbx --keyfile ~/htmp/rofi_keepass/tests/data/exampledatabase.key 

