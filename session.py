"""
Session class for scavanger hunt that manages data models
"""

import cli
import os
import storage
from constants import (
    STRINGS as S,
)
from datetime import date
from dotenv import load_dotenv
from models import (
    Question,
    QuestionBank,
    Player
)
from pdfgen import generate_pdf
from typing import Callable
from utils import (
    get_unique_alpha_response,
    get_valid_int_response,
    get_user_str_choice_from_menu,
    get_yes_no_response
)
from xai_sdk import Client


class Session:
   
    # ======================
    # INITIALIZATION
    # ======================

    def __init__(self):
        load_dotenv()
        self.client: Client = Client(api_key=os.getenv("XAI_API_KEY"))
        self.existing_players: list[Player] = []
        self.existing_qbanks: list[QuestionBank] = []
        self.player_id_to_question_bank_lookup: dict[str, QuestionBank] = {} # Player.player_id -> QuestionBank.


    # ======================
    # USER CHOICES & MENUS
    # ======================

    def has_qbank(self, player: Player) -> bool:
        """Predicate: does this player have questions assigned?"""
        return self.player_id_to_question_bank_lookup.get(player.player_id) is not None

    def playername_player_dict(self, filter: Callable[[Player], bool] | None=None) -> dict[str, Player] | None:
        """Return a dict of player.name: Player if any exist in existing players, else return None.
        Filterable to only build dict of players that matches filter condition.
        """
        if filter is None:
            return {p.name: p for p in self.existing_players}
        return {p.name: p for p in self.existing_players if filter(p)}
    
    def player_name_set(self, filter: Callable[[Player], bool] | None=None) -> set[str] | None:
        """Return a set of existing player names if any exist in existing players, else return None.
        Filterable to only build set of players that matches filter condition.
        """
        if filter is None:
            return {p.name for p in self.existing_players}
        return {p.name for p in self.existing_players if filter(p)}
        
    
    def route_menu_actions(self) -> None:
        S.MAIN_MENU = {
            S.MANAGE_PLAYERS: {
                S.ADD_PLAYER: self.add_player,
                S.EDIT_PLAYER: self.edit_player,
                S.REMOVE_PLAYER: self.remove_player,
                S.VIEW_PLAYERS: self.view_players,
                S.BACK: self.back
            },
            S.MANAGE_QUESTIONS: {
                S.ASSIGN_NEW_QUESTIONS_TO_PLAYER: self.start_new_run_for_player,
                S.PRINT_QUESTIONS: self.generate_question_pdf,
                S.DISPLAY_QUESTIONS_FOR_PLAYER: self.display_questions_for_player,
                S.DELETE_QUESTIONS_FOR_PLAYER: self.delete_question,
                S.EDIT_QUESTION_STATUS: self.edit_question_status,
                S.BACK: self.back
            },
            S.MANAGE_SCORES: {
                S.VIEW_SCORES: self.view_scores,
                S.DELETE_CURRENT_QUESTIONS_SCORE_HISTORY: self.delete_current_run_score_history,
                S.DELETE_ALL_SCORE_HISTORY: self.delete_all_score_history,
                S.BACK: self.back
            },
            S.ANSWER_QUESTIONS: {
                S.MULTIPLE_CHOICE: lambda: self.run_game_loop(is_ask_answer=False),
                S.ASK_AND_ANSWER: lambda: self.run_game_loop(is_ask_answer=True),
                S.BACK: self.back
            },
            S.EXIT: self.exit
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
    
    def back(self):
        """Returns False to break out of the current submenu loop."""
        return False

    def exit(self):
        """Returns False to break out of the main menu loop."""
        return False

    # ======================
    # PLAYER MANAGEMENT
    # ======================

    def add_player(self) -> None:
        fresh_player = Player(birth_date=(date.today()), name="Newplayer")
        existing_names = {p.name for p in self.existing_players}
        fresh_player.edit_player_attributes(existing_names)
        self.existing_players.append(fresh_player)

    def edit_player(self) -> None:
        if not self.existing_players:
            print("\nNo editable players.")
            return
        player = self.get_user_choice_of_existing_players()
        existing_names = {p.name for p in self.existing_players if p != player}
        player.edit_player_attributes(existing_names)

    def remove_player(self) -> None:
        if not self.existing_players:
            print("\nNo removable players.")
            return
        player = self.get_user_choice_of_existing_players()
        if self.player_id_to_question_bank_lookup[player.player_id] or player.total_questions_answered > 0:
            warning_prompt = "\nWARNING: Deleting this player will cause all score history to be deleted. Would you like to proceed "
            if not get_yes_no_response(warning_prompt):
                print("\nPlayer not deleted. User manually aborted.")
                return
        self.existing_players.remove(player)
        print(f'\nPlayer "{player.name}" Removed')

    def view_players(self) -> None:
        print()
        for index, player in enumerate(self.existing_players):
            print(f"""=== No. {index + 1} ===""")
            pass #TODO

    # ======================
    # RUN MANAGEMENT
    # ======================

    def get_category(self, player: Player) -> str:
        while True:
            category = input(f"\nWhat should the category of {player.name}'s questions be?: ").strip()
            if category:
                return category
            print("\nInvalid Input. Category must not be left blank.")
    
    def get_run_length(self, player: Player) -> int:
        prompt = f"\nHow many questions would you like to generate for {player.name}? (1 - {MAX_QUESTIONS}): "
        run_length = get_valid_int_response(VALID_QUESTION_NUMBERS, prompt)
        return run_length

    def start_new_run_for_player(self) -> None:
        if not self.existing_players:
            print("\nNo players to assign questions to.")
            return
        player = self.get_user_choice_of_existing_players()
        if self.player_id_to_question_bank_lookup[player.player_id]:
            warning_prompt = "\nWARNING: Assigning new questions will delete any unanswered questions. Would you like to proceed "
            if not get_yes_no_response(warning_prompt):
                print("\nNo questions generated. User manually aborted.")
                return
        cat = self.get_category(player)
        r_length = self.get_run_length(player)
        existing_question_ids = set()
        for qbank in self.existing_qbanks:
            for q in qbank.question_list:
                existing_question_ids.add(q.question_id)
        question_bank = generate_questions(self.client, player, cat, r_length, existing_question_ids)
        if not any(question_bank.question_list):
            print("\nQuestion generation failed. Player questions not assigned.")
            return
        self.player_id_to_question_bank_lookup[player.player_id] = question_bank
        
    def generate_question_pdf(self) -> None:
        if not any([v for v in self.player_id_to_question_bank_lookup.values()]):
            print("\nNo players available to print questions for.")
            return
        player = self.get_user_choice_of_existing_players_with_questions()
        question_bank = self.player_id_to_question_bank_lookup[player.player_id]
        pdf = generate_pdf(player, question_bank)
        pdf.output(f"{player.name}" + PDF_FILE_NAME)


    def display_questions_for_player(self) -> None:
        if not any([v for v in self.player_id_to_question_bank_lookup.values()]):
            print("\nNo players available to view questions for.")
            return
        player = self.get_user_choice_of_existing_players_with_questions()
        player.run.question_bank.display_questions() # pyright: ignore[reportOptionalMemberAccess]
    
    def delete_question(self) -> None:
        if not any([v for v in self.player_id_to_question_bank_lookup.values()]):
            print("\nNo players available to remove questions for.")
            return
        player = self.get_user_choice_of_existing_players_with_questions()
        question = player.run.question_bank.get_user_choice_of_existing_questions() # pyright: ignore[reportOptionalMemberAccess]
        player.run.question_bank.question_list.remove(question) # pyright: ignore[reportOptionalMemberAccess]
        self.q_p_lookup.pop(question.id)
        if not player.run.question_bank.question_list: # pyright: ignore[reportOptionalMemberAccess]
            player.run = None
        print(f'\nQuestion removed.')
    
    def edit_question_status(self) -> None:
        if not any([v for v in self.player_id_to_question_bank_lookup.values()]):
            print("\nNo players available to edit question statuses for.")
            return
        player = self.get_user_choice_of_existing_players_with_questions()
        question = player.run.question_bank.get_user_choice_of_existing_questions() # pyright: ignore[reportOptionalMemberAccess]
        question.edit_status()

    # ======================
    # GAME LOOP
    # ======================

    def generate_eligible_question_dict(self) -> dict[str, Question]:
        question_list_list = [p.run.question_bank.question_list for p in self.existing_players if p.run] # pyright: ignore[reportOptionalMemberAccess]
        eligible_question_dict = {q.id: q for ls in question_list_list for q in ls if q.status == UNANSWERED}
        return eligible_question_dict
    
    def generate_eligible_player_dict(self) -> dict[str, Player]:
        eligible_player_dict = {p.id: p for p in self.existing_players if p.run}
        return eligible_player_dict

    def _evaluate_answer(self, question: Question, player: Player, ask_answer_flag: bool) -> None:
        if ask_answer_flag:
            user_answer_bool: bool = question.get_user_choice_of_ask_answer_question()
        else:
            user_answer: str = question.get_user_choice_of_mult_choice_question()
        if ask_answer_flag and user_answer_bool:
            question.status = CORRECTLY_ANSWERED
            self.update_scores(player, correct_flag=True)
            print("\nCongratulations!")
        elif ask_answer_flag and not user_answer_bool:
            question.status = INCORRECTLY_ANSWERED
            self.update_scores(player, correct_flag=False)
            print(f"\nBetter luck with the next one!")
        elif question.answer == user_answer:
            question.status = CORRECTLY_ANSWERED
            self.update_scores(player, correct_flag=True)
            print("\nCorrect!")
        else:
            question.status = INCORRECTLY_ANSWERED
            self.update_scores(player, correct_flag=False)
            print(f"\nIncorrect.\nCorrect answer: {question.answer}")

    def _run_game_logic(self, eligible_question_dict: dict[str, Question], eligible_player_dict: dict[str, Player], ask_answer_flag: bool) -> bool:
        scanned_id = input("\nPlease Scan Barcode (Enter 'F' to quit): ").strip()
        if scanned_id.upper() == "F":
            return False
        elif scanned_id in eligible_question_dict:
            question = eligible_question_dict[scanned_id]
            player_id = self.q_p_lookup[question.id]
            player = eligible_player_dict[player_id]
            self._evaluate_answer(question, player, ask_answer_flag)
            eligible_question_dict.pop(scanned_id)
        else:
            print("\nQuestion not found. Question may have already been answered or from an older question set. Please scan a new question.")
        return True

    def run_game_loop(self, ask_answer_flag: bool) -> None:
        eligible_question_dict = self.generate_eligible_question_dict()
        eligible_player_dict = self.generate_eligible_player_dict()
        running = True
        while running:
            if not eligible_question_dict:
                print("\nNo available questions")
                return
            running = self._run_game_logic(eligible_question_dict, eligible_player_dict, ask_answer_flag)
            save_session(self.existing_players)

    # ======================
    # SCORE MANAGEMENT
    # ======================

    def update_scores(self, player: Player, correct_flag: bool) -> None:
        player.total_questions_answered += 1
        player.run.questions_attempted += 1 # pyright: ignore[reportOptionalMemberAccess]
        if correct_flag:
            player.total_questions_correctly_answered += 1
            player.run.questions_answered_correctly += 1 # pyright: ignore[reportOptionalMemberAccess]
    
    def view_scores(self) -> None:
        player = self.get_user_choice_of_existing_players()
        if player.run:
            print(f"\n{player.run.run_score}")
        print(f"\n{player.all_time_score}")

    def delete_current_run_score_history(self) -> None:
        player = self.get_user_choice_of_existing_players_with_questions()
        if player.run:
            warning_prompt = f"\nWARNING: Deleting current question score history will delete score history for all questions with the current {player.run.question_bank.category} category. Would you like to proceed " # pyright: ignore[reportOptionalMemberAccess]
            if not get_yes_no_response(warning_prompt):
                print("\nNo score history deleted. User manually aborted.")
                return
        player.run.questions_attempted = 0 # pyright: ignore[reportOptionalMemberAccess]
        player.run.questions_answered_correctly = 0 # pyright: ignore[reportOptionalMemberAccess]

    def delete_all_score_history(self) -> None:
        player = self.get_user_choice_of_existing_players()
        if player.run or player.total_questions_answered > 0:
            warning_prompt = f"\nWARNING: Deleting all score history will delete score history for all questions ever assigned to {player.name} (including current). Would you like to proceed "
            if not get_yes_no_response(warning_prompt):
                print("\nNo score history deleted. User manually aborted.")
                return
            player.run.questions_attempted = 0 # pyright: ignore[reportOptionalMemberAccess]
            player.run.questions_answered_correctly = 0 # pyright: ignore[reportOptionalMemberAccess]
        player.total_questions_answered = 0
        player.total_questions_correctly_answered = 0