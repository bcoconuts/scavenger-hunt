"""Persistence: save and load the full game state to and from JSON.

The only module that touches the save file on disk. Uses Pydantic to dump
models to JSON-safe dicts and to validate them back into real objects on load,
so dates and other types round-trip correctly.
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


def save_session(existing_players: list[Player], player_id_to_qbank_lookup: dict[str, QuestionBank | None]) -> None:
    """Write all players and their question banks to the save file as JSON.

    Each player is stored with their bank (or null if they have none). Uses
    Pydantic's mode="json" dump so dates serialize as ISO strings.
    """
    session_dict = {}
    for index, player in enumerate(existing_players):
        session_dict[index] = {}
        session_dict[index][S.PLAYER] = player.model_dump(mode="json")
        qbank = player_id_to_qbank_lookup.get(player.player_id)
        if qbank:
            session_dict[index][S.QBANK] = qbank.model_dump(mode="json")
        else:
            session_dict[index][S.QBANK] = qbank
    with open(FILE_NAMES[S.PLAYER_FILE_NAME], "w") as f:
        json.dump(session_dict, f, indent=4)


def load_session() -> Session:
    """Build a Session from the save file, or a fresh one if no file exists.

    Validates each stored player and bank back into model objects and rebuilds
    the player-to-qbank lookup. Returns an empty Session on FileNotFoundError.
    """
    try:
        with open(FILE_NAMES[S.PLAYER_FILE_NAME], "r") as f:
            session_dict: dict[str, dict] = json.load(f)
            session = Session()
            for k in session_dict:
                player: Player = Player.model_validate(session_dict[k][S.PLAYER])
                qbank: QuestionBank | None = session_dict[k][S.QBANK]
                session.existing_players.append(player)
                if qbank:
                    session.player_id_to_question_bank_lookup[player.player_id] = QuestionBank.model_validate(qbank)
                else:
                    session.player_id_to_question_bank_lookup[player.player_id] = qbank
    except FileNotFoundError:
        session = Session()
    
    return session