from collections import OrderedDict
from readkeepass import rofi
import unittest


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


if __name__ == '__main__':
    try:
        print('Running tests for {}'.format(__file__))
    except NameError:
        pass
    unittest.main()
