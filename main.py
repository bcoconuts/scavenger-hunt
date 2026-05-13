"""scavenger hunt game where printed barcodes are linked to questions from a grok API call and are integrated into a CLI game"""

import json
import os
from dotenv import load_dotenv
from datetime import datetime, date
from pydantic import BaseModel, Field
from utils import (
    get_unique_alpha_response,
    get_valid_int_response,
    get_user_choice_from_menu,
    warn_player_yes_no
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
DELETE_SCORE_HISTORY = "Delete Score History"
MULTIPLE_CHOICE = "Multiple Choice"
ASK_AND_ANSWER = "Ask & Answer"
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
        2: DELETE_SCORE_HISTORY,
        3: BACK
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


class Question_Bank(BaseModel):
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
    question_bank: Question_Bank | None = None
    date_generated: str = Field(default_factory=lambda: str(datetime.now()))

    def generate_questions(self, client: Client, player: "Player", category: str, run_length: int) -> Question_Bank | None:
        chat = client.chat.create(model="grok-latest")

        chat.append(user(f"""
            Generate {run_length} trivia questions for a
            {player.age} old. Category: {category}. 
            Questions should be simple but challenging, 
            only something the top 25% of 
            {player.years_old} year olds would know.
        """)
        )

        # The parse method returns a tuple of the full response object as well as the parsed pydantic object.

        try:
            response, question_bank = chat.parse(Question_Bank)
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
    age: str = ""
    name: str = ""
    run: Run | None = None
    
    def edit_player_attributes(self, existing_names: set) -> None:
        self.edit_player_name(existing_names)
        self.edit_player_age()
        print(f"Player Information Saved.\n    Name: {self.name}, Age: {self.age}")

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
        self.age = f"{self.years_old} years, {self.months_old} month(s)"

    def display_player_info(self) -> None:
        print(f"""\
              Name: {self.name}
               Age: {self.age}
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
        self.q_p_lookup: dict[str, str] = {}

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
            3: "placeholder",
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
    
    def route_play_game_menu_actions(self) -> bool:
        choice = get_user_choice_from_menu(CHOICES[ANSWER_QUESTIONS], numbered=True, header="\nGAME TYPE")
        actions = {
            1: self.multiple_choice,
            2: self.ask_and_answer,
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
            if not warn_player_yes_no(warning_prompt):
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
            self.q_p_lookup[q.id] = player
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

    def multiple_choice(self) -> None:
        if not self.q_p_lookup:
            print("\nNo questions assigned to players.")
            return
        all_question_list = [q for ls in [p.run.question_bank.question_list for p in self.existing_players if p.run] for q in ls]
        eligible_question_ids: dict[str, Question] = {}
        ineligible_question_ids: dict[str, Question] = {}
        for q in all_question_list:
            if q.status == UNANSWERED:
                eligible_question_ids[q.id] = q
            else:
                ineligible_question_ids[q.id] = q
        if not eligible_question_ids:
            print("\nNo more avaliable questions")
            return
        all_players: dict[str, Player] = {p.id: p for p in self.existing_players if p.run} #TODO: update scoring logic. players accessible through player id and q_p_lookup here.
        while True:
            id = input("\nPlease Scan Barcode (Enter 'F' to quit): ").strip()
            if id.upper() == "F":
                break
            elif id in eligible_question_ids:
                question = eligible_question_ids[id]
                user_answer = question.get_user_choice_of_mult_choice_question()
                if question.answer == user_answer:
                    question.status = CORRECTLY_ANSWERED
                    print("\nCorrect!")
                else:
                    question.status = INCORRECTLY_ANSWERED
                    print("\nIncorrect...")
                eligible_question_ids.pop(id)
                ineligible_question_ids[id] = question
            elif id in ineligible_question_ids:
                print("\nQuestion already answered. Please scan a new question.")
            else:
                print("\nQuestion not found. Question may be from a previous question set. Please scan a new question.")
            save_session(self.existing_players)
            if not eligible_question_ids:
                print("\nNo more avaliable questions")
                break

    #TODO
    def ask_and_answer(self) -> None:
        pass


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
        session.q_p_lookup = {q.id: p for p, ls in {p.id: p.run.question_bank.question_list for p in session.existing_players if p.run}.items() for q in ls}

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