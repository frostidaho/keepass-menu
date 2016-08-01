from readkeepass import utils
from readkeepass import kdb
from readkeepass import userinput
from readkeepass import rofi
from readkeepass import output
from readkeepass import keyring


rkp = utils.root

@rkp.register
class GrabCredentials:
    _userinput = rkp.userinput.node_leaves
    _default_inp = next(iter(_userinput))
    _keyring = rkp.KeyRing

    def __init__(self, pw_query=_default_inp, use_keyring=True,
                 del_keyring=False, **kwargs):
        self.use_keyring = use_keyring
        self.del_keyring = del_keyring
        self.pw_query = pw_query

    def __call__(self, db, keyfile='', password=''):
        self.db = db
        self.keyfile = keyfile
        self.password = password
        if self.del_keyring:
            self.delete()
        self.get_cred()
        return self.credentials

    @property
    def pw_query(self):
        return self._pw_query

    @pw_query.setter
    def pw_query(self, val):
        if val in self._userinput:
            self._pw_query = val
        else:
            msg = "{} is not in {}".format(val, backends)
            raise ValueError(msg)

    @property
    def credentials(self):
        return utils.KPCredentials(self.db, self.keyfile, self.password)

    def delete(self):
        self._keyring(self.db).delete()

    def get_cred(self):
        if self.use_keyring:
            cred = self._keyring(self.db).get()
            if cred:
                self.password = cred.password
                self.keyfile = cred.keyfile
                return True
        prompt = self.db.rsplit('/', maxsplit=1)[-1]
        self.password = self._userinput[self.pw_query](prompt)
        if self.use_keyring:
            self._keyring(self.db).set(password=self.password, keyfile=self.keyfile)
        return True


__all__ = ['rkp', 'GrabCredentials']
