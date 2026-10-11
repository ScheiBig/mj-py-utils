'''
``db`` module provides utilities for working with databases using universal-ish API.

Functions named with database name, return ``Connection`` objects of their respective libraries,
using provided configuration.

Most of configuration can fed using defaults, which will be used when their respective parameters
are left ``None``, using ``def_*`` variables.
'''
from ._connections import (
    def_Ora_username,
    def_Ora_getpassword,
    def_Ora_tnsnames,
    def_Ora_odbc_driver,
    def_MS_port,
    def_MS_odbc_driver,
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
from . import libname

__all__ = [
    'def_Ora_username',
    'def_Ora_getpassword',
    'def_Ora_tnsnames',
    'def_Ora_odbc_driver',
    'def_MS_port',
    'def_MS_odbc_driver',
    'oracle',
    'sqlserver',
    'libname',
    'data_sources',
    'odbc_drivers',
    'oracledb_Connection',
    'pyodbc_Connection',
    'polars_arrow_ODBCCursorProxy',
]
