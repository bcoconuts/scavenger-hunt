"""scavenger hunt game where printed barcodes are linked to questions from a grok API call and are integrated into a CLI game"""

import json
import os
import random
from dotenv import load_dotenv
from datetime import date
from models import (
    Question,
    QuestionBank,
    Player
)
from pdfgen import generate_pdf
from pydantic import BaseModel, Field, computed_field
from utils import (
    get_unique_alpha_response,
    get_valid_int_response,
    get_user_choice_from_menu,
    get_yes_no_response
)
from uuid import uuid4
from xai_sdk import Client
from xai_sdk.chat import user


## ======================
## CONFIG
## ======================

#DEVELOPMENT
DEBUG = False

#STRINGS
YES = "Yes"
NO = "No"
YEARS = "years"
MONTHS = "months"
CATEGORY = "category"
MANAGE_PLAYERS = "Manage Players"
MANAGE_QUESTIONS = "Manage Questions"
MANAGE_SCORES = "Manage Scores"
ANSWER_QUESTIONS = "Answer Questions (Play Game)"
EXIT = "Exit"
ADD_PLAYER = "Add Player"
EDIT_PLAYER = "Edit Player"
REMOVE_PLAYER = "Remove Player"
VIEW_PLAYERS = "View Players"
BACK = "Back"
ASSIGN_NEW_QUESTIONS_TO_PLAYER = "Assign New Questions To Player"
PRINT_QUESTIONS = "Create Question PDF"
DISPLAY_QUESTIONS_FOR_PLAYER = "Display Questions For Player"
DELETE_QUESTIONS_FOR_PLAYER = "Delete Questions For Player"
EDIT_QUESTION_STATUS = "Edit Question Status"
VIEW_SCORES = "View Scores"
DELETE_CURRENT_QUESTIONS_SCORE_HISTORY = "Delete Current Question Set Score History"
DELETE_ALL_SCORE_HISTORY = "Delete All Score History"
MULTIPLE_CHOICE = "Multiple Choice"
ASK_AND_ANSWER = "Ask & Answer (Parents guide game)"
UNANSWERED = "Unanswered"
CORRECTLY_ANSWERED = "Correctly Answered"
INCORRECTLY_ANSWERED = "Incorrectly Answered"

#MENU OPTIONS
CHOICES = {
    MANAGE_PLAYERS: {
        1: ADD_PLAYER,
        2: EDIT_PLAYER,
        3: REMOVE_PLAYER,
        4: VIEW_PLAYERS,
        5: BACK
    },
    MANAGE_QUESTIONS: {
        1: ASSIGN_NEW_QUESTIONS_TO_PLAYER,
        2: PRINT_QUESTIONS,
        3: DISPLAY_QUESTIONS_FOR_PLAYER,
        4: DELETE_QUESTIONS_FOR_PLAYER,
        5: EDIT_QUESTION_STATUS,
        6: BACK
    },
    MANAGE_SCORES: {
        1: VIEW_SCORES,
        2: DELETE_CURRENT_QUESTIONS_SCORE_HISTORY,
        3: DELETE_ALL_SCORE_HISTORY,
        4: BACK
    },
    ANSWER_QUESTIONS: {
        1: MULTIPLE_CHOICE,
        2: ASK_AND_ANSWER,
        3: BACK
    },
    EXIT: {

    }
}
QUESTION_STATUSES = {1: UNANSWERED, 2: CORRECTLY_ANSWERED, 3: INCORRECTLY_ANSWERED}
YES_NO_DICT = {1: YES, 2: NO}

#NUMBER RANGES
MAX_QUESTIONS = 100
VALID_QUESTION_NUMBERS = {num for num in range(1, MAX_QUESTIONS + 1)}
MAX_PLAYERS = 100
MAX_AGE = 100
CURRENT_YEAR = date.today().year
BIRTH_YEAR_RANGE = set(range(CURRENT_YEAR - MAX_AGE, CURRENT_YEAR + 1))
VALID_MONTHS = set(range(1, 13))

# FILES
PLAYER_FILE_NAME = "players.json"
PDF_FILE_NAME = f"_questions_{date.today()}.pdf"


## ======================
## GAME CLASSES
## ======================
    
def generate_id(existing_question_ids: set) -> str:
    while True:
        new_id = str(random.randint(10000000, 99999999))
        if new_id not in existing_question_ids:
            existing_question_ids.add(new_id)
            return new_id

def generate_questions(client: Client, player: "Player", category: str, run_length: int, existing_question_ids: set[str]) -> QuestionBank:
    chat = client.chat.create(model="grok-latest")

    chat.append(user(f"""\
Generate {run_length} trivia questions.

Questions aimed at {player.age_bucket} 

Category for questions: {category}."""
        )
    )

    # The parse method returns a tuple of the full response object as well as the parsed pydantic object.

    try:
        response, question_bank = chat.parse(QuestionBank)
        for q in question_bank.question_list:
            q.question_id = generate_id(existing_question_ids)
    except Exception as e:
        print("Something went wrong with question generation. Please try again")
        if DEBUG: print(e)
        question_bank = QuestionBank(category="General")

    return question_bank


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

    def greet_user(self) -> None:
        print("Hello! Welcome to The Inquisitor!. Here's how the game works.....")

    # ======================
    # USER CHOICES & MENUS
    # ======================
    
    def get_user_choice_of_existing_players(self) -> Player:
        player_dict = {player.name: player for player in self.existing_players}
        player_prompt = "Which player would you like to select?: "
        choice = get_user_choice_from_menu(player_dict, header="\nPLAYERS:", prompt=player_prompt)
        player = self.existing_players[choice - 1]
        return player
    
    def get_user_choice_of_existing_players_with_questions(self) -> Player:
        player_list = [p for p in self.existing_players if self.player_id_to_question_bank_lookup[p.player_id]]
        player_dict = {player.name: player for player in player_list}
        player_prompt = "Which player would you like to select?: "
        choice = get_user_choice_from_menu(player_dict, header="\nPLAYERS:", prompt=player_prompt)
        player = player_list[choice - 1]
        return player
    
    def route_main_menu_actions(self) -> bool:
        choice = get_user_choice_from_menu(CHOICES, header="\nMAIN MENU")
        actions = {
            1: self.route_player_management_menu_actions,
            2: self.route_run_management_menu_actions,
            3: self.route_score_management_menu_actions,
            4: self.route_play_game_menu_actions,
            5: self.exit
        }

        action = actions.get(choice)

        if action == self.exit:
            return action() # pyright: ignore[reportOptionalCall]
        
        running = True
        while running and action:
            flag = action()
            if flag == None:
                continue
            else:
                running = flag
        return True
    
    def route_player_management_menu_actions(self) -> bool:
        choice = get_user_choice_from_menu(CHOICES[MANAGE_PLAYERS], numbered=True, header="\nMANAGE PLAYERS")
        actions = {
            1: self.add_player,
            2: self.edit_player,
            3: self.remove_player,
            4: self.view_players,
            5: self.back
        }

        action = actions.get(choice)
        if action:
            flag = action()
            self.existing_players.sort(key= lambda p: p.name)
            save_session(self.existing_players, self.player_id_to_question_bank_lookup)
            if flag == None:
                return True
            else:
                return flag
        return True

    def route_run_management_menu_actions(self) -> bool:
        choice = get_user_choice_from_menu(CHOICES[MANAGE_QUESTIONS], numbered=True, header="\nMANAGE QUESTIONS")
        actions = {
            1: self.start_new_run_for_player,
            2: self.generate_question_pdf,
            3: self.display_questions_for_player,
            4: self.delete_question,
            5: self.edit_question_status,
            6: self.back
        }

        action = actions.get(choice)
        if action:
            flag = action()
            save_session(self.existing_players, self.player_id_to_question_bank_lookup)
            if flag == None:
                return True
            else:
                return flag
        return True
    
    def route_score_management_menu_actions(self) -> bool:
        choice = get_user_choice_from_menu(CHOICES[MANAGE_SCORES], numbered=True, header="\nMANAGE SCORES")
        actions = {
            1: self.view_scores,
            2: self.delete_current_run_score_history,
            3: self.delete_all_score_history,
            4: self.back
        }

        action = actions.get(choice)
        if action:
            flag = action()
            save_session(self.existing_players, self.player_id_to_question_bank_lookup)
            if flag == None:
                return True
            else:
                return flag
        return True

    def route_play_game_menu_actions(self) -> bool:
        choice = get_user_choice_from_menu(CHOICES[ANSWER_QUESTIONS], numbered=True, header="\nGAME TYPE")
        actions = {
            1: lambda: self.run_game_loop(ask_answer_flag=False),
            2: lambda: self.run_game_loop(ask_answer_flag=True),
            3: self.back
        }

        action = actions.get(choice)
        if action:
            flag = action()
            if flag == None:
                return True
            else:
                return flag
        return True
    
    def back(self):
        return False

    def exit(self):
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


## ======================
## FILE I/O
## ======================

def save_session(existing_players: list[Player], player_id_to_qbank_lookup: dict[str, QuestionBank]) -> None:
    session_dict = {}
    for index, player in enumerate(existing_players):
        session_dict[index] = {"player": player, "qbank": player_id_to_qbank_lookup[player.player_id]}
    with open(PLAYER_FILE_NAME, "w") as f:
        json.dump(session_dict, f, indent=4)


def load_session() -> Session:
    try:
        with open(PLAYER_FILE_NAME, "r") as f:
            session_dict: dict[str, dict] = json.load(f)
            session = Session()
            for k in session_dict:
                player: Player = session_dict[k]["player"]
                qbank: QuestionBank = session_dict[k]["qbank"]
                session.existing_players.append(player)
                session.player_id_to_question_bank_lookup[player.player_id] = qbank
    except FileNotFoundError:
        session = Session()
    
    return session


## ======================
## MAIN LOOP
## ======================

def main():
    session = load_session()
    session.greet_user()
    running = True
    while running:
        running = session.route_main_menu_actions()


if __name__ == "__main__":
    main()