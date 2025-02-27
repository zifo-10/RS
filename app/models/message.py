from pydantic import BaseModel, Field


class Message(BaseModel):
    question: str = Field(description="The question to add.")
    answer: str = Field(description="The answer to add.")