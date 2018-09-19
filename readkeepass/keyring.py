import json as _json
from hashlib import md5 as _md5
from collections import namedtuple as _namedtuple

import secretstorage  # https://pythonhosted.org/SecretStorage/
import readkeepass.utils as _utils


_logger = _utils.get_logger(__name__)
_DEFAULT_COLLECTION = 'keepass-menu'

KeyringItem = _namedtuple('KeyringItem', ('label', 'secret', 'raw'))
KPCredentials = _utils.KPCredentials


def _text_to_md5_digest(text):
    "Compute the md5sum of text and return it as a string"
    htext = _md5(text.encode())
    return htext.hexdigest()


def _unlock(collection):
    "Unlock the secretstorage collection object"
    if collection.is_locked():
        collection.unlock()


class Secret:

    @staticmethod
    def create(**kwargs):
        return _json.dumps(kwargs, sort_keys=True)

    @staticmethod
    def parse(secret):
        return _json.loads(secret)


class Keyring:

    def __init__(self, collection_name):
        self.bus = secretstorage.dbus_init()
        self.coll = self._get_or_make_coll(self.bus, collection_name)
        self.collection_name = collection_name

    def __enter__(self):
        return self

    def __exit__(self, exc_ty, exc_val, tb):
        self.close()
        self.bus = None
        self.coll = None

    def get_secret(self, item_label):
        item = self.get_item(item_label)
        try:
            return Secret.parse(item.secret)
        except AttributeError:
            return item

    def set_secret(self, item_label, **kwargs):
        item = self._make_item(
            label=item_label,
            collection=self.coll,
            **kwargs,
        )
        return Secret.parse(item.secret)

    def close(self):
        try:
            self.bus.close()
        except AttributeError:
            pass

    def delete_keyring(self):
        self.coll.delete()

    @staticmethod
    def _get_or_make_coll(bus, label):
        """Get the secretstorage collection named label

        If it does not exist, it will be created.
        In that case the user will be prompted to enter
        a password for the new collection.
        """
        def get_collection(bus, label):
            "Return the secretstorage collection called label"
            colls = list(secretstorage.get_all_collections(bus))
            for c in colls:
                clabel = c.get_label()
                if clabel == label:
                    return c

        coll = get_collection(bus, label)
        if coll:
            _logger.debug('Collection {} exists'.format(label))
            return coll
        _logger.debug('Creating collection {}'.format(label))
        return secretstorage.create_collection(bus, label)

    @staticmethod
    def _make_item(label, collection, **kwargs):
        "Serialize kwargs and write them to the item label in collection"
        def _set():
            # Careful about changing the attrib dict.
            # It needs to be unique for replace=True to work
            # You really only want one key, otherwise you'll end up with
            # duplicates based on the other keys.
            attrib = {
                'readkeepass:db': str(label),
                'readkeepass:keyring_version': '0.1',
            }
            item = collection.create_item(
                label,
                attrib,
                Secret.create(**kwargs),
                replace=True,
            )
            msg = 'Creating item {} in collection {}'
            _logger.debug(msg.format(label, collection.get_label()))
            return KeyringItem(
                label=item.get_label(),
                secret=item.get_secret().decode(),
                raw=item,
            )
        try:
            return _set()
        except secretstorage.LockedException:
            _unlock(collection)
        return _set()


    def get_items(self):
        "Return all of the items in the secretstorage collection as a list of tuples"
        def _get():
            itemsgen = self.coll.get_all_items()
            pack_tuple = lambda item: KeyringItem(
                label=item.get_label(),
                secret=item.get_secret().decode(),
                raw=item,
            )
            return [pack_tuple(item) for item in itemsgen]
        try:
            return _get()
        except secretstorage.LockedException:
            _unlock(self.coll)
        return _get()

    def get_item(self, item_label):
        items = self.get_items()
        items = [x for x in items if x.label == item_label]
        li = len(items)
        msg = 'Found {} in collection {}'
        if li == 1:
            _logger.debug(msg.format(item_label, self.coll.get_label()))
            return items[0]
        elif li == 0:
            msg = 'Did not find {} in collection {}'
            _logger.debug(msg.format(item_label, self.coll.get_label()))
            return None
        else:
            msg = 'Found multiple keyring items with label: {}'
            _logger.warning(msg.format(item_label))
            return items[0]

    def delete_item(self, item_label):
        item = self.get_item(item_label)
        try:
            item.raw.delete()
            return True
        except AttributeError:
            return False



class KPKeyring(Keyring):
    # TODO Simplify or remove KPKeyring

    def __init__(self, db, keyfile='', collection_name=_DEFAULT_COLLECTION):
        self.db = db
        self.keyfile = keyfile
        super().__init__(collection_name)

    def get_secret(self):
        msg = 'Retrieving secret from keyring "{}" for {}'
        _logger.debug(msg.format(self.collection_name, self.db))
        try:
            secret = super().get_secret(self.label)
            cred = KPCredentials(**secret)
            _logger.debug('Received secret for {}'.format(self.db))
            return cred
        except (AttributeError, TypeError):
            _logger.debug('No secret found for {}'.format(self.db))
            return None

    def set_secret(self, password, keyfile=None):
        msg = 'Setting secret for {} in keyring "{}"'
        _logger.debug(msg.format(self.db, self.collection_name))
        if keyfile is None:
            keyfile = self.keyfile

        secret = super().set_secret(
            self.label,
            db=self.db,
            keyfile=keyfile,
            password=password
        )
        return KPCredentials(**secret)

    def delete_item(self):
        return super().delete_item(self.label)

    @property
    def label(self):
        return _text_to_md5_digest(self.db)

@_utils.root.register(name='KeyRing')
class Credentials:
    def __init__(self, db_path, collection_name=_DEFAULT_COLLECTION):
        self.db_path = db_path
        self.collection_name = collection_name

    def _keyring(self):
        return KPKeyring(db=self.db_path, collection_name=self.collection_name)
        
    def get(self):
        with self._keyring() as ring:
            return ring.get_secret()

    def set(self, password='', keyfile=''):
        with self._keyring() as ring:
            return ring.set_secret(password=password, keyfile=keyfile)

    def delete(self):
        with self._keyring() as ring:
            return ring.delete_item()
