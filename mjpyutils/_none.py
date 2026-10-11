from typing import overload
from functools import reduce

@overload
def coalesce[T](first: T | None, last: T) -> T: ...

@overload
def coalesce[T](first: T | None, second: T| None, last: T) -> T: ...

@overload
def coalesce[T](first: T | None, second: T | None, third: T | None, last: T) -> T: ...

@overload
def coalesce[T](first: T | None, second: T | None, third: T | None, fourth: T | None, last: T) -> T: ...

@overload
def coalesce[T](first: T | None, second: T | None, third: T | None, fourth: T | None, fifth: T | None,  last: T) -> T: ...

@overload
def coalesce[T](first: T | None, second: T | None, third: T | None, fourth: T | None, fifth: T | None, sixth: T | None, last: T) -> T: ...

@overload
def coalesce[T](first: T | None, second: T | None, third: T | None, fourth: T | None, fifth: T | None, sixth: T | None, seventh: T | None, last: T) -> T: ...

@overload
def coalesce[T](first: T | None, second: T | None, third: T | None, fourth: T | None, fifth: T | None, sixth: T | None, seventh: T | None, eight: T | None, last: T) -> T: ...

@overload
def coalesce[T](first: T | None, second: T | None, third: T | None, fourth: T | None, fifth: T | None, sixth: T | None, seventh: T | None, eight: T | None, nineth: T | None,  last: T) -> T: ...

@overload
def coalesce[T](first: T | None, second: T | None, *rest: T | None) -> T | None: ...

def coalesce[T](first: T | None, second: T | None, *rest: T | None) -> T | None: # pyright: ignore[reportInconsistentOverload] - overloads expose utility signatures
    '''Returns first non-`None` value from provided arguments, 
        or `None` if neither one is concrete.
    '''
    return reduce(
        lambda p, n: n if p is None else p,
        rest, 
        second if first is None else first
    )
