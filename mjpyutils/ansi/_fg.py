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
