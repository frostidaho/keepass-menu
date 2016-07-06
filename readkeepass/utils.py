import logging
import subprocess as _subprocess
from inspect import signature as _signature
from functools import wraps as _wraps

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

