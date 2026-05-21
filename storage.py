"""
Handle save and load operations.
"""

from constants import (
    STRINGS as S,
    FILE_NAMES
)
from models import (
    QuestionBank,
    Player
)
from session import Session
import json


def save_session(existing_players: list[Player], player_id_to_qbank_lookup: dict[str, QuestionBank]) -> None:
    session_dict = {}
    for index, player in enumerate(existing_players):
        session_dict[index] = {"player": player.model_dump(), "qbank": player_id_to_qbank_lookup[player.player_id].model_dump()}
    with open(FILE_NAMES[S.PLAYER_FILE_NAME], "w") as f:
        json.dump(session_dict, f, indent=4)


def load_session() -> Session:
    try:
        with open(FILE_NAMES[S.PLAYER_FILE_NAME], "r") as f:
            session_dict: dict[str, dict] = json.load(f)
            session = Session()
            for k in session_dict:
                player: Player = session_dict[k]["player"]
                qbank: QuestionBank = session_dict[k]["qbank"]
                session.existing_players.append(Player.model_validate(player))
                session.player_id_to_question_bank_lookup[player.player_id] = QuestionBank.model_validate(qbank)
    except FileNotFoundError:
        session = Session()
    
    return session