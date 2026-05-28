"""Domain models for the scavenger hunt: Question, QuestionBank, and Player.

These are the core data types the rest of the app is built around. They hold
state and the rules tightly bound to that state (age calculation, answer
checking, score adjustment) but perform no I/O — no printing, prompting, file
access, or network calls. This module depends only on constants; everything
else depends on it.
"""

from constants import (
    STRINGS as S,
)
from datetime import date
from pydantic import BaseModel, Field, computed_field
from uuid import uuid4
import random


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
        default=S.UNANSWERED,
        description="The status of the question"
    )
    question_id: str = ""

    def all_choices_shuffled(self) -> list[str]:
        """Return the correct answer plus fake answers in randomized order.

        Shuffled so the correct answer's position varies between presentations.
        """
        choices = self.fake_answers + [self.answer]
        random.shuffle(choices)
        return choices
    
    def check_answer(self, user_input: str) -> bool:
        """Return True if user_input matches the correct answer
        """
        return user_input.strip().lower() == self.answer.strip().lower()
    
    def update_status(self, is_correct: bool) -> None:
        """Set status to CORRECTLY_ANSWERED or INCORRECTLY_ANSWERED per is_correct."""
        if is_correct:
            self.status = S.CORRECTLY_ANSWERED
        else:
            self.status = S.INCORRECTLY_ANSWERED



class QuestionBank(BaseModel):
    """
    QuestionBank class meant to serve as a collector object 
    for each set of questions that might be assigned to a player. 
    """
    question_list: list[Question] = Field(
        default_factory=list, description="List of questions in the bank"
    )
    category: str = Field(description="The category of the list of questions")
    
    def retrieve_question_by_id(self, unique_identifier: str) -> Question:
        """Return the Question with the given question_id. Raises KeyError if absent."""
        question_dict = {q.question_id: q for q in self.question_list}
        question = question_dict[unique_identifier]
        return question
    
    def eligible_question_id_map(self) -> dict[str, Question]:
        """Return {question_id: Question} for UNANSWERED questions only.

        Builds the pool of still-playable questions for a game session; answered
        questions are excluded so they can't be scanned again.
        """
        question_map = {q.question_id: q for q in self.question_list if q.status == S.UNANSWERED}
        return question_map
    
    def question_content_to_id_map(self) -> dict[str, str]:
        """Return {question_text: question_id}.

        Lets the UI offer questions by their readable text while the caller
        resolves the choice back to a unique id, since question text is not
        guaranteed to be unique but ids are.
        """
        question_map = {q.question: q.question_id for q in self.question_list}
        return question_map

    def question_id_list(self) -> list[str]:
        """Return a list of every question_id in the bank, in list order."""
        question_id_list = [q.question_id for q in self.question_list]
        return question_id_list
    
    def remove_question(self, question: Question) -> None:
        """Remove the given question from the bank."""
        self.question_list.remove(question)

    def score(self) -> tuple[int, int, int]:
        """Return this bank's score as (total, correct, attempted).

        total     - number of questions in the bank
        correct   - questions whose status is CORRECTLY_ANSWERED
        attempted - questions answered either correctly or incorrectly
                    (i.e. excludes UNANSWERED)
        """
        correct = 0
        attempted = 0
        for q in self.question_list:
            if q.status == S.CORRECTLY_ANSWERED:
                correct += 1
                attempted += 1
            elif q.status == S.INCORRECTLY_ANSWERED:
                attempted += 1
        return len(self.question_list), correct, attempted




class Player(BaseModel):
    """A player and their lifetime score history.

    Stores identity (id, name, birth_date) and all-time tallies. Age is
    computed from birth_date rather than stored, so it never goes stale.
    """
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
        """Return the player's age in whole years, computed from birth_date."""
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
                "know common animals and their sounds, and understand very simple stories. "
            )
        elif self.years_old <= 5:
            return (
                "a bright, well-educated preschooler aged 4-5. They are beginning to read, "
                "know numbers past 20, understand basic opposites, seasons, and simple science "
            )
        elif self.years_old <= 7:
            return (
                "a bright, well-educated early elementary child aged 6-7. They can read simple "
                "books, do basic addition and subtraction, and know geography basics. "
            )
        elif self.years_old <= 10:
            return (
                "a bright, well-educated elementary child aged 8-10. They read fluently, "
                "understand basic history, multiplication, and science concepts. "
            )
        elif self.years_old <= 13:
            return (
                "a bright, well-educated preteen aged 11-13. They have solid general knowledge "
                "across history, science, geography and literature. "
            )
        elif self.years_old <= 18:
            return (
                "a teenager aged 14-18. They have solid general knowledge "
                "across history, science, math, geography and literature. "
            )
        elif self.years_old <= 22:
            return (
                "an adult aged 19-22. They have solid general knowledge "
                "across history, science, math, geography and literature. "
            )
        else:
            return (
                "an adult with a college eductaion. They have solid general knowledge "
                "across history, science, math, geography and literature. "
            )
        
    def record_attempt(self, is_correct: bool) -> None:
        """Update values of score history attributes 
        given if the player got an answer correct.
        """
        self.total_questions_answered += 1
        if is_correct:
            self.total_questions_correctly_answered += 1
    
    def adjust_attempt(self, old_status: str, new_status: str) -> None:
        """Adjust all-time score counters when a question's status is edited by hand.

        Treats a hand-edit as moving an attempt into or out of score history:
        editing away from UNANSWERED adds an attempt, editing toward UNANSWERED
        removes one, and switching between correct and incorrect adjusts only the
        correct counter. Keeps total and correct counts consistent with the
        question's new status.

        Note: the caller must read the question's status BEFORE reassigning it,
        then pass the old and new values here.
        """
        if old_status == S.UNANSWERED:
            self._add_attempt(new_status)
        elif old_status != S.UNANSWERED:
            self._delete_attempt(old_status, new_status)
    
    def _add_attempt(self, new_status: str) -> None:
        """Increment counters for a question moving from UNANSWERED to a graded status."""
        if new_status == S.CORRECTLY_ANSWERED:
            self.total_questions_answered += 1
            self.total_questions_correctly_answered += 1
        elif new_status == S.INCORRECTLY_ANSWERED:
            self.total_questions_answered += 1
        else:
            return # in case someone changed from unanswered to unanswered status
    
    def _delete_attempt(self, old_status: str, new_status: str) -> None:
        """Adjust counters for a question moving away from its previous graded status."""
        if old_status == S.CORRECTLY_ANSWERED and new_status == S.INCORRECTLY_ANSWERED:
            self.total_questions_correctly_answered -= 1
        elif old_status == S.CORRECTLY_ANSWERED and new_status == S.UNANSWERED:
            self.total_questions_answered -= 1
            self.total_questions_correctly_answered -= 1
        elif old_status == S.INCORRECTLY_ANSWERED and new_status == S.CORRECTLY_ANSWERED:
            self.total_questions_correctly_answered += 1
        else:
            return # in case someone swaps from incorrect to incorrect or correct to correct