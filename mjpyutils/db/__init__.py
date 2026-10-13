'''
`db` module provides utilities for working with databases using universal-ish API.

Functions named with database name, return `Connection` objects of their respective libraries,
using provided configuration.

Most of configuration can fed using defaults, which will be used when their respective parameters
are left `None`, using `def_*` variables.
'''
from ._connections import (
    defs,
    data_sources,
    odbc_drivers,
    oracledb_Connection,
    pyodbc_Connection,
    polars_arrow_ODBCCursorProxy,
)
from ._db import (
    oracle,
    sqlserver,
)
from ._libname import libname

__all__ = [
    'defs',
    'oracle',
    'sqlserver',
    'libname',
    'data_sources',
    'odbc_drivers',
    'oracledb_Connection',
    'pyodbc_Connection',
    'polars_arrow_ODBCCursorProxy',
]
