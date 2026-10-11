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
