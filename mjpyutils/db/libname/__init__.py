'''
`db.libname` module extends :mod:`db` with functionality akin to SAS libraries.

All functions in this module that mirror main module ones, instead or connections itself,
return :class:`db_library`, which holds configuration necessary to create new connections,
and creates new connections per `with`-block. This helps preventing problem, where stale
connections are auto-closed when other code is executed, by recreating connection per each query.
'''
from ._libname import (
    db_library,
    oracle,
    sqlserver,
)

__all__ = [
    'db_library',
    'oracle',
    'sqlserver',
]
