import os
from dotenv import load_dotenv
from datetime import date
from pydantic import BaseModel, Field
from xai_sdk import Client
from xai_sdk.chat import user, system

load_dotenv()

# Pydantic Schemas

class Question(BaseModel):
    question_number: int = Field(description="Number of question generated")
    question: str = Field(description="Question")
    answer: str = Field(description="Answer")
    fake_answers: list[str] = Field(description="List of incorrect answers for the question, used for multiple choice")

class Question_Bank(BaseModel):
    question_list: list[Question] = Field(description="List of the questions generated")
    qty: int = Field(description="Quantity of question generated")
    category: str = Field(description="Category of the questions generated")
    date_generated: date = Field(description="Date the questions were generated")

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(model="grok-latest")

chat.append(system("You are Grok, A teacher who tries to push people past their comfort zone."))
chat.append(
user("""
Generate a question bank of 10 questions for a 4 year, 10 month old person. The category for the questions is animals.
""")
)

# The parse method returns a tuple of the full response object as well as the parsed pydantic object.

response, question_bank = chat.parse(Question_Bank)
assert isinstance(question_bank, Question_Bank)

# Can access fields of the parsed invoice object directly

# print(invoice.vendor_name)
# print(invoice.invoice_number)
# print(invoice.invoice_date)
# print(invoice.line_items)
# print(invoice.total_amount)
# print(invoice.currency)

# Can also access fields from the raw response object such as the content.

# In this case, the content is the JSON schema representation of the parsed invoice object

print(response.content)