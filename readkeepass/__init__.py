from . import kdb
from . import xquery

load = kdb.load
KPEntry = kdb.KPEntry

__all__ = ['load', 'KPEntry', 'kdb', 'xquery']

