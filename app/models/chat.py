from typing import Optional

from pydantic import BaseModel, Field


class Chat(BaseModel):
    query: str = Field(description="The query to search for.")
    limit: Optional[int] = Field(description="The maximum number of results to return.", default=10)
    score_threshold: Optional[float] = Field(description="The minimum score threshold for search results.", default=0.3)
    filters: Optional[dict] = Field(description="The filters to apply to the search results.", default=None)
    search: Optional[bool] = Field(description="Whether to perform a web search.", default=False)
    conversation_id: Optional[str] = Field(description="The conversation ID to track the chat history.", default=None)
