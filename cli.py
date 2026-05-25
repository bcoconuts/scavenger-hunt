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
    """Raised to abort the current action: a declined warning, or 'F' to quit a game.

    Caught by the menu loop, which treats it as 'cancel and stay in the menu'.
    """


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
    """Build a bracketed choice suffix from option keys, e.g. ' [Y] or [N]?: '.

    Each key gets its first letter bracketed; keys are joined with commas and a
    trailing 'or' so the result reads naturally at the end of a prompt.
    """
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
    """Print the welcome banner shown once at program start."""
    print(
        "\nWelcome to THE INQUISITOR — a scavenger hunt made of trivia.\n"
        "Add players, generate their questions, print and hide the barcodes, "
        "then scan them to play. Find 'em all and answer 'em all.\n"
    )


# ======================
# GENERIC OUTPUT TO CLI
# ======================

def display_msg(msg: str) -> None:
    """Print a message to the user, preceded by a blank line for spacing."""
    print(f"\n{msg}")


def display_options_from_numbered_dict(header: str, target_dict: dict[int, str]) -> None:
    """Print a header then each option from a {number: label} dict as 'number. label'."""
    print(header)
    for k, v in target_dict.items():
        print(f"    {k}. {v}")


def display_options_from_dict(header: str, target_dict: dict) -> None:
    """Print a header then number each of the dict's keys for selection."""
    print(header)
    for index, key in enumerate(target_dict):
        print(f"    {index + 1}. {key}")


def display_attributes_for_object(header: str, seq_number: int | None=None, **kwargs: str | int | bool) -> None:
    """Print a formatted, aligned block of label: value lines under a header.

    Labels come from the keyword argument names (underscores become spaces,
    title-cased) and are right-aligned on the colon. If seq_number is given it
    appears in the header, for numbering items in a list.

    Example:
        display_attributes_for_object("PLAYER", 1, player_name="Blanton", age=10)
        ===== Player: 1 ====
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
    """Prompt for a unique, alphabetic player name and return it title-cased.

    Re-prompts until the name is alphabetic and not already in existing_names.
    """
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
    """Read one scanned barcode (or typed id) and return it.

    The USB scanner acts as a keyboard, so this is a plain input(). Entering
    'F' raises ManualAbort to quit the game loop.
    """
    scanned_id = input("\nPlease Scan Barcode (Enter 'F' to quit): ").strip()
    if scanned_id.upper() == "F":
        raise ManualAbort
    return scanned_id


def prompt_ask_answer(question_content: str, answer: str) -> bool:
    """Show the question and its answer to a parent; return whether the child was right.

    Used in ask-and-answer mode, where an adult judges the spoken answer.
    """
    prompt = "Was the question answered correctly?: "
    choice = get_user_str_choice_from_menu(YES_NO_DICT, numbered=True, header=f"\n{question_content} [Answer: {answer}]", prompt=prompt)
    if choice == S.YES:
        return True
    else:
        return False
    

def prompt_multiple_choice_answer(question_content: str, all_answers: list[str]) -> str:
    """Show the question with numbered choices; return the selected answer text."""
    answer_dict = {index + 1: a for index, a in enumerate(all_answers)}
    prompt = f"What is your answer (1-{len(all_answers)})?: "
    answer = get_user_str_choice_from_menu(answer_dict, numbered=True, header=f"\n{question_content}", prompt=prompt)
    return answer


def get_key_int_choice_from_dict(prompt: str, target_dict: dict) -> int:
    """Prompt for an integer in 1..len(target_dict) and return it.

    The valid range is derived from the dict's size, for picking a numbered option.
    """
    dict_range = {i for i in range(1, len(target_dict) + 1)}
    choice = get_valid_int_response(dict_range, prompt)

    return choice


# ======================
# GENERIC I/O
# ======================

def get_user_str_input(prompt: str) -> str:
    """Prompt the user and return their stripped text response."""
    response = input(f"\n{prompt}").strip()
    return response


def get_user_int_input(max_choice: int, prompt: str, min_choice: int=1) -> int:
    """Prompt for an integer within [min_choice, max_choice] and return it.

    Re-prompts until the input is a valid integer in range.
    """
    valid_choices = {num for num in range(min_choice, max_choice + 1)}
    response = get_valid_int_response(valid_choices, prompt)
    return response


def get_user_str_choice_from_menu(target_dict: dict, numbered: bool=False, header="\nOPTIONS", prompt="What would you like to do?: ") -> str:
    """Display a menu and return the chosen key as a string.

    If numbered is True, target_dict is treated as {number: label} and the chosen
    label is returned. Otherwise the dict's keys are listed and the chosen key is
    returned. Re-prompts until a valid number is entered.
    """
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
    """Display a menu of the dict's keys and return the chosen key's value.

    Like get_user_str_choice_from_menu, but resolves the selection to the value
    behind it. Used to show questions by text while returning the question_id.
    """
    display_options_from_dict(header, target_dict)
    new_dict = {(index + 1): k for index, k in enumerate(target_dict)}
    int_choice = get_key_int_choice_from_dict(prompt, target_dict)
    str_choice = new_dict[int_choice]
    value_choice = target_dict[str_choice]
    
    return value_choice


def warn_user(warning_msg: str) -> bool:
    """Display a boxed warning and require confirmation before continuing.

    Prints the warning framed in '=' lines, then asks the user to proceed.
    Returns True if they confirm. If they decline, prints an abort notice and
    raises ManualAbort, which the menu loop catches to cancel the action.

    Formatted as:
        ======================
        WARNING: {warning_msg}
        ======================
        Would you like to proceed [Y] or [N]?:
    """
    total_warning = f"WARNING: {warning_msg}"
    msg_length = len(total_warning)
    print(
        "",
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
    """Ask a yes/no question and return True for yes, False for no.

    The prompt is given a ' [Y] or [N]?: ' suffix and re-asked until the user
    enters y or n.
    """
    options = ["y", "n"]
    prompt_end = _construct_prompt_ending(options)
    full_prompt = prompt + prompt_end
    choice = get_valid_str_response(set(options), full_prompt)
    if choice == 'y':
        return True
    else:
        return False


def get_valid_str_response(valid_choices: set[str], prompt: str, case=str.lower) -> str:
    """Prompt until the user's response (normalized by case) is in valid_choices.

    case is a string method applied before comparison (default str.lower); pass
    str.upper or str.title to change normalization.
    """
    while True:
        response = case(input(prompt).strip())
        if response not in valid_choices:
            print("Invalid Input.")
        else:
            return response


def get_valid_int_response(valid_choices: set[int], prompt: str) -> int:
    """Prompt until the user enters an integer that is in valid_choices.

    Re-prompts on non-integer input or values outside the allowed set.
    """
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
    """Prompt until the response is alphabetic and not already in invalid_choices.

    case normalizes the input before the uniqueness check (default str.lower).
    """
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