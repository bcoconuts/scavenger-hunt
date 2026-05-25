"""Generic, interface-neutral helpers with no domain or I/O knowledge.

Everything here would work unchanged in a CLI, GUI, or scriptanything that
prints or prompts now lives in cli.py instead.
"""

from calendar import monthrange
from random import randint
from typing import Callable
    

def days_in_month(year: int, month: int) -> int:
    """Return the number of days in the given month, accounting for leap years."""
    return monthrange(year, month)[1]


def format_info(arg_name: str, case: Callable[[str],str] | None=str.title) -> str:
    """Return arg_name with underscores replaced by spaces, formatted by case.

    case is applied to the result (default str.title); pass None to leave the
    casing untouched. Used to turn keyword arg names into readable labels.
    """
    if case:
        formatted_str = case(arg_name.replace("_", " "))
    else:
        formatted_str = arg_name.replace("_", " ")
    return formatted_str


def generate_unique_id(existing_question_ids: set) -> str:
    """Return a new 8-digit id string not already in existing_question_ids."""
    while True:
        new_id = str(randint(10000000, 99999999))
        if new_id not in existing_question_ids:
            return new_id