"""Question generation via the xAI (Grok) API.

Calls Grok with structured output to produce a QuestionBank, then stamps each
question with a unique id. Producing a QuestionBank is this module's whole job,
so its dependency on that type is expected. On failure it returns an empty
QuestionBank rather than raising.
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
    ) -> QuestionBank | None:
    """Generate run_length trivia questions for an age bucket and category.

    Asks Grok to return a QuestionBank via structured output, then assigns each
    question a unique id not already in existing_question_ids. On any API or
    parsing error, prints a message and returns an empty QuestionBank.
    """

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
            existing_question_ids.add(q.question_id)
    except Exception as e:
        if DEBUG: print(e)
        question_bank = None
    return question_bank