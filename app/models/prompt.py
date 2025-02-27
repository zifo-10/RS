from pydantic import BaseModel, Field


class Prompt(BaseModel):
    user: str = Field(description="The user's query.")
    system: str = Field(description="The system's response.")
