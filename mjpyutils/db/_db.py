import _connections
from _connections import (
    oracledb_Connection,
    polars_arrow_ODBCCursorProxy,
    pyodbc_Connection,
    arrow_odbc_Connection,
)

from typing import (
    Literal as _lit,
    overload as _overload,
)

@_overload
def oracle(
    dsn: str,
    *,
    username: str | None = None,
    password: str | None = None,
    tnsnames: str | None = None,
    odbc_driver: _lit[False],
) -> oracledb_Connection: ...

@_overload
def oracle(
    dsn: str,
    *,
    username: str | None = None,
    password: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: _lit['arrow-odbc (polars proxy)'] = 'arrow-odbc (polars proxy)',
) -> polars_arrow_ODBCCursorProxy: ...

@_overload
def oracle(
    dsn: str,
    *,
    username: str | None = None,
    password: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: _lit['pyodbc'],
) -> pyodbc_Connection: ...

@_overload
def oracle(
    dsn: str,
    *,
    username: str | None = None,
    password: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: _lit['arrow-odbc'],
) -> arrow_odbc_Connection: ...


def oracle(
    dsn: str,
    *,
    username: str | None = None,
    password: str | None = None,
    tnsnames: str | None = None,
    odbc_driver: str | _lit[False] | None = None,
    odbc_lib: _lit['pyodbc', 'arrow-odbc (polars proxy)', 'arrow-odbc'] = 'arrow-odbc (polars proxy)',
) -> oracledb_Connection | polars_arrow_ODBCCursorProxy | pyodbc_Connection | arrow_odbc_Connection:
    '''Returns connection to Oracle Database.

    Function tries to assume that ``dsn`` is name of DSN defined in ODBC manager;
    if it does not find such connection then assumes that it is name of connection in tnsnames.ora.

    :param dsn: Name of tnsnames connection or data source
    :param username: Username used on database server
        - defaults to ``db.def_Ora_username``
    :param password: Password used on database server
        - defaults to return of calling ``db.def_Ora_getpassword``
    :param tnsnames: Location of tnsnames.ora (path to folder containing it);
        might be ignored when ``odbc_driver= False`` or thick client is initialized
        - defaults to ``db.def_Ora_tnsnames``
    :param odbc_driver: Name of driver used for odbc connection;
        if ``False``, then ``oracledb`` library is used instead of odbc
        - defaults to ``db.def_Ora_odbc_driver``
    :param odbc_lib: What library to use as ODBC;
        - defaults to internal polars proxy for arrow-odbc, since it allows usage
        of connection in ``polars.read_database``, but allows choosing raw _arrow-odbc_,
        or _pyodbc_ for max compatibility with trade for performance
    :raises ValueError: When one of required configuration arguments is missing
        and there is no default setup
    :return: Connection to specified Oracle Database
    '''
    # we fork logic so that typechecker does not complain that overloads don't match arguments
    if odbc_driver == False:
        conn_fun, args, kwargs = _connections.oracle(
            dsn,
            username= username,
            password= password,
            tnsnames= tnsnames,
            odbc_driver= False,
        )

        return conn_fun(*args, **kwargs)
    else:
        conn_fun, args, kwargs = _connections.oracle(
            dsn,
            username= username,
            password= password,
            odbc_driver= odbc_driver,
            odbc_lib= odbc_lib,
        )

        return conn_fun(*args, **kwargs)

@_overload
def sqlserver(
    dsn: str,
    port: int | None = None,
    *,
    db: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: _lit['arrow-odbc (polars proxy)'] = 'arrow-odbc (polars proxy)',
) -> polars_arrow_ODBCCursorProxy: ...

@_overload
def sqlserver(
    dsn: str,
    port: int | None = None,
    *,
    db: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: _lit['pyodbc'],
) -> pyodbc_Connection: ...

@_overload
def sqlserver(
    dsn: str,
    port: int | None = None,
    *,
    db: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: _lit['arrow-odbc'],
) -> arrow_odbc_Connection: ...

def sqlserver(
    dsn: str,
    port: int | None = None,
    *,
    db: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: _lit['pyodbc', 'arrow-odbc (polars proxy)', 'arrow-odbc'] = 'arrow-odbc (polars proxy)',
) -> polars_arrow_ODBCCursorProxy | pyodbc_Connection | arrow_odbc_Connection: 
    '''Returns connection to SQL Server.

    Function tries to assume that ``dsn`` is name of DSN defined in ODBC manager;
    if it does not find such connection then assumes that it is name / address of server.

    :param dsn: Name of server or data source or address of server
    :param port: Port number of server; ignored when using ODBC DSN
        - defaults to ``db.def_MS_port``
    :param odbc_driver: Name of driver used for odbc connection
        - defaults to ``db.def_MS_odbc_driver``
    :param odbc_lib: What library to use as ODBC;
        - defaults to internal polars proxy for arrow-odbc, since it allows usage
        of connection in ``polars.read_database``, but allows choosing raw _arrow-odbc_,
        or _pyodbc_ for max compatibility with trade for performance
    :raises ValueError: When one of required configuration arguments is missing
        and there is no default setup
    :return: Connection to specified SQL Server
    '''
    conn_fun, args, kwargs = _connections.sqlserver(
        dsn, 
        port,
        odbc_driver= odbc_driver,
        odbc_lib= odbc_lib,
    )

    return conn_fun(*args, **kwargs)
