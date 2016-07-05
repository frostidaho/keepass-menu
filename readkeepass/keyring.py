# import warnings
import hashlib
from collections import namedtuple

import secretstorage # https://pythonhosted.org/SecretStorage/
import readkeepass.utils
_logsensitive = readkeepass.utils.SensitiveLoggerD(__name__)
_logger = readkeepass.utils.get_logger(__name__)

KeyringItem = namedtuple('KeyringItem', ('label', 'secret', 'raw'))
KPCredentials = namedtuple('KPCredentials', ('db', 'keyfile', 'password'))

def text_to_md5_digest(text):
    htext = hashlib.md5(text.encode())
    return htext.hexdigest()

def create_secret(db, keyfile, password):
    s = 'db == {} :::: keyfile == {} :::: password == {}'
    return s.format(db, keyfile, password)

def parse_secret(secret):
    fields = secret.split(' :::: ')
    fields = [x.split(' == ') for x in fields]
    return KPCredentials(**dict(fields))

def get_collection(bus, label):
    colls = list(secretstorage.get_all_collections(bus))
    for c in colls:
        clabel = c.get_label()
        if clabel == label:
            return c

def get_items(collection):
    def _get():
        itemsgen = collection.get_all_items()
        items = []
        for i in itemsgen:
            items.append(KeyringItem(i.get_label(), i.get_secret().decode(), i))
        return items
    try:
        return _get()
    except secretstorage.LockedException:
        unlock(collection)
        return _get()

def make_item(label, db, keyfile, password, collection):
    def _set():
        attrib = {
            'keypass:db' : 'True',
            'keypass:keyfile' : 'True' if keyfile else 'False',
            # 'xdg:schema': 'org.gnome.keyring.Note', # Seahorse crashes without this?
        }
        # secret2 = 'db == {} :::: keyfile == {} :::: password == {}'.format(db, keyfile, secret)
        secret2 = create_secret(db, keyfile, password)
        i = collection.create_item(label, attrib, secret2, replace=True)
        msg = 'Creating item {} in collection {}'
        _logger.debug(msg.format(label, collection.get_label()))
        return KeyringItem(i.get_label(), i.get_secret().decode(), i)
    try:
        return _set()
    except secretstorage.LockedException:
        unlock(collection)
        return _set()
    return _set()

def unlock(collection):
    if collection.is_locked():
        collection.unlock()

def get_or_make_collection(bus, label):
    coll = get_collection(bus, label)
    if coll:
        _logger.debug('Collection {} exists'.format(label))
        return coll
    _logger.debug('Creating collection {}'.format(label))
    return secretstorage.create_collection(bus, label)

def get_item(label, collection):
    items = get_items(collection)
    items = [x for x in items if x.label == label]
    li = len(items)
    msg = 'Found {} in collection {}'
    if li == 1:
        _logger.debug(msg.format(label, collection.get_label()))
        return items[0]
    elif li == 0:
        msg = 'Did not find {} in collection {}'
        _logger.debug(msg.format(label, collection.get_label()))
        return None
    else:
        msg = 'Found multiple keyring items with label: {}'
        _logger.warning(msg.format(label))
        return items[0]

class Keyring:
    def __init__(self, collection_name):
        self.bus = secretstorage.dbus_init()
        self.coll = get_or_make_collection(self.bus, collection_name)

    def close(self):
        self.bus.close()

    def delete_keyring(self):
        self.coll.delete()
        
class KPKeyring(Keyring):
    def __init__(self, db, keyfile=''):
        self.db = db
        self.keyfile = keyfile
        super().__init__('keepass-menu')

    def _get_item_tuple(self):
        return get_item(self.label, self.coll)

    @_logsensitive
    def get_credentials(self):
        item = self._get_item_tuple()
        try:
            # sec = parse_secret(item.secret)
            # logger.info('Successfully retrieved credentials for {}'.format(self.db))
            # return sec
            return parse_secret(item.secret)
        except AttributeError:
            return None

    @_logsensitive
    def set_credentials(self, password):
        # label = self.label
        # logger.info('Saving credentials for {} to keyring {}'.format(self.db, label))
        # item = make_item(label, self.db, self.keyfile, password, self.coll)
        item = make_item(self.label, self.db, self.keyfile, password, self.coll)
        return parse_secret(item.secret)

    def delete_item(self):
        ituple = self._get_item_tuple()
        try:
            ituple.raw.delete()
            return True
        except AttributeError:
            return False

    @property
    def label(self):
        return text_to_md5_digest(self.db)

