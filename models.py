"""The data models and their pure logic"""

from datetime import date
from pydantic import BaseModel, Field, computed_field
from uuid import uuid4
import random

UNANSWERED = "Unanswered"
CORRECTLY_ANSWERED = "Correctly Answered"
INCORRECTLY_ANSWERED = "Incorrectly Answered"

VALID_STATUSES = {
    UNANSWERED,
    CORRECTLY_ANSWERED,
    INCORRECTLY_ANSWERED
}


class Question(BaseModel):
    """
    Question class meant to serve as a question object 
    for each question that might be assigned to a player. 
    
    Attribute question_id is purposefully left bare 
    because Grok will attempt and often fail to assign a unique identifier.
    question_id shall be set immediately after instantiation.
    """
    question: str = Field(description="The question text")
    answer: str = Field(description="The correct answer")
    fake_answers: list[str] = Field(
        description="3 incorrect answers used as distractors in multiple choice"
    )
    status: str = Field(
        default=UNANSWERED,
        description="The status of the question"
    )
    question_id: str = ""

    def all_choices_shuffled(self) -> list[str]:
        """Return all answer options (correct + fakes) in random order
        """
        choices = self.fake_answers + [self.answer]
        random.shuffle(choices)
        return choices
    
    def check_answer(self, user_input: str) -> bool:
        """Return True if user_input matches the correct answer
        """
        return user_input.strip().lower() == self.answer.strip().lower()


class QuestionBank(BaseModel):
    """
    QuestionBank class meant to serve as a collector object 
    for each set of questions that might be assigned to a player. 
    """
    question_list: list[Question] = Field(
        default_factory=list, description="List of questions in the bank"
    )
    category: str = Field(description="The category of the list of questions")
    
    def retrieve_question(self, unique_identifier: str) -> Question:
        """Return a question for a given question identifier
        """
        question_dict = {q.question_id: q for q in self.question_list}
        question = question_dict[unique_identifier]
        return question
    
    def question_map(self) -> dict[str, Question]:
        """Return a dict whose keys are question identification numbers, 
        and whose values are the Question object they are attached to.
        """
        question_map = {q.question_id: q for q in self.question_list}
        return question_map

    def question_id_list(self) -> list[str]:
        question_id_list = [q.question_id for q in self.question_list]
        return question_id_list


class Player(BaseModel):
    player_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier of the player"
    )
    birth_date: date = Field(
        description="Birth year, month, and day of player."
    )
    name: str = Field(description="Name of player.")
    total_questions_answered: int = Field(
        default=0, 
        description="Value of all questions attempted "
        "since the player instance has been instantiated."
    )
    total_questions_correctly_answered: int = Field(
        default=0,
        description="Value of all questions answered correctly "
        "since the player instance has been instantiated."
    )

    @computed_field
    @property
    def years_old(self) -> int:
        "Calculate age of player in years and return it"
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    @computed_field
    @property
    def age_bucket(self) -> str:
        """Return a description of the player's knowledge group 
        based upon players age in years"""
        if self.years_old <= 3:
            return (
                "a bright toddler aged 2-3. They know basic colors, can count to 10+, "
                "know common animals and their sounds, and understand simple stories. "
                "Questions should challenge the top 25 percent of kids this age — not softballs."
            )
        elif self.years_old <= 5:
            return (
                "a bright, well-educated preschooler aged 4-5. They are beginning to read, "
                "know numbers past 20, understand basic opposites, seasons, and simple science "
                "Questions should challenge the top 25 percent of kids this age — not softballs."
            )
        elif self.years_old <= 7:
            return (
                "a bright, well-educated early elementary child aged 6-7. They can read simple "
                "books, do basic addition and subtraction, and know geography basics. "
                "Questions should challenge the top 25 percent of kids this age — not softballs."
            )
        elif self.years_old <= 10:
            return (
                "a bright, well-educated elementary child aged 8-10. They read fluently, "
                "understand basic history, multiplication, and science concepts. "
                "Questions should challenge the top 25 percent of kids this age — not softballs."
            )
        elif self.years_old <= 13:
            return (
                "a bright, well-educated preteen aged 11-13. They have solid general knowledge "
                "across history, science, geography and literature. "
                "Questions should genuinely challenge the top 25 percent of kids this age."
            )
        elif self.years_old <= 18:
            return (
                "a teenager aged 14-18. They have solid general knowledge "
                "across history, science, math, geography and literature. "
                "Questions should genuinely challenge the top 25 percent of kids this age."
            )
        elif self.years_old <= 22:
            return (
                "a college educated person aged 19-22. They have solid general knowledge "
                "across history, science, math, geography and literature. "
                "Questions should genuinely challenge the top 25 percent of people this age."
            )
        else:
            return (
                "an adult with a college eductaion. They have solid general knowledge "
                "across history, science, math, geography and literature. "
                "Questions should genuinely challenge the top 50 percent of college educated adults."
            )
        
    def record_attempt(self, is_correct: bool) -> None:
        """Update values of score history attributes 
        given if the player got an answer correct.
        """
        self.total_questions_answered += 1
        if is_correct:
            self.total_questions_correctly_answered += 1