from typing import overload as _overload
from functools import reduce as _reduce

@_overload
def coalesce[T](first: T | None, last: T) -> T: ...

@_overload
def coalesce[T](first: T | None, second: T| None, last: T) -> T: ...

@_overload
def coalesce[T](first: T | None, second: T | None, third: T | None, last: T) -> T: ...

@_overload
def coalesce[T](first: T | None, second: T | None, third: T | None, fourth: T | None, last: T) -> T: ...

@_overload
def coalesce[T](first: T | None, second: T | None, third: T | None, fourth: T | None, fifth: T | None,  last: T) -> T: ...

@_overload
def coalesce[T](first: T | None, second: T | None, third: T | None, fourth: T | None, fifth: T | None, sixth: T | None, last: T) -> T: ...

@_overload
def coalesce[T](first: T | None, second: T | None, third: T | None, fourth: T | None, fifth: T | None, sixth: T | None, seventh: T | None, last: T) -> T: ...

@_overload
def coalesce[T](first: T | None, second: T | None, third: T | None, fourth: T | None, fifth: T | None, sixth: T | None, seventh: T | None, eight: T | None, last: T) -> T: ...

@_overload
def coalesce[T](first: T | None, second: T | None, third: T | None, fourth: T | None, fifth: T | None, sixth: T | None, seventh: T | None, eight: T | None, nineth: T | None,  last: T) -> T: ...

@_overload
def coalesce[T](first: T | None, second: T | None, *rest: T | None) -> T | None: ...

def coalesce[T](first: T | None, second: T | None, *rest: T | None) -> T | None: # pyright: ignore[reportInconsistentOverload] - overloads expose utility signatures
    '''Returns first non-``None`` value from provided arguments, 
        or ``None`` if neither one is concrete.
    '''
    return _reduce(
        lambda p, n: n if p is None else p,
        rest, 
        second if first is None else first
    )
