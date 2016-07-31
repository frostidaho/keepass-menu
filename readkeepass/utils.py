import logging
from inspect import signature as _signature
from functools import wraps as _wraps, partial as _partial
from collections import OrderedDict as _OrderedDict
from collections import namedtuple as _namedtuple

KPCredentials = _namedtuple('KPCredentials', ('db', 'keyfile', 'password'))


def _preserve_sig(fn):
    """Preserve the signature of the wrapped fn.

    This is used for writing decorator functions.
    """
    def wrapper(new_fn):
        new_fn = _wraps(fn)(new_fn)
        new_fn.__signature__ = _signature(fn)
        return new_fn
    return wrapper


def get_logger(name):
    logger = logging.getLogger(name)
    logger.addHandler(logging.NullHandler())
    return logger


class LoggerD:
    "A logger decorator factory"

    def __init__(self, name, msg_level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.addHandler(logging.NullHandler())

        self.msg_level = msg_level

    def __call__(self, fn):
        logger = self.logger.getChild(fn.__name__)

        @_preserve_sig(fn)
        def log(*pargs, **kwargs):
            res = fn(*pargs, **kwargs)
            logger.log(self.msg_level, str(res))
            return res
        return log


class SensitiveLoggerD(LoggerD):
    "A logger decorator factory for sensitive information"

    def __call__(self, fn):
        logger = self.logger.getChild(fn.__qualname__)

        @_preserve_sig(fn)
        def sensitive_log(*pargs, **kwargs):
            res = fn(*pargs, **kwargs)
            msg = []
            msg.append('type(result) -> {}'.format(type(res)))
            msg.append('bool(result) -> {}'.format(bool(res)))
            try:
                msg.append('len(result) -> {}'.format(len(res)))
            except TypeError:
                pass
            logger.log(self.msg_level, ' :: '.join(msg))
            return res
        return sensitive_log


class OrderedNamespace:
    "A namespace class where attributes are stored in an ordered dict"
    def __init__(self, name, key_value_pairs=None):
        """Create a namespace named name

        key_value_pairs is an optional iterable of pairs
        that will be used to populate the namespace.
        """
        self._odict = _OrderedDict()
        self._name = name
        if key_value_pairs is not None:
            for k, v in key_value_pairs:
                setattr(self, k, v)

    def __eq__(self, other):
        if not isinstance(other, OrderedNamespace):
            return NotImplemented
        return self._odict == other._odict

    def __contains__(self, key):
        return key in self.__dict__

    def __setattr__(self, name, value):
        if not name.startswith('_'):
            self.__dict__['_odict'][name] = value
        super().__setattr__(name, value)

    def __iter__(self):
        return iter(self._odict.items())
            
    def _repr_inner(self):
        torep = []
        for k, v in self:
            if isinstance(v, OrderedNamespace):
                torep.append(''.join(v._repr_inner()))
            else:
                torep.append(k)
        inner = ', '.join(torep)
        cls = str(self.__class__.__name__)
        tot = [self._name, '.{', inner, '}']
        return tot

    def __repr__(self):
        cls = str(self.__class__.__name__)
        tot = [cls, ' :: ']
        tot.extend(self._repr_inner())
        return ''.join(tot)


class Node(OrderedNamespace):
    """Node is a namespace class for registering objects

    Use Node().register to register objects as leaves
    Example:
        root = Node('root')
        @root.register
        def somefunc(): pass
        root.register({'a':1, 'b':2}, name='somedict')

    Use Node().__call__ to add sub-nodes
    Example:
        root = Node('root')
        subnode = root('subnode')
    """
    def register(self, obj=None, *, name=None, overwrite=False):
        "register is a decorator that will add object to this instance"
        if obj is None:
            return _partial(self.register, name=name, overwrite=overwrite)
        if name is None:
            name = obj.__name__
        if (overwrite is False) and (name in self.__dict__):
            msg = "{} is already registered in {}"
            raise ValueError(msg.format(name, self))
        setattr(self, name, obj)
        return obj

    def __call__(self, name, overwrite=False):
        if (overwrite is False) and (name in self.__dict__):
            return getattr(self, name)
            # msg = "{} is already registered in {}"
            # raise ValueError(msg.format(name, self))
        else:
            obj = self.__class__(name)
            setattr(self, name, obj)
            return obj
    
    @property
    def node_children(self):
        def _child():
            for name, val in self:
                if isinstance(val, self.__class__):
                    yield val
        return list(_child())

    @property
    def node_leaves(self):
        # odict = _OrderedDict()
        def _leaves():
            for name, val in self:
                if not isinstance(val, self.__class__):
                    yield name, val
        return _OrderedDict(_leaves())


root = Node('root')
