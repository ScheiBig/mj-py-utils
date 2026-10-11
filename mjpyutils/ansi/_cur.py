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
