"""
The Question data model and all of its pure logic.
"""

from pydantic import BaseModel, Field, computed_field

UNANSWERED = "Unanswered"
CORRECTLY_ANSWERED = "Correctly Answered"
INCORRECTLY_ANSWERED = "Incorrectly Answered"

VALID_STATUSES = {
    UNANSWERED,
    CORRECTLY_ANSWERED,
    INCORRECTLY_ANSWERED
}


class Question(BaseModel):
    question: str = Field(description="The question text")
    answer: str = Field(description="The correct answer")
    fake_answers: list[str] = Field(
        description="3 incorrect answers used as distractors in multiple choice"
    )
    status: str = UNANSWERED
    id: str = ""

    @computed_field
    @property
    def all_choices_shuffled(self) -> set[str]:
        """Return all answer options (correct + fakes) in random order
        """
        answer_set = {ans for ans in self.fake_answers}
        answer_set.add(self.answer)
        return answer_set
    
    def check_answer(self, user_input: str) -> bool:
        """Return True if user_input matches the correct answer
        """
        return user_input.strip().lower() == self.answer.strip().lower()