"""The UI protocol: the interface every UI implementation must satisfy.
"""

from typing import Protocol
from datetime import date


class UI(Protocol):

    # ======================
    # SPECIFIC OUTPUT
    # ======================

    def greet_user(self) -> None: ...


    # ======================
    # GENERIC OUTPUT
    # ======================

    def display_msg(self, msg: str) -> None: ...

    def display_attributes_for_object(self, header: str, seq_number: int | None = None, **kwargs: str | int | bool | list[str]) -> None: ...


    # ======================
    # SPECIFIC I/O
    # ======================

    def get_player_name(self, existing_names: set[str]) -> str: ...

    def get_birth_date(self, player_name: str) -> date: ...

    def get_scanned_id(self) -> str: ...

    def prompt_ask_answer(self, question_content: str, answer: str) -> bool: ...

    def prompt_multiple_choice_answer(self, question_content: str, all_answers: list[str]) -> str: ...


    # ======================
    # GENERIC I/O
    # ======================

    def get_user_str_input(self, prompt: str) -> str: ...

    def get_user_int_input(self, max_choice: int, prompt: str, min_choice: int=1) -> int: ...

    def get_user_str_choice_from_menu(self, target_dict: dict, header="OPTIONS") -> str: ...

    def warn_user(self, warning_msg: str) -> bool: ...