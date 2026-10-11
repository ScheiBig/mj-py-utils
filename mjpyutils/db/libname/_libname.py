from .. import _connections
from .._connections import (
    oracledb_Connection,
    polars_arrow_ODBCCursorProxy,
    pyodbc_Connection,
    arrow_odbc_Connection,
)
from typing import (
    Callable as fun,
    Literal as lit,
    overload,
)
from types import TracebackType

class db_library[
    TConnection: oracledb_Connection | polars_arrow_ODBCCursorProxy | pyodbc_Connection | arrow_odbc_Connection,
    **TConnArgs = ...,
]:
    '''`db_library` is reentrant resource that works as connection provider to defined
    database connection. For simplicity, `db_library` supports only one connection at the time.

    When you enter `with` block using `db_library`, it will create (and return) new connection,
    which will be disposed after block exits.
    '''
    def __init__(self,
        conn_provider: fun[TConnArgs, TConnection],
        *args: TConnArgs.args,
        **kwargs: TConnArgs.kwargs,
    ) -> None:
        '''Creates new :class:`db_library`, by taking connection provider
        and arguments to pass to it when creating new connection.

        :param conn_provider: A function that returns connection
        :param args: Positional arguments to be passed into `conn_provider` at call
        :param kwargs: Keyword arguments to be passed into `conn_provider` at call
        '''
        self.__conn: TConnection | None = None
        self.__conn_provider: fun[TConnArgs, TConnection] = conn_provider
        self.__conn_args = args
        self.__conn_kwargs = kwargs

    @property
    def conn(self) -> TConnection:
        '''Returns current connection.

        Usage of this property is only valid inside `with` block using this :class:`db_library`.

        :raises ValueError: When property is used outside `with` block
        '''
        if self.__conn is None:
            raise ValueError('Library is not in use - no connection available')
        return self.__conn

    def __enter__(self) -> TConnection:
        '''Creates new connection.

        :raises ValueError: When this method is called again before :meth:`__exit__`
        :return: Created connection
        '''
        if self.__conn is not None:
            raise ValueError('Library is already in use - cannot connect again before exiting')
        self.__conn = self.__conn_provider(*self.__conn_args, **self.__conn_kwargs)
        if isinstance(self.__conn, (oracledb_Connection, pyodbc_Connection)):
            self.__conn.__enter__()
        return self.__conn

    def __exit__(self, 
        exc_type: type[Exception] | None, 
        exc: Exception | None, 
        tb: TracebackType | None,
    ):
        '''
        Disposes current connection, via its own `__exit__` / `__del__` if available,
        passing all arguments to it.

        :raises ValueError: When this method is called again before :meth:`__enter__`
        '''
        if self.__conn is None:
            raise ValueError('Library is not in use - no connection to exit')
        conn = self.__conn
        self.__conn = None
        if isinstance(conn, (oracledb_Connection, pyodbc_Connection)):
            conn.__exit__(exc_type, exc, tb)
        elif isinstance(conn, arrow_odbc_Connection):
            conn.__del__()



@overload
def oracle(
    dsn: str,
    *,
    username: str | None = None,
    password: str | None = None,
    tnsnames: str | None = None,
    odbc_driver: lit[False],
) -> db_library[oracledb_Connection]: ...

@overload
def oracle(
    dsn: str,
    *,
    username: str | None = None,
    password: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: lit['arrow-odbc (polars proxy)'] = 'arrow-odbc (polars proxy)',
) -> db_library[polars_arrow_ODBCCursorProxy]: ...

@overload
def oracle(
    dsn: str,
    *,
    username: str | None = None,
    password: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: lit['pyodbc'],
) -> db_library[pyodbc_Connection]: ...

@overload
def oracle(
    dsn: str,
    *,
    username: str | None = None,
    password: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: lit['arrow-odbc'],
) -> db_library[arrow_odbc_Connection]: ...


def oracle(
    dsn: str,
    *,
    username: str | None = None,
    password: str | None = None,
    tnsnames: str | None = None,
    odbc_driver: str | lit[False] | None = None,
    odbc_lib: lit['pyodbc', 'arrow-odbc (polars proxy)', 'arrow-odbc'] = 'arrow-odbc (polars proxy)',
) -> db_library[oracledb_Connection | polars_arrow_ODBCCursorProxy | pyodbc_Connection | arrow_odbc_Connection]:
    '''Returns library that connects to Oracle Database.

    Function tries to assume that `dsn` is name of DSN defined in ODBC manager;
    if it does not find such connection then assumes that it is name of connection in tnsnames.ora.

    :param dsn: Name of tnsnames connection or data source
    :param username: Username used on database server
        - defaults to :data:`db.def_Ora_username`
    :param password: Password used on database server
        - defaults to return of calling :data:`db.def_Ora_getpassword`
    :param tnsnames: Location of tnsnames.ora (path to folder containing it);
        might be ignored when `odbc_driver= False` or thick client is initialized
        - defaults to :data:`db.def_Ora_tnsnames`
    :param odbc_driver: Name of driver used for odbc connection;
        if `False`, then :mod:`oracledb` library is used instead of odbc
        - defaults to :data:`db.def_Ora_odbc_driver`
    :param odbc_lib: What library to use as ODBC;
        - defaults to internal polars arrow-odbc proxy (:class:`polars_arrow_ODBCCursorProxy`),
        since it allows usage of connection in :func:`polars.read_database`, but allows choosing raw _arrow-odbc_ (:class:`arrow_odbc_Connection`), or _pyodbc_ (:class:`pyodbc_Connection`)
        for max compatibility with trade for performance
    :raises ValueError: When one of required configuration arguments is missing
        and there is no default setup
    :return: :class:`db_library` that connects to specified Oracle Database
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

        return db_library(conn_fun, *args, **kwargs)
    else:
        conn_fun, args, kwargs = _connections.oracle(
            dsn,
            username= username,
            password= password,
            odbc_driver= odbc_driver,
            odbc_lib= odbc_lib,
        )

        return db_library(conn_fun, *args, **kwargs)

@overload
def sqlserver(
    dsn: str,
    port: int | None = None,
    *,
    db: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: lit['arrow-odbc (polars proxy)'] = 'arrow-odbc (polars proxy)',
) -> db_library[polars_arrow_ODBCCursorProxy]: ...

@overload
def sqlserver(
    dsn: str,
    port: int | None = None,
    *,
    db: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: lit['pyodbc'],
) -> db_library[pyodbc_Connection]: ...

@overload
def sqlserver(
    dsn: str,
    port: int | None = None,
    *,
    db: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: lit['arrow-odbc'],
) -> db_library[arrow_odbc_Connection]: ...

def sqlserver(
    dsn: str,
    port: int | None = None,
    *,
    db: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: lit['pyodbc', 'arrow-odbc (polars proxy)', 'arrow-odbc'] = 'arrow-odbc (polars proxy)',
) -> db_library[polars_arrow_ODBCCursorProxy | pyodbc_Connection | arrow_odbc_Connection]:
    '''Returns library that connects to SQL Server.

    Function tries to assume that `dsn` is name of DSN defined in ODBC manager;
    if it does not find such connection then assumes that it is name / address of server.

    :param dsn: Name of server or data source or address of server
    :param port: Port number of server; ignored when using ODBC DSN
        - defaults to :data:`db.def_MS_port`
    :param odbc_driver: Name of driver used for odbc connection
        - defaults to :data:`db.def_MS_odbc_driver`
    :param odbc_lib: What library to use as ODBC;
        - defaults to internal polars arrow-odbc proxy (:class:`polars_arrow_ODBCCursorProxy`),
        since it allows usage of connection in :func:`polars.read_database`, but allows choosing raw _arrow-odbc_ (:class:`arrow_odbc_Connection`), or _pyodbc_ (:class:`pyodbc_Connection`)
        for max compatibility with trade for performance
    :raises ValueError: When one of required configuration arguments is missing
        and there is no default setup
    :return: :class:`db_library` that connects to specified SQL Server
    '''
    conn_fun, args, kwargs = _connections.sqlserver(
        dsn,
        port,
        odbc_driver= odbc_driver,
        odbc_lib= odbc_lib,
    )

    return db_library(conn_fun, *args, **kwargs)
