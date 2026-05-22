"""All functions that print to the CLI and inputs from user"""


from constants import (
    STRINGS as S,
    RANGES
)
from datetime import date
from utils import (
    display_options_from_dict,
    display_options_from_numbered_dict,
    get_key_int_choice_from_dict,
    get_unique_alpha_response,
    get_valid_int_response,
    days_in_month,
    get_yes_no_response,
    format_info
)

def greet_user() -> None:
    print("Hello! Welcome to The Inquisitor!. Here's how the game works.....")


def display_msg(msg: str) -> None:
    print(msg)


def warn_user(warning_msg: str) -> bool:
    """Present the player with a warning and return their response as a bool.
    Warning will be formatted as follows:

    ======================
    WARNING: {warning_msg}
    ======================
    Would you like to proceed [Y] or [N]?: 

    Returns
    True
    if player selects yes ("y"). False: if player selects no ("n").
    """
    total_warning = f"WARNING: {warning_msg}"
    msg_length = len(total_warning)
    print(
        "=" * msg_length,
        total_warning,
        "=" * msg_length,
        sep="\n"
    )
    return get_yes_no_response("Would you like to proceed")


def get_user_str_choice_from_menu(target_dict: dict, numbered: bool=False, header="\nOPTIONS", prompt="What would you like to do?: ") -> str:
    if numbered:
        display_options_from_numbered_dict(header, target_dict)
        new_dict = target_dict
    else:
        display_options_from_dict(header, target_dict)
        new_dict = {(index + 1): k for index, k in enumerate(target_dict)}

    int_choice = get_key_int_choice_from_dict(prompt, target_dict)
    str_choice = new_dict[int_choice]
    
    return str_choice


def get_player_name(existing_names: set[str]) -> str:
    prompt = "\nWhat should the player be called?: "
    name = get_unique_alpha_response(existing_names, prompt, str.title)
    return name


def get_birth_date(player_name: str) -> date:
    """Prompt for year, month, day. Validates each piece and confirms the date is real."""
    while True:
        year = get_valid_int_response(
            RANGES[S.BIRTH_YEAR_RANGE],
            f"\nWhat year was {player_name} born? ({min(RANGES[S.BIRTH_YEAR_RANGE])}-{max(RANGES[S.BIRTH_YEAR_RANGE])}): "
        )
        month = get_valid_int_response(
            RANGES[S.VALID_MONTHS],
            f"What month? (1-12): "
        )
        max_day = days_in_month(year, month)
        day = get_valid_int_response(
            set(range(1, max_day + 1)),
            f"What day? (1-{max_day}): "
        )
        try:
            return date(year, month, day)
        except ValueError:
            print("That's not a valid date. Let's try again.")


def _format_presented_info(**kwargs: str | int | bool) -> tuple[list[tuple[str, str]], int]:
    """Returns argument names and values for printing, 
    adjusted onto the colon for the longest argument name.
    return is a tuple of a list of tuples and an int ready for printing

    Example tuple:
    _format_presented_info(player_name="blanton", player_age=3) will return:
    [("Player Name: ", "Blanton"), ("Player Age: ", "10")]
    """
    max_front_str_length = 0
    front_str_list: list[str] = []
    for kwarg in kwargs:
        new_str = format_info(kwarg)
        front_str_list.append(new_str)
        str_length = len(new_str)
        if str_length > max_front_str_length:
            max_front_str_length = str_length
    back_str_list = [str(v) for v in kwargs.values()]
    full_str_list = list(zip(front_str_list, back_str_list))
    return full_str_list, max_front_str_length
    


def display_attributes_for_object(header: str, seq_number: int, **kwargs: str | int | bool) -> None:
    """Prints a formatted block of information to the screen 
    for a given header and any number of given keyword args. 

    Kwargs should be given in the following format to achieve the subsequent example
    Kwargs:
    (player_name="blanton", age=3)

    Example format:
    ====== HEADER ======
    Player Name: Blanton
            Age: 10
    """
    header_length = len(header)
    full_str_list, max_front_str_length = _format_presented_info(**kwargs)
    for (f, b) in full_str_list:
        l = len(f + b)
        if l > header_length:
            header_length = l

    equal_int = (header_length - len(header) - 2)//2 # subrtact two for extra spaces and index number
    if (header_length - len(f" {header} "))%2 == 0:
        print(f"{"=" * equal_int} {header.capitalize()} {seq_number} {"=" * equal_int}")
    else:
        print(f"{"=" * equal_int} {header.capitalize()}: {seq_number} {"=" * equal_int}")
    for f, b in full_str_list:
        print(f"{" " * (max_front_str_length - len(f))}{f}: {b}")