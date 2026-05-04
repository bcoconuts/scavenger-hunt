from utils import get_unique_alpha_response, get_valid_response
from datetime import date

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



def get_player_name(existing_players: set) -> str:
    prompt = "What is the new Player's name?: "
    name = get_unique_alpha_response(existing_players, prompt, str.title)
    print(name)
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
    print(player_year, player_month)
    return (player_year, player_month)
    

def add_player(existing_players: set) -> None:
    player_name = get_player_name(existing_players)
    age = get_player_age(player_name)



existing_players = {"Blanton", "Stella"}
add_player(existing_players)