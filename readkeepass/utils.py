import logging
import subprocess as _subprocess
from inspect import signature as _signature
from functools import wraps as _wraps, partial as _partial
from collections import OrderedDict as _OrderedDict, UserDict as _UserDict
from collections import namedtuple as _namedtuple

KPCredentials = _namedtuple('KPCredentials', ('db', 'keyfile', 'password'))

def notify_send(message):
    "Send desktop notification using 'notify-send'"
    _subprocess.run(['notify-send', message])


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


class Registered:
    def register(self, obj=None, *, name=None, overwrite=False):
        "register is a decorator that will add object to this instance"
        reg = self.registry
        if obj is None:
            return _partial(self.register, name=name, overwrite=overwrite)
        if name is None:
            name = obj.__name__
        if (overwrite is False) and (name in reg):
            msg = "{} is already registered in {}"
            raise ValueError(msg.format(name, self))
        setattr(self, name, obj)
        reg[name] = obj
        return obj

    @property
    def registry(self):
        try:
            return self._registry
        except AttributeError:
            self._registry = _OrderedDict()
            return self._registry

    def __repr__(self):
        msg = '(reg = {})'.format(list(self.registry.keys()))
        return self.__class__.__name__ + msg

    # @property
    # def registry_keys(self):
    #     return list(self._registry.keys())


class Node:
    def __init__(self, name, children=None):
        self.name = name
        d = _OrderedDict()
        if children is not None:
            for name in children:
                d[name] = self.__class__(name)
        self._children = d
        self._registry = _OrderedDict()

    def __call__(self, name, overwrite=False):
        """Create a new child"""
        if (overwrite is False) and (name in self._children):
            self._raise_val_err(name)
        obj = self.__class__(name)
        self._children[name] = obj
        return obj

    def __getattr__(self, val):
        try:
            return self._children[val]
        except:
            msg = "{} not found in {}._children"
            raise AttributeError(msg.format(val, self.name))

    def _raise_val_err(self, new_name):
        msg = "{} is already a child of {}"
        raise ValueError(msg.format(new_name, self.name))

    # @property
    # def children(self):
    #     childiter = self._flatten()
    #     next(childiter)
    #     return list(childiter)

    def _flatten(self):
        yield self
        for child in self._children.values():
            yield from child._flatten()

    def __iter__(self):
        return self._flatten()

    def __repr__(self):
        cls_name = self.__class__.__name__
        name = "'{}'".format(self.name)
        child_list = list(self._children)
        if child_list:
            children = ', children={}'.format(repr(list(self._children.values())))
        else:
            children = ''
        totl = [cls_name, '(', name, children, ')']
        return ''.join(totl)

    def __str__(self):
        return repr(self)


class Root(Node, Registered):
    def __init__(self, name, children=None):
        super().__init__(name, children=children)

    @property
    def all_registered(self):
        # TODO Fix for arbitrarily nested objects
        # Could have multiple nodes with same name
        d = _OrderedDict()
        for node in self:
            if node.name in d:
                msg = "Node with name {} seen multiple times"
                raise ValueError(msg.format(node.name))
            d[node.name] = node.registry
        return d


root = Root('root')

