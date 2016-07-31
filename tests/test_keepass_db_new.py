import unittest
from os import path
from readkeepass import kdb
try:
    data_dir = path.join(path.dirname(path.abspath(__file__)), 'data')
except NameError:
    data_dir = path.join(os.getcwd(), 'data')

class Database:
    def test_load_entries(self):
        entries = kdb.load_entries(self.db, keyfile=self.keyfile,
                                   password=self.password)
        self.assertEqual(self.dict_entries, entries)

    def test_load(self):
        kpdb = kdb.load(self.db, keyfile=self.keyfile,
                        password=self.password)
        db_entries = kpdb[self.db]
        self.assertEqual([x.as_dict for x in db_entries], self.dict_entries)
        for d, kpentry in zip(self.dict_entries, db_entries):
            username, password = d['username'], d['password']
            nt_entry = kpentry.as_ntuple
            self.assertEqual(username, nt_entry.username)
            self.assertEqual(password, nt_entry.password)
            

class Test_KeePassX2_OnlyKey(unittest.TestCase, Database):
    """Database created with the keepassx2"""
    @classmethod
    def setUpClass(cls):
        cls.db = path.join(data_dir, 'keepassx_onlykey.kdbx')
        cls.keyfile = path.join(data_dir, 'keepassx_onlykey.key')
        cls.password = ''
        cls.dict_entries = [
            {'groupname': 'Root',
             'notes': 'Wir schaffen irgendwas!',
             'password': 'bahnhofsklatscher',
             'title': 'Zweites Deutsches Fernsehen',
             'url': 'zdf.de',
             'username': 'mamamerkel'},
            {'groupname': 'Root',
             'notes': 'Maaskantje',
             'password': 'SoEinFeuerballJunge',
             'title': 'npr.org',
             'url': 'https://www.youtube.com/watch?v=yrtUKe5Q82w',
             'username': 'müslifresser1796'},
        ]


class Test_KeePassX2_PWandKey(unittest.TestCase, Database):
    """Database created with the keepassx2"""
    @classmethod
    def setUpClass(cls):
        cls.db = path.join(data_dir, 'exampledatabase.kdbx')
        cls.keyfile = path.join(data_dir, 'exampledatabase.key')
        cls.password = 'pass'
        cls.dict_entries =[
            {'groupname': 'Root',
             'notes': 'this is for digital ocean',
             'password': 'meow',
             'title': 'digitalocean',
             'url': 'digitalocean.com',
             'username': 'doswag@gmail.com'},
            {'groupname': 'group one',
             'notes': '',
             'password': 'coolbeans',
             'title': 'entry in group one',
             'url': 'g1.com',
             'username': 'g1swag@gmail.com'},
            {'groupname': 'group one',
             'notes': 'wow great entry',
             'password': 'roger',
             'title': 'second entry in group one',
             'url': 'secondone.net',
             'username': 'seconding1@gmail.com'},
            {'groupname': 'group one two',
             'notes': '',
             'password': 'yolo',
             'title': 'group one two entry',
             'url': 'g12.com',
             'username': 'g12entry@gmail.com'},
            {'groupname': 'group two',
             'notes': '',
             'password': 'koolbeanz',
             'title': 'gtwo entry',
             'url': 'https://www.g2sweet.org',
             'username': 'g2entry@yahoo.com'},
            {'groupname': 'group two',
             'notes': '',
             'password': '',
             'title': 'An almost empty entry ;)',
             'url': '',
             'username': ''}
        ]


class Test_KeePassX2_PW(unittest.TestCase, Database):
    """Database created with the keepassx2"""
    @classmethod
    def setUpClass(cls):
        cls.db = path.join(data_dir, 'db2.kdbx')
        cls.keyfile = ''
        cls.password = 'testpass1234'
        cls.dict_entries = [
            {'groupname': 'Root',
             'notes': '',
             'password': 'andchill',
             'title': 'Netflix',
             'url': '',
             'username': 'netflix-user@example.com'},
            {'groupname': 'Root',
             'notes': 'Google is a big thing these days.',
             'password': 'asdf',
             'title': 'Google',
             'url': '',
             'username': 'googleuser@mydomain.net'}
        ]

class Test_KeePass_PWKey(unittest.TestCase, Database):
    """Database created with the original keepass from http://keepass.info/"""
    @classmethod
    def setUpClass(cls):
        cls.db = path.join(data_dir, 'NewDatabase.kdbx')
        cls.keyfile = path.join(data_dir, 'NewDatabase.key')
        cls.password = 'pass'
        cls.dict_entries = [
            {'groupname': 'NewDatabase',
             'notes': 'Notes',
             'password': 'Password',
             'title': 'Sample Entry',
             'url': 'http://keepass.info/',
             'username': 'User Name'},
            {'groupname': 'NewDatabase',
             'password': '12345',
             'title': 'Sample Entry #2',
             'url': 'http://keepass.info/help/kb/testform.html',
             'username': 'Michael321'}
        ]


if __name__ == '__main__':
    try:
        print('Running tests for {}'.format(__file__))
    except NameError:
        pass
    unittest.main()



