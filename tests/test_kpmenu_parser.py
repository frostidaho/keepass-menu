import unittest
from functools import partial

from keepass_menu import parser


class TestBuildParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.output = ['output1', 'output2']
        cls.pw_query = ['input1', 'input2']
        cls.parser =  parser.build(
            output=cls.output,
            pw_query=cls.pw_query,
        )
        cls.parse_args = cls.parser.parse_args

    def test_default_backends(self):
        res = self.parse_args([])
        self.assertEqual(res.output, self.output[0])
        self.assertEqual(res.pw_query, self.pw_query[0])

    def test_other_backends(self):
        res = self.parse_args(['--output', 'output2', '--pw-query', 'input2'])
        self.assertEqual(res.output, self.output[1])
        self.assertEqual(res.pw_query, self.pw_query[1])
        
    def test_filename(self):
        res = self.parse_args(['-f', 'somefile'])
        self.assertEqual(len(res.filename[0]), 1)
        self.assertEqual(res.filename[0][0], 'somefile')

    def test_filename_multi(self):
        res = self.parse_args(['-f', 'file0', '-f+k', 'file1', 'keyfile1'])
        self.assertEqual(len(res.filename[0]), 1)
        self.assertEqual(res.filename[0][0], 'file0')
        self.assertEqual(len(res.filename[1]), 2)
        self.assertEqual(res.filename[1], ['file1', 'keyfile1'])


class TestTransfArgs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.output = ['output1', 'output2']
        cls.pw_query = ['input1', 'input2']
        cls.parser =  parser.build(
            output=cls.output,
            pw_query=cls.pw_query,
        )
        cls.parse_args = cls.parser.parse_args

        @classmethod
        def transform(cls, args_list):
            args = cls.parse_args(args_list)
            return parser.transform_args(args)
        
        cls.transform = transform

    def test_no_args(self):
        res = self.transform([])
        self.assertFalse(res.success)
        self.assertFalse(res[0])

    def test_one_file(self):
        res = self.transform(['-f', 'somefile'])
        self.assertTrue(res.success)
        self.assertEqual(res.args.filename[0][0], 'somefile')
        self.assertEqual(res.args.db_paths[0].db, 'somefile')
        self.assertEqual(res.args.db_paths[0].keyfile, '')

    def test_multi_files(self):
        files = [['file0'], ['file1', 'keyfile1'], ['file2']]
        files_args = ['-f', '-f+k', '-f']
        args_list = []
        for fargs, fname in zip(files_args, files):
            args_list.append(fargs)
            args_list.extend(fname)
            
        res = self.transform(args_list)
        self.assertTrue(res.success)
        for resfile, origfile in zip(res.args.filename, files):
            self.assertEqual(resfile, origfile)
        for resfile, origfile in zip(res.args.db_paths, files):
            self.assertEqual(resfile.db, origfile[0])
            try:
                self.assertEqual(resfile.keyfile, origfile[1])
            except IndexError:
                self.assertEqual(resfile.keyfile, '')


if __name__ == '__main__':
    try:
        print('Running tests for {}'.format(__file__))
    except NameError:
        pass
    unittest.main()
