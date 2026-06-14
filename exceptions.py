"""custom exceptions for scavenger hunt"""


class NoSelection(Exception):
    """Raised when there's nothing for the user to pick."""


class ManualAbort(Exception):
    """Raised to abort the current action: a declined warning, or 'F' to quit a game.

    Caught by the menu loop, which treats it as 'cancel and stay in the menu'.
    """