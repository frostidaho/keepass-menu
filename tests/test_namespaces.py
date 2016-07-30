import unittest
from itertools import count
from string import ascii_lowercase

from readkeepass import utils

class TestNamespace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.Namespace = utils.OrderedNamespace
        cls.ex_kv_list = list(zip(ascii_lowercase, count(start=1)))

    def setUp(self):
        self.root = self.Namespace('root')

    def test_base(self):
        self.assertEqual(self.root._name, 'root')
        x = self.Namespace('xyz')
        self.assertEqual(self.root, x)

    def test_init(self):
        x = self.Namespace('abc', self.ex_kv_list)
        self.assertEqual(list(x), self.ex_kv_list)

    def test_setattr(self):
        for k, v in self.ex_kv_list:
            setattr(self.root, k, v)
        self.assertEqual(list(self.root), self.ex_kv_list)

    def test_contains(self):
        x = self.Namespace('x', self.ex_kv_list)
        for k, v in self.ex_kv_list:
            self.assertIn(k, x)


class TestNode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.Node = utils.Node
        cls.ex_kv_list = list(zip(ascii_lowercase, count(start=1)))

    def setUp(self):
        self.node = self.Node('node', self.ex_kv_list)
        self.node1 = self.Node('node1')
        self.node2 = self.Node('node2')
        self.node.node1 = self.node1
        self.node.node2 = self.node2

    @staticmethod
    def fn_ident(x):
        "Identity fn"
        return x

    @staticmethod
    def fn_ident2(x, y, z):
        "Identity fn for 3 args"
        return x, y, z

    def test_leaves(self):
        for k, v in self.ex_kv_list:
            self.assertIn(k, self.node.node_leaves)

    def test_leaves2(self):
        self.assertNotIn('node1', self.node.node_leaves)
        self.assertNotIn('node2', self.node.node_leaves)

    def test_leaves_register(self):
        self.node.register(self.fn_ident)
        self.assertIn('fn_ident', self.node.node_leaves)
        self.assertIs(self.fn_ident, self.node.fn_ident)

    def test_create_exist_child(self):
        self.assertIs(self.node1, self.node('node1'))

    def test_node_children(self):
        self.assertIs(self.node.node_children[0], self.node1)
        self.assertIs(self.node.node_children[1], self.node2)


# TODO Add tests for utils.Namespace and utils.Node
class TestRegistered(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.Rec = utils.Node

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
        return self.root.node_leaves

    @property
    def register(self):
        return self.root.register

    def setUp(self):
        self.root = self.Rec('root')

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
