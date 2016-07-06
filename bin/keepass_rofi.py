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

DEBUG = True

if DEBUG:
    import logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

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

    entries = rk.kdb.load(filename, password, keyfile)
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

    default_output = rk.xoutput.backends[0]
    parser.add_argument(
        '-o', '--output',
        type = str,
        choices = rk.xoutput.backends,
        default = default_output,
        help = ('Output username & password with this method.'
                "\nDefaults to '{}'".format(default_output))
    )

    default_input = rk.userinput.backends[0]
    parser.add_argument(
        '-pw', '--pw-query',
        type = str,
        choices = rk.userinput.backends,
        default = default_input,
        help = ('Output username & password with this method.'
                "\nDefaults to '{}'".format(default_input))
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-kr', '--key-ring',
        help="Use keyring for pw retrieval.",
        action="store_true",
    )
    group.add_argument(
        '-kd', '--key-ring-delete',
        help="Remove keyring entry for filename.",
        action="store_true",
    )
    parser.add_argument(
        '-ks', '--key-ring-set',
        help="Add keyring entry for filename.",
        action="store_true",
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

def credentials_from_keyring(ring, filename):
    cred = ring.get_credentials()
    try:
        return cred.password, cred.keyfile
    except AttributeError:
        print('Key for {} does not exist in keyring'.format(filename))
        return '', ''

def main():
    args = parse_args()
    keyfile = args.keyfile
    pw = ''

    if args.key_ring_delete or args.key_ring or args.key_ring_set:
        ring = rk.keyring.KPKeyring(args.filename, keyfile)
        ring_keyfile = ''
        ring_pw = ''
        
    if args.key_ring_delete:
        ring.delete_item()
    elif args.key_ring:         # Can not get key if deleted
        ring_pw, ring_keyfile = credentials_from_keyring(ring, args.filename)
        pw = ring_pw
        keyfile = keyfile if keyfile else ring_keyfile
        
    try:
        if not pw:
            pw = pw_query(args.filename, args.pw_query)
    except ValueError as e:
        print(e)
        return

    if args.key_ring_set:
        if (keyfile, pw) != (ring_keyfile, ring_pw):
            ring.keyfile = keyfile
            ring.set_credentials(pw)

    # if not keyfile:
    #     keyfile = args.keyfile
        
    try:
        key, res = launch_rofi(args.filename, pw, keyfile)
        msg = 'Selected: {} ({}) - {}'.format(res.title, res.url, res.username)
        print(msg)
        rk.utils.notify_send(msg)
    except AttributeError as e:
        print('Rofi did not return a key.')
        print(e)
        return

    try:
        getattr(rk.xoutput, args.output)(res.username, res.password)
    except EnvironmentError as e:
        print(e)

if __name__ == '__main__':
    main()
