"""scavenger hunt game where printed barcodes are linked to questions from a grok API call and are integrated into a CLI game"""

from datetime import date
from utils import get_unique_alpha_response, get_valid_response

sample_question_bank = {
    1: {"question": "How many legs does an Octupus have?", "answer": "8", "player": "Stella"},
    2: {"question": "How many legs does an Elephant have?", "answer": "4", "player": "Stella"},
    3: {"question": "How many legs does an Person have?", "answer": "2", "player": "Charlie"}
}

sample_category = "Animals"

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
## PLAYER SETUP
## ======================

def get_player_name(existing_players: set) -> str:
    prompt = "What is the new Player's name?"
    name = get_unique_alpha_response(existing_players, prompt, str.title)
    return name


def get_player_age(player_name: str) -> tuple[int, int]:
    """Obtain the age of the player (years and months).

    Args:
        player_name: name of player who's age is being obtained.

    Returns:
        A tuple with birth year and month information, formatted (YYYY, MM).
    """
    valid_year_keys = BIRTH_YEAR_RANGE
    year_prompt = f"What year was {player_name} born? Select a year between {min(BIRTH_YEAR_RANGE)} - {max(BIRTH_YEAR_RANGE)}: "
    player_year = get_valid_response(valid_year_keys, year_prompt)

    valid_month_keys = VALID_MONTHS
    month_prompt = f"What month was {player_name} born? Select a month between {min(VALID_MONTHS)} - {max(VALID_MONTHS)} months: "
    player_month = get_valid_response(valid_month_keys, month_prompt)

    age = (player_month, player_year)
    return age


def add_player(existing_players: set) -> None:
    player_name = get_player_name(existing_players)
    age = get_player_age(player_name)


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
    
    def edit_player(self) -> None:
        pass
        
        def edit_player_name(self) -> None:
            pass

        def edit_player_age(self) -> None:
            pass


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


class Session:
    def __init__(self):
        pass
    
    # def get_categories(self) -> dict[str, str]:
    #     pass
    
    # def generate_question_banks(self) -> dict[str, Question_Bank]:
    #     pass
        
        



def main():
    p1 = Player("Blanton", 1996, 8)
    print(p1.name, p1.age)


if __name__ == "__main__":
    main()