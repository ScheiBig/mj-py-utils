'''
``db`` module provides utilities for working with databases using universal-ish API.

Functions named with database name, return ``Connection`` objects of their respective libraries,
using provided configuration.

Most of configuration can fed using defaults, which will be used when their respective parameters
are left ``None``, using ``def_*`` variables.
'''
__all__ = [
    'def_Ora_username',
    'def_Ora_getpassword',
    'def_Ora_tnsnames',
    'def_Ora_odbc_driver',
    'def_MS_port',
    'def_MS_odbc_driver',
    'oracle',
    'sqlserver',
]

import oracledb as _oracledb
import pyodbc as _pyodbc
from typing import (
    Callable as _fun,
    Literal as _lit,
    overload as _overload
)
import os as _os

def_Ora_username: str | None = None
'''Default value used for ``oracle(username=)``'''
def_Ora_getpassword: _fun[[], str] | None = None
'''Function returning default value for ``oracle(password=)``'''
def_Ora_tnsnames: str | None = None
'''Default value for ``oracle(tnsnames=)``'''
def_Ora_odbc_driver: str | None = None
'''Default value for ``oracle(odbc_driver=)``'''
def_MS_port: int | None = 1433
'''Default value for ``sqlserver(port=)``, preset by library to common 1433 port'''
def_MS_odbc_driver: str | None = None
'''Default value for ``sqlserver(odbc_driver=)``'''


@_overload
def oracle(
    dsn: str, 
    *,
    username: str | None = None,
    password: str | None = None,
    tnsnames: str | None = None,
    odbc_driver: _lit[False],
) -> _oracledb.Connection: ...


@_overload
def oracle(
    dsn: str, 
    *,
    username: str | None = None,
    password: str | None = None,
    tnsnames: str | None = None,
    odbc_driver: str | None = None,
) -> _pyodbc.Connection: ...


def oracle(
    dsn: str, 
    *,
    username: str | None = None,
    password: str | None = None,
    tnsnames: str | None = None,
    odbc_driver: str | _lit[False] | None = None,
) -> _oracledb.Connection | _pyodbc.Connection:
    '''Returns connection to Oracle Database.

    Function tries to assume that ``dsn`` is name of DSN defined in ODBC manager;
    if it does not find such connection then assumes that it is name of connection in tnsnames.ora.

    :param dsn: Name of tnsnames connection or data source
    :param username: Username used on database server
        - defaults to ``db.def_Ora_username``
    :param password: Password used on database server
        - defaults to return of calling ``db.def_Ora_getpassword``
    :param tnsnames: Location of tnsnames.ora (path to folder containing it);
        might be ignored when ``odbc_driver= False``
        - defaults to ``db.def_Ora_tnsnames``
    :param odbc_driver: Name of driver used for odbc connection;
        if ``False``, then ``oracledb`` library is used instead of odbc
        - defaults to ``db.def_Ora_odbc_driver``
    :raises ValueError: When one of configuration arguments is missing
        and there is no default setup.
    :return: Connection to specified Oracle Database
    '''
    if username is None:
        if def_Ora_username is None:
            raise ValueError(
                'No username passed or default set via [db.def_Ora_username]'
            )
        username = def_Ora_username
    if password is None:
        if def_Ora_getpassword is None:
            raise ValueError(
                'No password passed or default provider set via [db.def_Ora_getpassword]'
            )
        password = def_Ora_getpassword()
    if tnsnames is None:
        if def_Ora_tnsnames is None and odbc_driver == False:
            raise ValueError(
                'No tnsnames passed or default set via [db.def_Ora_tnsnames]'
            )
        tnsnames = def_Ora_tnsnames
    if odbc_driver is None:
        if def_Ora_odbc_driver is None:
            raise ValueError(
                'No odbc_driver passed or default set via [db.def_Ora_odbc_driver]'
            )
        odbc_driver = def_Ora_odbc_driver

    if odbc_driver == False:
        return _oracledb.connect(
            dsn= dsn,
            user= username,
            password= password,
            config_dir= tnsnames,
        )

    if tnsnames is not None:
        _os.environ['TNS_ADMIN'] = tnsnames

    avail_dsn = [k.lower() for k in _pyodbc.dataSources().keys()]

    if dsn.lower() in avail_dsn:
        return _pyodbc.connect(
            f'DSN={dsn};'
            f'UID={username};'
            f'PWD={password};'
        )

    return _pyodbc.connect(
        f'DRIVER={{{odbc_driver}}};'
        f'DBQ={dsn};'
        f'UID={username};'
        f'PWD={password};'
    )


def sqlserver(
    dsn: str,
    port: int | None = None,
    *,
    db: str | None = None,
    odbc_driver: str | None = None,
) -> _pyodbc.Connection:
    '''Returns connection to SQL Server.

    Function tries to assume that ``dsn`` is name of DSN defined in ODBC manager; 
    if it does not find such connection then assumes that it is name / address of server.

    :param dsn: Name of server or data source or address of server
    :param port: Port number of server; ignored when using ODBC DSN
        - defaults to ``db.def_MS_port``
    :param odbc_driver: Name of driver used for odbc connection
        - defaults to ``db.def_MS_odbc_driver``
    :raises ValueError: When one of configuration arguments is missing 
        and there is no default setup.
    :return: Connection to specified SQL Server
    '''
    avail_dsn = [k.lower() for k in _pyodbc.dataSources().keys()]

    if dsn.lower() in avail_dsn:
        conn = f'DSN={dsn};'

        if db:
            conn += f'DATABASE={db};'

        conn += 'Trusted_Connection=yes;'

        return _pyodbc.connect(conn)

    if port is None:
        if def_MS_port is None:
            raise ValueError(
                'No port passed or default set via [db.def_MS_port]')
        port = def_MS_port
    conn = f'SERVER={dsn},{port};'

    if db:
        conn += f'DATABASE={db};'

    if odbc_driver is None:
        if def_MS_odbc_driver is None:
            raise ValueError(
                'No odbc_driver passed or default set via [db.def_MS_odbc_driver]')
        odbc_driver = def_MS_odbc_driver

    conn += f'DRIVER={{{odbc_driver}}};'

    conn += 'Trusted_Connection=yes;'

    return _pyodbc.connect(conn)
