"""Command-line interface: all terminal printing and input collection.

This is the CLI implementation of the "ui" layer that workflows depend on.
Every print() and input() call in the program lives here (or in the input
helpers it calls from utils). Functions take plain data and return plain
data; they know nothing about Session or the domain collections. A future
gui.py would expose the same function names with the same signatures so the
workflows could drive either interface unchanged.
"""

from constants import (
    STRINGS as S,
    RANGES,
    YES_NO_DICT
)
from datetime import date
from utils import (
    days_in_month,
    format_info,
)


# ======================
# CUSTOM EXCEPTIONS
# ======================

class ManualAbort(Exception):
    """Raised when the user stops based on a warning"""


# ======================
# HELPERS
# ======================

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


def _construct_prompt_ending(keys: list[str]) -> str:
    keys_with_brackets = [
        f"[{i[0].upper()}]{i[1:]}" if len(i) > 1 else f"[{i.upper()}]" for i in keys
    ]
    main_text = ", ".join(keys_with_brackets[:-1])
    if len(keys_with_brackets) == 2:
        main_text = main_text + " or"
    elif len(keys_with_brackets) > 2:
        main_text = main_text + ", or"
    prompt_end = f" {main_text} {keys_with_brackets[-1]}?: "
    return prompt_end


# ======================
# SPECIFIC OUTPUT TO CLI
# ======================

def greet_user() -> None:
    print("Hello! Welcome to The Inquisitor!. Here's how the game works.....")


# ======================
# GENERIC OUTPUT TO CLI
# ======================

def display_msg(msg: str) -> None:
    print(f"\n{msg}")


def display_options_from_numbered_dict(header: str, target_dict: dict[int, str]) -> None:
    '''
    Display options to user for a dict formatted {Option Number: Option Name}.

    Args:
        header: Header to be displayed prior to options list being displayed.
        target_dict: Dict from which options will be derived.    
    '''
    print(header)
    for k, v in target_dict.items():
        print(f"    {k}. {v}")


def display_options_from_dict(header: str, target_dict: dict) -> None:
    '''
    Display options to user for a dict formatted with options stored as keys.

    Args:
        header: Header to be displayed prior to options list being displayed.
        target_dict: Dict from which options will be derived.    
    '''
    print(header)
    for index, key in enumerate(target_dict):
        print(f"    {index + 1}. {key}")


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


# ======================
# SPECIFIC I/O
# ======================

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


def get_key_int_choice_from_dict(prompt: str, target_dict: dict) -> int:
    dict_range = {i for i in range(1, len(target_dict) + 1)}
    choice = get_valid_int_response(dict_range, prompt)

    return choice


# ======================
# GENERIC I/O
# ======================

def get_user_str_input(prompt: str) -> str:
    response = input(f"\n{prompt}").strip()
    return response


def get_user_int_input(max_choice: int, prompt: str, min_choice: int=1) -> int:
    valid_choices = {num for num in range(min_choice, max_choice + 1)}
    response = get_valid_int_response(valid_choices, prompt)
    return response


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


def get_yes_no_response(prompt: str) -> bool:
    '''
    Present the player with a prompt and return their response as a bool

    Args:
        prompt: The prompt the user is presented with to evoke an input. Given prompt will be modified to end with " [Y] or [N]?: "

    Returns:
        True: if player selects yes ("y").
        False: if player selects no ("n").
    '''
    options = ["y", "n"]
    prompt_end = _construct_prompt_ending(options)
    full_prompt = prompt + prompt_end
    choice = get_valid_str_response(set(options), full_prompt)
    if choice == 'y':
        return True
    else:
        return False


def get_valid_str_response(valid_choices: set[str], prompt: str, case=str.lower) -> str:
    '''
    Ensure a valid string is returned from the user's input.

    Args:
        valid_choices: A set of strings, of which the user must match their
            input exactly with any in the set.
        prompt: The prompt the user is presented with to evoke an input.
        case: A string method used to normalize user input before comparison.
            Defaults to str.lower. Pass str.upper or str.title to change
            normalization behavior.

    Returns:
        Value of the users valid input.
    '''
    while True:
        response = case(input(prompt).strip())
        if response not in valid_choices:
            print("Invalid Input.")
        else:
            return response


def get_valid_int_response(valid_choices: set[int], prompt: str) -> int:
    '''
    Ensure a valid int is returned from the user's input.

    Args:
        valid_choices: A set of ints, of which the user must match their
            input exactly with any in the set.
        prompt: The prompt the user is presented with to evoke an input.

    Returns:
        Value of the users valid input.
    '''
    while True:
        try:
            response = int(input(prompt).strip())
            if response not in valid_choices:
                print("Invalid Input.")
            else:
                return response
        except ValueError:
            print("Invalid Input. Input must an integer only within the range specified. No alphabetical or special chars.")


def get_unique_alpha_response(invalid_choices: set, prompt: str, case=str.lower) -> str:
    '''
    Ensure a unique alphabetical string is returned from the user's input.

    Args:
        invalid_choices: A set of strings, of which the user must not match their
            input with any in the set.
        prompt: The prompt the user is presented with to evoke an input.
        case: A string method used to normalize user input before comparison.
            Defaults to str.lower. Pass str.upper or str.title to change
            normalization behavior.

    Returns:
        Value of the users unique input.
    '''
    unique_error_msg = "Already Taken."
    alpha_error_msg = "Must be alphabetical only. No numbers or special chars."
    while True:
        response = case(input(prompt).strip())
        if not response.isalpha():
            print(alpha_error_msg)
        elif response in invalid_choices:
            print(unique_error_msg)
        else:
            return response