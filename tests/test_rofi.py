import unittest
from collections import OrderedDict
from readkeepass import rofi, kdb
from os import path

try:
    data_dir = path.join(path.dirname(path.abspath(__file__)), 'data')
except NameError:
    data_dir = path.join(os.getcwd(), 'data')


class TestNLinesPerKey(unittest.TestCase):
    "Test if the correct # of lines per key are returned"
    @classmethod
    def setUpClass(cls):
        cls.prep_dict = staticmethod(rofi._prepare_stdin_dict)
        cls.entry_short = """\
        e0 line1
        e0 line2
        """
        cls.entry_long = """\
        e1 line1
        e1 line2
        e1 line3
        """
        cls.od_fromkeys = OrderedDict.fromkeys

    def test_small_first(self):
        d = self.od_fromkeys([self.entry_short, self.entry_long])
        dout, n_lines_per_key = self.prep_dict(d, -1)
        self.assertEqual(n_lines_per_key, 3)

    def test_large_first(self):
        d = self.od_fromkeys([self.entry_long, self.entry_short])
        dout, n_lines_per_key = self.prep_dict(d, -1)
        self.assertEqual(n_lines_per_key, 3)

    def test_explicit(self):
        d = self.od_fromkeys([self.entry_short, self.entry_long])
        dout, n_lines_per_key = self.prep_dict(d, 99)
        self.assertEqual(n_lines_per_key, 99)


class TestBuildRofiInput(unittest.TestCase):
    """Test build_rofi_input, which converts a kdb.KeePassDB

    to a dict format that the rofi.run function can use
    """
    @classmethod
    def setUpClass(cls):
        # cls.build_input = staticmethod(rofi.build_rofi_input)
        db = path.join(data_dir, 'exampledatabase.kdbx')
        keyfile = path.join(data_dir, 'exampledatabase.key')
        password = 'pass'
        cls.db = kdb.load(db, keyfile=keyfile, password=password)
        cls.n_entries = len(cls.db.entries)
        cls.result = rofi.build_rofi_input(cls.db)

    def test_n_entries(self):
        self.assertEqual(len(self.result.keys()), self.n_entries)

    def test_values(self):
        for entry, res in zip(self.db.entries, self.result.values()):
            self.assertEqual(entry.as_ntuple, res)
            pass

if __name__ == '__main__':
    try:
        print('Running tests for {}'.format(__file__))
    except NameError:
        pass
    unittest.main()
