"""Select entries from KeePass databases using rofi.
"""
import subprocess
from readkeepass import rkp
from keepass_menu import parser

DEBUG = False

if DEBUG:
    import logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

def notify_send(message):
    "Send desktop notification using 'notify-send'"
    subprocess.run(['notify-send', message])

def notify_selected(entry):
    "Send desktop notification about the selected entry."
    fields = [entry.title, entry.url, entry.username]
    fields = [x for x in fields if x]
    notify_send('Selected:' + ' -- '.join(fields))

def get_creds(args, *kp_credentials):
    "Return a list of credentials for all of the dbs in kp_credentials."
    grab = rkp.GrabCredentials(
        pw_query=args.pw_query,
        use_keyring=args.key_ring,
        del_keyring=args.key_ring_delete,
    )
    return [grab(*db) for db in kp_credentials]


def main(test_args=None):
    "Run keepass-menu"
    output_methods = rkp.output.node_leaves
    success, args = parser.get_args(
        output=output_methods,
        pw_query=rkp.userinput.node_leaves,
        test_args=test_args,    # test_args is used for testing the arg parser
    )
    if not success:
        return False

    credentials = get_creds(args, *args.db_paths)
    keepass_databases = [rkp.load_db(*cred) for cred in credentials]

    selected_key, selected_entry = rkp.rofi(*keepass_databases)
    notify_selected(selected_entry)

    try:
        username, password = selected_entry.username, selected_entry.password
    except AttributeError:
        print('No entry was selected. Quitting')
        return False
    output_methods[args.output](username=username, password=password)
    return True


if __name__ == '__main__':
    main()
