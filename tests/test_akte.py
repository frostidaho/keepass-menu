import unittest
from readkeepass import utils


class TestNode(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.Rec = utils.Node

    def setUp(self):
        self.root = self.Rec('root')

    def assertRecordIs(self, record0, record1):
        self.assertIs(record0, record1)
        self.assertIsInstance(record0, self.Rec)

    def assertChildrenAreAttr(self, record):
        # Make sure there is a correspondence between the
        # objects stored in self._children and self.__dict__
        for cname, child in record._children.items():
            child_as_attr = getattr(record, cname)
            self.assertRecordIs(child, child_as_attr)
        
    def test_add_sub(self):
        yolo = self.root('yolo')
        self.assertRecordIs(yolo, self.root.yolo)

    def test_add_multi(self):
        yolo = self.root('yolo')
        abc = self.root('abc')
        self.assertRecordIs(yolo, self.root.yolo)
        self.assertRecordIs(abc, self.root.abc)
        self.assertChildrenAreAttr(self.root)

    def test_assert_already_set(self):
        self.root('test')
        with self.assertRaises(ValueError):
            self.root('test')

    def test_overwrite(self):
        test0 = self.root('test')
        test1 = self.root('test', overwrite=True)
        self.assertIsNot(test0, test1)
        self.assertRecordIs(test1, self.root.test)
        self.assertChildrenAreAttr(self.root)


class TestRegistered(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.Rec = utils.Registered

    @staticmethod
    def fn_ident(x):
        "Identity fn"
        return x

    @staticmethod
    def fn_ident2(x, y, z):
        "Identity fn for 3 args"
        return x, y, z

    @property
    def registry(self):
        return self.root.registry

    @property
    def register(self):
        return self.root.register

    def setUp(self):
        self.root = self.Rec()

    def assertInRegistry(self, name):
        self.assertIn(name, self.registry)

    def test_reg(self):
        self.register(self.fn_ident)
        self.assertIs(self.fn_ident, self.root.fn_ident)
        self.assertInRegistry(self.fn_ident.__name__)

    def test_reg_setname(self):
        self.register(self.fn_ident, name='wow')
        self.assertIs(self.fn_ident, self.root.wow)
        self.assertInRegistry('wow')

    def test_override_err(self):
        self.register(self.fn_ident)
        with self.assertRaises(ValueError):
            self.register(self.fn_ident)

    def test_override(self):
        self.register(self.fn_ident)
        self.register(self.fn_ident2, name='fn_ident', overwrite=True)
        self.assertInRegistry('fn_ident')
        self.assertIs(self.root.fn_ident, self.fn_ident2)

    def test_decor(self):
        @self.register
        def testfn(*pargs, **kwargs):
            pass
        self.assertInRegistry('testfn')
        self.assertIs(testfn, self.root.testfn)

    def test_decor_named(self):
        @self.register(name='othername')
        def testfn(*pargs, **kwargs):
            pass
        self.assertInRegistry('othername')
        self.assertIs(testfn, self.root.othername)

if __name__ == '__main__':
    try:
        print('Running tests for {}'.format(__file__))
    except NameError:
        pass
    unittest.main()
