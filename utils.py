"""Common utility functions."""

from calendar import monthrange
from random import randint
from typing import Callable
    

def days_in_month(year: int, month: int) -> int:
    '''
    Returns the number of days for a given month.

    Args:
        year: Target year - matters for leap years
        month: Target month

    Returns:
        Value of the number of days
    '''
    return monthrange(year, month)[1]


def format_info(arg_name: str, case: Callable[[str],str] | None=str.title) -> str:
    '''
    Returns a string whose underscores 
    have been replaced with spaces.

    Args:
        arg_name: Name of argument whos name is being returned.
        case: Format of returned string.
    
    Returns:
        Value of newly formatted string
    '''
    if case:
        formatted_str = case(arg_name.replace("_", " "))
    else:
        formatted_str = arg_name.replace("_", " ")
    return formatted_str


def generate_unique_id(existing_question_ids: set) -> str:
    while True:
        new_id = str(randint(10000000, 99999999))
        if new_id not in existing_question_ids:
            existing_question_ids.add(new_id)
            return new_id