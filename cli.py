"""All functions that print to the CLI and inputs from user"""

from models import (
    Question,
    QuestionBank,
    Player
)
from utils import (
    display_options_from_dict,
    display_options_from_numbered_dict,
    get_key_int_choice_from_dict
)

def greet_user() -> None:
    print("Hello! Welcome to The Inquisitor!. Here's how the game works.....")


def display_msg(msg: str) -> None:
    print(msg)


def get_specific_player(player_dict: dict[str, Player]) -> Player:
    """Returns a player based on user selection of one player 
    from a given dict of player.names: players
    """
    player_prompt = "Which player would you like to select?: "
    choice = get_user_str_choice_from_menu(player_dict, header="\nPLAYERS:", prompt=player_prompt)
    player = player_dict[choice]
    return player


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