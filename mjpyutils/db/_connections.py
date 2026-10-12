import oracledb
from oracledb import Connection as oracledb_Connection
import pyodbc
from pyodbc import Connection as pyodbc_Connection
import arrow_odbc
from arrow_odbc import Connection as arrow_odbc_Connection
from typing import (
    Callable as fun,
    Literal as lit,
    overload as overload,
    Any as any_type,
)
from pathlib import Path
import sys
from polars.io.database._cursor_proxies import ODBCCursorProxy as polars_arrow_ODBCCursorProxy

def_Ora_username: str | None = None
'''Default value used for `oracle(username=)`'''
def_Ora_getpassword: fun[[], str] | None = None
'''Function returning default value for `oracle(password=)`'''
def_Ora_tnsnames: str | None = None
'''Default value for `oracle(tnsnames=)`

When using Oracle via ODBC, or when Oracle Client libraries are located
and `oracledb` successfully loads into thick mode, this variable will have
no effect whatsoever, as driver/client will use `.env.TNS_ADMIN` or client-specific
tns_names.ora.
'''
def_Ora_odbc_driver: str | None = None
'''Default value for `oracle(odbc_driver=)`

During initialization, library will attempt to find any Oracle DB driver and assign
it to this variable.
'''
def_MS_port: int | None = 1433
'''Default value for `sqlserver(port=)`, preset by library to common 1433 port'''
def_MS_odbc_driver: str | None = None
'''Default value for `sqlserver(odbc_driver=)`

During initialization, library will attempt to find any SQL Server driver and assign
it to this variable.
'''

def _init_defaults():
    global def_Ora_odbc_driver
    global def_MS_odbc_driver
    import itertools
    ora_driver = max(filter(
        lambda x: x.lower().find('oracle') >= 0,
         pyodbc.drivers(),
    ), default= None)
    def_Ora_odbc_driver = ora_driver
    try:
        oracledb.init_oracle_client()
    except:
        pass
    ms_driver = max(filter(
        lambda x: x.lower().find('sql server') >= 0,
         pyodbc.drivers(),
    ), default= None)
    def_MS_odbc_driver = ms_driver
_init_defaults()

@overload
def oracle(
    dsn: str,
    *,
    username: str | None = None,
    password: str | None = None,
    tnsnames: str | None = None,
    odbc_driver: lit[False],
) -> tuple[fun[..., oracledb_Connection], tuple[any_type, ...], dict[str, any_type]]: ...

@overload
def oracle(
    dsn: str,
    *,
    username: str | None = None,
    password: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: lit['arrow-odbc (polars proxy)'] = 'arrow-odbc (polars proxy)',
) -> tuple[fun[..., polars_arrow_ODBCCursorProxy], tuple[any_type, ...], dict[str, any_type]]: ...

@overload
def oracle(
    dsn: str,
    *,
    username: str | None = None,
    password: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: lit['pyodbc'],
) -> tuple[fun[..., pyodbc_Connection], tuple[any_type, ...], dict[str, any_type]]: ...

@overload
def oracle(
    dsn: str,
    *,
    username: str | None = None,
    password: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: lit['arrow-odbc'],
) -> tuple[fun[..., arrow_odbc_Connection], tuple[any_type, ...], dict[str, any_type]]: ...


def oracle(
    dsn: str,
    *,
    username: str | None = None,
    password: str | None = None,
    tnsnames: str | None = None,
    odbc_driver: str | lit[False] | None = None,
    odbc_lib: lit['pyodbc', 'arrow-odbc (polars proxy)', 'arrow-odbc'] = 'arrow-odbc (polars proxy)',
) -> tuple[
    fun[..., oracledb_Connection | polars_arrow_ODBCCursorProxy | pyodbc_Connection | arrow_odbc_Connection],
    tuple[any_type, ...],
    dict[str, any_type],
]:
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
    if tnsnames is None and oracledb.is_thin_mode():
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
        return oracledb.connect, (), {
            'dsn': dsn,
            'user': username,
            'password': password,
            'config_dir': tnsnames,
        }

    avail_dsn = [k.lower() for k in pyodbc.dataSources().keys()]

    match odbc_lib:
        case 'pyodbc':
            conn_fun = pyodbc.connect
        case 'arrow-odbc':
            conn_fun = arrow_odbc.connect
        case 'arrow-odbc (polars proxy)':
            conn_fun = polars_arrow_ODBCCursorProxy

    if dsn.lower() in avail_dsn:
        c_str = _conn_str({
            'DSN': dsn,
            'UID': username,
            'PWD': _conn_esc(password),
        })
        return conn_fun, (c_str, ), {}

    c_str = _conn_str({
        'DRIVER': _conn_esc(odbc_driver),
        'DBQ': dsn,
        'UID': username,
        'PWD': _conn_esc(password),
    })
    return conn_fun, (c_str, ), {}


@overload
def sqlserver(
    dsn: str,
    port: int | None = None,
    *,
    db: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: lit['arrow-odbc (polars proxy)'] = 'arrow-odbc (polars proxy)',
) -> tuple[fun[..., polars_arrow_ODBCCursorProxy], tuple[any_type, ...], dict[str, any_type]]: ...

@overload
def sqlserver(
    dsn: str,
    port: int | None = None,
    *,
    db: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: lit['pyodbc'],
) -> tuple[fun[..., pyodbc_Connection], tuple[any_type, ...], dict[str, any_type]]: ...

@overload
def sqlserver(
    dsn: str,
    port: int | None = None,
    *,
    db: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: lit['arrow-odbc'],
) -> tuple[fun[..., arrow_odbc_Connection], tuple[any_type, ...], dict[str, any_type]]: ...

def sqlserver(
    dsn: str,
    port: int | None = None,
    *,
    db: str | None = None,
    odbc_driver: str | None = None,
    odbc_lib: lit['pyodbc', 'arrow-odbc (polars proxy)', 'arrow-odbc'] = 'arrow-odbc (polars proxy)',
) ->tuple[
    fun[..., polars_arrow_ODBCCursorProxy | pyodbc_Connection | arrow_odbc_Connection],
    tuple[any_type, ...],
    dict[str, any_type],
]:
    avail_dsn = [k.lower() for k in pyodbc.dataSources().keys()]

    match odbc_lib:
        case 'pyodbc':
            conn_fun = pyodbc.connect
        case 'arrow-odbc':
            conn_fun = arrow_odbc.connect
        case 'arrow-odbc (polars proxy)':
            conn_fun = polars_arrow_ODBCCursorProxy

    if dsn.lower() in avail_dsn:
        con_conf = {'DSN': dsn}

        if db:
            con_conf['DATABASE'] = db

        con_conf['Trusted_Connection'] = 'yes'
        c_str = _conn_str(con_conf)

        return conn_fun, (c_str,), {}

    if port is None:
        if def_MS_port is None:
            raise ValueError(
                'No port passed or default set via [db.def_MS_port]')
        port = def_MS_port
    con_conf = {'SERVER': f'{dsn},{port}'}

    if db:
        con_conf['DATABASE'] = db

    if odbc_driver is None:
        if def_MS_odbc_driver is None:
            raise ValueError(
                'No odbc_driver passed or default set via [db.def_MS_odbc_driver]')
        odbc_driver = def_MS_odbc_driver

    con_conf['DRIVER'] = _conn_esc(odbc_driver)
    con_conf['Trusted_Connection'] = 'yes'

    c_str = _conn_str(con_conf)

    return conn_fun, (c_str,), {}


@overload
def data_sources(*, names_only: lit[False] | None = None) -> dict[str, str]: ...

@overload
def data_sources(*, names_only: lit[True]) -> list[str]: ...

def data_sources(*, names_only: bool | None = None) -> dict[str, str] | list[str]:
    '''Returns dictionary of registered ODBC Data Source Names, as well as their descriptions.

    If `names_only` is set, then function returns list instead without descriptions.
    '''
    if names_only:
        return list(pyodbc.dataSources().keys())
    else:
        return pyodbc.dataSources()


@overload
def odbc_drivers(*, names_only: lit[False] | None = None) -> dict[str, Path | None]: ...

@overload
def odbc_drivers(*, names_only: lit[True]) -> list[str]: ...

def odbc_drivers(*, names_only: bool | None = None) -> dict[str, Path | None] | list[str]:
    '''Returns dictionary of odbc drivers and paths to their locations.

    It might not be possible to fetch driver locations, in which case `None`
    will be associated instead of :class:`Path`.

    If `names_only` is set, then function returns list instead without descriptions.
    '''
    if names_only:
        return pyodbc.drivers()
    else:
        return {
            driver: _get_driver_path(driver)
            for driver in pyodbc.drivers()
        }

def _get_driver_path(driver: str | None) -> Path | None:
    if driver is None: return None
    if sys.platform == 'win32':
        import winreg
        import platform
        if platform.architecture()[0] == '32bit':
            base_key = r'SOFTWARE\WOW6432Node\ODBC\ODBCINST.INI'
        else:
            base_key = r'SOFTWARE\ODBC\ODBCINST.INI'
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f'{base_key}\\{driver}')

            for valueEx in ('Diver', 'Setup'):
                try:
                    value, _ = winreg.QueryValueEx(key, valueEx)
                    path = Path(value)

                    if path.exists(): return path
                except FileNotFoundError:
                    pass
        except FileNotFoundError:
            pass
    if sys.platform == 'darwin' or sys.platform == 'linux':
        import subprocess

        try:
            result = subprocess.run(
                ['odbcinst', '-q', '-d', '-n', driver],
                capture_output=True,
                text=True,
                check=True,
            )
        except Exception:
            return None

        for line in result.stdout.splitlines():
            if line.startswith('Driver='):
                return Path(line.removeprefix('Driver='))

    return None

def _conn_str(odbc_conf: dict[str, str]) -> str:
    return ';'.join([
        f'{k}={v}'
        for k, v in odbc_conf.items()
    ]) + ';'

def _conn_esc(odbc_val: str) -> str:
    return f'{{{odbc_val.replace('}', '}}')}}}'
