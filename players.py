"""The Player data model and its pure logic"""

from datetime import date
from pydantic import BaseModel, Field, computed_field
from uuid import uuid4


class Player(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    birth_date: tuple[date.year, date.month] = Field(
        description="Birth year and month of player."
    )
    name: str = Field(description="Name of player.")
    total_questions_answered: int = Field(default=0)
    total_questions_correctly_answered: int = Field(default=0)

    @computed_field
    @property
    def years_old(self) -> int:
        today = date.today()
        birth_year, birth_month = self.birth_date
        total_months = (
            ((today.year - birth_year) * 12) + (today.month - birth_month)
        )
        years_old = total_months//12
        return years_old

    @computed_field
    @property
    def age_bucket(self) -> str:
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
        if is_correct:
            self.total_questions_answered += 1
            self.total_questions_correctly_answered += 1
        else:
            self.total_questions_answered += 1