import unittest
import readkeepass.keyring as keyring

test_pw = 'testpassword1234'
test_collection = 'readkeepass_test'

def get_ring(database, keyfile=''):
    ring = keyring.KPKeyring(
        database,
        keyfile = keyfile,
        collection_name = test_collection,
    )
    ring.delete_item()
    return ring

class TestInitialKeyring(unittest.TestCase):
    def test_get(self):
        ring = get_ring('testinitial.kdbx', 'testinitial.key')
        cred = ring.get_credentials()
        self.assertIsNone(cred)
        ring.close()

    def test_set(self):
        ring = get_ring('testinitial.kdbx', 'testinitial.key')
        cred = ring.set_credentials(test_pw)
        self.assertIsNotNone(cred)
        self.assertIsInstance(cred, keyring.KPCredentials)
        self.assertEqual(test_pw, cred.password)
        self.assertEqual('testinitial.kdbx', cred.db)
        self.assertEqual('testinitial.key', cred.keyfile)
        cred = ring.get_credentials()
        self.assertIsNotNone(cred)
        self.assertIsInstance(cred, keyring.KPCredentials)
        self.assertEqual(test_pw, cred.password)
        self.assertEqual('testinitial.kdbx', cred.db)
        self.assertEqual('testinitial.key', cred.keyfile)
        ring.delete_item()
        cred = ring.get_credentials()
        self.assertIsNone(cred)
        ring.close()

try:
    print('Running tests for {}'.format(__file__))
except NameError:
    pass
unittest.main()

# ring.close()        
