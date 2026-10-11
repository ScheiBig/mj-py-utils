import re as _re

_ANSI = _re.compile(
    r'\u001b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]|\][^\u0007\u001b]*(?:\u0007|\u001b\\))'
)

def strip_escapes(src: str) -> str:
    '''Removes all (common) ansi escape sequences from source

    :param src: Source string
    :return: ``src`` with stripped ansi escapes
    '''
    return _ANSI.sub('', src)
