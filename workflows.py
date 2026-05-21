"""Workflows that orchastrate all of the domain and UI logic"""


from constants import STRINGS as S
import session


    # ======================
    # USER CHOICES & MENUS
    # ======================




def _get_user_choice_of_existing_players(players_have_qbank=False) -> Player:
    players = 
    return cli.get_specific_player(player_dict)

def route_menu_actions(self) -> None:
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
        choice = get_user_str_choice_from_menu(S.MAIN_MENU, header=f"\n{S.MAIN_MENU}")
        if choice == S.EXIT:
            main_running = S.MAIN_MENU[choice]()
        else:
            running = True
            while running:
                sub_choice = get_user_str_choice_from_menu(S.MAIN_MENU[choice], header=f"\n{choice}")
                running = S.MAIN_MENU[choice][sub_choice]()
                if choice != S.ANSWER_QUESTIONS:
                    storage.save_session(self.existing_players, self.player_id_to_question_bank_lookup)

def back():
    """Returns False to break out of the current submenu loop."""
    return False

def exit():
    """Returns False to break out of the main menu loop."""
    return False
