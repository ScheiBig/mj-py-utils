__all__ = [
    'timer',
]

from time import (
    perf_counter as _perftime,
    time as _time,
)
from typing import (
    Any as _any,
    Generator as _gen,
    Callable as _fun,
    TypedDict as _tdict,
    Literal as _lit,
)
from math import (
    nan as _NaN,
    isnan as _isNaN,
)
from datetime import datetime as _datetime
from types import MethodType as _MethodType

class timer(object):
    '''Allows measuring time - especially useful for measurement of fragments of code.

    ``timer`` can be used in two main ways - created (started) and stopped manually,
    or as contextual resource:
    
    ```
    ## manual
    t1 = Timer(auto_start= True)
    do_something()
    t1.stop()
    print(repr(t1))

    ## context resource
    with Timer() as t2:
        do_some_else()
    print(t2)
    ```
    '''

    def __init__(self, *, 
        auto_start: bool = False,
        use_perf_time: bool = True,
        onstart_print: _fun[[timer], str | None] | _lit[True] | None = None,
        onpause_print: _fun[[timer], str | None] | _lit[True] | None = None,
        onresume_print: _fun[[timer], str | None] | _lit[True] | None = None,
        onstop_print: _fun[[timer], str | None] | _lit[True] | None = None,
    ) -> None:
        '''Creates new ``timer``.

        New ``timer`` can auto-start after creation (it will when using context manager) 
        and by default it uses ``time.perftime`` to ensure proper counting.

        ``on{}_print`` lifecycle hooks can be used to provide function that takes ``timer``
        and returns message to print; ``True`` can also be provided, which will result in
        using default-provided hook.

        :param auto_start: If ``True``, timer will start running after creation
        :param use_perf_time: If ``True``, uses ``time.perftime()`` instead of ``time.time()``;
            should not be modified unless you know what you're doing
        :param onstart_print: Hook used when ``timer`` starts after being stopped or initialized
        :param onpause_print: Hook used when ``timer`` pauses
        :param onresume_print: Hook used when ``timer`` starts after being paused
        :param onstop_print: Hook used when ``timer`` stops
        '''

        self.__start_time: float | None = None
        self.__execution_time_s: float | None = None
        self.__curtime: _fun[[], float] = _perftime if use_perf_time else _time

        self.__onstart_print: _fun[[], str | None] | None = (
            _MethodType(_default_print('started'), self) if onstart_print == True
            else _MethodType(onstart_print, self) if onstart_print is not None
            else None
        ) 
        self.__onpause_print: _fun[[], str | None] | None = (
            _MethodType(_default_print('paused'), self) if onpause_print == True
            else _MethodType(onpause_print, self) if onpause_print is not None
            else None
        ) 
        self.__onresume_print: _fun[[], str | None] | None = (
            _MethodType(_default_print('resumed'), self) if onresume_print == True
            else _MethodType(onresume_print, self) if onresume_print is not None
            else None
        ) 
        self.__onstop_print: _fun[[], str | None] | None = (
            _MethodType(_default_print('stopped'), self) if onstop_print == True
            else _MethodType(onstop_print, self) if onstop_print is not None
            else None
        ) 

        if auto_start:
            self.start()

    def start(self) -> None:
        '''Starts measuring time.

        If timer is initialized or stopped, it begins counting from now, resetting any
        previous start point; if timer was paused, it resumes counting from last execution time.

        Will print ``onstart_print(self)`` if timer starts from initialized/stopped state
        or ``onresume_print(self)`` if it starts from paused state.

        :raises ValueError: If timer is already running
        '''
        # initialized or stopped
        if self.__start_time is None:
            self.__start_time = self.__curtime()
            _call_hook(self.__onstart_print)
        # paused
        elif self.__execution_time_s is not None:
            self.__start_time = self.__curtime() - self.__execution_time_s
            self.__execution_time_s = None
            _call_hook(self.__onresume_print)
        # running
        else:
            raise ValueError('Timer is already running')


    def pause(self) -> None:
        '''Pauses measuring of the time.

        Will print ``onpause__print(self)``.

        :raises ValueError: If timer is not running
        '''
        pause_time = self.__curtime()

        if self.__start_time is None:
            raise ValueError('Timer is not running')

        if self.__execution_time_s is not None:
            raise ValueError('Timer is already paused')

        self.__execution_time_s = pause_time - self.__start_time
        _call_hook(self.__onpause_print)


    def stop(self) -> None:
        '''Stops measuring of the time.

        Will print ``onstop__print(self)``.

        :raises ValueError: If timer is stopped or initialized (not started yet).
        '''
        end_time = self.__curtime()

        if self.__start_time is None:
            raise ValueError('Timer was not started yet')

        if self.__execution_time_s is None:
            self.__execution_time_s = end_time - self.__start_time

        self.__start_time = None

        _call_hook(self.__onstop_print)

    def __str__(self) -> str:
        '''
        :return: Current time of timer in default format.
        '''
        v = format(self, '(%+.3D days) %+02H:%M:%S.%l')
        if v[1] == '0': v = v.split(') ')[1]
        return v

    def __format__(self, format_spec: str) -> str:
        '''
        Format specifiers take form of %{modifier}directive, with available directives:

        Time parts:
        * ``D`` - day,
        * ``H`` - hours,
        * ``M`` - minutes,
        * ``S`` - seconds,
        * ``l`` - milliseconds,
        * ``f`` - microseconds.

        Time by default, represent only their segment of duration, with 0-padding (to 2 characters for HMS, to 3 for lf).

        Those behaviors can be modified by:
        * ``#`` - removes padding, without turning off segment-of-duration,
        * ``+`` - instead of segment, returns total duration in this unit.

        ``+`` can be followed by numerical format ``{{0/_}{n}}{.{m}}``, ``{n}`` and ``{m}`` being unsigned integers, representing:
        - ``{n}`` - padding of duration, depending on preceding character either 0 or space padding,
        - ``{m}`` - number of digits after decimal point
        
        ``{{0/_}{n}}`` format is also allowed for unflagged time segment.

        Additional available directives, without modifiers:
        * ``s`` - prints state in which timer is currently in (initialized/running/paused/stopped),
        * ``%`` - prints ``'%'`` character (``%%`` is escape sequence for percent).

        For example, assuming paused ``timer`` counted 90123.456789 seconds, default format used by ``str(timer)`` would be equivalent to:
        ```py
        print(f'{timer:<%s> (%+.3D days) %+02H:%M:%D.%l}')
        # <paused> (1.043 days) 25:02:03.456
        ```
        '''

        if format_spec == '':
            return str(self)

        if self.__execution_time_s is None:
            if self.__start_time is None:
                execution_time = _NaN
            else:
                execution_time = self.__curtime() - self.__start_time
        else:
            execution_time = self.__execution_time_s

        total_days = execution_time / 86_400
        total_hours = execution_time / 3600
        total_minutes = execution_time / 60
        total_seconds = execution_time / 1
        total_milliss = execution_time * 1000
        total_micross = execution_time * 1000_000


        days, rest = divmod(execution_time, 86400)
        hours, rest = divmod(rest, 3600)
        minutes, rest = divmod(rest, 60)
        seconds, rest = divmod(rest, 1)
        seconds = int(seconds) if not _isNaN(seconds) else seconds
        rest *= 1_000_000
        milliss, micross = divmod(rest, 1000)


        start_none, exec_none = self.__start_time is None, self.__execution_time_s is None

        if start_none and exec_none:
            state = 'initialized'
        elif not start_none and exec_none:
            state = 'running'
        elif start_none and not exec_none:
            state = 'stopped'
        elif not start_none and not exec_none:
            state = 'paused'
        else:
            raise AssertionError('Unknown timer state')

        out = ''
        for t in _tokenize(format_spec):
            if isinstance(t, str):
                out += t
                continue

            v = _validate_token(t)
            if isinstance(v, ValueError):
                raise v

            match v['directive']:
                case '%': out += '%'; continue
                case 's': out += state; continue
                case 'D': tot, part, deff = total_days, days, ''
                case 'H': tot, part, deff = total_hours, hours, '02'
                case 'M': tot, part, deff = total_minutes, minutes, '02'
                case 'S': tot, part, deff = total_seconds, seconds, '02'
                case 'l': tot, part, deff = total_milliss, milliss, '03'
                case 'f': tot, part, deff = total_micross, micross, '03'
                case _: raise AssertionError(f'Unknown directive in token: [{v['raw']}]')

            val = tot if v['flag'] == '+' else part
            fmt = ''

            fmt += ( 
                deff if v['flag'] != '#'
                else f'{v['pad']}{v['width']}' if v['width'] is not None
                else ''
            )
            fmt += ( 
                f'.{v['prec']}f' if v['prec'] is not None
                else '.0f'
            )
            if v['prec'] is None and not _isNaN(tot):
                val = int(val)
            
            out += (
                f'{val:{fmt}}' if not _isNaN(tot)
                else f'{0.0:{fmt}}'.replace('0', '-')
            )

        return out

    def __repr__(self) -> str:
        '''
        :return: Representation of ``timer`` state and current time in default format
        '''
        return f'Timer({self:<%s>} {str(self)})'


    def __enter__(self) -> timer:
        '''Starts ``timer`` used as resource in context block

        :return: ``self``
        '''
        if self.__start_time is None:
            self.start()
        return self

    def __exit__(self, exc_type: _any, exc_value: _any, traceback: _any) -> None:
        '''Finalizes usage of ``timer`` as resource, by stopping it

        :param exc_type: _Ignored_
        :param exc_value: _Ignored_
        :param traceback: _Ignored_
        '''
        self.stop()

class _token(_tdict):
    directive: _lit['D', 'H', 'M', 'S', 'l', 'f', 's', '%'] | str
    width: int | None
    pad: _lit['0', ' '] | None
    prec: int | None
    flag: _lit['#', '+'] | None
    raw: str

def _tokenize(spec: str) -> _gen[_token | str, _any, None]:
    ptr = spec

    while ptr:
        # parse token
        if ptr[0:1] == '%':
            tok = _token(
                directive= '',
                width= None,
                pad= None,
                prec= None,
                flag= None,
                raw= ptr[0:1],
            )
            # dispose %
            ptr = ptr[1:]
            # capture flag
            match ptr[0:1]:
                case '#':
                    tok['flag'] = '#'
                    tok['raw'], ptr = tok['raw'] + ptr[0], ptr[1:]
                case '+':
                    tok['flag'] = '+'
                    tok['raw'], ptr = tok['raw'] + ptr[0], ptr[1:]
                case _: pass
            # capture padding
            if ptr[0:1] == '_' or ptr[0:1].isdigit():
                match ptr[0:1]:
                    case '0':
                        tok['pad'] = '0'
                        tok['raw'], ptr = tok['raw'] + ptr[0], ptr[1:]
                    case '_':
                        tok['pad'] = ' '
                        tok['raw'], ptr = tok['raw'] + ptr[0], ptr[1:]
                    case _:
                        tok['pad'] = None
                p = 0
                while ptr[0:1].isdigit():
                    tok['raw'] += ptr[0]
                    p, ptr = (p or 0) * 10 + int(ptr[0]), ptr[1:]
                tok['width'] = p
            # capture precision
            if ptr[0:1] == '.':
                p = 0
                tok['raw'], ptr = tok['raw'] + ptr[0], ptr[1:]
                while ptr[0:1].isdigit():
                    tok['raw'] += ptr[0]
                    p, ptr = (p or 0) * 10 + int(ptr[0]), ptr[1:]
                tok['prec'] = p
            # capture directive name
            tok['raw'] += ptr[0:1]
            tok['directive'], ptr = ptr[0:1], ptr[1:]

            yield tok
        # consume literal
        else:
            lit = ''
            while ptr[0:1] not in ['%', '']:
                lit, ptr = lit + ptr[0], ptr[1:]
            yield lit

def _validate_token(tok: _token) -> ValueError | _token:
    if tok['directive'] == '':
        return ValueError(f'[{tok['raw']}]: Format specifier attemts to use directive without providing its name')

    if tok['directive'] == '%':
        if tok['width'] is not None:
            return ValueError(f'[{tok['raw']}]: Width not allowed in percent escape sequence')
        if tok['prec'] is not None:
            return ValueError(f'[{tok['raw']}]: Precision not allowed in percent escape sequence')
        if tok['flag'] is not None:
            return ValueError(f'[{tok['raw']}]: Modifier flags not allowed in percent escape sequence')
        return tok

    if tok['directive'] == 's':
        if tok['width'] is not None:
            return ValueError(f'[{tok['raw']}]: Width not allowed in state directive')
        if tok['prec'] is not None:
            return ValueError(f'[{tok['raw']}]: Precision not allowed in state directive')
        if tok['flag'] is not None:
            return ValueError(f'[{tok['raw']}]: Modifier flags not allowed in state directive')
        return tok

    if tok['directive'] in ['D', 'H', 'M', 'S', 'l', 'f']:
        if tok['flag'] == '#':
            if tok['pad'] is not None:
                return ValueError(f'[{tok['raw']}]: Padding specifier not allowed in time segment directive without padding')
            if tok['width'] is not None:
                return ValueError(f'[{tok['raw']}]: Width not allowed in time segment directive without padding')
            if tok['prec'] is not None:
                return ValueError(f'[{tok['raw']}]: Precision not allowed in time segment directive')
            return tok

        if tok['flag'] == '+':
            return tok

        if tok['flag'] is None:
            if tok['prec'] is not None:
                return ValueError(f'[{tok['raw']}]: Precision not allowed in time segment directive')
            return tok

    return ValueError(f'[{tok['raw']}]: Unknown format directive: %{tok['directive']}')

def _default_print(state: str) -> _fun[[timer], str | None]:
    if state == 'started':
        return lambda _ : f'Timer {state} @ {_datetime.now()}'
    return lambda s: f'Timer {state} after {s} @ {_datetime.now()}'

def _call_hook(hook: _fun[[], str | None] | None) -> None:
    if hook is not None:
        s = hook()
        if s is not None:
            print(s)
