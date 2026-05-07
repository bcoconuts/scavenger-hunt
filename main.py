"""scavenger hunt game where printed barcodes are linked to questions from a grok API call and are integrated into a CLI game"""

import os
from dotenv import load_dotenv
from datetime import date
from pydantic import BaseModel, Field
from utils import (
    get_unique_alpha_response,
    get_valid_int_response,
    get_key_int_choice_from_dict,
    display_options_from_dict,
    get_user_choice_from_menu
)
from xai_sdk import Client
from xai_sdk.chat import user, system

sample_question_bank = {
    1: {"question": "How many legs does an Octupus have?", "answer": "8", "player": "Stella"},
    2: {"question": "How many legs does an Elephant have?", "answer": "4", "player": "Stella"},
    3: {"question": "How many legs does a Person have?", "answer": "2", "player": "Charlie"}
}

sample_category = "Animals"


## ======================
## CONFIG
## ======================

DEBUG = True
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
ASSIGN_NEW_QUESTIONS_TO_ALL_PLAYERS = "Assign New Questions To All Players"
ASSIGN_NEW_QUESTIONS_TO_SINGLE_PLAYER = "Assign New Questions To Single Player"
PRINT_QUESTIONS = "Create Question PDF"
DISPLAY_QUESTIONS_FOR_ALL_PLAYERS = "Display Questions For All Players"
DISPLAY_QUESTIONS_FOR_SINGLE_PLAYER = "Display Questions For Single Player"
EDIT_QUESTION_STATUS = "Edit Question Status"
VIEW_SCORES = "View Scores"
DELETE_SCORE_HISTORY = "Delete Score History"
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
        1: ASSIGN_NEW_QUESTIONS_TO_SINGLE_PLAYER,
        2: ASSIGN_NEW_QUESTIONS_TO_ALL_PLAYERS,
        3: PRINT_QUESTIONS,
        4: DISPLAY_QUESTIONS_FOR_SINGLE_PLAYER,
        5: DISPLAY_QUESTIONS_FOR_ALL_PLAYERS,
        6: EDIT_QUESTION_STATUS,
        7: BACK
    },
    MANAGE_SCORES: {
        1: VIEW_SCORES,
        2: DELETE_SCORE_HISTORY,
        3: BACK
    },
    ANSWER_QUESTIONS: {

    },
    EXIT: {

    }
}
QUESTION_STATUSES = {1: UNANSWERED, 2: CORRECTLY_ANSWERED, 3: INCORRECTLY_ANSWERED}
Y_N_CHOICES = {1: YES, 2: NO}


MAX_PLAYERS = 100
MAX_AGE = 100
CURRENT_YEAR = date.today().year
BIRTH_YEAR_RANGE = {num for num in range(CURRENT_YEAR - MAX_AGE, CURRENT_YEAR + 1)}
VALID_MONTHS = {num for num in range(1, 12 + 1)}


## ======================
## GAME CLASSES
## ======================

class Player:
    def __init__(self) -> None:

        self.years_old = 0
        self.months_old = 0
        self.age = f"{self.years_old} years, {self.months_old} month(s)"
        self.name = "New"
        self.qbank_assigned = NO
    
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


class Question(BaseModel):
    question_number: int = Field(description="Number of question generated")
    question: str = Field(description="Question")
    answer: str = Field(description="Answer")
    fake_answers: list[str] = Field(
        description="""List of incorrect answers used for 
        the other options in a multiple choice question"""
    )
    status: str = UNANSWERED

    # def display_question(self) -> None:
    #     pass

    # def display_answer(self) -> None:
    #     pass


class Question_Bank(BaseModel):
    question_list: list[Question] = Field(description="List of the questions generated")
    qty: int = Field(description="Quantity of questions generated")
    category: str = Field(description="Category of the questions generated")
    date_generated: date = Field(default_factory=date.today())

    # def generate_pdf():
    #     pass


class Run:

    def __init__(self, player: Player, client: Client):
        self.player = player
        self.client = client
        self.category = self.get_category()
        self.runlength = self.get_run_length()
        self.question_bank = self.generate_questions()

    def generate_questions(self) -> Question_Bank:
        chat = self.client.chat.create(model="grok-latest")

        chat.append(user(f"""
            Generate 10 trivia questions for a
            {self.player.age} old. Category: {self.category}. 
            Questions should be simple but challenging, 
            only something the top 25% of 
            {self.player.years_old} year olds would know.
        """)
        )

        # The parse method returns a tuple of the full response object as well as the parsed pydantic object.

        try:
            response, question_bank = chat.parse(Question_Bank)
        except Exception as e:
            print("Something went wrong with question generation. Please try again")
            if DEBUG: print(e)
            return None

        return question_bank

    def get_category(self) -> str:
        return sample_category
    
    def get_run_length(self) -> int:
        return 10
    
    # def generate_all_question_banks(self) -> dict[str, Question_Bank]:
    #     pass


class Session:
   
    # ======================
    # INITIALIZATION
    # ======================

    def __init__(self):
        load_dotenv()
        self.client = Client(api_key=os.getenv("XAI_API_KEY"))
        self.existing_players: set[Player] = set()

    # def load_previous_session(self):
    #     pass

    # def save_session(self):
    #     pass

    def greet_user(self) -> None:
        print("Hello! Welcome to The Inquisitor!. Here's how the game works.....")

    # ======================
    # USER CHOICES & MENUS
    # ======================
    
    def get_user_choice_of_single_player(self) -> Player:
        player_list = sorted(self.existing_players, key= lambda p: p.name)
        player_dict = {player.name: player for player in player_list}
        header = "\nPLAYERS:"
        display_options_from_dict(header, player_dict)

        prompt = "Which player would you like to select?: "
        choice = get_key_int_choice_from_dict(prompt, player_dict)
        player = player_list[choice - 1]

        return player
    
    def route_main_menu_actions(self) -> bool:
        choice = get_user_choice_from_menu(CHOICES, header="\nMAIN MENU")
        actions = {
            1: self.route_player_management_menu_actions,
            2: self.route_run_management_menu_actions,
            3: "placeholder",
            4: "placeholder",
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
            if flag == None:
                return True
            else:
                return flag
        return True

    def route_run_management_menu_actions(self) -> bool:
        choice = get_user_choice_from_menu(CHOICES[MANAGE_QUESTIONS], numbered=True, header="\nMANAGE QUESTIONS")
        actions = {
            1: self.start_new_run_for_single_player,
            2: "placeholder",
            3: "placeholder",
            4: "placeholder",
            5: "placeholder",
            6: "placeholder",
            7: self.back
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
        self.existing_players.add(fresh_player)

    def edit_player(self) -> None:
        if not self.existing_players:
            print("\nNo editable players.")
            return
        player = self.get_user_choice_of_single_player()
        existing_names = {p.name for p in self.existing_players if p != player}
        player.edit_player_attributes(existing_names)

    def remove_player(self) -> None:
        if not self.existing_players:
            print("\nNo removable players.")
            return
        player = self.get_user_choice_of_single_player()
        self.existing_players.discard(player)
        print(f'\nPlayer "{player.name}" Removed')

    def view_players(self) -> None:
        player_list = sorted(self.existing_players, key=lambda p: p.name)
        print()
        for index, player in enumerate(player_list):
            print(f"{index + 1}. Name: {player.name}, Age: {player.age}")

    # ======================
    # RUN MANAGEMENT
    # ======================

    def start_new_run_for_single_player(self) -> None:
        if not self.existing_players:
            print("\nNo players to assign questions to.")
            return
        player = self.get_user_choice_of_single_player()
        run = Run(player, self.client)
        print(run.question_bank)
    


def main():
    session = Session()
    session.greet_user()
    running = True
    while running:
        running = session.route_main_menu_actions()


if __name__ == "__main__":
    main()