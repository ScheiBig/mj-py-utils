from . import _connections
from ._connections import (
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
from wakepy import (
    keep,
    Mode,
    ModeExit,
)

class libname[
    TConnection: oracledb_Connection | polars_arrow_ODBCCursorProxy | pyodbc_Connection | arrow_odbc_Connection,
    **TConnArgs = ...,
]:
    '''`db.libname` is reentrant resource that works as connection provider to defined
    database connection. For simplicity, `db.libname` supports only one connection at the time.

    When you enter `with` block using `db.libname`, it will create (and return) new connection,
    which will be disposed after block exits.

    `db.libname` extends :mod:`db` with functionality akin to SAS libraries.

    All factory methods in this class that mirror main module ones, instead or connections itself,
    return :class:`db.libname`, which holds configuration necessary to create new connections,
    and creates new connections per `with`-block. This helps preventing problem, where stale
    connections are auto-closed when other code is executed, by recreating connection per each query.

    Additionally, :class:`db.libname` leverages :mod:`wakepy` to keep screen on, to prevent any
    corruption of connection due to sleep / screen saver / lower power mode.
    '''
    def __init__(self,
        conn_provider: fun[TConnArgs, TConnection],
        *args: TConnArgs.args,
        **kwargs: TConnArgs.kwargs,
    ) -> None:
        '''Creates new :class:`db.libname`, by taking connection provider
        and arguments to pass to it when creating new connection.

        :param conn_provider: A function that returns connection
        :param args: Positional arguments to be passed into `conn_provider` at call
        :param kwargs: Keyword arguments to be passed into `conn_provider` at call
        '''
        self.__conn: TConnection | None = None
        self.__conn_provider: fun[TConnArgs, TConnection] = conn_provider
        self.__conn_args = args
        self.__conn_kwargs = kwargs

        self.__screen_hold: Mode = keep.presenting()

    @property
    def conn(self) -> TConnection:
        '''Returns current connection.

        Usage of this property is only valid inside `with` block using this :class:`db.libname`.

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
        self.__screen_hold.__enter__()
        return self.__conn

    def __exit__(self,
        exc_type: type[Exception] | None,
        exc: Exception | None,
        tb: TracebackType | None,
    ) -> bool:
        '''
        Disposes current connection, via its own `__exit__` / `__del__` if available,
        passing all arguments to it.

        :raises ValueError: When this method is called again before :meth:`__enter__`
        '''
        self.__screen_hold.__exit__(None, None, None)
        if self.__conn is None:
            raise ValueError('Library is not in use - no connection to exit')
        conn = self.__conn
        self.__conn = None
        if isinstance(conn, (oracledb_Connection, pyodbc_Connection)):
            conn.__exit__(exc_type, exc, tb)
        elif isinstance(conn, arrow_odbc_Connection):
            conn.__del__()

        # we should swallow ModeExit exception per Mode.__exit__ implementation
        return exc is None or isinstance(exc, ModeExit)

    @overload
    @staticmethod
    def oracle(
        dsn: str,
        *,
        username: str | None = None,
        password: str | None = None,
        tnsnames: str | None = None,
        odbc_driver: lit[False],
    ) -> libname[oracledb_Connection]: ...

    @overload
    @staticmethod
    def oracle(
        dsn: str,
        *,
        username: str | None = None,
        password: str | None = None,
        odbc_driver: str | None = None,
        odbc_lib: lit['arrow-odbc (polars proxy)'] = 'arrow-odbc (polars proxy)',
    ) -> libname[polars_arrow_ODBCCursorProxy]: ...

    @overload
    @staticmethod
    def oracle(
        dsn: str,
        *,
        username: str | None = None,
        password: str | None = None,
        odbc_driver: str | None = None,
        odbc_lib: lit['pyodbc'],
    ) -> libname[pyodbc_Connection]: ...

    @overload
    @staticmethod
    def oracle(
        dsn: str,
        *,
        username: str | None = None,
        password: str | None = None,
        odbc_driver: str | None = None,
        odbc_lib: lit['arrow-odbc'],
    ) -> libname[arrow_odbc_Connection]: ...

    @staticmethod
    def oracle(
        dsn: str,
        *,
        username: str | None = None,
        password: str | None = None,
        tnsnames: str | None = None,
        odbc_driver: str | lit[False] | None = None,
        odbc_lib: lit['pyodbc', 'arrow-odbc (polars proxy)', 'arrow-odbc'] = 'arrow-odbc (polars proxy)',
    ) -> libname[oracledb_Connection | polars_arrow_ODBCCursorProxy | pyodbc_Connection | arrow_odbc_Connection]:
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
        :return: :class:`db.libname` that connects to specified Oracle Database
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

            return libname(conn_fun, *args, **kwargs)
        else:
            conn_fun, args, kwargs = _connections.oracle(
                dsn,
                username= username,
                password= password,
                odbc_driver= odbc_driver,
                odbc_lib= odbc_lib,
            )

            return libname(conn_fun, *args, **kwargs)


    @overload
    @staticmethod
    def sqlserver(
        dsn: str,
        port: int | None = None,
        *,
        db: str | None = None,
        odbc_driver: str | None = None,
        odbc_lib: lit['arrow-odbc (polars proxy)'] = 'arrow-odbc (polars proxy)',
    ) -> libname[polars_arrow_ODBCCursorProxy]: ...

    @overload
    @staticmethod
    def sqlserver(
        dsn: str,
        port: int | None = None,
        *,
        db: str | None = None,
        odbc_driver: str | None = None,
        odbc_lib: lit['pyodbc'],
    ) -> libname[pyodbc_Connection]: ...

    @overload
    @staticmethod
    def sqlserver(
        dsn: str,
        port: int | None = None,
        *,
        db: str | None = None,
        odbc_driver: str | None = None,
        odbc_lib: lit['arrow-odbc'],
    ) -> libname[arrow_odbc_Connection]: ...

    @staticmethod
    def sqlserver(
        dsn: str,
        port: int | None = None,
        *,
        db: str | None = None,
        odbc_driver: str | None = None,
        odbc_lib: lit['pyodbc', 'arrow-odbc (polars proxy)', 'arrow-odbc'] = 'arrow-odbc (polars proxy)',
    ) -> libname[polars_arrow_ODBCCursorProxy | pyodbc_Connection | arrow_odbc_Connection]:
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
        :return: :class:`db.libname` that connects to specified SQL Server
        '''
        conn_fun, args, kwargs = _connections.sqlserver(
            dsn,
            port,
            odbc_driver= odbc_driver,
            odbc_lib= odbc_lib,
        )

        return libname(conn_fun, *args, **kwargs)
