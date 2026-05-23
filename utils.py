"""Common utility functions."""

from calendar import monthrange
from typing import Callable
from random import randint



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


def construct_prompt_ending(keys: list[str]) -> str:
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


def get_key_int_choice_from_dict(prompt: str, target_dict: dict) -> int:
    dict_range = {i for i in range(1, len(target_dict) + 1)}
    choice = get_valid_int_response(dict_range, prompt)

    return choice


def get_user_int_choice_from_menu(target_dict: dict, numbered: bool=False, header="\nOPTIONS", prompt="What would you like to do?: ") -> int:
    if numbered:
        display_options_from_numbered_dict(header, target_dict)
    else:
        display_options_from_dict(header, target_dict)

    choice = get_key_int_choice_from_dict(prompt, target_dict)
    
    return choice


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
    prompt_end = construct_prompt_ending(options)
    full_prompt = prompt + prompt_end
    choice = get_valid_str_response(set(options), full_prompt)
    if choice == 'y':
        return True
    else:
        return False
    

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