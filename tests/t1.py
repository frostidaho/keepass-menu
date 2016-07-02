import unittest
import os
from os import path

import readkeepass as rkp
kdb = rkp.kdb

try:
    data_dir = path.join(path.dirname(path.abspath(__file__)), 'data')
except NameError:
    data_dir = path.join(os.getcwd(), 'data')
ex_db = path.join(data_dir, 'exampledatabase.kdbx')
ex_key = path.join(data_dir, 'exampledatabase.key')
ex_password = 'pass'

ex_credentials = {
    'filename' : ex_db,
    'password' : ex_password,
    'keyfile' : ex_key,
}

entries = rkp.load(**ex_credentials)
dentries = list(kdb.load_entries(**ex_credentials))

dentry_0 = {
    'groupname': 'Root',
    'notes': 'this is for digital ocean',
    'password': 'meow',
    'title': 'digitalocean',
    'url': 'digitalocean.com',
    'username': 'doswag@gmail.com',
}

entry_0 = rkp.KPEntry(dentry_0)

dformatted_0 = {
    'groupname': '[Root]',
    'notes': ' »this is for digital ocean«',
    'password': 'meow',
    'title': '• Digitalocean',
    'url': '(digitalocean.com)',
    'username': '✉ doswag@gmail.com'
}

class TestKPEntry(unittest.TestCase):
    def test_ntuple(self):
        d_orig = entry_0.as_dict
        as_nt = entry_0.as_ntuple
        d_nt = as_nt._asdict()
        for k in d_nt:
            self.assertEqual(d_nt[k], d_orig[k])

    def test_dict(self):
        self.assertEqual(dentry_0, entry_0.as_dict)

    def test_dict_formatted(self):
        df = entries[0].as_formatted_dict
        for k in df:
            self.assertEqual(df[k], dformatted_0[k])

class TestLoading(unittest.TestCase):
    def test_db_loader(self):
        d0 = dentries[0]
        self.assertEqual(d0, dentry_0)

    def test_main_loader(self):
        self.assertEqual(entries[0].as_dict, dentry_0)
        
try:
    print('Running tests for {}'.format(__file__))
except NameError:
    pass
unittest.main()

