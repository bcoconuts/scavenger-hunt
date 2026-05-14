"""scavenger hunt game where printed barcodes are linked to questions from a grok API call and are integrated into a CLI game"""

import json
import os
from dotenv import load_dotenv
from datetime import datetime, date
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

DEBUG = True
PLAYER_FILE = "players.json"
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

MAX_QUESTIONS = 100
VALID_QUESTION_NUMBERS = {num for num in range(1, MAX_QUESTIONS + 1)}
MAX_PLAYERS = 100
MAX_AGE = 100
CURRENT_YEAR = date.today().year
BIRTH_YEAR_RANGE = set(range(CURRENT_YEAR - MAX_AGE, CURRENT_YEAR + 1))
VALID_MONTHS = set(range(1, 13))


## ======================
## GAME CLASSES
## ======================

class Question(BaseModel):
    question: str = Field(description="Question")
    answer: str = Field(description="Answer")
    fake_answers: list[str] = Field(
        description="""List of 3 incorrect answers used for 
        the other options in a multiple choice question"""
    )
    status: str = UNANSWERED
    id: str = ""

    def display_all_question_content(self) -> None:
        fake_ans = "\n              ".join(self.fake_answers)
        print(f"""\
    Question: {self.question}
      Answer: {self.answer}
Fake Answers: {fake_ans}
      Status: {self.status}
        """
        )
        
    def edit_status(self) -> None:
        prompt = "Which status would you like to select?: "
        choice = get_user_choice_from_menu(QUESTION_STATUSES, numbered=True, header="\nSTATUSES:", prompt=prompt)
        self.status = QUESTION_STATUSES[choice]

    def get_user_choice_of_mult_choice_question(self) -> str:
        all_answers = {a for a in self.fake_answers}
        all_answers.add(self.answer)
        answer_dict = {index + 1: a for index, a in enumerate(all_answers)}
        prompt = "What is your final answer?: "
        choice = get_user_choice_from_menu(answer_dict, numbered=True, header=f"\n{self.question}", prompt=prompt)
        answer = answer_dict[choice]
        return answer
    
    def get_user_choice_of_ask_answer_question(self) -> bool:
        prompt = "Was the question answered correctly?: "
        choice = get_user_choice_from_menu(YES_NO_DICT, numbered=True, header=f"\n{self.question} [Answer: {self.answer}]", prompt=prompt)
        if YES_NO_DICT[choice] == YES:
            return True
        else:
            return False

class QuestionBank(BaseModel):
    question_list: list[Question] = Field(description="List of the questions generated")
    category: str = Field(description="Category associated with questions generated")

    def display_questions(self) -> None:
        print()
        for index, q in enumerate(self.question_list):
            print(f"=== No. {index + 1} ===")
            q.display_all_question_content()
    
    def get_user_choice_of_existing_questions(self) -> Question:
        question_dict = {q.question: q for q in self.question_list}
        prompt = "Which question would you like to select?: "
        choice = get_user_choice_from_menu(question_dict, header="\nQUESTIONS:", prompt=prompt)
        question = self.question_list[choice - 1]

        return question
    

class Run(BaseModel):
    question_bank: QuestionBank | None = None
    date_generated: str = Field(default_factory=lambda: str(datetime.now()))
    questions_answered_correctly: int = 0
    questions_attempted: int = 0

    @computed_field
    @property
    def run_score(self) -> str:
        if not self.question_bank:
            return "No Questions Assigned"
        return f"""\
For currently assigned question set (Category: {self.question_bank.category}):
   Total Questions Assigned: {len(self.question_bank.question_list)}
        Questions Attempted: {self.questions_attempted}
Questions Correctly Guessed: {self.questions_answered_correctly}
        """

    def generate_questions(self, client: Client, player: "Player", category: str, run_length: int) -> QuestionBank | None:
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
                q.id = str(uuid4())
        except Exception as e:
            print("Something went wrong with question generation. Please try again")
            if DEBUG: print(e)
            return None

        return question_bank
    
    #TODO
    def generate_pdf(self):
        print("This is where a pdf would be generated, If I would have writen the code to do it")


class Player(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    years_old: int = 0
    months_old: int = 0
    name: str = ""
    run: Run | None = None
    total_questions_answered: int = 0
    total_questions_correctly_answered: int = 0

    @computed_field
    @property
    def age_bucket(self) -> str:
        if self.years_old <= 3:
            return (
                "a bright toddler aged 2-3. They know basic colors, can count to 10+, "
                "know common animals and their sounds, and understand simple stories. "
                "Questions should challenge the top 25 percent of kids this age — not softballs."
            )
        elif self.years_old <= 5:
            return (
                "a bright, well-educated preschooler aged 4-5. They are beginning to read, "
                "know numbers past 20, understand basic opposites, seasons, and simple science "
                "Questions should challenge the top 25 percent of kids this age — not softballs."
            )
        elif self.years_old <= 7:
            return (
                "a bright, well-educated early elementary child aged 6-7. They can read simple "
                "books, do basic addition and subtraction, and know geography basics. "
                "Questions should challenge the top 25 percent of kids this age — not softballs."
            )
        elif self.years_old <= 10:
            return (
                "a bright, well-educated elementary child aged 8-10. They read fluently, "
                "understand basic history, multiplication, and science concepts. "
                "Questions should challenge the top 25 percent of kids this age — not softballs."
            )
        elif self.years_old <= 13:
            return (
                "a bright, well-educated preteen aged 11-13. They have solid general knowledge "
                "across history, science, geography and literature. "
                "Questions should genuinely challenge the top 25 percent of kids this age."
            )
        elif self.years_old <= 18:
            return (
                "a teenager aged 14-18. They have solid general knowledge "
                "across history, science, math, geography and literature. "
                "Questions should genuinely challenge the top 25 percent of kids this age."
            )
        elif self.years_old <= 22:
            return (
                "a college educated person aged 19-22. They have solid general knowledge "
                "across history, science, math, geography and literature. "
                "Questions should genuinely challenge the top 25 percent of people this age."
            )
        else:
            return (
                "an adult with a college eductaion. They have solid general knowledge "
                "across history, science, math, geography and literature. "
                "Questions should genuinely challenge the top 50 percent of college educated adults."
            )
        
    @computed_field
    @property
    def all_time_score(self) -> str:
        return f"""\
For all questions ever attempted by {self.name}:
        Questions Attempted: {self.total_questions_answered}
Questions Correctly Guessed: {self.total_questions_correctly_answered}
        """
    
    def edit_player_attributes(self, existing_names: set) -> None:
        self.edit_player_name(existing_names)
        self.edit_player_age()
        print(f"Player Information Saved.\n    Name: {self.name}, Age: {self.years_old}")

    def edit_player_name(self, existing_names: set) -> None:
        prompt = "\nWhat should the player be called?: "
        self.name = get_unique_alpha_response(existing_names, prompt, str.title)

    def edit_player_age(self) -> None:
        valid_year_keys = BIRTH_YEAR_RANGE
        year_prompt = f"What year was {self.name} born? Select a year between {min(BIRTH_YEAR_RANGE)} - {max(BIRTH_YEAR_RANGE)}: "
        new_birth_year = get_valid_int_response(valid_year_keys, year_prompt)

        valid_month_keys = VALID_MONTHS
        month_prompt = f"What month was {self.name} born? Select between {min(VALID_MONTHS)} - {max(VALID_MONTHS)}: "
        new_birth_month = get_valid_int_response(valid_month_keys, month_prompt)

        today = date.today()
        total_months = ((today.year - new_birth_year) * 12) + (today.month - new_birth_month)

        self.years_old = total_months//12
        self.months_old = total_months%12

    def display_player_info(self) -> None:
        print(f"""\
              Name: {self.name}
               Age: {self.years_old}
Questions Assigned: {True if self.run else False}
"""
        )


class Session:
   
    # ======================
    # INITIALIZATION
    # ======================

    def __init__(self):
        load_dotenv()
        self.client: Client = Client(api_key=os.getenv("XAI_API_KEY"))
        self.existing_players: list[Player] = []
        self.q_p_lookup: dict[str, str] = {} # question.id -> player.id

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
        player_list = [p for p in self.existing_players if p.run]
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
            return action()
        
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
            save_session(self.existing_players)
            if flag == None:
                return True
            else:
                return flag
        return True

    def route_run_management_menu_actions(self) -> bool:
        choice = get_user_choice_from_menu(CHOICES[MANAGE_QUESTIONS], numbered=True, header="\nMANAGE QUESTIONS")
        actions = {
            1: self.start_new_run_for_player,
            2: self.print_questions,
            3: self.display_questions_for_player,
            4: self.delete_question,
            5: self.edit_question_status,
            6: self.back
        }

        action = actions.get(choice)
        if action:
            flag = action()
            save_session(self.existing_players)
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
            save_session(self.existing_players)
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
        fresh_player = Player()
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
        if player.run:
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
            player.display_player_info()

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
        if player.run:
            warning_prompt = "\nWARNING: Assigning new questions will delete any unanswered questions. Would you like to proceed "
            if not get_yes_no_response(warning_prompt):
                print("\nNo questions generated. User manually aborted.")
                return
        cat = self.get_category(player)
        r_length = self.get_run_length(player)
        run = Run()
        run.question_bank = run.generate_questions(self.client, player, cat, r_length)
        if run.question_bank is None:
            print("\nQuestion generation failed. Player questions not assigned.")
            return
        for q in run.question_bank.question_list:
            self.q_p_lookup[q.id] = player.id
        player.run = run
    
    def print_questions(self) -> None:
        if not any([p.run for p in self.existing_players]):
            print("\nNo players available to print questions for.")
            return
        player = self.get_user_choice_of_existing_players_with_questions()
        player.run.generate_pdf()

    def display_questions_for_player(self) -> None:
        if not any([p.run for p in self.existing_players]):
            print("\nNo players available to view questions for.")
            return
        player = self.get_user_choice_of_existing_players_with_questions()
        player.run.question_bank.display_questions()
    
    def delete_question(self) -> None:
        if not any([p.run for p in self.existing_players]):
            print("\nNo players available to remove questions for.")
            return
        player = self.get_user_choice_of_existing_players_with_questions()
        question = player.run.question_bank.get_user_choice_of_existing_questions()
        player.run.question_bank.question_list.remove(question)
        self.q_p_lookup.pop(question.id)
        if not player.run.question_bank.question_list:
            player.run = None
        print(f'\nQuestion removed.')
    
    def edit_question_status(self) -> None:
        if not any([p.run for p in self.existing_players]):
            print("\nNo players available to edit question statuses for.")
            return
        player = self.get_user_choice_of_existing_players_with_questions()
        question = player.run.question_bank.get_user_choice_of_existing_questions()
        question.edit_status()

    # ======================
    # GAME LOOP
    # ======================

    def generate_eligible_question_dict(self) -> dict[str, Question]:
        question_list_list = [p.run.question_bank.question_list for p in self.existing_players if p.run]
        eligible_question_dict = {q.id: q for ls in question_list_list for q in ls if q.status == UNANSWERED}
        return eligible_question_dict
    
    def generate_eligible_player_dict(self) -> dict[str, Player]:
        eligible_player_dict = {p.id: p for p in self.existing_players if p.run}
        return eligible_player_dict

    def _evaluate_answer(self, question: Question, player: Player, ask_answer_flag: bool) -> None:
        if ask_answer_flag:
            user_answer: bool = question.get_user_choice_of_ask_answer_question()
        else:
            user_answer: str = question.get_user_choice_of_mult_choice_question()
        if ask_answer_flag and user_answer:
            question.status = CORRECTLY_ANSWERED
            self.update_scores(player, correct_flag=True)
            print("\nCongratulations!")
        elif ask_answer_flag and not user_answer:
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
        player.run.questions_attempted += 1
        if correct_flag:
            player.total_questions_correctly_answered += 1
            player.run.questions_answered_correctly += 1
    
    def view_scores(self) -> None:
        player = self.get_user_choice_of_existing_players()
        if player.run:
            print(f"\n{player.run.run_score}")
        print(f"\n{player.all_time_score}")

    def delete_current_run_score_history(self) -> None:
        player = self.get_user_choice_of_existing_players_with_questions()
        if player.run:
            warning_prompt = f"\nWARNING: Deleting current question score history will delete score history for all questions with the current {player.run.question_bank.category} category. Would you like to proceed "
            if not get_yes_no_response(warning_prompt):
                print("\nNo score history deleted. User manually aborted.")
                return
        player.run.questions_attempted = 0
        player.run.questions_answered_correctly = 0

    def delete_all_score_history(self) -> None:
        player = self.get_user_choice_of_existing_players()
        if player.run:
            warning_prompt = f"\nWARNING: Deleting all score history will delete score history for all questions ever assigned to {player.name} (including current). Would you like to proceed "
            if not get_yes_no_response(warning_prompt):
                print("\nNo score history deleted. User manually aborted.")
                return
            player.run.questions_attempted = 0
            player.run.questions_answered_correctly = 0
        player.total_questions_answered = 0
        player.total_questions_correctly_answered = 0


## ======================
## FILE I/O
## ======================

def save_session(existing_players: list[Player]) -> None:
    save_dict = {f"Player {(i + 1)}:": p.model_dump() for i, p in enumerate(existing_players)} 
    with open(PLAYER_FILE, "w") as f:
        json.dump(save_dict, f, indent=5)


def load_session() -> Session:
    try:
        with open(PLAYER_FILE, "r") as f:
            loaded_dict = json.load(f)
            session = Session()
            session.existing_players = [Player.model_validate(p) for p in loaded_dict.values()]
        playerid_player_dict = {p.id: p.run.question_bank.question_list for p in session.existing_players if p.run}
        session.q_p_lookup = {q.id: playerid for playerid, ls in playerid_player_dict.items() for q in ls}

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