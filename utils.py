"""Common utility functions."""


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
    prompt_end = f"{main_text} {keys_with_brackets[-1]}?: "
    return prompt_end


def construct_prompt_and_keys(selection: int | dict) -> tuple[str, set[str]]:
    if isinstance(selection, int):
        valid_input_list = [str(i) for i in range(1, selection + 1)]
        prompt_end = construct_prompt_ending(valid_input_list)
        valid_keys = set(valid_input_list)
        return prompt_end, valid_keys
    else:
        valid_input_list = [v for v in selection.values()]
        prompt_end = construct_prompt_ending(valid_input_list)
        valid_keys = set(i[0].lower() for i in valid_input_list)
        return prompt_end, valid_keys


def get_key_int_choice_from_dict(prompt: str, target_dict: dict) -> int:
    dict_range = {i for i in range(1, len(target_dict) + 1)}
    choice = get_valid_int_response(dict_range, prompt)

    return choice


def get_user_choice_from_menu(target_dict: dict, numbered: bool=False) -> int:
    header = "\nOPTIONS:"
    if numbered:
        display_options_from_numbered_dict(header, target_dict)
    else:
        display_options_from_dict(header, target_dict)

    prompt = "What would you like to do?: "
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