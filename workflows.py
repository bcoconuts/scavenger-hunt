"""Workflows that orchastrate all of the domain and UI logic"""


from constants import STRINGS as S
from session import Session
from models import Player
import cli
import storage
from typing import Callable

UI=cli

# ======================
# USER CHOICES & MENUS
# ======================


def _get_user_choice_of_existing_players(session: Session, ui, filter: Callable[[Player], bool] | None=None) -> Player | None:
    player_dict = session.playername_player_dict(filter=filter)
    player = ui.get_specific_player(player_dict)
    return player
        

def route_menu_actions(session: Session, ui) -> None:
    S.MAIN_MENU = {
        S.MANAGE_PLAYERS: {
            S.ADD_PLAYER: add_player,
            S.EDIT_PLAYER: edit_player,
            S.REMOVE_PLAYER: remove_player,
            S.VIEW_PLAYERS: view_players,
            S.BACK: back
        },
        S.MANAGE_QUESTIONS: {
            S.ASSIGN_NEW_QUESTIONS_TO_PLAYER: start_new_run_for_player,
            S.PRINT_QUESTIONS: generate_question_pdf,
            S.DISPLAY_QUESTIONS_FOR_PLAYER: display_questions_for_player,
            S.DELETE_QUESTIONS_FOR_PLAYER: delete_question,
            S.EDIT_QUESTION_STATUS: edit_question_status,
            S.BACK: back
        },
        S.MANAGE_SCORES: {
            S.VIEW_SCORES: view_scores,
            S.DELETE_CURRENT_QUESTIONS_SCORE_HISTORY: delete_current_run_score_history,
            S.DELETE_ALL_SCORE_HISTORY: delete_all_score_history,
            S.BACK: back
        },
        S.ANSWER_QUESTIONS: {
            S.MULTIPLE_CHOICE: lambda: run_game_loop(is_ask_answer=False),
            S.ASK_AND_ANSWER: lambda: run_game_loop(is_ask_answer=True),
            S.BACK: back
        },
        S.EXIT: exit
    }
    
    main_running = True
    while main_running:
        choice = ui.get_user_str_choice_from_menu(S.MAIN_MENU, header=f"\n{S.MAIN_MENU}")
        if choice == S.EXIT:
            main_running = S.MAIN_MENU[choice]()
        else:
            running = True
            while running:
                sub_choice = ui.get_user_str_choice_from_menu(S.MAIN_MENU[choice], header=f"\n{choice}")
                running = S.MAIN_MENU[choice][sub_choice]()
                if choice != S.ANSWER_QUESTIONS:
                    storage.save_session(session.existing_players, session.player_id_to_question_bank_lookup)


def back():
    """Returns False to break out of the current submenu loop."""
    return False


def exit():
    """Returns False to break out of the main menu loop."""
    return False


# ======================
# PLAYER MANAGEMENT
# ======================


def edit_player(session: Session, ui) -> bool:
    player = _get_user_choice_of_existing_players(session, ui)
    if player is None:
        ui.display_msg("No available players to choose from")
        return False
    existing_names = session.player_name_set()
    if existing_names is None:
        ui.display_msg("Error: Players exist, but Player name cannot be accessed. "
        "Manually record player scores, then delete and re-add player")
        return False
    existing_names.remove(player.name)
    new_name = ui.get_player_name(existing_names)
    player.name = new_name
    new_birth_date = ui.get_birth_date(player)
    player.birth_date = new_birth_date
    return True