'''
### ``ansi`` module provides escape sequences for text formatting and cursor manipulation in console.

ANSI escape sequences are supported in almost every *nix terminal,
in PowerShell 5 (might need a flag to be activated) and Windows Terminal app (natively).

#### Within this module, you will find namespaces for:
* ``ansi.fg`` - changing font color,
* ``ansi.bg`` - changing background color (directly behind font),
* ``ansi.fmt`` - changing font decoration style,
* ``ansi.clear`` - clearing console,
* ``ansi.cur`` - moving cursor,
* ``strip_escapes`` - removing esc-seq from string.

Please note, that **escape sequences modify console state** and so **format will probably outlive
application** that uses it, therefore application using this module **should
``print(ansi.fmt.RESET)`` in cleanup code** to restart format of console.

Not all sequences are guaranteed to be fully portable - please use https://ansicode.eversources.app/en/terminals or other compatibility reference.
'''
from ._fg import fg
from ._bg import bg
from ._fmt import fmt
from ._clear import clear
from ._cur import cur
from ._strip_escapes import strip_escapes

__all__ = [
    'fg',
    'bg',
    'fmt',
    'clear',
    'cur',
    'strip_escapes'
]
