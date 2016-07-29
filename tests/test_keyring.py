import unittest
import readkeepass.keyring as keyring
import readkeepass as rk
from functools import partial


class TestKPKeyring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_pw = 'testpassword1234'
        test_collection = 'readkeepass_test'

        @staticmethod
        def get_ring(database, keyfile=''):
            ring = keyring.KPKeyring(
                database,
                keyfile = keyfile,
                collection_name = test_collection,
            )
            ring.delete_item()
            return ring
        cls.get_ring = get_ring

    def test_get(self):
        ring = self.get_ring('testinitial.kdbx', 'testinitial.key')
        cred = ring.get_secret()
        self.assertIsNone(cred)
        ring.close()

    def test_set(self):
        ring = self.get_ring('testinitial.kdbx', 'testinitial.key')
        cred = ring.set_secret(self.test_pw)
        self.assertIsNotNone(cred)
        self.assertIsInstance(cred, keyring.KPCredentials)
        self.assertEqual(self.test_pw, cred.password)
        self.assertEqual('testinitial.kdbx', cred.db)
        self.assertEqual('testinitial.key', cred.keyfile)
        cred = ring.get_secret()
        self.assertIsNotNone(cred)
        self.assertIsInstance(cred, keyring.KPCredentials)
        self.assertEqual(self.test_pw, cred.password)
        self.assertEqual('testinitial.kdbx', cred.db)
        self.assertEqual('testinitial.key', cred.keyfile)
        ring.delete_item()
        cred = ring.get_secret()
        self.assertIsNone(cred)
        ring.close()


class TestCredentials(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.collection = 'readkeepass_test'
        cls.Credentials = partial(rk.keyring.Credentials,
                                  collection_name=cls.collection)
        cls.db = '/test/keyring2/example_db.kdbx'
        
        cred = cls.Credentials(cls.db)
        cls.cred = cred

    @classmethod
    def tearDownClass(cls):
        cls.cred.delete()

    def test_get_none(self):
        cred = self.Credentials('asdl;kfjadfl3zz33z,n3z')
        self.assertIsNone(cred.get())

    def test_get(self):
        c = self.cred
        set_creds = c.set(password = 'expw')
        self.assertEqual(set_creds, (self.db, '', 'expw'))

        get_creds = c.get()
        self.assertEqual(set_creds, get_creds)

    def test_set(self):
        c = self.cred
        set_creds = c.set()
        self.assertEqual(set_creds, (self.db, '', ''))

        set_creds = c.set(password='expw')
        self.assertEqual(set_creds, (self.db, '', 'expw'))

        set_creds = c.set(keyfile='/some/keyfile', password='expw')
        self.assertEqual(set_creds, (self.db, '/some/keyfile', 'expw'))

    def test_del(self):
        c = self.cred
        self.assertEqual(c.set(), (self.db, '', ''))
        self.assertEqual(c.get(), (self.db, '', ''))
        
        self.assertEqual(c.delete(), True) # True since deleted item
        self.assertIsNone(c.get())
        self.assertEqual(c.delete(), False) # False since no item to delete
        self.assertIsNone(c.get())

        self.assertEqual(c.set(), (self.db, '', ''))
        self.assertEqual(c.get(), (self.db, '', ''))


if __name__ == '__main__':
    try:
        print('Running tests for {}'.format(__file__))
    except NameError:
        pass
    unittest.main()

