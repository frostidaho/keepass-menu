import readkeepass as rk
from collections import OrderedDict
import unittest

e0 = """\
e0 line1
e0 line2
"""

e1 = """\
e1 line1
e1 line2
e1 line3
"""

d = OrderedDict(((e0, 0), (e1, 1)))
dout, n_lines_per_key = rk.rofi._prepare_stdin_dict(d, -1)

class TestNLinesPerKey(unittest.TestCase):
    "Test if the correct # of lines per key are returned"
    def test_small_first(self):
        d = OrderedDict(((e0, 0), (e1, 1)))
        dout, n_lines_per_key = rk.rofi._prepare_stdin_dict(d, -1)
        self.assertEqual(n_lines_per_key, 3)

    def test_large_first(self):
        d = OrderedDict(((e1, 1), (e0, 0)))
        dout, n_lines_per_key = rk.rofi._prepare_stdin_dict(d, -1)
        self.assertEqual(n_lines_per_key, 3)

    def test_explicit(self):
        nlines = 99
        d = OrderedDict(((e1, 1), (e0, 0)))
        dout, n_lines_per_key = rk.rofi._prepare_stdin_dict(d, nlines)
        self.assertEqual(n_lines_per_key, nlines)


if __name__ == '__main__':
    try:
        print('Running tests for {}'.format(__file__))
    except NameError:
        pass
    unittest.main()
