import io
from collections import namedtuple
from collections import OrderedDict
from . import libkeepass

def _ntuple_from_dict(d, NamedTuple):
    """Return instance of NamedTuple based on dict d.

    NamedTuple is filled using the key/value pairs
    found in the dictionary d.
    """
    return NamedTuple(
        **{k:v for k,v in d.items() if k in NamedTuple._fields}
    )

def load_entries(filename, password='', keyfile=''):
    "Return the entries in the keepass-db as an iterable of dicts"
    def load_kdb(filename, password, keyfile):
        "Return the loaded kdb"
        # kdb = libkeepass.open(filename, password='pass')
        with io.open(filename, 'rb') as stream:
            signature = libkeepass.common.read_signature(stream)
            cls = libkeepass.get_kdb_reader(signature)
            kdb = cls(stream, password=password, keyfile=keyfile)
            kdb.close()
        return kdb

    def entry_to_dict(entry):
        strs = entry.findall('String')
        d = {str(s.Key).lower() : str(s.Value) for s in strs}
        try:
            d['groupname'] = str(entry.getparent().Name)
        except AttributeError:  # If there is no group it is deleted or something
            return None
        return d

    kdb = load_kdb(filename, password, keyfile)
    entries = kdb.obj_root.findall('.//Entry')
    entries2 = []
    for e in entries:
        d = entry_to_dict(e)
        if d:
            entries2.append(d)
    return entries2

def _pad_or_truncate(some_str, pad='<30', maxlen=-1):
    "Return the padded or truncated string s"
    def truncate_str(s, maxlen=None, append='...'):
        if maxlen is None:
            return s
        if len(s) <= maxlen:
            return s
        lapp = len(append)
        return s[:maxlen - lapp] + append
    
    if maxlen != -1:
        n = str(maxlen)
        frmt = '{:' + pad + '.' + n + '}'
        return frmt.format(truncate_str(some_str, maxlen))
    frmt = '{:' + pad + '}'
    return frmt.format(some_str)

EntryFields = namedtuple(
    'EntryFields',
    ['title', 'url', 'username', 'password', 'groupname'],
)

class KPEntry:
    format_fn_name = 'format_for_rofi'
    NamedTuple = EntryFields
    
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

    def format_for_rofi(self):
        # TODO Clean up the formatting mess here and in
        # _pad_or_truncate
        pot = _pad_or_truncate
        e = self.as_dict
        dformatted = {
            'title' : pot(e['title'].capitalize(), '', 50),
            'url' : '({})'.format(pot(e['url'], '', 50)) if e['url'] else '',
            'groupname' : '[{}]'.format(pot(e['groupname'], '', 50)) if e['groupname'] else '',
            'username' : '✉' + pot( e['username'], '', 50),
            # 'Notes' : pot(e['Notes'], '>45'),
        }

        n_cols_normal = 30        
        def reformat(key, ):
            frmt_str='{:<' + str(n_cols_normal) + '}'
            dformatted[key] = frmt_str.format(dformatted[key])
            
        reformat('url')
        reformat('title')
        reformat('username')
        reformat('groupname')

        line1 = ' '.join(('•', dformatted['title'], dformatted['url'],))
        line2 = ' '.join((' ', dformatted['username'], dformatted['groupname'],))
        line3 = '  ' + e['notes']
        return line1 + '\n' + line2 + '\n' + line3

    def format(self, fn=None):
        """Return the formatted string representation of the entry.

        By default the formatting function (fn) is self.format_fn_name.

        If fn is given it can be the name of another method in KPEntry,
        or a function which takes the entry's dictionary as its argument.
        """
        if fn:
            try:                    # Allow passing in a function
                return str(fn(self.as_dict))
            except TypeError:
                return str(getattr(self, fn)())
        return str(getattr(self, self.format_fn_name)())

    def __str__(self):
        return self.format()

    def __repr__(self):
        return 'KPEntry(' + repr(self.as_dict) + ')'

def load(filename, password='', keyfile=''):
    entries = load_entries(
        filename,
        password=password,
        keyfile=keyfile,
    )
    return [KPEntry(x) for x in entries]

