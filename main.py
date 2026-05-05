"""scavenger hunt game where printed barcodes are linked to questions from a grok API call and are integrated into a CLI game"""

from datetime import date
from utils import get_unique_alpha_response, get_valid_str_response, get_valid_int_response, display_options_from_dict, get_key_number_choice_from_dict

sample_question_bank = {
    1: {"question": "How many legs does an Octupus have?", "answer": "8", "player": "Stella"},
    2: {"question": "How many legs does an Elephant have?", "answer": "4", "player": "Stella"},
    3: {"question": "How many legs does a Person have?", "answer": "2", "player": "Charlie"}
}

sample_category = "Animals"

MANAGE_PLAYERS = "Manage Players"
MANAGE_QUESTION_BANKS = "Manage Questions"
ANSWER_QUESTIONS = "Answer Questions"
VIEW_SCORES = "View Scores"
EXIT = "Exit"
UNANSWERED = "Unanwered"
CORRECTLY_ANSWERED = "Correctly Answered"
INCORRECTLY_ANSWERED = "Incorrectly Answered"
YES = "Yes"
NO = "No"
Y_N_CHOICES = {1: YES, 2: NO}
CHOICES = {1: MANAGE_PLAYERS, 2: MANAGE_QUESTION_BANKS, 3: ANSWER_QUESTIONS, 4: VIEW_SCORES, 5: EXIT}
QUESTION_STATUSES = {1: UNANSWERED, 2: CORRECTLY_ANSWERED, 3: INCORRECTLY_ANSWERED}
YEARS = "years"
MONTHS = "months"
CATEGORY = "category"
MAX_PLAYERS = 10
MAX_AGE = 50
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
        self.age = ""
        self.name = ""
    
    def edit_player_name(self, existing_names: set) -> None:
        prompt = "What should the player be called?: "
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


class Question:
    def __init__(self, content: dict):
        self.content = content

    # def display_question(self) -> None:
    #     pass

    # def display_answer(self) -> None:
    #     pass


class Question_Bank:
    def __init__(self, category: str):
        self.category = category

    # def generate_questions(self, player: Player) -> dict[int[str, str]]:
    #     pass

    # def generate_pdf():
    #     pass


class Run:
    def __init__(self):
        pass
    
    # def get_categories(self) -> dict[str, str]:
    #     pass
    
    # def generate_all_question_banks(self) -> dict[str, Question_Bank]:
    #     pass


class Session:
    def __init__(self):
        self.existing_players: set[Player] = set()

    # def load_previous_session(self):
    #     pass

    # def save_session(self):
    #     pass

    def greet_user(self) -> None:
        print("Hello! Welcome to The Inquisitor!. Heres how the game works.....")

    def get_user_choice(self):
        header = "\nOPTIONS:"
        display_options_from_dict(header, CHOICES)

        prompt = "What would you like to do?: "
        choice = get_key_number_choice_from_dict(prompt, CHOICES)
        
        return choice

    def view_players(self) -> None:
        player_list = sorted(self.existing_players, key=lambda p: p.name)
        for index, player in enumerate(player_list):
            print(f"{index + 1}. Name: {player.name}, Age: {player.age}")

    def add_player(self) -> None:
        fresh_player = Player()
        fresh_player.edit_player_name({player.name for player in self.existing_players})
        fresh_player.edit_player_age()
        self.existing_players.add(fresh_player)

    # def edit_player(self, player: Player) -> None:
    #     pass

    # def remove_player(self, player: Player) -> None:
    #     pass
    


def main():
    session = Session()
    session.greet_user()
    session.get_user_choice()
    session.add_player()
    session.view_players()
    session.add_player()
    session.view_players()


if __name__ == "__main__":
    main()