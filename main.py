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
NEW_GAME_CHOICES = {"y": "yes", "n": "no"}
YES = "y"
NO = "n"
MAX_PLAYERS = 10
MAX_AGE = 50
CURRENT_YEAR = date.today().year
BIRTH_YEAR_RANGE = {num for num in range(CURRENT_YEAR - MAX_AGE, CURRENT_YEAR + 1)}
VALID_MONTHS = {num for num in range(1, 12 + 1)}


## ======================
## PLAYER MANAGEMENT
## ======================

def get_player_name(existing_players: set) -> str:
    prompt = "What is the new Player's name?: "
    name = get_unique_alpha_response(existing_players, prompt, str.title)
    return name


def get_player_age(player_name: str) -> tuple[int, int]:
    """Obtain the age of the player (years and months).

    Args:
        player_name: name of player who's age is being obtained.

    Returns:
        A tuple with birth year and month information, formatted (YYYY, M/MM)
        e.g. (1996, 8), or (1996, 11).
    """
    valid_year_keys = BIRTH_YEAR_RANGE
    year_prompt = f"What year was {player_name} born? Select a year between {min(BIRTH_YEAR_RANGE)} - {max(BIRTH_YEAR_RANGE)}: "
    player_year = get_valid_int_response(valid_year_keys, year_prompt)

    valid_month_keys = VALID_MONTHS
    month_prompt = f"What month was {player_name} born? Select between {min(VALID_MONTHS)} - {max(VALID_MONTHS)}: "
    player_month = get_valid_int_response(valid_month_keys, month_prompt)

    age = (player_year, player_month)
    return age


def edit_player_name(self) -> None:
    pass


def edit_player_age(self) -> None:
    pass


## ======================
## GAME CLASSES
## ======================

class Player:
    def __init__(self, name: str, birth_year: int, birth_month: int) -> None:

        today = date.today()
        total_months = ((today.year - birth_year) * 12) + (today.month - birth_month)
        years_old = total_months//12
        months_old = total_months%12

        self.age = f"{years_old} years, {months_old} month(s)"
        self.name = name


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

    def load_previous_session(self):
        pass

    def save_session(self):
        pass

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
        player_name = get_player_name(self.existing_players)
        birth_year, birth_month = get_player_age(player_name)
        new_player = Player(player_name, birth_year, birth_month)
        self.existing_players.add(new_player)

    def edit_player(self, player: Player) -> None:
        pass

    def remove_player(self, player: Player) -> None:
        pass
    


def main():
    session = Session()
    session.add_player()
    session.view_players()
    session.add_player()
    session.view_players()


if __name__ == "__main__":
    main()