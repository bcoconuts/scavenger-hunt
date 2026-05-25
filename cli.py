"""All functions that print to the CLI and inputs from user"""

from constants import (
    STRINGS as S,
    RANGES,
    YES_NO_DICT
)
from datetime import date
from utils import (
    days_in_month,
    display_options_from_dict,
    display_options_from_numbered_dict,
    format_info,
    get_key_int_choice_from_dict,
    get_unique_alpha_response,
    get_valid_int_response,
    get_yes_no_response
)


class ManualAbort(Exception):
    """Raised when the user stops based on a warning"""


def greet_user() -> None:
    print("Hello! Welcome to The Inquisitor!. Here's how the game works.....")


def display_msg(msg: str) -> None:
    print(f"\n{msg}")


def get_user_str_input(prompt: str) -> str:
    response = input(f"\n{prompt}").strip()
    return response


def get_user_int_input(max_choice: int, prompt: str, min_choice: int=1) -> int:
    valid_choices = {num for num in range(min_choice, max_choice + 1)}
    response = get_valid_int_response(valid_choices, prompt)
    return response


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
        "\n",
        "=" * msg_length,
        total_warning,
        "=" * msg_length,
        sep="\n"
    )
    if get_yes_no_response("Would you like to proceed"):
        return True
    else:
        display_msg("Operation Aborted.")
        raise ManualAbort


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


def get_user_value_choice_from_key_menu(target_dict: dict, header="\nOPTIONS", prompt="What would you like to do?: ") -> str:
    display_options_from_dict(header, target_dict)
    new_dict = {(index + 1): k for index, k in enumerate(target_dict)}
    int_choice = get_key_int_choice_from_dict(prompt, target_dict)
    str_choice = new_dict[int_choice]
    value_choice = target_dict[str_choice]
    
    return value_choice


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
    


def display_attributes_for_object(header: str, seq_number: int | None=None, **kwargs: str | int | bool) -> None:
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
        h_length = len(f"{" " * (max_front_str_length - len(f))}{f}: {b}")
        if h_length > header_length:
            header_length = h_length
    
    header = " " + header.capitalize() # add 2 for spacing around header
    if not seq_number:
        object_num_holder = " "
        equal_int = (header_length - len(header))//2
        if (header_length - len(header))%2 == 0:
            print(f"\n{"=" * equal_int}{header}{object_num_holder}{"=" * (equal_int - 1)}")
        else:
            print(f"\n{"=" * equal_int}{header}{object_num_holder}{"=" * equal_int}")
    else:
        object_num_holder = ": " + str(seq_number) + " "
        equal_int = (header_length - len(header) - 4)//2
        if (header_length - len(header))%2 == 0:
            print(f"\n{"=" * equal_int}{header}{object_num_holder}{"=" * (equal_int)}")
        else:
            print(f"\n{"=" * equal_int}{header}{object_num_holder}{"=" * (equal_int + 1)}")

    for f, b in full_str_list:
        print(f"{" " * (max_front_str_length - len(f))}{f}: {b}")


def get_scanned_id() -> str:
    scanned_id = input("\nPlease Scan Barcode (Enter 'F' to quit): ").strip()
    if scanned_id.upper() == "F":
        raise ManualAbort
    return scanned_id


def prompt_ask_answer(question_content: str, answer: str) -> bool:
    prompt = "Was the question answered correctly?: "
    choice = get_user_str_choice_from_menu(YES_NO_DICT, numbered=True, header=f"\n{question_content} [Answer: {answer}]", prompt=prompt)
    if choice == S.YES:
        return True
    else:
        return False
    

def prompt_multiple_choice_answer(question_content: str, all_answers: list[str]) -> str:
    answer_dict = {index + 1: a for index, a in enumerate(all_answers)}
    prompt = f"What is your answer (1-{len(all_answers)})?: "
    answer = get_user_str_choice_from_menu(answer_dict, numbered=True, header=f"\n{question_content}", prompt=prompt)
    return answer