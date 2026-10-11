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
