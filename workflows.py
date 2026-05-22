"""Workflows that orchastrate all of the domain and UI logic"""


from constants import STRINGS as S
from session import Session
from models import Player
import storage
from typing import Callable
from types import ModuleType

# ======================
# USER CHOICES & MENUS
# ======================


def _get_user_choice_of_existing_players(session: Session, ui: ModuleType, filter: Callable[[Player], bool] | None=None) -> Player:
    player_dict = session.playername_player_dict(filter=filter)
    player_name = ui.get_user_str_choice_from_menu(
        player_dict,
        header="\nPLAYERS",
        prompt="Which player would you like to pick?"
    )
    player = player_dict[player_name]
    return player
        

def route_menu_actions(session: Session, ui: ModuleType) -> None:
    main_menu = {
        S.MANAGE_PLAYERS: {
            S.ADD_PLAYER: lambda: add_player(session, ui),
            S.EDIT_PLAYER: lambda: edit_player(session, ui),
            S.REMOVE_PLAYER: lambda: remove_player(session, ui),
            S.VIEW_PLAYERS: lambda: view_players(session, ui),
            S.BACK: back
        },
        S.MANAGE_QUESTIONS: {
            # S.ASSIGN_NEW_QUESTIONS_TO_PLAYER: start_new_run_for_player,
            # S.PRINT_QUESTIONS: generate_question_pdf,
            # S.DISPLAY_QUESTIONS_FOR_PLAYER: display_questions_for_player,
            # S.DELETE_QUESTIONS_FOR_PLAYER: delete_question,
            # S.EDIT_QUESTION_STATUS: edit_question_status,
            S.BACK: back
        },
        S.MANAGE_SCORES: {
            # S.VIEW_SCORES: view_scores,
            # S.DELETE_CURRENT_QUESTIONS_SCORE_HISTORY: delete_current_run_score_history,
            # S.DELETE_ALL_SCORE_HISTORY: delete_all_score_history,
            S.BACK: back
        },
        S.ANSWER_QUESTIONS: {
            # S.MULTIPLE_CHOICE: lambda: run_game_loop(is_ask_answer=False),
            # S.ASK_AND_ANSWER: lambda: run_game_loop(is_ask_answer=True),
            S.BACK: back
        },
        S.EXIT: exit
    }
    
    main_running = True
    while main_running:
        choice = ui.get_user_str_choice_from_menu(main_menu, header=f"\n{S.MAIN_MENU}")
        if choice == S.EXIT:
            main_running = main_menu[choice]()
        else:
            running = True
            while running:
                sub_choice = ui.get_user_str_choice_from_menu(main_menu[choice], header=f"\n{choice}")
                running = main_menu[choice][sub_choice]()
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


def edit_player(session: Session, ui: ModuleType) -> bool:
    """Walk the user through editing an existing player's name and birth date.

    Returns True to remain in the submenu.
    """
    player = _get_user_choice_of_existing_players(session, ui)
    if not player:
        ui.display_msg("No available players to choose from")
        return True
    existing_names = session.player_name_set()
    existing_names.remove(player.name)
    new_name = ui.get_player_name(existing_names)
    player.name = new_name
    new_birth_date = ui.get_birth_date(player.name)
    player.birth_date = new_birth_date
    return True


def add_player(session: Session, ui: ModuleType) -> bool:
    """Walk the user through collecting a new player's name and birth date.
    Instantiates the player and passes it to Session.

    Returns True to remain in the submenu.
    """
    existing_names = session.player_name_set()
    name = ui.get_player_name(existing_names)
    birth_date = ui.get_birth_date(name)
    player = Player(birth_date=birth_date, name=name)
    session.add_player(player)
    return True


def remove_player(session: Session, ui: ModuleType) -> bool:
    """Walk the user through deleting an existing player.
    Guards against deleting players with existing questions and score hiostory.

    Returns True to remain in the submenu.
    """
    player = _get_user_choice_of_existing_players(session, ui)
    if not player:
        ui.display_msg("No available players to choose from")
        return True
    if session.has_qbank(player) or player.total_questions_answered > 0:
        warning_prompt = "Deleting this player will cause all score history to be deleted."
        if not ui.warn_user(warning_prompt):
            ui.display_msg("Player removal manually aborted. Player still exists.")
            return True
    session.remove_player(player)
    ui.display_msg(f'\nPlayer "{player.name}" Removed')
    return True


def view_players(session: Session, ui: ModuleType) -> None:
    for index, player in enumerate(session.existing_players):
        ui.display_attributes_for_object(
            header="PLAYER",
            seq_number=index + 1,
            name=player.name,
            age=player.years_old, 
            questions_assigned=session.has_qbank(player)
        )


