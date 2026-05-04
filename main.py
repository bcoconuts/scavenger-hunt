"""scavenger hunt game where printed barcodes are linked to questions from a grok API call and are integrated into a CLI game"""

from datetime import date

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
MAX_PLAYERS = 100
MAX_AGE = 10
CURRENT_YEAR = date.today().year
BIRTH_YEAR_RANGE = {num for num in range(CURRENT_YEAR - MAX_AGE, CURRENT_YEAR + 1)}

## ======================
## UTILITY
## ======================


def get_valid_response(valid_choices: set, prompt: str, case=str.lower) -> str:
    while True:
        response = case(input(prompt).strip())
        if response not in valid_choices:
            print("Invalid Input.")
        else:
            return response


def get_unique_alpha_response(invalid_choices: set, prompt: str, case=str.lower) -> str:
    unique_error_msg = "Already Taken."
    alpha_error_msg = "Must be alphabetical only. No numbers or special chars."
    while True:
        response = case(input(prompt).strip())
        if not response.isalpha():
            print(alpha_error_msg)
        elif response in invalid_choices:
            print(unique_error_msg)
        else:
            return response


def construct_prompt_ending(keys: list[str]) -> str:
    keys_with_brackets = [
        f"[{i[0].upper()}]{i[1:]}" if len(i) > 1 else f"[{i.upper()}]" for i in keys
    ]
    main_text = ", ".join(keys_with_brackets[:-1])
    if len(keys_with_brackets) == 2:
        main_text = main_text + " or"
    elif len(keys_with_brackets) > 2:
        main_text = main_text + ", or"
    prompt_end = f"{main_text} {keys_with_brackets[-1]}?: "
    return prompt_end


def construct_prompt_and_keys(selection: int | dict) -> tuple[str, set[str]]:
    if isinstance(selection, int):
        valid_input_list = [str(i) for i in range(1, selection + 1)]
        prompt_end = construct_prompt_ending(valid_input_list)
        valid_keys = set(valid_input_list)
        return prompt_end, valid_keys
    else:
        valid_input_list = [v for v in selection.values()]
        prompt_end = construct_prompt_ending(valid_input_list)
        valid_keys = set(i[0].lower() for i in valid_input_list)
        return prompt_end, valid_keys


## ======================
## GAME SETUP
## ======================


def play_new_game_choice() -> bool:
    prompt_start = "\nNew game?"
    prompt_end, valid_keys = construct_prompt_and_keys(NEW_GAME_CHOICES)

    response = get_valid_response(valid_keys, f"{prompt_start} {prompt_end}")

    return response == YES


def get_players() -> int:
    prompt_start = f"\nHow many players are playing against me?"
    prompt_end, valid_keys = construct_prompt_and_keys(MAX_PLAYERS)

    response = int(get_valid_response(valid_keys, f"{prompt_start} {prompt_end}"))
    return response


def collect_player_names(players: int) -> list[str]:
    player_sheet = []
    name_set = set()
    for p in range(1, players + 1):
        name = get_unique_alpha_response(
            name_set, f"\nWhat is Player {p}'s name?: ", str.title
        )
        player_sheet.append(name)
        name_set.add(name)

    return player_sheet

# def collect_player_dob(player_sheet: list) -> dict[str[str, int]]:
    
#     valid_year_keys = BIRTH_YEAR_RANGE
#     player_dict = {}

#     for player in player_sheet:
#         player_dict[player] = {}
#         year_prompt = f"What year was {player} born? Select a number between {BIRTH_YEAR_RANGE[0]} - {BIRTH_YEAR_RANGE[-1]}"
#         player_dict[player][YEARS] = get_valid_response(valid_year_keys, year_prompt)



#     return player_dict


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

    def display_question(self) -> None:
        pass

    def display_answer(self) -> None:
        pass


class Question_Bank:
    def __init__(self, category: str):
        self.category = category

    # def generate_questions(self, player: Player) -> dict[int[str, str]]:
    #     pass

    # def generate_pdf():
    #     pass


class Session:
    def __init__(self, player_dict: dict):

        self.player_list = [Player(player, player_dict[player][YEARS], player_dict[player][MONTHS]) for player in player_dict]
        self.banks = {player: Question_Bank(player.category) for player in self.player_list}
    
    # def get_categories(self) -> dict[str, str]:
    #     pass
    
    # def generate_question_banks(self) -> dict[str, Question_Bank]:
    #     pass
        
        



def main():
    print("hello")
    p1 = Player("Blanton", 1996, 8)
    print(p1.name, p1.age)


if __name__ == "__main__":
    main()