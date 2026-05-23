"""Return stuctured response from Grok via xAI API for a question bank object 
with a specified number of question objects contained in it.
and assign unique identifiers to each question object generated.
"""

from constants import DEBUG
from models import QuestionBank
from utils import generate_unique_id
from xai_sdk import Client
from xai_sdk.chat import user


def generate_questions(
        client: Client, age_bucket: str,
        category: str, run_length: int,
        existing_question_ids: set[str]
    ) -> QuestionBank:

    chat = client.chat.create(model="grok-latest")

    chat.append(user(
            f"Generate {run_length} trivia questions.\n"
            f"Questions aimed at {age_bucket}\n"
            f"Category for questions: {category}."
        )
    )

    # The parse method returns a tuple of the full response object as well as the parsed pydantic object.

    try:
        response, question_bank = chat.parse(QuestionBank)
        for q in question_bank.question_list:
            q.question_id = generate_unique_id(existing_question_ids)
    except Exception as e:
        print("Something went wrong with question generation. Please try again")
        if DEBUG: print(e)
        question_bank = QuestionBank(category="General")

    return question_bank