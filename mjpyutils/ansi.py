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

import re as _re


class fg:
    '''Foreground colors'''
    BLACK = '\u001b[30m'
    '''Sets black foreground'''
    RED = '\u001b[31m'
    '''Sets red foreground'''
    GREEN = '\u001b[32m'
    '''Sets green foreground'''
    YELLOW = '\u001b[33m'
    '''Sets yellow foreground'''
    BLUE = '\u001b[34m'
    '''Sets blue foreground'''
    MAGENTA = '\u001b[35m'
    '''Sets magenta foreground'''
    CYAN = '\u001b[36m'
    '''Sets cyan foreground'''
    WHITE = '\u001b[37m'
    '''Sets white foreground'''

    RESET = '\u001b[39m'
    '''Reset foreground color'''

    class b:
        '''Bright foreground colors'''
        BLACK = '\u001b[90m'
        '''Sets bright black foreground (might be bold instead in some tty)'''
        RED = '\u001b[91m'
        '''Sets bright red foreground (might be bold instead in some tty)'''
        GREEN = '\u001b[92m'
        '''Sets bright green foreground (might be bold instead in some tty)'''
        YELLOW = '\u001b[93m'
        '''Sets bright yellow foreground (might be bold instead in some tty)'''
        BLUE = '\u001b[94m'
        '''Sets bright blue foreground (might be bold instead in some tty)'''
        MAGENTA = '\u001b[95m'
        '''Sets bright magenta foreground (might be bold instead in some tty)'''
        CYAN = '\u001b[96m'
        '''Sets bright cyan foreground (might be bold instead in some tty)'''
        WHITE = '\u001b[97m'
        '''Sets bright white foreground (might be bold instead in some tty)'''

    @staticmethod
    def c4bit(c: int) -> str:
        '''Returns 4-bit foreground color for given value

        :param c: Color value - must be 4-bit unsigned integer
        :raises ValueError: If not ``0 <= c < 16``
        :return: Escape sequence that sets foreground color
            (same as using named color from ``fg`` / ``fg.b``)
        '''
        match c:
            case 0: return fg.BLACK
            case 1: return fg.RED
            case 2: return fg.GREEN
            case 3: return fg.YELLOW
            case 4: return fg.BLUE
            case 5: return fg.MAGENTA
            case 6: return fg.CYAN
            case 7: return fg.WHITE
            case 8: return fg.b.BLACK
            case 9: return fg.b.RED
            case 10: return fg.b.GREEN
            case 11: return fg.b.YELLOW
            case 12: return fg.b.BLUE
            case 13: return fg.b.MAGENTA
            case 14: return fg.b.CYAN
            case 15: return fg.b.WHITE
            case _: raise ValueError('c must be 4-bit unsigned integer')

    @staticmethod
    def c8bit(c: int) -> str:
        '''Returns 8-bit foreground color for given value

        :param c: Color value - must be 8-bit unsigned integer
        :raises ValueError: If not ``0 <= c < 256``
        :return: Escape sequence that sets foreground color
        '''
        match c:
            case int(c_) if 0 <= c_ < 256:
                return f'\u001b[38;5;{c_}m'
            case _: raise ValueError('c must be 8-bit unsigned integer')

    @staticmethod
    def c24bit(r: int, g: int, b: int) -> str:
        '''Returns 24-bit (rgb) foreground color for given value

        :param r: Red channel value - must be 8-bit unsigned integer
        :param g: Green channel value - must be 8-bit unsigned integer
        :param b: Blue channel value - must be 8-bit unsigned integer
        :raises ValueError: If any of params is not ``0 <= _arg_ < 256``
        :return: Escape sequence that sets foreground color
        '''
        match (r, g, b):
            case (int(r_), int(g_), int(b_)) if (
                0 <= r_ < 256 and 0 <= g_ < 256 and 0 <= b_ < 256
            ):
                return f'\u001b[38;2;{r_};{g_};{b_}m'
            case _: raise ValueError('(r, g, b) must all be 8-bit unsigned integers')


class bg:
    '''Background colors'''
    BLACK = '\u001b[40m'
    '''Sets black background'''
    RED = '\u001b[41m'
    '''Sets red background'''
    GREEN = '\u001b[42m'
    '''Sets green background'''
    YELLOW = '\u001b[43m'
    '''Sets yellow background'''
    BLUE = '\u001b[44m'
    '''Sets blue background'''
    MAGENTA = '\u001b[45m'
    '''Sets magenta background'''
    CYAN = '\u001b[46m'
    '''Sets cyan background'''
    WHITE = '\u001b[47m'
    '''Sets white background'''

    RESET = '\u001b[49m'
    '''Reset background color'''

    class b:
        '''Bright background colors'''
        BLACK = '\u001b[100m'
        '''Sets bright black background'''
        RED = '\u001b[101m'
        '''Sets bright red background'''
        GREEN = '\u001b[102m'
        '''Sets bright green background'''
        YELLOW = '\u001b[103m'
        '''Sets bright yellow background'''
        BLUE = '\u001b[104m'
        '''Sets bright blue background'''
        MAGENTA = '\u001b[105m'
        '''Sets bright magenta background'''
        CYAN = '\u001b[106m'
        '''Sets bright cyan background'''
        WHITE = '\u001b[107m'
        '''Sets bright white background'''

    @staticmethod
    def c4bit(c: int) -> str:
        '''Returns 4-bit background color for given value

        :param c: Color value - must be 4-bit unsigned integer
        :raises ValueError: If not ``0 <= c < 16``
        :return: Escape sequence that sets background color 
            (same as using named color from ``fg`` / ``fg.b``)
        '''
        match c:
            case 1: return bg.BLACK
            case 2: return bg.RED
            case 3: return bg.GREEN
            case 4: return bg.YELLOW
            case 5: return bg.BLUE
            case 6: return bg.MAGENTA
            case 7: return bg.CYAN
            case 8: return bg.WHITE
            case 9: return bg.b.BLACK
            case 10: return bg.b.RED
            case 11: return bg.b.GREEN
            case 12: return bg.b.YELLOW
            case 13: return bg.b.BLUE
            case 14: return bg.b.MAGENTA
            case 15: return bg.b.CYAN
            case 16: return bg.b.WHITE
            case _: raise ValueError('c must be 4-bit unsigned integer')

    @staticmethod
    def c8bit(c: int) -> str:
        '''Returns 8-bit background color for given value

        :param c: Color value - must be 8-bit unsigned integer
        :raises ValueError: If not ``0 <= c < 256``
        :return: Escape sequence that sets background color 
        '''
        match c:
            case int(c_) if 0 <= c_ < 256:
                return f'\u001b[48;5;{c_}m'
            case _: raise ValueError('c must be 8-bit unsigned integer')

    @staticmethod
    def c24bit(r: int, g: int, b: int) -> str:
        '''Returns 24-bit (rgb) background color for given value

        :param r: Red channel value - must be 8-bit unsigned integer
        :param g: Green channel value - must be 8-bit unsigned integer
        :param b: Blue channel value - must be 8-bit unsigned integer
        :raises ValueError: If any of params is not ``0 <= _arg_ < 256``
        :return: Escape sequence that sets background color 
        '''
        match (r, g, b):
            case (int(r_), int(g_), int(b_)) if (
                0 <= r_ < 256 and 0 <= g_ < 256 and 0 <= b_ < 256
            ):
                return f'\u001b[48;2;{r_};{g_};{b_}m'
            case _: raise ValueError('(r, g, b) must all be 8-bit unsigned integers')


class fmt:
    '''Text formatting'''
    RESET = '\u001b[0m'
    '''Resets all colors and formats; only guaranteed way to clear any format'''

    BOLD = '\u001b[1m'
    '''Turns on bold text format'''
    NOT_BOLD = '\u001b[22m'
    '''Turns off bold text format'''

    ITALIC = '\u001b[3m'
    '''Turns on italic text format'''
    NOT_ITALIC = '\u001b[23m'
    '''Turns off italic text format'''

    UNDERLINE = '\u001b[4m'
    '''Turns off underlined text format'''
    NOT_UNDERLINE = '\u001b[24m'
    '''Turns on underlined text format'''

    STRIKE = '\u001b[9m'
    '''Turns on strikethrough text format'''
    NOT_STRIKE = '\u001b[29m'
    '''Turns off strikethrough text format'''

    REVERSE = '\u001b[7m'
    '''Swaps foreground and background colors'''
    NOT_REVERSE = '\u001b[27m'
    '''Swaps back foreground and background colors'''

    SLOW_BLINK = '\x1b[5m'
    '''Turns on slow blinking'''
    FAST_BLINK = '\x1b[6m'
    '''Turns on fast blinking'''
    NOT_BLINK = '\x1b[25m'
    '''Turns off all blinking'''

    HIDDEN = '\x1b[8m'
    '''Turns on visually hidden text format 
        (this is not password-safe - assume text is still copyable)
    '''
    NOT_HIDDEN = '\x1b[28m'
    '''Turns off visually hidden text format'''


class clear:
    '''Utilities for console clearing'''
    class disp:
        '''Clears display'''
        END = '\u001b[0J'
        '''Clears from cursor to end of the screen'''
        BEGIN = '\u001b[1J'
        '''Clears from cursor to beginning of the screen'''
        ALL = '\u001b[2J'
        '''Clears the entire screen and moves to beginning of first line'''
        SCROLL = '\u001b[3J'
        '''Clears the entire screen, scrollback buffer and moves to beginning of first line'''
    class ln:
        '''Clears current line'''
        END = '\u001b[0K'
        '''Clears from cursor to end of the current line'''
        BEGIN = '\u001b[1K'
        '''Clears from cursor to beginning of the current line'''
        ALL = '\u001b[2K'
        '''Clears the entire current line, without moving cursor'''


class cur:
    '''Utilities for cursor position'''
    class rel:
        '''Relative cursor position movement'''
        UP = '\u001b[1A'
        '''Moves cursor 1 position up (if already on edge of screen - does nothing)'''
        DOWN = '\u001b[1B'
        '''Moves cursor 1 position down (if already on edge of screen - does nothing)'''
        RIGHT = '\u001b[1C'
        '''Moves cursor 1 position right (if already on edge of screen - does nothing)'''
        LEFT = '\u001b[1D'
        '''Moves cursor 1 position left (if already on edge of screen - does nothing)'''

        NEXT_LN = '\u001b[1E'
        '''Moves cursor to beginning of next line'''
        PREV_LN = '\u001b[1F'
        '''Moves cursor to beginning of previous line'''

        @staticmethod
        def pos(row: int = 1) -> str:
            '''Moves cursor to given relative position.

            Moves only between rows - always resets column to first one.

            :param row: How many rows to move cursor by (1-indexed, negative goes to previous)
            :return: Escape sequence that moves cursor position
            '''
            if row < 0:
                return f'\u001b[{row}F'
            else:
                return f'\u001b[{row}E'

    class abs:
        '''Absolute cursor position movement'''
        BEGIN = '\u001b[1G'
        '''Moves cursor to beginning of current line'''
        TOP_BEGIN = '\u001b[1;1H'
        '''Moves cursor to beginning of first line'''

        @staticmethod
        def pos(col: int = 1, row: int | None = None) -> str:
            '''Moves cursor to given absolute position.

            If row is omitted, then only changes column.

            :param col: Column to move cursor into (1-indexed)
            :param row: Row to move cursor into (1-indexed)
            :return: Escape sequence that moves cursor position
            '''
            if row == None:
                return f'\u001b[{col}G'
            else:
                return f'\u001b[{row};{col}H'


_ANSI = _re.compile(
    r'\u001b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]|\][^\u0007\u001b]*(?:\u0007|\u001b\\))'
)


def strip_escapes(src: str) -> str:
    '''Removes all (common) ansi escape sequences from source

    :param src: Source string
    :return: ``src`` with stripped ansi escapes
    '''
    return _ANSI.sub('', src)
