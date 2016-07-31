"""
kdb contains code to load and manipulate KeePass databases.

Most users should just call kdb.load()
"""
import io
from collections import namedtuple as _namedtuple, UserDict as _UserDict
from collections import OrderedDict as _OrderedDict
from itertools import chain as _chain, count as _count

import readkeepass.utils as _utils
from . import libkeepass
_logger = _utils.get_logger(__name__)


def _ntuple_from_dict(d, NamedTuple):
    """Return instance of NamedTuple based on dict d.

    NamedTuple is filled using the key/value pairs
    found in the dictionary d.
    """
    return NamedTuple(
        **{k: v for k, v in d.items() if k in NamedTuple._fields}
    )


def load_entries(db, keyfile='', password=''):
    "Return the entries in the keepass-db as an iterable of dicts"
    def load_kdb(db, password, keyfile):
        "Return the loaded kdb"
        # kdb = libkeepass.open(db, password='pass')
        credentials = {}
        if keyfile:
            credentials['keyfile'] = keyfile
        if password:
            credentials['password'] = password
        with io.open(db, 'rb') as stream:
            signature = libkeepass.common.read_signature(stream)
            cls = libkeepass.get_kdb_reader(signature)
            kdb = cls(stream, **credentials)
            kdb.close()
        return kdb

    def entry_to_dict(entry):
        strs = entry.findall('String')
        d = {str(s.Key).lower(): str(s.Value) for s in strs}
        try:
            d['groupname'] = str(entry.getparent().Name)
        except AttributeError:  # If there is no group it is deleted or something
            return None
        return d
    msg = 'Loading {} [given keyfile = {}, given password = {}]'
    _logger.debug(msg.format(db, bool(keyfile), bool(password)))
    kdb = load_kdb(db, password, keyfile)
    entries = kdb.obj_root.findall('.//Entry')
    entries2 = []
    for e in entries:
        d = entry_to_dict(e)
        if d:
            entries2.append(d)
    msg = 'Successfully loaded {}: found {} entries'
    _logger.debug(msg.format(db, len(entries2)))
    return entries2


class StringElements:
    "Formatter class for a KeePass entry dictionary."
    maxlen_longest = 40
    maxlen_normal = 30

    def __init__(self, d_entry):
        """\
        Format key,value pairs in d_entry using the method StringElements.key(value).

        You only need to define methods for those keys you want to transform.
        If no method is defined for a key, the transformation is just the identity fn.

        Usage example:
            d = {
                'title' : 'digitalocean',
                'notes' : 'this is for digital ocean',
                'password' : 'meow',
                'url': 'digitalocean.com',
                'username' : 'doswag@gmail.com',
                'groupname' : 'Root',
            }
            se = StringElements(d)
            dformatted = se.format()
        """
        self.d_formatted = {}
        self.d_entry = d_entry

    def format(self):
        d_formatted = {}
        for k, v in self.d_entry.items():
            try:
                if v:
                    d_formatted[k] = getattr(self, k)(str(v))
                else:
                    d_formatted[k] = ''
            except AttributeError:
                d_formatted[k] = str(v)
        self.d_formatted = d_formatted
        return d_formatted

    def title(self, x):
        x = x.capitalize()
        return '• ' + self.truncate_str(x, self.maxlen_longest)

    def url(self, x):
        # See here for stripping http:// and similar
        # http://stackoverflow.com/a/14625862
        x = self.truncate_str(x, self.maxlen_longest)
        x = '({})'.format(x)
        return x

    def groupname(self, x):
        x = self.truncate_str(x, self.maxlen_normal)
        x = '[{}]'.format(x)
        return x

    def username(self, x):
        x = self.truncate_str(x, self.maxlen_longest)
        x = '✉ ' + x
        return x

    def notes(self, x):
        x = self.truncate_str(x, self.maxlen_normal)
        x = ' »' + x + '«'
        return x

    @staticmethod
    def truncate_str(s, maxlen=None, append='...'):
        if maxlen is None:
            return s
        if len(s) <= maxlen:
            return s
        lapp = len(append)
        return s[:maxlen - lapp] + append

    def __str__(self):
        return str(self.d_formatted)

    def __repr__(self):
        return repr(self.d_formatted)

EntryFields = _namedtuple(
    'EntryFields',
    ['title', 'url', 'username', 'password', 'groupname'],
)


class KeePassEntry:
    NamedTuple = EntryFields
    dict_formatter = lambda entry_dict: StringElements(entry_dict).format()

    def __init__(self, entry_dict, NamedTuple=None):
        self.as_dict = entry_dict
        if NamedTuple:
            self.NamedTuple = NamedTuple

    def get_as_ntuple(self, NamedTuple=None):
        if NamedTuple:
            return _ntuple_from_dict(self.as_dict, NamedTuple)
        return _ntuple_from_dict(self.as_dict, self.NamedTuple)

    @property
    def as_ntuple(self):
        return self.get_as_ntuple()

    @property
    def as_string(self):
        return self.__str__()

    @property
    def as_formatted_dict(self):
        return __class__.dict_formatter(self.as_dict)

    def __str__(self):
        fields = []
        for k, v in self.as_formatted_dict.items():
            if k != 'password':
                fields.append('{} -> {}'.format(k, v))
        return '\n'.join(fields)

    def __repr__(self):
        name = str(self.__class__.__name__)
        return name + '(' + repr(self.as_dict) + ')'


class KeePassDB(_OrderedDict):
    def __init__(self, *pargs, db_path='', entries=None):
        super().__init__(*pargs)
        if db_path:
            entries = entries if entries is not None else []
            new_tup_tup = ((db_path, entries),)
            self.update(new_tup_tup)
            return
        if entries is None:
            return
        # Make following key a string
        # since all of the other keys will be strings
        key = next(x for x in map(str, _count()) if x not in self)
        self[key] = entries

    @property
    def paths(self):
        return list(self.keys())

    @property
    def entries(self):
        return list(_chain(*self.values()))


@_utils.root.register(name='load_db')
def load(db, keyfile='', password=''):
    """Extract the entries from the KeePass database corresponding to filename.

    It returns a named tuple with fields `filename`, and `entries`

    :param filename: the path of the KeePass database (db)
    :param password: the password for the db (if there is no pw use '')
    :param keyfile: the key-file for the db (if there is no key-file use '')
    :returns: a named tuple containing (db filename, db entries)
    :rtype: KeePassDB

    :Example:

    >>> db = readkeepass.kdb.load(filename='db2.kdbx', password='testpass1234')
    >>> db.filename
    'db2.kdbx'
    >>> db.entries[0]
    KeePassEntry({'url': '', 'notes': '', 'password': 'andchill', 'title': 'Netflix', 'groupname': 'Root', 'username': 'netflix-user@example.com'})
    """
    entries = load_entries(db, keyfile, password)
    return KeePassDB(db_path=db, entries=[KeePassEntry(x) for x in entries])
    # return _utils.KeePassDB(db, [KeePassEntry(x) for x in entries])
