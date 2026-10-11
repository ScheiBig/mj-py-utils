__all__ = [
    'password',
]

from getpass import getpass as _getpass
from inspect import signature as _signature

def password(
    prompt: str = "Hasło: ",
    *,
    echo_char: str = '*',
) -> str:
    '''Prompts user for password and returns entered result.

    Uses ``getpass`` to hide entered password, using sane defaults for password masking,
    while making sure mask works correctly in Jupyter notebooks.

    :param prompt: Prompt to display to user
    :param echo_char: Character used for password masking - must be a single, ascii character;
        this parameter is ignored in interactive environments, where ``getpass`` is delegated
        to a widget implementation ``Kernel.getpass``
    :return: Entered password ``str`` - if empty, then user cancelled
    '''
    if 'echo_char' in _signature(_getpass).parameters:
        try:
            return _getpass(prompt, echo_char= echo_char)
        except (KeyboardInterrupt, EOFError):
            return ''
    else:
        return _getpass(prompt)
