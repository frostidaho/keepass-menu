import argparse as _argparse
from collections import namedtuple as _namedtuple
from pathlib import Path as _Path
from readkeepass import utils as _utils
from operator import attrgetter as _attrgetter


def build(output, pw_query):
    "Build parser"
    output = list(output)
    pw_query = list(pw_query)
    db_name = 'KEEPASS_DB'
    parser = _argparse.ArgumentParser(
        description=__doc__,
        allow_abbrev=False,
    )

    filegrp = parser.add_argument_group(
        title='database files',
        description="""\
        Specify the Keepass database and optional key-file paths.
        Multiple keepass databases can be given.""",
    )
    filegrp.add_argument(
        '-f', '--filename',
        type = str,
        help = 'The keepass database file',
        action = 'append',
        dest = 'filename',
        nargs = 1,
        metavar = db_name
    )
    filegrp.add_argument(
        '-f+k', '--filename+keyfile',
        type = str,
        help = 'The keypass databasefile followed by its corresponding keyfile',
        nargs = 2,
        action = 'append',
        metavar = (db_name, 'KEYFILE'),
        dest = 'filename',
    )

    parser.add_argument(
        '-o', '--output',
        type = str,
        choices = output,
        default = output[0],
        help = """Output selected username & password with this backend.
        The default output method is {}, and all of the choices are {}.
        """.format(output[0], output),
    )

    parser.add_argument(
        '-pw', '--pw-query',
        type = str,
        choices = pw_query,
        default = pw_query[0],
        help = """Query the password using this backend.
        By default query uses {}, while the total choices are {}.
        """.format(pw_query[0], pw_query),
    )

    keyring_grp = parser.add_argument_group(
        title='keyring options',
        description="""Optionally use the desktop's keyring to store and retrieve
        passwords for the KeePass databases.
        """,
    )
    keyring_grp.add_argument(
        '-kr', '--key-ring',
        help="Use keyring for password retrieval if possible, and store it if it does not exist.",
        action="store_true",
    )
    keyring_grp.add_argument(
        '-kd', '--key-ring-delete',
        help="Remove keyring entry for all of the databases given.",
        action="store_true",
    )
    return parser


_ParsedArgs = _namedtuple('_ParsedArgs', 'success args')
def transform_args(args):
    """Transform args object into a namedtuple with keys (success, args_dict)"""
    if args.filename is None:
        return _ParsedArgs(success=False, args=None)

    def pathify(fnames):
        "Try to turn each name into an absolute path as a string"
        for fname in fnames:
            try:
                yield str(_Path(fname).resolve()) if fname else fname
            except FileNotFoundError: # FIXME Maybe I should just let this come up?
                # If this isn't caught testing becomes more difficult
                yield fname

    make_credentials = _utils.KPCredentials._make
    # Turn filenames into tuples of (db, keyfile, password)
    fnames = []
    for x in args.filename:
        if len(x) == 2:
            fnames.append(x + [''])
        else:
            fnames.append(x + ['', ''])
    fnames = [make_credentials(pathify(x)) for x in fnames]
    args.db_paths = fnames
    return _ParsedArgs(success=True, args=args)

def get_args (output, pw_query, *pargs, test_args=None):
    parser = build(
        output=output,
        pw_query=pw_query,
    )
    args = parser.parse_args(test_args)
    success, args = transform_args(args)
    if not success:
        print('Must give at least one database file path!')
        parser.print_help()
    return _ParsedArgs(success=success, args=args)
