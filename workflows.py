"""Workflows that orchastrate all of the domain and UI logic"""


from constants import (
    STRINGS as S,
    INTS,
    QUESTION_STATUSES
)
from models import (
    Player,
    Question
)
from pdfgen import generate_pdf
from session import Session
from typing import Callable
from types import ModuleType
from xai import generate_questions
import storage

# ======================
# CUSTOM EXCEPTIONS
# ======================

class NoSelection(Exception):
    """Raised when there's nothing for the user to pick."""


# ======================
# USER CHOICES & MENUS
# ======================


def _get_user_choice_of_existing_players(session: Session, ui: ModuleType, filter: Callable | None=None) -> Player:
    player_dict = session.playername_player_dict(filter=filter)
    if player_dict:
        player_name = ui.get_user_str_choice_from_menu(
            player_dict,
            header="\nPLAYERS",
            prompt="Which player would you like to pick?: "
        )
        player = player_dict[player_name]
        return player
    ui.display_msg("No available players to choose from.")
    raise NoSelection
    

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
            S.ASSIGN_NEW_QUESTIONS_TO_PLAYER: lambda: start_new_run_for_player(session, ui),
            S.PRINT_QUESTIONS: lambda: generate_question_pdf(session, ui),
            S.DISPLAY_QUESTIONS_FOR_PLAYER: lambda: display_questions_for_player(session, ui),
            S.DELETE_QUESTIONS_FOR_PLAYER: lambda: delete_question(session, ui),
            S.EDIT_QUESTION_STATUS: lambda: edit_question_status(session, ui),
            S.BACK: back
        },
        S.MANAGE_SCORES: {
            S.VIEW_SCORES: lambda: view_scores(session, ui),
            S.DELETE_SCORE_HISTORY: lambda: delete_score_history(session, ui),
            S.BACK: back
        },
        S.ANSWER_QUESTIONS: {
            S.MULTIPLE_CHOICE: lambda: play_game(session, ui, is_ask_answer=False),
            S.ASK_AND_ANSWER: lambda: play_game(session, ui, is_ask_answer=True),
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
                try:
                    running = main_menu[choice][sub_choice]()
                except (NoSelection, ui.ManualAbort):
                    running = True
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
    if session.has_qbank(player) or player.total_questions_answered > 0:
        warning_prompt = "Deleting this player will cause all score history to be deleted."
        ui.warn_user(warning_prompt)
    session.remove_player(player)
    ui.display_msg(f'\nPlayer "{player.name}" Removed')
    return True


def view_players(session: Session, ui: ModuleType) -> bool:
    if session.existing_players:
        for index, player in enumerate(session.existing_players):
            ui.display_attributes_for_object(
                header="PLAYER",
                seq_number=index + 1,
                name=player.name,
                age=player.years_old, 
                questions_assigned=session.has_qbank(player)
            )
    else:
        ui.display_msg("No availiable players to view")
    return True


# ======================
# QUESTION MANAGEMENT
# ======================


def start_new_run_for_player(session: Session, ui: ModuleType) -> bool:
    player = _get_user_choice_of_existing_players(session, ui)
    if session.has_qbank(player):
        warning_msg = "Assigning new questions will delete any unanswered questions."
        ui.warn_user(warning_msg)
    cat = ui.get_user_str_input("What category should the questions be about?: ")
    r_length = ui.get_user_int_input(INTS[S.MAX_QUESTIONS], f"How many questions should be generated (1-{INTS[S.MAX_QUESTIONS]})?: ")
    existing_question_ids = session.all_existing_question_ids()
    question_bank = generate_questions(session.client, player.age_bucket, cat, r_length, existing_question_ids)
    session.process_new_qbank(player, question_bank)
    return True


def generate_question_pdf(session: Session, ui: ModuleType) -> bool:
    player = _get_user_choice_of_existing_players(session, ui, filter=session.has_qbank)
    question_bank = session.get_qbank(player)
    generate_pdf(player.name, question_bank.question_id_list(), question_bank.category)
    return True


def display_questions_for_player(session: Session, ui: ModuleType) -> bool:
    player = _get_user_choice_of_existing_players(session, ui, filter=session.has_qbank)
    question_bank = session.get_qbank(player)
    for index, question in enumerate(question_bank.question_list):
        ui.display_attributes_for_object(
            header="QUESTION",
            seq_number=index + 1,
            question=question.question,
            answer=question.answer, 
            fake_answers=question.fake_answers,
            status=question.status
        )
    return True


def delete_question(session: Session, ui: ModuleType) -> bool:
    player = _get_user_choice_of_existing_players(session, ui, filter=session.has_qbank)
    question_bank = session.get_qbank(player)
    question_map = question_bank.question_content_map()
    question_content = ui.get_user_str_choice_from_menu(question_map, prompt="Which question would you like to select?: ")
    question = question_bank.retrieve_question_by_content(question_content)
    question_bank.remove_question(question)
    ui.display_msg(f'Question removed.')
    return True


def edit_question_status(session: Session, ui: ModuleType) -> bool:
    player = _get_user_choice_of_existing_players(session, ui, filter=session.has_qbank)
    question_bank = session.get_qbank(player)
    question_map = question_bank.question_content_map()
    question_content = ui.get_user_str_choice_from_menu(question_map, prompt="Which question ststus would you like to edit?: ")
    new_status = ui.get_user_str_choice_from_menu(QUESTION_STATUSES, numbered=True, prompt="Which status would you like to select?: ")
    question = question_bank.retrieve_question_by_content(question_content)
    old_status = question.status
    question.status = new_status
    player.adjust_attempt(old_status, new_status)
    return True


# ======================
# SCORE MANAGEMENT
# ======================

def view_scores(session: Session, ui: ModuleType) -> bool:
    player = _get_user_choice_of_existing_players(session, ui)
    if session.has_qbank(player):
        qbank = session.get_qbank(player)
        total, correct, attempted = qbank.score()
        ui.display_attributes_for_object(
            "CURRENT QUESTION SET",
            questions_assigned=total,
            questions_attempted=attempted,
            question_answered_correctly=correct
        )
    ui.display_attributes_for_object(
        "ALL TIME SCORES",
        total_question_attempted=player.total_questions_answered,
        total_question_answered_correctly=player.total_questions_correctly_answered
    )
    return True


def delete_score_history(session: Session, ui: ModuleType) -> bool:
    player = _get_user_choice_of_existing_players(session, ui)
    if player.total_questions_answered > 0:
        warning_msg = f"Deleting score history will delete score history for all questions ever assigned to {player.name}"
        ui.warn_user(warning_msg)
    player.total_questions_answered = 0
    player.total_questions_correctly_answered = 0
    return True


# ======================
# GAME LOGIC
# ======================

def _evaluate_answer(question: Question, ui: ModuleType, is_ask_answer: bool) -> bool:
    question_content = question.question
    answer = question.answer
    if is_ask_answer:
        is_correct = ui.prompt_ask_answer(question_content, answer)
    else:
        all_answers = question.all_choices_shuffled()
        user_answer: str = ui.prompt_multiple_choice_answer(question_content, all_answers)
        is_correct = question.check_answer(user_answer)
    question.update_status(is_correct)
    return is_correct


def play_game(session: Session, ui: ModuleType, is_ask_answer: bool) -> bool:
    question_dict = session.all_question_id_to_question_dict()
    player_dict = session.all_question_id_to_player_dict()

    running = True
    while running:
        if not question_dict:
            ui.display_msg("\nNo available questions")
            break
        scanned_id = ui.get_scanned_id() #will raise ManualAbort if user selects to exit game
        if scanned_id in question_dict:
            question = question_dict[scanned_id]
            is_correct = _evaluate_answer(question, ui, is_ask_answer)
            player = player_dict[scanned_id]
            player.record_attempt(is_correct)
            question_dict.pop(scanned_id)
        else:
            ui.display_msg(
                "\n Question has either already been scanned, overwritten, or deleted."
                "Please try different barcode."
            )
        storage.save_session(session.existing_players, session.player_id_to_question_bank_lookup)
    return True