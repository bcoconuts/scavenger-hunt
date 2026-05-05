"""scavenger hunt game where printed barcodes are linked to questions from a grok API call and are integrated into a CLI game"""

from datetime import date
from utils import get_unique_alpha_response, get_valid_int_response, get_key_int_choice_from_dict, display_options_from_dict, get_user_choice_from_menu

sample_question_bank = {
    1: {"question": "How many legs does an Octupus have?", "answer": "8", "player": "Stella"},
    2: {"question": "How many legs does an Elephant have?", "answer": "4", "player": "Stella"},
    3: {"question": "How many legs does a Person have?", "answer": "2", "player": "Charlie"}
}

sample_category = "Animals"


## ======================
## CONFIG
## ======================


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
DELETE_SCROE_HISTORY = "Delete Score History"
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
        1: ASSIGN_NEW_QUESTIONS_TO_ALL_PLAYERS,
        2: ASSIGN_NEW_QUESTIONS_TO_SINGLE_PLAYER,
        3: PRINT_QUESTIONS,
        4: DISPLAY_QUESTIONS_FOR_ALL_PLAYERS,
        5: DISPLAY_QUESTIONS_FOR_SINGLE_PLAYER,
        6: EDIT_QUESTION_STATUS,
        7: BACK
    },
    MANAGE_SCORES: {
        1: VIEW_SCORES,
        2: DELETE_SCROE_HISTORY,
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

class Question:
    def __init__(self, content: dict):
        self.content = content
        self.status = UNANSWERED

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


class Run:
    def __init__(self):
        pass
    
    # def get_categories(self) -> dict[str, str]:
    #     pass
    
    # def generate_all_question_banks(self) -> dict[str, Question_Bank]:
    #     pass


class Session:
   
    # ======================
    # INITIALIZATION
    # ======================

    def __init__(self):
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
        choice = get_user_choice_from_menu(CHOICES)
        actions = {
            1: self.route_player_management_menu_actions,
            2: "placeholder",
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
        choice = get_user_choice_from_menu(CHOICES[MANAGE_PLAYERS], numbered=True)
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
    
    def back(self):
        return False

    def exit(self):
        return False

    # ======================
    # PLAYER MANAGEMENT
    # ======================

    def add_player(self) -> None:
        fresh_player = Player()
        fresh_player.edit_player_name({player.name for player in self.existing_players})
        fresh_player.edit_player_age()
        self.existing_players.add(fresh_player)

    def edit_player(self) -> None:
        player = self.get_user_choice_of_single_player()
        existing_players = {p.name for p in self.existing_players if p != player}
        player.edit_player_name(existing_players)
        player.edit_player_age()

    def remove_player(self) -> None:
        player = self.get_user_choice_of_single_player()
        self.existing_players.discard(player)

    def view_players(self) -> None:
        player_list = sorted(self.existing_players, key=lambda p: p.name)
        for index, player in enumerate(player_list):
            print(f"{index + 1}. Name: {player.name}, Age: {player.age}")
    


def main():
    session = Session()
    session.greet_user()
    running = True
    while running:
        running = session.route_main_menu_actions()


if __name__ == "__main__":
    main()