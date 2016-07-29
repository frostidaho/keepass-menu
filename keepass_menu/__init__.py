"""Select entries from KeePass databases using rofi.
"""
import readkeepass
from readkeepass import rkp, GrabCredentials

from keepass_menu import parser
from collections import OrderedDict, ChainMap
from tabulate import tabulate
import re

DEBUG = False

if DEBUG:
    import logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

def load_all(*kp_credentials):
    return [rkp.load_db(*cred) for cred in kp_credentials]

def get_creds(args, *kp_credentials):
    grab = GrabCredentials(
        pw_query = args.pw_query,
        use_keyring = args.key_ring,
        del_keyring = args.key_ring_delete,
    )
    return [grab(*db) for db in kp_credentials]


def main(list_args=None):
    backends = rkp.all_registered
    success, args = parser.get_args(
        output=backends['output'],
        pw_query=backends['userinput'],
        list_args=list_args,
    )
    if not success:
        return False
    
    credentials = get_creds(args, *args.db_paths)
    dbs = load_all(*credentials)
    # print(*dbs, sep='\n\n')
    key, res = rkp.rofi(*dbs)
    backends['output'][args.output](**res._asdict())
    return True


if __name__ == '__main__':
    main()

