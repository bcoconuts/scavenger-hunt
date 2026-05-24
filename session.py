"""
Session class for scavanger hunt that manages data models
"""

import os
from constants import (
    STRINGS as S,
)
from dotenv import load_dotenv
from models import (
    Question,
    QuestionBank,
    Player
)
from typing import Callable
from xai_sdk import Client


class Session:

    # ======================
    # INITIALIZATION
    # ======================

    def __init__(self):
        load_dotenv()
        self.client: Client = Client(api_key=os.getenv("XAI_API_KEY"))
        self.existing_players: list[Player] = []
        self.player_id_to_question_bank_lookup: dict[str, QuestionBank | None] = {} # Player.player_id -> QuestionBank.


    # ======================
    # DATA
    # ======================

    def get_qbank(self, player: Player) -> QuestionBank:
        qbank = self.player_id_to_question_bank_lookup.get(player.player_id)
        if qbank is None:
            raise KeyError(f"No questions assigned to {player.name}")
        else:
            return qbank
        
    def has_qbank(self, player: Player) -> bool:
        """Predicate: does this player have questions assigned?"""
        return self.player_id_to_question_bank_lookup.get(player.player_id) is not None

    def playername_player_dict(self, filter: Callable[[Player], bool] | None=None) -> dict[str, Player] | None:
        """Return a dict of player.name: Player if any exist in existing players, else return None.
        Filterable to only build dict of players that matches filter condition.
        """
        if filter is None:
            return {p.name: p for p in self.existing_players}
        return {p.name: p for p in self.existing_players if filter(p)}
    
    def player_name_set(self, filter: Callable[[Player], bool] | None=None) -> set[str]:
        """Return a set of existing player names if any exist in existing players, else return None.
        Filterable to only build set of players that matches filter condition.
        """
        if filter is None:
            return {p.name for p in self.existing_players}
        return {p.name for p in self.existing_players if filter(p)}

    def all_existing_question_ids(self) -> set[str]:
        ids = set()
        qbanks = [self.get_qbank(p) for p in self.existing_players if self.has_qbank(p)]
        for qbank in qbanks:
            question_ids = qbank.question_id_list()
            for q_id in question_ids:
                ids.add(q_id)
        return ids

    def all_question_id_to_player_dict(self) -> dict[str, Player]:
        question_id_to_player_dict = dict()
        player_qbank_list = [(p, self.get_qbank(p)) for p in self.existing_players if self.has_qbank(p)]
        for p, qbank in player_qbank_list:
            question_ids = qbank.question_id_list()
            for q_id in question_ids:
                question_id_to_player_dict[q_id] = p
        return question_id_to_player_dict
    
    def eligible_question_id_to_question_dict(self) -> dict[str, Question]:
        question_id_to_question_dict = dict()
        qbanks = [self.get_qbank(p) for p in self.existing_players if self.has_qbank(p)]
        for qbank in qbanks:
            qbank_id_dict = qbank.eligible_question_id_map()
            question_id_to_question_dict.update(qbank_id_dict)
        return question_id_to_question_dict

    # ======================
    # PLAYER MANAGEMENT
    # ======================

    def add_player(self, player: Player) -> None:
        self.existing_players.append(player)
        self.player_id_to_question_bank_lookup[player.player_id] = None

    def remove_player(self, player: Player) -> None:
        self.existing_players.remove(player)
        self.player_id_to_question_bank_lookup.pop(player.player_id, None)

    # ======================
    # QBANK MANAGEMENT
    # ======================

    def process_new_qbank(self, player: Player, qbank: QuestionBank) -> None:
        self.player_id_to_question_bank_lookup[player.player_id] = qbank