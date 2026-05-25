"""The Session class: the in-memory hub for all players and their question banks.

Session owns the live collections (the player list and the player-to-qbank
lookup) and is the single place responsible for keeping them consistent. It
exposes queries and derived views for the workflows to read, plus narrow
mutation methods for adding/removing players and assigning question banks. It
performs no terminal I/O. The xAI client lives here because question
generation needs it, but Session never calls it directly — workflows do.
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
        """Return the player's question bank, or raise KeyError if they have none.

        The non-optional return type lets callers use the result directly; guard
        with has_qbank first when a player might not have one.
        """
        qbank = self.player_id_to_question_bank_lookup.get(player.player_id)
        if qbank is None:
            raise KeyError(f"No questions assigned to {player.name}")
        else:
            return qbank
        
    def has_qbank(self, player: Player) -> bool:
        """Predicate: does this player have questions assigned?"""
        return self.player_id_to_question_bank_lookup.get(player.player_id) is not None

    def playername_player_dict(self, filter: Callable[[Player], bool] | None=None) -> dict[str, Player]:
        """Return {player_name: Player} for all players, or those matching filter.

        Returns an empty dict if no players qualify. Used to build a selectable
        menu of players.
        """
        if filter is None:
            return {p.name: p for p in self.existing_players}
        return {p.name: p for p in self.existing_players if filter(p)}
    
    def player_name_set(self, filter: Callable[[Player], bool] | None=None) -> set[str]:
        """Return the set of player names, or those matching filter.

        Returns an empty set if no players qualify. Used to enforce unique names.
        """
        if filter is None:
            return {p.name for p in self.existing_players}
        return {p.name for p in self.existing_players if filter(p)}

    def all_existing_question_ids(self) -> set[str]:
        """Return every question_id across all players' banks.

        Used when generating new questions to avoid assigning a colliding id.
        """
        ids = set()
        qbanks = [self.get_qbank(p) for p in self.existing_players if self.has_qbank(p)]
        for qbank in qbanks:
            question_ids = qbank.question_id_list()
            for q_id in question_ids:
                ids.add(q_id)
        return ids

    def all_question_id_to_player_dict(self) -> dict[str, Player]:
        """Return {question_id: owning Player} across all banks.

        A derived lookup built fresh for gameplay, letting a scanned id resolve to
        the player it belongs to.
        """
        question_id_to_player_dict = dict()
        player_qbank_list = [(p, self.get_qbank(p)) for p in self.existing_players if self.has_qbank(p)]
        for p, qbank in player_qbank_list:
            question_ids = qbank.question_id_list()
            for q_id in question_ids:
                question_id_to_player_dict[q_id] = p
        return question_id_to_player_dict
    
    def eligible_question_id_to_question_dict(self) -> dict[str, Question]:
        """Return {question_id: Question} for unanswered questions across all banks.

        A derived lookup built fresh for gameplay; answered questions are excluded
        so they can't be scanned again. Callers pop entries as questions are played.
        """
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
        """Add a player and register a (None) question-bank slot for them."""
        self.existing_players.append(player)
        self.player_id_to_question_bank_lookup[player.player_id] = None

    def remove_player(self, player: Player) -> None:
        """Remove a player and drop their question-bank lookup entry."""
        self.existing_players.remove(player)
        self.player_id_to_question_bank_lookup.pop(player.player_id, None)

    # ======================
    # QBANK MANAGEMENT
    # ======================

    def process_new_qbank(self, player: Player, qbank: QuestionBank) -> None:
        """Assign (or replace) a player's question bank."""
        self.player_id_to_question_bank_lookup[player.player_id] = qbank