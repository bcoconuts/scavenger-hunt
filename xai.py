"""Return stuctured response from Grok via xAI API for a question bank object 
with a specified number of question objects contained in it.
and assign unique identifiers to each question object generated.
"""

from constants import DEBUG
from models import (
    QuestionBank,
    Player
)
from random import randint
from xai_sdk import Client
from xai_sdk.chat import user


def generate_questions(
        client: Client, player: Player,
        category: str, run_length: int,
        existing_question_ids: set[str]
    ) -> QuestionBank:

    chat = client.chat.create(model="grok-latest")

    chat.append(user(f"""\
Generate {run_length} trivia questions.

Questions aimed at {player.age_bucket} 

Category for questions: {category}."""
        )
    )

    # The parse method returns a tuple of the full response object as well as the parsed pydantic object.

    try:
        response, question_bank = chat.parse(QuestionBank)
        for q in question_bank.question_list:
            q.question_id = _generate_id(existing_question_ids)
    except Exception as e:
        print("Something went wrong with question generation. Please try again")
        if DEBUG: print(e)
        question_bank = QuestionBank(category="General")

    return question_bank


def _generate_id(existing_question_ids: set) -> str:
    while True:
        new_id = str(randint(10000000, 99999999))
        if new_id not in existing_question_ids:
            existing_question_ids.add(new_id)
            return new_id